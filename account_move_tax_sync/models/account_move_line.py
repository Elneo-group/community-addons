# Copyright 2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.account.models.account_move import AccountMoveLine as AML_OC


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def write(self, vals):
        if self.env.context.get("sync_taxes"):
            return super(AML_OC, self).write(vals)
        return super().write(vals)
