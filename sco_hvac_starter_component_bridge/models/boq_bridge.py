from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

from .purchase_requirement import (
    REQUIREMENT_REVISION_CONTEXT_KEY,
    REQUIREMENT_REVISION_TOKEN,
)


class StarterBOQ(models.Model):
    _inherit = "sco.hvac.boq"

    source_sale_order_id = fields.Many2one("sale.order", readonly=True, copy=False, ondelete="restrict")

    def _create_revision(self):
        return super(StarterBOQ, self.with_context({
            REQUIREMENT_REVISION_CONTEXT_KEY: REQUIREMENT_REVISION_TOKEN,
        }))._create_revision()


class StarterBOQLine(models.Model):
    _inherit = "sco.hvac.boq.line"

    purchase_requirement_ids = fields.One2many(
        "sco.hvac.purchase.requirement",
        "boq_line_id",
        string="Purchase Requirements",
    )
    component_bridge_line_id = fields.Many2one(
        "sco.hvac.product.component.bridge.line", readonly=True, copy=False, ondelete="restrict",
    )
    source_sale_line_id = fields.Many2one("sale.order.line", readonly=True, copy=False, ondelete="restrict")
    component_generation_key = fields.Char(readonly=True, copy=False, index=True)
    project_phase_ref = fields.Char(string="Project Phase")
    purchased_qty = fields.Float(compute="_compute_component_balances", string="Purchased")
    received_qty = fields.Float(compute="_compute_component_balances", string="Received")
    remaining_to_purchase = fields.Float(compute="_compute_component_balances", string="Remaining to Purchase")
    remaining_to_receive = fields.Float(compute="_compute_component_balances", string="Remaining to Receive")

    def _revision_values(self):
        self.ensure_one()
        values = super()._revision_values()
        values["purchase_requirement_ids"] = [
            (0, 0, requirement._revision_values())
            for requirement in self.purchase_requirement_ids
        ]
        return values

    def _purchase_lines(self):
        self.ensure_one()
        return self.env["purchase.order.line"].sudo().search([("sco_boq_line_id", "=", self.id)])

    def _approved_overage(self):
        self.ensure_one()
        if "sco.hvac.procurement.change" not in self.env:
            return False
        return bool(self.env["sco.hvac.procurement.change"].sudo().search_count([
            ("kind", "=", "quantity_overage"), ("state", "=", "approved"),
            ("sco_boq_line_id", "=", self.id),
        ]))

    @api.depends("quantity", "uom_id", "product_id")
    def _compute_component_balances(self):
        for line in self:
            purchased = received = 0.0
            for purchase_line in line._purchase_lines():
                if purchase_line.order_id.state not in ("purchase", "done"):
                    continue
                purchased += purchase_line.product_uom_id._compute_quantity(
                    purchase_line.product_qty, line.uom_id)
                for move in purchase_line.move_ids.filtered(lambda item: item.state == "done"):
                    qty = move.product_uom_qty
                    qty = move.product_uom._compute_quantity(qty, line.uom_id) if move.product_uom else qty
                    received += -qty if move.origin_returned_move_id else qty
            line.purchased_qty = purchased
            line.received_qty = received
            line.remaining_to_purchase = max(line.quantity - purchased, 0.0)
            line.remaining_to_receive = max(line.quantity - received, 0.0)

    @api.constrains("component_bridge_line_id", "source_sale_line_id", "component_generation_key")
    def _check_component_trace(self):
        for line in self:
            if line.component_bridge_line_id and line.component_bridge_line_id.bridge_id.state != "approved":
                raise ValidationError(_("A requirement must reference an approved component bridge."))

    def action_open_purchase_orders(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Component Purchase Orders"),
            "res_model": "purchase.order",
            "view_mode": "list,form",
            "domain": [("order_line.sco_boq_line_id", "=", self.id)],
            "context": {"default_project_id": self.boq_id.project_id.id},
        }

    def action_generate_component_requirements(self):
        self.ensure_one()
        if self.source_sale_line_id:
            return self.source_sale_line_id.action_generate_component_requirements()
        raise UserError(_("This requirement is not linked to a confirmed sale line."))
