# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MergePurchaseOrder(models.TransientModel):
    _name = 'merge.purchase.order'
    _description = "Merge Purchase Orders"

    merge_type = \
        fields.Selection([
            ('new_cancel',
                'Create new order and cancel all selected purchase orders'),
            ('new_delete',
             'Create new order and delete all selected purchase orders'),
            ('merge_cancel',
             'Merge order on existing selected order and cancel others'),
            ('merge_delete',
                'Merge order on existing selected order and delete others')],
            default='new_cancel')
    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order')

    @api.onchange('merge_type')
    def onchange_merge_type(self):
        res = {}
        for order in self:
            order.purchase_order_id = False
            if order.merge_type in ['merge_cancel', 'merge_delete']:
                purchase_orders = self.env['purchase.order'].browse(
                    self._context.get('active_ids', []))
                res['domain'] = {
                    'purchase_order_id':
                    [('id', 'in',
                        [purchase.id for purchase in purchase_orders])]
                }
            return res

    def create_new_po(self,partner,purchase_orders):
        po = self.env['purchase.order'].with_context({
            'trigger_onchange': True,
            'onchange_fields_to_trigger': [partner]
        }).create({'partner_id': partner})
        po.onchange_partner_id()
        po.origin = ' / '.join((p.origin for p in purchase_orders.filtered(lambda p: p.origin)))
        pick_type_id = purchase_orders.mapped('picking_type_id')
        dest_address_id = purchase_orders.mapped('dest_address_id')
        if len(pick_type_id) == 1:
            po.picking_type_id = pick_type_id.id
        if len(dest_address_id) == 1:
            po.dest_address_id = dest_address_id.id
        team_id = purchase_orders.mapped('team_id') 
        if len(team_id) == 1:
            po.team_id = team_id.id
        default = {'order_id': po.id}
        for order in purchase_orders:
            for sale in order.sale_ids:
                po.sale_ids = [(4, sale.id)]
            for intervention in order.intervention_ids:
                po.intervention_ids = [(4, intervention.id)]
            for line in order.order_line:
                existing_po_line = self.env['purchase.order.line']
                if po.order_line:
                    for poline in po.order_line:
                        if line.product_id == poline.product_id and \
                                line.price_unit == poline.price_unit:
                            existing_po_line = poline
                            break
                if existing_po_line:
                    existing_po_line.product_qty += line.product_qty
                    po_taxes = [
                        tax.id for tax in existing_po_line.taxes_id]
                    [po_taxes.append((tax.id))
                     for tax in line.taxes_id]
                    existing_po_line.taxes_id = \
                        [(6, 0, po_taxes)]
                    for move_dest in line.move_dest_ids:
                        move_dest.write({'created_purchase_line_id':existing_po_line.id})
                    for move in line.move_ids:
                        move.write({'purchase_line_id':existing_po_line.id})
                    for sale_line in line.sale_order_line_ids:
                        existing_po_line.sale_order_line_ids = [(4, sale_line.id)]
                    if line.sale_line_id and not existing_po_line.sale_line_id:
                        existing_po_line.sale_line_id = line.sale_line_id
                else:
                    new_line = line.copy(default=default)
                    for move_dest in line.move_dest_ids:
                        move_dest.write({'created_purchase_line_id':new_line.id})
                    for move in line.move_ids:
                        move.write({'purchase_line_id':new_line.id})
                    for sale_line in line.sale_order_line_ids:
                        new_line.sale_order_line_ids = [(4, sale_line.id)]
                    if line.sale_line_id and not new_line.sale_line_id:
                        new_line.sale_line_id = line.sale_line_id
                        
        return po

    def merge_into_po(self,purchase_orders,po,default):
        po.origin = ' / '.join((p.origin for p in purchase_orders.filtered(lambda p: p.origin)))
        for order in purchase_orders:
            if order == po:
                continue
            for sale in order.sale_ids:
                po.sale_ids = [(4, sale.id)]
            for intervention in order.intervention_ids:
                po.intervention_ids = [(4, intervention.id)]
            for line in order.order_line:
                existing_po_line = self.env['purchase.order.line']
                if po.order_line:
                    for po_line in po.order_line:
                        if line.product_id == po_line.product_id and \
                                line.price_unit == po_line.price_unit:
                            existing_po_line = po_line
                            break
                if existing_po_line:
                    existing_po_line.product_qty += line.product_qty
                    po_taxes = [
                        tax.id for tax in existing_po_line.taxes_id]
                    [po_taxes.append((tax.id))
                     for tax in line.taxes_id]
                    existing_po_line.taxes_id = \
                        [(6, 0, po_taxes)]
                    for move_dest in line.move_dest_ids:
                        move_dest.write({'created_purchase_line_id':existing_po_line.id})
                    for move in line.move_ids:
                        move.write({'purchase_line_id':existing_po_line.id})
                    for sale_line in line.sale_order_line_ids:
                        existing_po_line.sale_order_line_ids = [(4, sale_line.id)]
                    if line.sale_line_id and not existing_po_line.sale_line_id:
                        existing_po_line.sale_line_id = line.sale_line_id
                else:
                    new_line = line.copy(default=default)
                    for move_dest in line.move_dest_ids:
                        move_dest.write({'created_purchase_line_id':new_line.id})
                    for move in line.move_ids:
                        move.write({'purchase_line_id':new_line.id})
                    for sale_line in line.sale_order_line_ids:
                        new_line.sale_order_line_ids = [(4, sale_line.id)]
                    if line.sale_line_id and not new_line.sale_line_id:
                        new_line.sale_line_id = line.sale_line_id

    def merge_orders(self):
        purchase_orders = self.env['purchase.order'].browse(
            self._context.get('active_ids', []))
        if len(self._context.get('active_ids', [])) < 2:
            raise UserError(
                _('Please select atleast two purchase orders to perform '
                    'the Merge Operation.'))
        if any(order.state != 'draft' for order in purchase_orders):
            raise UserError(
                _('Please select Purchase orders which are in RFQ state '
                  'to perform the Merge Operation.'))
        partner = purchase_orders[0].partner_id.id
        if any(order.partner_id.id != partner for order in purchase_orders):
            raise UserError(
                _('Please select Purchase orders whose Vendors are same to '
                    ' perform the Merge Operation.'))
        if self.merge_type == 'new_cancel':
            new_po = self.create_new_po(partner,purchase_orders)
            for order in purchase_orders:
                order.button_cancel()
            return self.action_open_new_po(new_po)
        elif self.merge_type == 'new_delete':
            new_po = self.create_new_po(partner, purchase_orders)
            for order in purchase_orders:
                order.sudo().button_cancel()
                order.sudo().unlink()
            return self.action_open_new_po(new_po)
        elif self.merge_type == 'merge_cancel':
            default = {'order_id': self.purchase_order_id.id}
            po = self.purchase_order_id
            self.merge_into_po(purchase_orders,po,default)
            for order in purchase_orders:
                if order != po:
                    order.sudo().button_cancel()
            return self.action_open_new_po(po)
        else:
            default = {'order_id': self.purchase_order_id.id}
            po = self.purchase_order_id
            self.merge_into_po(purchase_orders, po, default)
            for order in purchase_orders:
                if order != po:
                    order.sudo().button_cancel()
                    order.sudo().unlink()
            return self.action_open_new_po(po)
                    
    def action_open_new_po(self, purchase_order_id):
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        form_view = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = purchase_order_id.id
        return action