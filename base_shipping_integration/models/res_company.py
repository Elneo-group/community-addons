# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    mail_template_id = fields.Many2one('mail.template', 'E-mail Template')
    is_automatic_shipment_mail = fields.Boolean('Automatic Send Shipment Confirmation Mail')
