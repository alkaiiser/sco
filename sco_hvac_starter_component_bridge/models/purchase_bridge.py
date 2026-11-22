from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    sco_boq_line_id = fields.Many2one("sco.hvac.boq.line", string="HVAC Component Requirement",
                                      copy=False, ondelete="restrict", check_company=True)

    @api.constrains("sco_boq_line_id", "order_id", "product_id", "product_uom_id", "product_qty")
    def _check_component_purchase_link(self):
        for line in self:
            boq = line.sco_boq_line_id
            if not boq:
                continue
            if boq.boq_id.state != "approved":
                raise ValidationError(_("A purchase may reference only an approved component requirement."))
            if line.order_id.project_id != boq.boq_id.project_id:
                raise ValidationError(_("The purchase project must match the component requirement project."))
            if line.product_id != boq.product_id:
                raise ValidationError(_("The purchase product must match the component requirement."))
            if not line.product_uom_id._has_common_reference(boq.uom_id):
                raise ValidationError(_("The purchase unit must match the component requirement unit."))
            if line.product_qty <= 0:
                raise ValidationError(_("A component purchase quantity must be positive."))


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _check_component_ceiling(self):
        for order in self:
            for line in order.order_line.filtered("sco_boq_line_id"):
                boq = line.sco_boq_line_id
                linked = self.env["purchase.order.line"].sudo().search([
                    ("sco_boq_line_id", "=", boq.id), ("order_id.state", "in", ("purchase", "done")),
                ])
                total = sum(item.product_uom_id._compute_quantity(item.product_qty, boq.uom_id) for item in linked)
                current = sum(item.product_uom_id._compute_quantity(item.product_qty, boq.uom_id)
                               for item in order.order_line.filtered(lambda item: item.sco_boq_line_id == boq))
                if float_compare(total + current, boq.quantity, precision_rounding=boq.uom_id.rounding) > 0 and not boq._approved_overage():
                    raise UserError(_("The confirmed purchase exceeds the approved component requirement for %s.") % boq.display_name)

    def button_confirm(self):
        self._check_component_ceiling()
        result = super().button_confirm()
        self.env.invalidate_all()
        return result


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        result = super().button_validate()
        self.env.invalidate_all()
        return result


class ProcurementChange(models.Model):
    _inherit = "sco.hvac.procurement.change"

    kind = fields.Selection(selection_add=[("quantity_overage", "Approved Quantity Overage")], ondelete={"quantity_overage": "cascade"})
    sco_boq_line_id = fields.Many2one("sco.hvac.boq.line", readonly=True, copy=False, ondelete="restrict")

    def _check_target(self):
        if self.kind != "quantity_overage":
            return super()._check_target()
        if not self.line_id or not self.line_id.sco_boq_line_id:
            raise ValidationError(_("A quantity overage request must identify a component purchase line."))
        if self.order_id.state != "purchase" or self.line_id.order_id != self.order_id:
            raise ValidationError(_("A quantity overage request must target a confirmed purchase."))
        if not self.reason or not self.reason.strip():
            raise ValidationError(_("A quantity overage request requires a reason."))
        self.sco_boq_line_id = self.line_id.sco_boq_line_id
        return True

    def _starter_additional_audit_values(self):
        values = super()._starter_additional_audit_values()
        if self.kind == "quantity_overage":
            values["sco_boq_line_id"] = self.line_id.sco_boq_line_id.id
        return values

    def action_approve(self):
        if self.kind != "quantity_overage":
            return super().action_approve()
        self.ensure_one()
        self._lock_target()
        self._check_reviewer()
        self._check_target()
        return super().write({"state": "approved", "reviewed_by": self.env.user.id,
                              "reviewed_on": fields.Datetime.now(), "after": self._snapshot()})
