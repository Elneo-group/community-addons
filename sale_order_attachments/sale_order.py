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

from openerp.osv import fields, orm
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class sale_order(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'attachment_ids': fields.one2many(
            'sale.order.attachment', 'sale_order_id', 'Attachments'),
    }

    def unlink(self, cr, uid, ids, context=None):
        att_obj = self.pool.get('sale.order.attachment')
        for obj in self.browse(cr, uid, ids, context=context):
            att_ids = [x.id for x in obj.attachment_ids]
            if att_ids:
                att_obj.unlink(cr, uid, att_ids, context)
        return super(sale_order, self).unlink(cr, uid, ids, context)


class sale_order_attachment(orm.Model):
    _name = 'sale.order.attachment'
    _description = 'Object to store Sale Order Attachments'

    def _get_data(self, cr, uid, ids, name, arg, context=None):
        if not context:
            context = {}
        att_obj = self.pool.get('ir.attachment')

        # we only download the data on file_data_d in order to
        # optimise performance when no download is required
        ctx = context.copy()
        ctx['bin_size'] = True

        result = {}
        for pt_att in self.browse(cr, uid, ids, context=ctx):
            domain = [
                ('res_model', '=', 'sale.order.attachment'),
                ('res_id', '=', pt_att.id)]
            att_ids = att_obj.search(cr, uid, domain, context=context)
            if att_ids:
                att = att_obj.read(
                    cr, uid, att_ids,
                    ['datas_fname', 'datas', 'file_size'],
                    context=context)[0]
                size = att['file_size'] or 0.0
                if size < 1000000:
                    size_char = '%s bytes' % size
                else:
                    size_char = '%s kb' % int(round(size/1024.0))
                result[pt_att.id] = {
                    'file_name': att['datas_fname'],
                    'file_size': size,
                    'file_size_char': size_char,
                    'file_data': att['datas'],
                }
            else:
                result[pt_att.id] = {
                    'file_name': False,
                    'file_size': 0,
                    'file_size_char': '0 bytes',
                    'file_data': False,
                }
        return result

    def _get_datas(self, cr, uid, ids, name, arg, context=None):
        if not context:
            context = {}
        att_obj = self.pool.get('ir.attachment')
        result = {}
        for pt_att in self.browse(cr, uid, ids, context=context):
            domain = [
                ('res_model', '=', 'sale.order.attachment'),
                ('res_id', '=', pt_att.id)]
            att_ids = att_obj.search(cr, uid, domain, context=context)
            if att_ids:
                att = att_obj.read(
                    cr, uid, att_ids,
                    ['datas', 'file_size'],
                    context=context)[0]
                result[pt_att.id] = att['datas']
        return result

    def _store_file_data(self, cr, uid, att_id,
                         name, value, arg, context=None):
        att_obj = self.pool.get('ir.attachment')
        pt_att = self.browse(cr, uid, att_id, context=context)
        domain = [
            ('res_model', '=', 'sale.order.attachment'),
            ('res_id', '=', pt_att.id)]
        att_ids = att_obj.search(cr, uid, domain, context=context)
        if att_ids:
            raise orm.except_orm(
                _('Error!'),
                _("Programming error in module '%s', method '%s'")
                % (__name__, '_store_file_data'))
        else:
            vals = {
                'name': pt_att.file_name_shadow,
                'datas': value,
                'datas_fname': pt_att.file_name_shadow,
                'res_model': 'sale.order.attachment',
                'res_id': att_id,
            }
            att_obj.create(cr, uid, vals, context=context)
        return True

    def onchange_file_data(self, cr, uid, ids, file_name, context=None):
        return {'value': {'file_name_shadow': file_name}}

    _columns = {
        'sale_order_id': fields.many2one(
            'sale.order', 'Sale Order', ondelete='cascade', readonly=True),
        'sequence': fields.integer(
            'Sequence',
            help="Gives the sequence order when displaying "
                 "a list of attachments."),
        'name': fields.char('Description', size=256, required=True),
        'note': fields.html('Notes'),
        'file_name': fields.function(
            _get_data, string='File Name',
            type="char", size=256, multi='get'),
        'file_data': fields.function(
            _get_data, fnct_inv=_store_file_data,
            string='File', type="binary", multi='get'),
        'file_size': fields.function(
            _get_data, string='File Size',
            type="integer", readonly=True, multi='get'),
        'file_size_char': fields.function(
            _get_data, string='File Size',
            type="char", size=128, readonly=True, multi='get'),
        # used for download
        'file_data_d': fields.function(
            _get_datas, string='File', type="binary"),
        # filled in via on_change on file_name
        'file_name_shadow': fields.char('File Name', size=256),
    }

    _order = 'sequence'
    _defaults = {
        'sequence': 10,
    }

    def unlink(self, cr, uid, ids, context=None):
        att_obj = self.pool.get('ir.attachment')
        for pt_att in self.browse(cr, uid, ids, context=context):
            domain = [
                ('res_model', '=', 'sale.order.attachment'),
                ('res_id', '=', pt_att.id)]
            att_ids = att_obj.search(cr, uid, domain, context=context)
            if att_ids:
                att_obj.unlink(cr, uid, att_ids, context)
        return super(sale_order_attachment, self).unlink(
            cr, uid, ids, context)

    def download(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        download_view = mod_obj.get_object_reference(
            cr, uid, 'sale_order_attachments',
            'sale_order_attachment_download_form')
        return {
            'name': _('Download File'),
            'context': context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': ids[0],
            'res_model': 'sale.order.attachment',
            'view_id': [download_view[1]],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
