# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Noviat nv/sa (www.noviat.com). All rights reserved.
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

{
    'name': 'Belgian Invoice Layout',
    'version': '0.2',
    'license': 'AGPL-3',
    'author': 'Noviat',
    'website': 'http://www.noviat.com',
    'category': 'Localization/Accounting',
    'summary': 'Belgian Invoice Layout',
    'depends': [
        'account',
        'l10n_be_partner',
    ],
    'data': [
        'account_report.xml',
        'views/report_be_invoice.xml',
        'views/report_be_invoice_style.xml',
        'views/report_be_invoice_layout.xml',
    ],
}
