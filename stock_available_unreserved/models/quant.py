from odoo import api, fields, models

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    contains_unreserved = fields.Boolean(
        string="Contains unreserved products",
        compute="_compute_contains_unreserved",
        store=True,
    )
    
    @api.depends('product_id','location_id','quantity','reserved_quantity')
    def _compute_contains_unreserved(self):
        for record in self:
            if isinstance(record.id, models.NewId):
                record.contains_unreserved = False
                continue
            available = record._get_available_quantity(
                record.product_id, record.location_id
            )
            record.contains_unreserved = True if available > 0 else False