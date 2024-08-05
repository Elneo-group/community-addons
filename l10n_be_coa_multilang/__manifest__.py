# Copyright 2009-2024 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Belgium - Multilingual Chart of Accounts (en/nl/fr)",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Noviat",
    "website": "https://www.noviat.com/",
    "category": "Accounting/Localizations/Account Charts",
    "countries": ["be"],
    "depends": [
        "account_tax_code",
        "account_usability",
        "l10n_account_translate_config",
        "base_vat",
        "base_iban",
        "report_xlsx_helper",
        #"web_tree_decoration_underline",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/account_report_data.xml",
        "data/account_report_line_data.xml",
        # "data/account_tax_template_data.xml",  TODO
        # "data/account_fiscal_position_template_data.xml",  TODO
        # "data/account_fiscal_position_tax_template_data.xml",  TODO
        # "data/account_fiscal_position_account_template_data.xml",  TODO
        "data/be_legal_financial_report_chart_data.xml",
        "data/be_legal_financial_report_scheme_data.xml",
        "data/ir_sequence_data.xml",
        "views/menuitem.xml",
        "views/account_account_views.xml",
        "views/be_legal_financial_report_scheme_views.xml",
        "views/l10n_be_layouts.xml",
        "views/report_l10nbevatdeclaration.xml",
        "views/report_l10nbevatintracom.xml",
        "views/report_l10nbevatlisting.xml",
        "views/report_l10nbelegalreport.xml",
        "views/res_partner_views.xml",
        "wizards/l10n_be_coa_multilang_config.xml",
        "wizards/l10n_be_update_be_reportscheme.xml",
        "wizards/l10n_be_vat_common.xml",
        "wizards/l10n_be_vat_declaration.xml",
        "wizards/l10n_be_vat_intracom.xml",
        "wizards/l10n_be_vat_listing.xml",
        "wizards/l10n_be_legal_report.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/l10n_be_coa_multilang/static/src/scss/l10n_be_report.scss",
        ],
    },
    "installable": True,
}
