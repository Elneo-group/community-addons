# Copyright 2023 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

from .mail_mail import format_emails


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    # ------------------------------------------------------------
    # MAIL.MESSAGE HELPERS
    # ------------------------------------------------------------

    def _get_message_create_valid_field_names(self):
        """
        add cc and bcc field to create record in mail.mail
        """
        field_names = super()._get_message_create_valid_field_names()
        field_names.update({"recipient_cc_ids", "recipient_bcc_ids"})
        return field_names

    # ------------------------------------------------------
    # NOTIFICATION API
    # ------------------------------------------------------

    def _notify_by_email_get_base_mail_values(self, message, additional_values=None):
        """
        This is to add cc, bcc addresses to mail.mail objects so that email
        can be sent to those addresses.
        """
        res = super()._notify_by_email_get_base_mail_values(
            message, additional_values=additional_values
        )
        context = self.env.context

        partners_cc = context.get("partner_cc_ids", None)
        if partners_cc:
            res["email_cc"] = format_emails(partners_cc)

        partners_bcc = context.get("partner_bcc_ids", None)
        if partners_bcc:
            res["email_bcc"] = format_emails(partners_bcc)

        return res

    def _notify_get_recipients(self, message, msg_vals, **kwargs):
        """
        This is to add cc, bcc recipients so that they can be grouped with
        other recipients.
        """
        ResPartner = self.env["res.partner"]
        MailFollowers = self.env["mail.followers"]
        rdata = super()._notify_get_recipients(message, msg_vals, **kwargs)
        context = self.env.context
        is_from_composer = context.get("is_from_composer", False)
        if not is_from_composer:
            return rdata
        for pdata in rdata:
            pdata["type"] = "customer"
        partners_cc_bcc = context.get("partner_cc_ids", ResPartner)
        partners_cc_bcc += context.get("partner_bcc_ids", ResPartner)
        msg_sudo = message.sudo()
        message_type = (
            msg_vals.get("message_type") if msg_vals else msg_sudo.message_type
        )
        subtype_id = msg_vals.get("subtype_id") if msg_vals else msg_sudo.subtype_id.id
        recipients_cc_bcc = MailFollowers._get_recipient_data(
            None, message_type, subtype_id, partners_cc_bcc.ids
        )
        for _, value in recipients_cc_bcc.items():
            for _, data in value.items():
                if not data.get("id"):
                    continue
                if not data.get(
                    "notif"
                ):  # notif is False, has no user, is therefore customer
                    notif = "email"
                msg_type = "customer"
                pdata = {
                    "id": data.get("id"),
                    "active": data.get("active"),
                    "share": data.get("share"),
                    "notif": data.get("notif") and data.get("notif") or notif,
                    "type": msg_type,
                    "is_follower": data.get("is_follower"),
                }
                rdata.append(pdata)
        return rdata

    def _notify_get_recipients_classify(
        self, message, recipients_data, model_description, msg_vals=None
    ):
        res = super()._notify_get_recipients_classify(
            message, recipients_data, model_description, msg_vals=msg_vals
        )
        is_from_composer = self.env.context.get("is_from_composer", False)
        if not is_from_composer:
            return res
        ids = []
        customer_data = None
        for rcpt_data in res:
            if rcpt_data["notification_group_name"] == "customer":
                customer_data = rcpt_data
            else:
                ids += rcpt_data["recipients"]
        if not customer_data:
            customer_data = res[0]
            customer_data["notification_group_name"] = "customer"
            customer_data["recipients"] = ids
        else:
            customer_data["recipients"] += ids
        return [customer_data]
