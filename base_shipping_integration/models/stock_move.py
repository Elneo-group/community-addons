from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        if self.sale_line_id.order_id.carrier_id and self.sale_line_id.order_id.carrier_id.carrier_id:
            vals['carrier_id'] = self.sale_line_id.order_id.carrier_id.carrier_id.id
        return vals
