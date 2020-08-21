# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from openerp import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(AccountMoveLine, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type,
            context=context, toolbar=toolbar, submenu=False)
        if context and 'account_move_line_search_extension' in context \
                and view_type in ['tree', 'form']:
            doc = etree.XML(res['arch'])
            tree = doc.xpath("/tree")
            for node in tree:
                if 'editable' in node.attrib:
                    del node.attrib['editable']
            form = doc.xpath("/form")
            for node in form:
                node.set('edit', 'false')
                node.set('create', 'false')
                node.set('delete', 'false')
            res['arch'] = etree.tostring(doc)
        return res

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        if context and 'account_move_line_search_extension' in context:
            ana_obj = self.pool['account.analytic.account']
            for arg in args:
                if (
                    arg[0] == 'analytic_account_id' and
                    isinstance(arg[0], basestring)
                ):
                    ana_dom = ['|',
                               ('name', 'ilike', arg[2]),
                               ('code', 'ilike', arg[2])]
                    ana_ids = ana_obj.search(
                        cr, uid, ana_dom, context=context)
                    ana_ids = ana_obj.search(
                        cr, uid, [('id', 'child_of', ana_ids)])
                    arg[2] = ana_ids
                    break
        return super(AccountMoveLine, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)
