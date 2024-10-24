# Copyright 2009-2024 Noviat.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class ResCurrency(models.Model):
    _inherit = "res.currency"

    def _get_rates(self, company, date):
        date = self.env.context.get("rate_date") or date
        return super()._get_rates(company, date)
