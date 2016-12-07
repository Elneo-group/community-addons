# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Noviat nv/sa (www.noviat.com).
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

from openerp.osv import osv


class account_period(osv.osv):
    _inherit = 'account.period'

    def build_ctx_periods(self, cr, uid, period_from_id, period_to_id):
        """ add close periods """
        period_ids = super(account_period, self).build_ctx_periods(
            cr, uid, period_from_id, period_to_id)
        period_to = self.browse(cr, uid, period_to_id)
        period_date_stop = period_to.date_stop
        close_period_ids = self.search(
                cr, uid,
                [('date_stop', '=', period_date_stop),
                 ('special', '=', True),
                 ('company_id', '=', period_to.company_id.id)])
        for p in close_period_ids:
            if p not in period_ids:
                period_ids.append(p)
        return period_ids
