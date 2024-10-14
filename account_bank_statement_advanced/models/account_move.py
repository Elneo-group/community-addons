# Copyright 2009-2024 Noviat.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_date(self):
        if (
            not self
            and self.env.context.get("form_view_ref")
            == "account_bank_statement_advanced.account_bank_statement_line_view_form"
        ):
            return (
                self.env.context.get("accounting_date")
                or self.env.context.get("statement_date")
                or fields.Date.context_today(self)
            )
        return super()._compute_date()

    def button_draft(self):
        for move in self:
            for move_line in move.line_ids:
                st = move_line.statement_id
                if st and st.state == "confirm":
                    raise UserError(
                        _(
                            "Operation not allowed ! "
                            "\nYou cannot unpost an Accounting Entry "
                            "that is linked to a Validated Bank Statement."
                        )
                    )
        return super().button_draft()

    def button_cancel(self):
        for move in self:
            for move_line in move.line_ids:
                st = move_line.statement_id
                if st and st.state == "confirm":
                    raise UserError(
                        _(
                            "Operation not allowed ! "
                            "\nYou cannot cancel an Accounting Entry "
                            "that is linked to a Validated Bank Statement."
                        )
                    )
        return super().button_cancel()
