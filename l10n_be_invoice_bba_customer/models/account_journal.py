from odoo import fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    def _valid_field_parameter(self, field, name):
        res = (
            field.name == "invoice_reference_model" and name == "selection_update_label"
        ) or super()._valid_field_parameter(field ,name)
        return res
    
    invoice_reference_model = fields.Selection(
        selection_add=[
            ("be", "Belgian OGM-VCS Structured Communication"),
            ("partner", "Defined on Customer record"),
        ],
        selection_update_label=[
            ("odoo", "Invoice Number or Customer Reference or Open"),
            ("be", "Belgian OGM-VCS Structured Communication"),
            ("euro", "European / ISO 11649 Structured Creditor Reference"),
        ],
        ondelete={
            "be": lambda recs: recs.write({"invoice_reference_model": "odoo"}),
            "partner": lambda recs: recs.write({"invoice_reference_model": "odoo"}),
        },
        help="You can set here the default Communication Standard that will appear "
        "on customer invoices, once validated, to help the customer to refer "
        "to that particular invoice when making the payment.\n"
        "If you select 'Invoice Number or Open' the Payment Reference will "
        "become the Invoice Number or remain empty in case of you select 'Open' as "
        "Communication Type.\n"
        "If you select 'Defined on Customer record', the Payment "
        "Communication Standard defined on the Customer record will be used.",
    )