# Copyright 2009-2021 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _prepare_line(self, order_line):
        if self.env.context.get("account_move_tax_sync"):
            order_line = order_line._origin
        return super()._prepare_line(order_line)
