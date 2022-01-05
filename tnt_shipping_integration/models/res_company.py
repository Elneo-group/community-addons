from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    use_tnt_shipping_provider = fields.Boolean(string="Is Use TNT Shipping Provider?",
                                               help="True when we need to use TNT shipping provider",
                                               default=False, copy=False)
    tnt_company = fields.Char(string='TNT UserID', help="Get UserId details from TNT")
    tnt_password = fields.Char(string='TNT Password', help="Enter Your Password.")
    tnt_app_id = fields.Char(string='TNT APP-ID', help="Enter AppId")
    tnt_api_url = fields.Char(string='TNT API URL', help="Enter Api Url")
    tnt_account_number = fields.Char(string="TNT Account Number")