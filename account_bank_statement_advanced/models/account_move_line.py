# Copyright 2009-2021 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    move_state = fields.Selection(
        related="move_id.state", string="Move State", readonly=True
    )

    def unlink(self):
        for move_line in self:
            st = move_line.statement_id
            if st and st.state == "confirm":
                raise UserError(
                    _(
                        "Operation not allowed ! "
                        "\nYou cannot delete an Accounting Entry "
                        "that is linked to a Confirmed Bank Statement."
                    )
                )
        return super().unlink()

    @api.model
    def _get_excluded_fields(self):
        return [
            "reconciled",
            "full_reconcile_id",
            "matched_debit_ids",
            "matched_credit_ids",
            "amount_residual",
            "amount_residual_currency",
        ]

    def write(self, vals):
        for move_line in self:
            st = move_line.statement_id
            if st and st.state == "confirm":
                for k in vals:
                    if k not in self._get_excluded_fields():
                        raise UserError(
                            _(
                                "Operation not allowed ! "
                                "\nYou cannot modify an Accounting Entry "
                                "that is linked to a Confirmed Bank Statement. "
                                "\nStatement = %s"
                                "\nMove = %s (id:%s)\nUpdate Values = %s"
                            )
                            % (
                                st.name,
                                move_line.move_id.name,
                                move_line.move_id.id,
                                vals,
                            )
                        )
        return super().write(vals)
