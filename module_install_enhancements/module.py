# -*- coding: utf-8 -*-
#############
#
# By Noviat 2014
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
#############

from openerp.osv import osv


class module(osv.osv):
    _name = "ir.module.module"

    _inherit = 'ir.module.module' 
    
    _order = 'name,sequence'