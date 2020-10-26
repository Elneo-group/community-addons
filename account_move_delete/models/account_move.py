# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def unlink(self):
        if self.env.user.has_group("account_move_delete.group_account_move_delete"):
            self = self.with_context(dict(self.env.context, force_delete=True))
        return super(AccountMove, self.with_context()).unlink()
