# Copyright 2011-2017 Akretion (http://www.akretion.com)
# Copyright 2009-2020 Noviat (http://www.noviat.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# @author Luc de Meyer <info@noviat.com>

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    intrastat_arrivals = fields.Selection(
        selection="_intrastat_arrivals",
        string="Arrivals",
        default="extended",
        required=True,
    )
    intrastat_dispatches = fields.Selection(
        selection="_intrastat_dispatches",
        string="Dispatches",
        default="extended",
        required=True,
    )
    intrastat_transport_id = fields.Many2one(
        comodel_name="intrastat.transport_mode",
        string="Default Transport Mode",
        ondelete="restrict",
    )
    intrastat = fields.Char(
        string="Intrastat Declaration",
        store=True,
        compute="_compute_intrastat",
    )
    intrastat_region_id = fields.Many2one(
        comodel_name="intrastat.region", string="Default Intrastat Region"
    )
    intrastat_accessory_costs = fields.Boolean(
        string="Include Accessory Costs in Fiscal Value of Product"
    )

    @api.model
    def _intrastat_arrivals(self):
        return [
            ("exempt", "Exempt"),
            ("standard", "Standard"),
            ("extended", "Extended"),
        ]

    @api.model
    def _intrastat_dispatches(self):
        return [
            ("exempt", "Exempt"),
            ("standard", "Standard"),
            ("extended", "Extended"),
        ]

    @api.depends("intrastat_arrivals", "intrastat_dispatches")
    def _compute_intrastat(self):
        for this in self:
            if (
                this.intrastat_arrivals == "exempt"
                and this.intrastat_dispatches == "exempt"
            ):
                this.intrastat = "exempt"
            elif (
                this.intrastat_arrivals == "extended"
                or this.intrastat_dispatches == "extended"
            ):
                this.intrastat = "extended"
            else:
                this.intrastat = "standard"
