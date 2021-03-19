# Copyright 2009-2021 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from itertools import combinations

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
        default=lambda self: self.env.company,
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
        tax_tags = self.env["account.account.tag"].search(
            [
                ("applicability", "=", "taxes"),
                ("country_id", "=", self.company_id.country_id.id),
            ]
        )
        wiz_dict = {
            "error_log": "",
            "error_cnt": 0,
            "warning_log": "",
            "warning_cnt": 0,
            "updates": self.env["account.move"],
            "check_account_invoice": False,
            "check_tax_code": False,
            "tax_tags": {x.id: x for x in tax_tags},
        }
        self._check_legacy_tables(wiz_dict)
        if not self._uid == self.env.ref("base.user_admin").id:
            raise UserError(_("You are not allowed to execute this Operation."))
        ams = self.move_id
        if not ams:
            am_dom = [("company_id", "=", self.company_id.id)]
            if self.date_from:
                am_dom.append(("date", ">=", self.date_from))
            if self.date_to:
                am_dom.append(("date", "<=", self.date_to))
            if self.journal_id:
                am_dom.append(("journal_id", "=", self.journal_id.id))
            ams = self.env["account.move"].search(am_dom)
        for am in ams:
            self._sync_taxes(am, wiz_dict)

        updates = wiz_dict["updates"]
        upd_nbr = len(updates)
        self.note = "Journal Entries update count: %s" % upd_nbr
        if wiz_dict["error_cnt"]:
            self.note += "\n\n"
            self.note += "Number of errors: %s" % wiz_dict["error_cnt"]
            self.note += "\n\n"
            self.note += wiz_dict["error_log"]
        if wiz_dict["warning_cnt"]:
            self.note += "\n\n"
            self.note += "Number of warnings: %s" % wiz_dict["warning_cnt"]
            self.note += "\n\n"
            self.note += wiz_dict["warning_log"]
        if upd_nbr:
            self.note += "\n\n"
            self.note += "Updated Journal Entries" + ":\n"
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

    def _check_legacy_tables(self, wiz_dict):
        """
        entries created <= Odoo 12.0: check account_invoice
        entries created <= Odoo 8.0: check account_tax_code
        """
        self.env.cr.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_name = 'account_invoice'"
        )
        res = self.env.cr.fetchone()
        if res:
            wiz_dict["check_account_invoice"] = True

        self.env.cr.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_name = 'account_tax_code'"
        )
        res = self.env.cr.fetchone()
        if res:
            wiz_dict["check_tax_code"] = True
            self.env.cr.execute(
                "SELECT id, code FROM account_tax_code " "WHERE company_id = %s",
                (self.company_id.id,),
            )
            res = self.env.cr.fetchall()
            wiz_dict["tax_codes"] = {x[0]: x[1] for x in res}

    def _sync_taxes(self, am, wiz_dict):
        error_cnt = 0
        error_log = []
        tax_amls = am.line_ids.filtered(lambda r: r.tax_ids)
        tax_line_amls = am.line_ids.filtered(lambda r: r.tax_line_id)
        amls_taxes = tax_amls.mapped("tax_ids") | tax_line_amls.mapped("tax_line_id")
        if not amls_taxes or (self.tax_id and self.tax_id not in amls_taxes):
            return

        am_dict = {
            "am": am,
            "to_update": [],
            "to_create": [],
            "aml_done": self.env["account.move.line"],
        }

        if am.type == "entry":
            pos = False
            if "pos.order" in self.env.registry:
                pos = self._get_pos_objects(am)
            if pos:
                self._sync_pos_taxes(pos, am_dict, wiz_dict)
            else:
                self._sync_entry_taxes(am_dict, wiz_dict)
        else:
            self._sync_invoice_taxes(am_dict, wiz_dict)

        to_update = am_dict["to_update"]
        to_create = am_dict["to_create"]
        to_unlink = am.line_ids - am_dict["aml_done"]
        if to_unlink:
            error_cnt += 1
            error_log.append(
                ("Tax recalc wants to remove Journal Items %s") % to_unlink.ids
            )
        if to_create:
            error_cnt += 1
            vals_list = [
                {f: aml[f] for f in ["account_id", "tax_audit", "tax_line_id", "name"]}
                for aml in to_create
            ]
            error_log.append(("Tax recalc wants to create %s") % vals_list)

        if error_cnt:
            wiz_dict["error_cnt"] += error_cnt
            wiz_dict["error_log"] += (
                "Errors detected during tax recalc of %s (ID: %s)"
            ) % (am.name, am.id)
            wiz_dict["error_log"] += ":\n"
            wiz_dict["error_log"] += "\n".join(error_log)
            wiz_dict["error_log"] += "\n"

        elif to_update:
            upd_ctx = dict(self.env.context, sync_taxes=True)
            [x[0].with_context(upd_ctx).update(x[1]) for x in to_update]
            wiz_dict["updates"] |= am

    def _sync_entry_taxes(self, am_dict, wiz_dict):
        """
        Equal to _sync_invoice_taxes at this point in time.
        """
        self._sync_invoice_taxes(am_dict, wiz_dict)

    def _sync_invoice_taxes(self, am_dict, wiz_dict):
        am = am_dict["am"]
        is_zero = am.company_id.currency_id.is_zero

        tax_match_fields = self._get_tax_match_fields()

        am_new = self.env["account.move"].new(origin=am)
        am_new._recompute_tax_lines()

        aml_new_done = self.env["account.move.line"]
        for aml_new in am_new.line_ids:

            def _check_match(aml, tax_match_fields):
                for f in tax_match_fields:
                    if isinstance(aml[f], float):
                        if not is_zero(aml[f] - aml_new[f]):
                            return False
                    else:
                        if aml[f] != aml_new[f]:
                            return False
                return True

            origin = aml_new._origin
            aml_new_dict = self._get_aml_new_dict(aml_new)
            if origin in am.line_ids and _check_match(origin, tax_match_fields):
                aml = am.line_ids.filtered(lambda r: r == origin)
            else:
                aml_todo = am.line_ids - am_dict["aml_done"]
                aml = aml_todo.filtered(lambda r: _check_match(r, tax_match_fields))
                if len(aml) != 1:
                    # fallback to lookup without account_id to cope with
                    # changed tax objects
                    match_fields_no_account = tax_match_fields[:]
                    match_fields_no_account.remove("account_id")
                    aml_no_account = aml_todo.filtered(
                        lambda r: _check_match(r, match_fields_no_account)
                    )
                    # limit match to same account group
                    # remark:
                    # this logic may fail for countries without standardised CoA
                    aml = aml_no_account.filtered(
                        lambda r: r.account_id.code[:3] == aml_new.account_id.code[:3]
                    )
                if len(aml) != 1:
                    # fallback to lookup with rounding diffs
                    diff = 0.1
                    match_fields_no_balance = tax_match_fields[:]
                    match_fields_no_balance.remove("balance")
                    aml_no_balance = aml_todo.filtered(
                        lambda r: _check_match(r, match_fields_no_balance)
                    )
                    aml = aml_no_balance.filtered(
                        lambda r: (r.balance - diff)
                        < aml_new.balance
                        < (r.balance + diff)
                    )
                if len(aml) != 1:
                    # fallback to lookup without account_id with rounding diffs
                    diff = 0.1
                    match_fields_no_account_balance = match_fields_no_account[:]
                    match_fields_no_account_balance.remove("balance")
                    aml_no_account_balance = aml_todo.filtered(
                        lambda r: _check_match(r, match_fields_no_account_balance)
                    )
                    # same account group
                    aml_no_account_balance = aml_no_account_balance.filtered(
                        lambda r: r.account_id.code[:3] == aml_new.account_id.code[:3]
                    )
                    aml = aml_no_account_balance.filtered(
                        lambda r: (r.balance - diff)
                        < aml_new.balance
                        < (r.balance + diff)
                    )
            if aml and len(aml) == 1:
                am_dict["aml_done"] |= aml
                aml_new_done += aml_new
                self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)
            elif not wiz_dict["check_account_invoice"]:
                am_dict["to_create"].append(aml_new_dict)
                aml_new_done += aml_new

        # lookup remaining entries via legacy account_invoice_tax table
        aml_new_todo = am_new.line_ids - aml_new_done
        if wiz_dict["check_account_invoice"] and aml_new_todo:
            self._check_account_invoice(aml_new_todo, am_dict, wiz_dict)

    def _sync_pos_taxes(self, pos, am_dict, wiz_dict):
        am = am_dict["am"]
        is_zero = am.company_id.currency_id.is_zero
        if pos._name == "pos.session":
            data = pos._accumulate_amounts({})
        else:
            # pre Odoo 13.0 entry
            ps = pos.mapped("session_id")
            ctx = dict(self.env.context, account_move_tax_sync=True)
            ps_new = self.env["pos.session"].with_context(ctx).new(origin=ps)
            ps_new.order_ids = pos
            ps_new.order_ids = pos
            # Legacy entries are incorrectly computed as invoiced
            # hence we need to set the account_move field to False
            ps_new.order_ids.update({"account_move": False})
            data = ps_new._accumulate_amounts({})
        aml_todo = am.line_ids - am_dict["aml_done"]

        for key in data["taxes"]:
            account_id, repartition_line_id, tax_id, tag_ids = key
            amounts = data["taxes"][key]
            aml_new_dict = {
                "tax_repartition_line_id": repartition_line_id,
                "tax_line_id": tax_id,
                "tax_ids": False,
                "tag_ids": tag_ids,
                "tax_audit": False,
            }
            amls = aml_todo.filtered(
                lambda r: r.account_id.id == account_id
                and r.tax_line_id.id == tax_id
                and r.tax_repartition_line_id.id == repartition_line_id
            )
            if not amls:
                # fallback to lookup without account_id to cope with
                # changed tax objects
                amls = aml_todo.filtered(
                    lambda r: r.tax_line_id.id == tax_id
                    and r.tax_repartition_line_id.id == repartition_line_id
                )
            for aml in amls:
                aml_todo -= aml
                # tax_base_amount = aml.tax_base_amount
                if len(amls) == 1:
                    if not is_zero(aml.balance - amounts["amount_converted"]):
                        raise UserError(
                            _("Error detected during tax recalc of %s") % aml
                        )
                    tax_base_amount = -amounts["base_amount_converted"]
                else:
                    tax_base_amount = self._get_tax_base_amount(aml, am_dict, wiz_dict)
                aml_new_dict["tax_base_amount"] = tax_base_amount
                self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)

        for key, _amounts in data["sales"].items():
            account_id, sign, tax_keys, tag_ids = key
            tax_ids = {tax[0] for tax in tax_keys}
            aml_new_dict = {
                "tax_repartition_line_id": False,
                "tax_line_id": False,
                "tax_ids": tax_ids,
                "tag_ids": tag_ids,
                "tax_base_amount": 0.0,
                "tax_audit": False,
            }
            amls = aml_todo.filtered(
                lambda r: r.account_id.id == account_id
                and set(r.tax_ids.ids) == set(tax_ids)
            )
            if len(amls) >= 1:
                if sign == 1:  # sales
                    amls = amls.filtered(lambda r: r.balance <= 0)
                else:  # refund
                    amls = amls.filtered(lambda r: r.balance > 0)
            for aml in amls:
                aml_todo -= aml
                self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)

        check_taxes = aml_todo.filtered(lambda r: r.tax_ids or r.tax_line_id)
        if check_taxes:
            raise UserError(
                _(
                    "Error during tax recalc of '%s' (ID: %s).\n"
                    "Non-handled taxes in %s"
                )
                % (am.name, am.id, check_taxes)
            )
        am_dict["aml_done"] = am.line_ids

    def _get_tax_sync_fields(self):
        """
        We include tax_line_id and tax_repartion_line_id since these
        could be wrongly set for entries created from Odoo <= 8.0
        invoices.
        The Odoo OE migration scripts put these fields equal to one of the
        tax objects with matching tax codes.
        As a consequence Odoo 8.0 tax llines created from VAT-OUT-21-S
        may show up with e.g. tax_line_id VAT-OUT-21-G in the migrated database.
        """
        return [
            "tax_base_amount",
            "tag_ids",
            "tax_line_id",
            "tax_repartition_line_id",
        ]

    def _get_tax_match_fields(self):
        return ["account_id", "balance", "tax_line_id", "tax_repartition_line_id"]

    def _calc_aml_updates(self, aml_new_dict, aml, am_dict, wiz_dict):
        to_update = am_dict["to_update"]
        is_zero = aml.company_id.currency_id.is_zero
        tax_sync_fields = self._get_tax_sync_fields()
        aml_updates = {}
        for fld in tax_sync_fields:
            if aml._fields[fld].type == "many2one":
                diff_check = aml_new_dict[fld] != aml[fld].id
            elif hasattr(aml[fld], "ids"):
                diff_check = set(aml_new_dict[fld]) != set(aml[fld].ids)
            elif isinstance(aml[fld], float):
                diff_check = not is_zero(aml_new_dict[fld] - aml[fld])
            else:
                diff_check = aml_new_dict[fld] != aml[fld]
            if diff_check:
                if aml._fields[fld].type == "many2one":
                    aml_updates[fld] = aml_new_dict[fld]
                elif hasattr(aml[fld], "ids"):
                    aml_updates[fld] = [(6, 0, aml_new_dict[fld])]
                else:
                    aml_updates[fld] = aml_new_dict[fld]
        if aml_new_dict["tax_audit"] != aml["tax_audit"]:
            # recalc tax_audit string
            aml_recalc = self.env["account.move.line"].new(origin=aml)
            aml_updates = {k: aml_updates[k] for k in aml_updates if k != "tax_audit"}
            aml_recalc.update(dict(aml_updates, debit=aml.debit, credit=aml.credit))
            if aml_recalc.tax_audit != aml.tax_audit:
                aml_updates["tax_audit"] = aml_recalc.tax_audit
        if aml_updates:
            to_update.append((aml, aml_updates))

    def _get_aml_new_dict(self, aml_new):
        return {
            "account_id": aml_new.account_id.id,
            "name": aml_new.name,
            "tax_repartition_line_id": aml_new.tax_repartition_line_id.id,
            "tax_line_id": aml_new.tax_line_id.id,
            "debit": aml_new.debit,
            "credit": aml_new.credit,
            "balance": aml_new.balance,
            "currency_id": aml_new.currency_id.id,
            "amount_currency": aml_new.amount_currency,
            "tax_base_amount": aml_new.tax_base_amount,
            "tag_ids": aml_new.tag_ids.ids,
            "tax_audit": aml_new.tax_audit,
        }

    def _get_pos_objects(self, am):
        self.env.cr.execute(
            "SELECT DISTINCT(ps.id) FROM pos_order po "
            "INNER JOIN pos_session ps on po.session_id = ps.id "
            "WHERE ps.move_id = %s",
            (am.id,),
        )
        res = self.env.cr.fetchall()
        if len(res) > 1:
            raise UserError(
                _(
                    "Data Error - multiple POS sessions linked "
                    "to a single Journal Entry.\n"
                    "Journal Entry: %s (ID: %s)"
                )
                % (am.name, am.id)
            )
        if len(res) == 1:
            return self.env["pos.session"].browse(res[0])
        elif not res:
            # The move_id field on pos.session has been introduced as from Odoo 13.0.
            # The Odoo OE migration scripts also do not create this field on
            # older sessions.
            # As a consequence we add extra logic to find the underlying orders.
            self.env.cr.execute(
                "SELECT id FROM pos_order WHERE account_move = %s", (am.id,)
            )
            res = self.env.cr.fetchall()
            if not res:
                return False
            pos_order_ids = [x[0] for x in res]
            return self.env["pos.order"].browse(pos_order_ids)

    def _check_account_invoice(self, aml_new_todo, am_dict, wiz_dict):
        """
        Find match via account_invoice table for databases which have been
        created prior to Odoo 13.0
        """
        am = am_dict["am"]
        to_create = am_dict["to_create"]
        self.env.cr.execute(
            "SELECT id FROM account_invoice WHERE move_id = %s", (am.id,)
        )
        res = self.env.cr.fetchone()
        if not res:
            return False

        inv_id = res[0]
        self.env.cr.execute(
            "SELECT * FROM account_invoice_tax WHERE invoice_id = %s", (inv_id,)
        )
        res = self.env.cr.dictfetchall()
        if any([ait.get("tax_code_id") for ait in res]):
            # Odoo <= 8.0 entry
            return self._check_account_invoice_tax_code(
                res, aml_new_todo, am_dict, wiz_dict
            )

        # Entry created by eOdoo > 8.0 and < 13.0
        aml_todo = am.line_ids - am_dict["aml_done"]
        sign = am.type in ("in_refund", "out_invoice") and -1 or 1
        for aml_new in aml_new_todo:
            aml_new_dict = self._get_aml_new_dict(aml_new)
            if aml_new_dict["currency_id"]:
                amt_fld = "amount_currency"
                is_zero = am.currency_id.is_zero
            else:
                amt_fld = "balance"
                is_zero = am.company_id.currency_id.is_zero
            tax_line_id = aml_new_dict["tax_line_id"]
            account_id = aml_new_dict["account_id"]
            for ait in res:
                if ait["account_id"] != account_id or ait["tax_id"] != tax_line_id:
                    continue
                aml = aml_todo.filtered(
                    lambda r: r.account_id.id == account_id
                    and r.tax_line_id.id == tax_line_id
                    and is_zero(r[amt_fld] - sign * ait["amount"])
                )
                if len(aml) == 1:
                    am_dict["aml_done"] |= aml
                    aml_todo -= aml
                    self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)
                    break
                else:
                    if aml_new_dict not in to_create:
                        to_create.append(aml_new_dict)

    def _check_account_invoice_tax_code(self, aits, aml_new_todo, am_dict, wiz_dict):
        am = am_dict["am"]
        to_create = am_dict["to_create"]
        aml_todo = am.line_ids - am_dict["aml_done"]
        sign = am.type in ("in_refund", "out_invoice") and -1 or 1
        if am.line_ids == am_dict["aml_done"]:
            # We observe missing 'tax_line_id' in Journal Items converted by the
            # Odoo OE migration service in case of legacy entries created from
            # tax children.
            # The _recompute_tax_lines creates new Journal Items in such cases
            # in stead of updating the existing ones.
            # We have added logic here to find and update the existing Journal Items.
            aml_todo = am.line_ids.filtered(
                lambda r: r.exclude_from_invoice_tab
                and not r.tax_line_id
                and r.account_internal_type not in ("receivable", "payable")
            )
        for aml_new in aml_new_todo:
            done = False
            aml_new_dict = self._get_aml_new_dict(aml_new)
            if aml_new_dict["currency_id"]:
                amt_fld = "amount_currency"
                is_zero = am.currency_id.is_zero
            else:
                amt_fld = "balance"
                is_zero = am.company_id.currency_id.is_zero
            tag_ids = aml_new_dict["tag_ids"]
            for ait in aits:
                if ait.get("tax_code_id"):
                    tax_code = wiz_dict["tax_codes"][ait["tax_code_id"]]
                    if len(tag_ids) != 1:
                        continue
                    tax_tag = wiz_dict["tax_tags"][tag_ids[0]]
                    if tax_code not in tax_tag.name:
                        continue
                if len(aml_todo) == 1:
                    aml = aml_todo
                    if (
                        is_zero(aml[amt_fld] - sign * ait["amount"])
                        and aml.account_id.id == ait["account_id"]
                    ):
                        self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)
                        am_dict["aml_done"] |= aml
                        aml_todo -= aml
                        done = True
                        break
                else:
                    aits_group = [
                        x
                        for x in aits
                        if x["tax_code_id"] == ait["tax_code_id"]
                        and x["base_code_id"] == ait["base_code_id"]
                        and x["account_id"] == ait["account_id"]
                    ]
                    aits_amount = sum([x["amount"] for x in aits_group])
                    aml = aml_todo.filtered(
                        lambda r: is_zero(r[amt_fld] - sign * aits_amount)
                        and r.account_id.id == ait["account_id"]
                    )
                    if aml:
                        base_amount = sum([x["base_amount"] for x in aits_group])
                        aml_new_dict["tax_base_amount"] = base_amount
                        for l in aml:
                            self._calc_aml_updates(aml_new_dict, l, am_dict, wiz_dict)
                        am_dict["aml_done"] |= aml
                        aml_todo -= aml
                        done = True
                        break

            if not done and aml_new_dict not in to_create:
                to_create.append(aml_new_dict)

    def _get_tax_base_amount(self, aml, am_dict, wiz_dict):
        """
        We try to find the tax_base_amls via reverse lookup.
        """
        am = am_dict["am"]
        tax_base_amount = 0.0
        tax_base_amls = am.line_ids.filtered(
            lambda r: aml.tax_line_id.id in r.tax_ids.ids
            and r.product_id == aml.product_id
        )
        if len(tax_base_amls) == 1:
            return -tax_base_amls.balance

        if aml.balance <= 0:  # sales
            tax_base_amls = tax_base_amls.filtered(lambda r: r.balance <= 0)
        else:  # refund
            tax_base_amls = tax_base_amls.filtered(lambda r: r.balance > 0)
        if len(tax_base_amls) == 1:
            return -tax_base_amls.balance

        tax = aml.tax_line_id
        if tax.amount_type == "percent":
            pct = (tax.amount * aml.tax_repartition_line_id.factor_percent) / 100
            factor = pct / 100.0
            tax_base_amount = aml.balance / factor
            for i in range(len(tax_base_amls)):
                to_check = combinations(tax_base_amls, i + 1)
                for entry in to_check:
                    # we observe rather large diff in reverse calc
                    # in historical databases
                    diff = 0.0
                    for _j in range(10):
                        diff += 0.1
                        tax_base = sum([x.balance for x in entry])
                        if (
                            (tax_base_amount - diff)
                            < tax_base
                            < (tax_base_amount + diff)
                        ):
                            tax_base_amls = self.env["account.move.line"]
                            for tax_base_aml in entry:
                                tax_base_amls += tax_base_aml
                            return -sum(tax_base_amls.mapped("balance"))
        warn_msg = ("tax_base_amount calculation failed for Journal Item %s") % aml.id
        wiz_dict["warning_cnt"] += 1
        wiz_dict["warning_log"] += ("Warnings during tax recalc of %s (ID: %s)") % (
            am.name,
            am.id,
        )
        wiz_dict["warning_log"] += ":\n"
        wiz_dict["warning_log"] += warn_msg
        wiz_dict["warning_log"] += "\n"

        return tax_base_amount or aml.tax_base_amount

    def _handle_zero_aml(self, aml, am_dict, wiz_dict):
        """
        Handle legacy zero lines with tax_code_id and tax_amount
        created in Odoo <= 8.0
        """
        raise NotImplementedError  # TODO
