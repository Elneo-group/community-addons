# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools


class WizardUpdateChartsAccounts(models.TransientModel):
    _inherit = "wizard.update.charts.accounts"

    update_tax_repartition_line_account = fields.Boolean(
        string="Update Tax Account",
        default=True,
        help="Update account_id field on existing Tax repartition lines",
    )
    update_tax_repartition_line_tags = fields.Boolean(
        string="Update Tax Tags",
        default=True,
        help="Update tag_ids field on existing Tax repartition lines",
    )

    @tools.ormcache("templates", "current_repartition")
    def find_repartition_by_templates(
        self, templates, current_repartition, inverse_name
    ):
        upd_acc = self.update_tax_repartition_line_account
        upd_tags = self.update_tax_repartition_line_tags
        if not (upd_acc or upd_tags):
            return super().find_repartition_by_templates(
                templates, current_repartition, inverse_name
            )

        result = []
        for tpl in templates:
            tax_id = self.find_tax_by_templates(tpl[inverse_name])
            factor_percent = tpl.factor_percent
            repartition_type = tpl.repartition_type
            account_id = self.find_account_by_templates(tpl.account_id)
            rep_obj = self.env["account.tax.repartition.line"]
            existing = rep_obj.search(
                [
                    (inverse_name, "=", tax_id),
                    ("factor_percent", "=", factor_percent),
                    ("repartition_type", "=", repartition_type),
                ]
            )

            if existing and len(existing) == 1:
                upd_vals = {}
                if upd_acc and existing.account_id.id != account_id:
                    upd_vals["account_id"] = account_id
                if upd_tags:
                    tags = self.env["account.account.tag"]
                    tags += tpl.plus_report_line_ids.mapped("tag_ids").filtered(
                        lambda x: not x.tax_negate
                    )
                    tags += tpl.minus_report_line_ids.mapped("tag_ids").filtered(
                        lambda x: x.tax_negate
                    )
                    tags += tpl.tag_ids
                    if existing.tag_ids != tags:
                        upd_vals["tag_ids"] = [(6, 0, tags.ids)]
                if upd_vals:
                    # update record
                    result.append((1, existing.id, upd_vals))
            if not existing:
                # create a new mapping
                result.append(
                    (
                        0,
                        0,
                        {
                            inverse_name: tax_id,
                            "factor_percent": factor_percent,
                            "repartition_type": repartition_type,
                            "account_id": account_id,
                            "tag_ids": [(6, 0, tpl.tag_ids.ids)],
                        },
                    )
                )
            else:
                current_repartition -= existing
        # Mark to be removed the lines not found
        if current_repartition:
            result += [(2, x.id) for x in current_repartition]
        return result
