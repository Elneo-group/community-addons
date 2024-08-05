# Copyright 2009-2023 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("product_id", "product_uom_id")
    def _compute_tax_ids(self):
        non_misc_moves = self.filtered(lambda m: m.move_type != "entry")
        return super(AccountMoveLine, non_misc_moves)._compute_tax_ids()
