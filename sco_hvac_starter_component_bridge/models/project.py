from odoo import fields, models, _


class ProjectProject(models.Model):
    _inherit = "project.project"

    purchase_requirement_count = fields.Integer(
        string="Purchase Requirements",
        compute="_compute_purchase_requirement_count",
    )

    def _compute_purchase_requirement_count(self):
        Requirement = self.env["sco.hvac.purchase.requirement"]
        grouped = Requirement._read_group(
            [("project_id", "in", self.ids)],
            ["project_id"],
            ["__count"],
        )
        counts = {project.id: count for project, count in grouped}
        for project in self:
            project.purchase_requirement_count = counts.get(project.id, 0)

    def action_open_purchase_requirements(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Purchase Requirements"),
            "res_model": "sco.hvac.purchase.requirement",
            "view_mode": "list,form",
            "views": [
                (
                    self.env.ref(
                        "sco_hvac_starter_component_bridge.view_project_purchase_requirement_list"
                    ).id,
                    "list",
                ),
                (
                    self.env.ref(
                        "sco_hvac_starter_component_bridge.view_project_purchase_requirement_form"
                    ).id,
                    "form",
                ),
            ],
            "domain": [("project_id", "=", self.id)],
            "context": {
                "search_default_group_by_purchase_product": 1,
                "search_default_group_by_kind": 2,
                "search_default_group_by_specification": 3,
                "search_default_group_by_uom": 4,
            },
        }
