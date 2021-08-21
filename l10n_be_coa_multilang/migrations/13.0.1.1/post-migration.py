# Copyright 2009-2021 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """
    assign account groups
    """
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        country_codes = env["account.account"]._get_be_scheme_countries()
        # find countries via SQL since res.company,country_id is a non-stored field
        cr.execute(
            """
        SELECT cpy.id FROM res_company cpy
        JOIN res_partner rp ON cpy.partner_id = rp.id
        JOIN res_country cntry ON rp.country_id = cntry.id
        WHERE cntry.code IN %s
            """,
            (tuple(country_codes),),
        )
        company_ids = [x[0] for x in cr.fetchall()]
        accounts = env["account.account"].search([("company_id", "in", company_ids)])
        for account in accounts:
            account.onchange_code()
