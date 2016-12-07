# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012-2015 Noviat nv/sa (www.noviat.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.osv.fields import datetime as datetime_field
from openerp.exceptions import Warning
from datetime import datetime


class overdue_payment_wizard(models.TransientModel):
    _name = 'overdue.payment.wizard'
    _description = 'Print Overdue Payments'

    def init(self, cr):
        """
        disable standard overdue print
        """
        cr.execute(
            "UPDATE ir_values "
            "SET key2='#client_print_multi' "
            "WHERE name='Due Payments' "
            "AND model='res.partner' "
            "AND value LIKE 'ir.actions.report.xml,%' "
            "AND key2='client_print_multi';")

    @api.model
    def _partner_select_default(self):
        active_ids = self._context.get('active_ids')
        if active_ids and len(active_ids) > 1:
            return 'all'
        else:
            return 'select'

    @api.model
    def _get_company(self):
        return self.env.user.company_id

    partner_select = fields.Selection([
        ('all', 'All Customers'),
        ('select', 'Selected Customers'),
        ], string='Partners', required=True,
        default=_partner_select_default)
    account_select = fields.Selection([
        ('receivable', 'Receivable Accounts'),
        ('all', 'Receivable and Payable Accounts')],
        string='Selected Accounts', required=True, default='receivable')
    # company_id not on UI in the current release of this module
    # user needs to switch to new company to send overdue letters
    # in multi-company environment
    company_id = fields.Many2one(
        'res.company', string='Company', readonly=True,
        default=_get_company)

    @api.multi
    def overdue_payment_print(self):
        """
        Select AR/AP moves and remove partially reconciled
        receivables/payables since these are on the report
        via the 'Amount Paid'.

        The following logic is used for this removal;
        Receivables: keep only Credit moves
        Payables: keep only Debit moves
        """

        def remove_filter(line):
            if line['reconcile_partial_id']:
                if line['type'] == 'receivable' and line['credit']:
                    return True
                elif line['type'] == 'payable' and line['debit']:
                    return True
            return False

        company = self.company_id
        partner_select = self.partner_select
        account_select = self.account_select

        if partner_select == 'select':
            partner_ids = self._context.get('active_ids', [])
            partners = self.env['res.partner'].browse(partner_ids)
        else:
            partners = self.env['res.partner'].search([])
        partners = set([x.commercial_partner_id for x in partners])

        open_partners = self.env['res.partner']
        open_moves = {}
        report_date = datetime_field.context_timestamp(
            self._cr, self._uid, datetime.now(), self._context).date()
        report_date = report_date.strftime('%Y-%m-%d')

        for partner in partners:

            self._cr.execute(
                "SELECT l.id, a.type, "
                "l.debit, l.credit, l.reconcile_partial_id, "
                "(CASE WHEN l.date_maturity IS NOT NULL THEN l.date_maturity "
                "ELSE ai.date_due END) AS date_maturity "
                "FROM account_move_line l "
                "INNER JOIN account_account a ON l.account_id = a.id "
                "INNER JOIN account_move am ON l.move_id = am.id "
                "LEFT OUTER JOIN account_invoice ai ON ai.move_id = am.id "
                "LEFT OUTER JOIN res_partner p ON l.partner_id = p.id "
                "WHERE l.partner_id = %s "
                "AND a.type IN ('receivable', 'payable') "
                "AND l.state != 'draft' AND l.reconcile_id IS NULL "
                "AND l.company_id = %s AND p.customer = TRUE "
                "AND (l.debit + l.credit) != 0 "
                "ORDER BY date_maturity",
                (partner.id, company.id)
            )
            all_lines = self._cr.dictfetchall()
            removes = filter(remove_filter, all_lines)
            remove_ids = [x['id'] for x in removes]
            lines = filter(lambda x: x['id'] not in remove_ids, all_lines)

            receivables = payables = []
            if account_select == 'receivable':
                receivables = filter(
                    lambda x: x['type'] == 'receivable', lines)
            if account_select == 'all':
                receivables = filter(
                    lambda x: x['type'] == 'receivable', lines)
                payables = filter(
                    lambda x: x['type'] == 'payable', lines)
                # remove payables which have been partially
                # reconciled with receivables
                ar_rec_partial_ids = [
                    x['reconcile_partial_id'] for x in filter(
                        lambda x: x['reconcile_partial_id'], receivables)]
                payables = filter(
                    lambda x: x['reconcile_partial_id'] not in
                    ar_rec_partial_ids, payables)

            # remove the partners with no entries beyond the maturity date
            overdues = filter(
                lambda x: x['date_maturity']
                and x['date_maturity'] <= report_date,
                receivables + payables)
            if not overdues:
                continue

            ar_ids = [x['id'] for x in receivables]
            ap_ids = [x['id'] for x in payables]
            if ar_ids or ap_ids:
                open_moves[str(partner.id)] = {
                    'ar_ids': ar_ids,
                    'ap_ids': ap_ids,
                }
                open_partners += partner

        if not open_partners:
            raise Warning(
                _('No Data Available'),
                _('No records found for your selection!'))

        datas = {
            'report_date': report_date,
            'company_id': company.id,
            'open_moves': open_moves,
        }

        return self.env['report'].get_action(
            open_partners, 'account_overdue.report_overdue',
            data=datas)
