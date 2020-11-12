# Copyright 2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMoveTaxSync(models.TransientModel):
    _name = "account.move.tax.sync"
    _description = "Sync taxes on Journal Items with Tax objects"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    move_id = fields.Many2one(comodel_name="account.move", string="Journal Entry")
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal")
    tax_id = fields.Many2one(comodel_name="account.tax", string="Tax")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )
    note = fields.Text(string="Notes", readonly=True)

    @api.onchange("journal_id", "company_id", "date_from", "date_to")
    def _onchange_journal_id(self):
        dom = [("company_id", "=", self.company_id.id)]
        move_dom = dom.copy()
        tax_dom = dom.copy()
        if self.date_from:
            move_dom += [("date", ">=", self.date_from)]
        if self.date_to:
            move_dom += [("date", "<=", self.date_to)]
        res = {"domain": {"move_id": move_dom, "tax_id": tax_dom}}
        if self.journal_id:
            move_dom += [("journal_id", "=", self.journal_id.id)]
            if self.journal_id.type == "sale":
                tax_dom += [("type_tax_use", "=", "sale")]
            elif self.journal_id.type == "purchase":
                tax_dom += [("type_tax_use", "=", "purchase")]
        return res

    def tax_sync(self):
        if not self._uid == self.env.ref("base.user_admin").id:
            raise UserError(_("You are not allowed to execute this Operation."))
        ams = self.move_id
        if not ams:
            am_dom = [("company_id", "=", self.company_id.id)]
            if self.date_from:
                am_dom.append(("date", ">=", self.date_from))
            if self.date_to:
                am_dom.append(("date", ">=", self.date_to))
            if self.journal_id:
                am_dom.append(("journal_id", "=", self.journal_id.id))
            ams = self.env["account.move"].search(am_dom)
        updates = self.env["account.move"]
        for am in ams:
            updates += self._sync_taxes(am)
        nbr = len(updates)
        self.note = "Journal Entries update count: %s" % nbr
        if nbr:
            self.note += "\n\n"
            self.note += ("Updated Journal Entries") + ":\n"
            numbers = [x.name or "*{}".format(x.id) for x in updates]
            self.note += ", ".join(numbers)
        module = __name__.split("addons.")[1].split(".")[0]
        result_view = self.env.ref("{}.{}_view_form_result".format(module, self._table))
        return {
            "name": _("Sync Journal Entry Taxes"),
            "res_id": self.id,
            "view_type": "form",
            "view_mode": "form",
            "res_model": self._name,
            "view_id": result_view.id,
            "context": self.env.context,
            "target": "new",
            "type": "ir.actions.act_window",
        }

    def _sync_taxes(self, am):
        # import pdb; pdb.set_trace()
        tax_amls = am.line_ids.filtered(lambda r: r.tax_ids)
        tax_line_amls = am.line_ids.filtered(lambda r: r.tax_line_id)
        amls_taxes = tax_amls.mapped("tax_ids") + tax_line_amls.mapped("tax_line_id")
        if not amls_taxes or (self.tax_id and self.tax_id not in amls_taxes):
            return
        am_new = self.env["account.move"].new(origin=am)
        am_new._recompute_tax_lines()
        update = False
        upd_ctx = dict(self.env.context, sync_taxes=True)
        tax_sync_fields = self._get_tax_sync_fields()
        to_create = []
        aml_done = self.env["account.move.line"]
        for i, aml_new in enumerate(am_new.line_ids):
            aml = False
            origin = aml_new._origin
            if origin in am.line_ids:
                aml = am.line_ids.filtered(lambda r: r == origin)
            else:
                if len(am_new.line_ids) == len(am.line_ids):
                    aml = am.line_ids[i]
                else:
                    update = True
                    to_create.append(aml_new)
            if aml:
                aml_done += aml
                for fld in tax_sync_fields:
                    if aml_new[fld] != aml[fld]:
                        update = True
                        aml.with_context(upd_ctx)[fld] = aml_new[fld]

        to_unlink = am.line_ids - aml_done
        if to_unlink:
            # TODO
            raise NotImplementedError
        if to_create:
            # TODO
            raise NotImplementedError

        if update:
            return am
        else:
            return am.browse()

    def _get_tax_sync_fields(self):
        return [
            "account_id",
            "balance",
            "tax_line_id",
            "tax_group_id",
            "tax_base_amount",
            "tax_exigible",
            "tag_ids",
            "tax_repartition_line_id",
            "tax_audit",
        ]
