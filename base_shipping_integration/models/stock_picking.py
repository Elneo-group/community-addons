from odoo import fields, models, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def auto_shipment_confirm_mail(self):
        self.ensure_one()
        ctx = dict(self._context) or {}
        company_id = self.carrier_id and self.carrier_id.company_id
        if company_id:
            email_template = company_id.mail_template_id or False
            if not email_template:
                return True
            tracking_link = self.carrier_id.get_tracking_link(self)
            ctx.update({'tracking_link': tracking_link})
            email_template.with_context(ctx).send_mail(self.id, True)
        return True

    def action_done(self):
        res = super(StockPicking, self).action_done()
        company_id = self.carrier_id and self.carrier_id.company_id or False
        if company_id  and company_id.is_automatic_shipment_mail == True:
            self.auto_shipment_confirm_mail()
        return res
