# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014-now Noviat nv/sa (www.noviat.com).
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
    'name': 'Sale order Attachments',
    'version': '0.1',
    'author': 'Noviat',
    'website': 'http://www.noviat.com',
    'category': 'Sale',
    'complexity': 'normal',
    'description': """
Sale Order Attachments
======================

- Add extra page to Sale Order notebook to store documents with metadata.

    """,
    'depends': [
        'sale',
        #'web_fix_binaryfile',  # fix onchange on binary fields
    ],
    'data': [
        'security/ir.model.access.csv',
        'sale_order_view.xml',
    ],
}
