# Copyright 2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    @api.depends("name", "type_tax_use")
    def name_get(self):
        if self._context.get("show_tax_id"):
            result = []
            for tax in self:
                name = "{} (ID: {})".format(tax.name, tax.id)
                result.append((tax.id, name))
            return result
        else:
            return super().name_get()
