from odoo import fields, models, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def tracking_get_contact_id(self):
        self.ensure_one()
        if self.sale_id and self.sale_id.partner_contact_id and self.sale_id.partner_contact_id.email:
            return self.sale_id.partner_contact_id
        elif self.sale_id and self.sale_id.partner_id and self.sale_id.partner_id.email:
            return self.sale_id.partner_id
        elif self.partner_id and self.partner_id.email:
            return self.partner_id
        else:
            return None
        
    def _tracking_email_get_lang(self):
        if self.sale_id and self.sale_id.partner_contact_id and self.sale_id.partner_contact_id.email:
            return self.sale_id.partner_contact_id.lang
        elif self.sale_id and self.sale_id.partner_id and self.sale_id.partner_id.email:
            return self.sale_id.partner_id.lang
        elif self.partner_id and self.partner_id.email:
            return self.partner_id.lang
        else:
            return None

    def auto_shipment_confirm_mail(self):
        self.ensure_one()
        ctx = dict(self._context) or {}
        company_id = self.company_id
        if company_id:
            email_template = company_id.mail_template_id or False
            if not email_template:
                return True
            ctx.update({
                'tracking_link': self.carrier_id.get_tracking_link(self),
                'lang': self._tracking_email_get_lang(),
                'subtype_id': self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
                'mail_notify_force_send': True,
            })
            self.with_context(ctx).message_post_with_template(
                email_template.id,
                composition_mode='comment',
                email_layout_xmlid='elneo_stock.mail_notification_tracking_picking',
                subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
            )
        return True

    def action_done(self):
        res = super(StockPicking, self).action_done()
        if self.picking_type_code == 'outgoing' and self.location_dest_id.usage == 'customer':
            company_id = self.company_id or False
            carrier_send_tracking = self.carrier_id and self.carrier_id.send_tracking or False
            if company_id  and company_id.is_automatic_shipment_mail == True and carrier_send_tracking:
                self.auto_shipment_confirm_mail()
        return res
