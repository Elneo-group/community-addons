from odoo import models, fields, api, _
from odoo.addons.delivery.models.delivery_carrier import DeliveryCarrier

def rate_shipment(self, order):
    ''' Compute the price of the order shipment
    :param order: record of sale.order
    :return dict: {'success': boolean,
                   'price': a float,
                   'error_message': a string containing an error message,
                   'warning_message': a string containing a warning message}
                   # TODO maybe the currency code?
    '''
    self.ensure_one()
    if hasattr(self, '%s_rate_shipment' % self.delivery_type):
        if self.fix_shipping_rate:
            if self.delivery_type_base == 'fixed':
                res = self.fixed_rate_shipment(order)
            if self.delivery_type_base == 'base_on_rule':
                res = self.base_on_rule_rate_shipment(order)
        else:
            res = getattr(self, '%s_rate_shipment' % self.delivery_type)(order)
        # apply margin on computed price
        res['price'] = float(res['price']) * (1.0 + (self.margin / 100.0))
        # save the real price in case a free_over rule overide it to 0
        res['carrier_price'] = res['price']
        # free when order is large enough
        if res['success'] and self.free_over and order._compute_amount_total_without_delivery() >= self.amount:
            res['warning_message'] = _('The shipping is free since the order amount exceeds %.2f.') % (self.amount)
            res['price'] = 0.0
        return res

DeliveryCarrier.rate_shipment = rate_shipment

class CustomdeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type_base = fields.Selection(
        [('fixed', 'Fixed Price'), ('base_on_rule', 'Based on Rules')],
        string='Pricing',
        default='fixed')
    fix_shipping_rate = fields.Boolean(default=False, string="Fix Shipping Rate")
    carrier_id = fields.Many2one('delivery.carrier',string="Shipping Service")
