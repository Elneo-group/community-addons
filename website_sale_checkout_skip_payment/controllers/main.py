# Copyright 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale

class CheckoutSkipPayment(WebsiteSale):

    @http.route()
    def shop_payment_confirmation(self, **post):
        if not request.website.checkout_skip_payment:
            return super().shop_payment_confirmation(**post)
        order = (
            request.env["sale.order"]
            .sudo()
            .browse(request.session.get("sale_last_order_id"))
        )
        if order.state in ('draft', 'sent'):
            try:
                order.action_confirm()
                order._send_order_confirmation_mail()
            except Exception:
                return request.render(
                    "website_sale_checkout_skip_payment.confirmation_order_error"
                )
        request.website.sale_reset()
        values = self._prepare_shop_payment_confirmation_values(order)
        return request.render("website_sale.confirmation", values)
    
    
    
    