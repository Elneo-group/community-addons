# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) 2009-2016 Noviat nv/sa (www.noviat.com).
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

from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _default_intrastat_transaction(self):
        transaction = super(
            AccountInvoice, self)._default_intrastat_transaction()
        if not transaction:
            cpy_id = self.env[
                'res.company']._company_default_get('account.invoice')
            cpy = self.env['res.company'].browse(cpy_id)
            if cpy.country_id.code.lower() == 'be':
                module = __name__.split('addons.')[1].split('.')[0]
                transaction = self.env.ref(
                    '%s.intrastat_transaction_1' % module)
        return transaction
