from odoo import fields, models, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    tnt_receiver_account = fields.Char(string="Receiver Account Number",
                          help="Enter Receiver Account Number If Payments From Receiver")
    tnt_complete_code = fields.Char(string="TNT Complete Code",
                          help="It's Storing for technical stuff")
