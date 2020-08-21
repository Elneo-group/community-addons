# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    
#    Copyright (c) 2013 Noviat nv/sa (www.noviat.be). All rights reserved.
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Datetime widget custo',
    'version': '1.0',
    'license': 'AGPL-3',
    'author': 'Noviat SA',
    'website': 'http://www.noviat.com',
    'category': '',
    'description': """
        A new widget datetime.

        instead of having the datetime widget, we replace it by a  "date field",
        "hour select field" and "min select field"

        options="{'minute_type': 'quarter'}" widget="datetime_custo"

        Add this on a datetime field: widget="datetime_custo"

        Options:

        'minute_type': 'quarter' -> default value
        'minute_type': 'all'

        Range : Min and max date allowed:
        - Either you specify a date field OR directly a date
        context="{'mindate':task_date_from, 'maxdate':task_date_to}"
        context="{'mindate':'2015-05-01', 'maxdate':'2015-10-01'}"
        - or you specify a context key for min and max date
          context="{'ctx_mindate': 'task_date_from', 'ctx_maxdate': 'task_date_to'}"


    """,
    'depends': [
        'web',
    ],
    'data': [
        'view/view.xml',
    ],
    'qweb': [
        'static/src/xml/datetime.xml',
    ],
    'installable': True,
}
