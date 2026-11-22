from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ComponentBridge(models.Model):
    _name = "sco.hvac.product.component.bridge"
    _description = "Approved HVAC Sale Component Bridge"
    _order = "id desc"
    _check_company_auto = True

    name = fields.Char(required=True)
    company_id = fields.Many2one("res.company", required=True, default=lambda self: self.env.company)
    sales_product_id = fields.Many2one("product.product", required=True, check_company=True, ondelete="restrict")
    qualification_id = fields.Many2one("sco.hvac.sales.equipment.qualification", required=True,
                                       check_company=True, ondelete="restrict")
    revision = fields.Integer(default=1, required=True, readonly=True)
    source_ref = fields.Char(required=True)
    source_version = fields.Char(required=True)
    source_attachment_id = fields.Many2one("ir.attachment", required=True, ondelete="restrict")
    state = fields.Selection([("draft", "Draft"), ("submitted", "Submitted"),
                              ("approved", "Approved"), ("retired", "Retired")],
                             default="draft", required=True, readonly=True, copy=False)
    approved_by = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)
    line_ids = fields.One2many("sco.hvac.product.component.bridge.line", "bridge_id")

    _one_active = models.Constraint(
        "unique(company_id, sales_product_id, qualification_id, revision)",
        "A component bridge revision already exists for this product and qualification.",
    )

    @api.constrains("sales_product_id", "qualification_id", "company_id", "source_attachment_id")
    def _check_identity(self):
        for bridge in self:
            qualification = bridge.qualification_id
            if qualification and (qualification.product_id != bridge.sales_product_id
                                  or qualification.company_id != bridge.company_id):
                raise ValidationError(_("The bridge sale product must match the approved qualification."))
            attachment = bridge.source_attachment_id
            if attachment and attachment.company_id and attachment.company_id != bridge.company_id:
                raise ValidationError(_("The bridge evidence belongs to another company."))

    def _check_approval(self):
        for bridge in self:
            if bridge.qualification_id.state != "approved":
                raise ValidationError(_("The equipment qualification must be approved first."))
            if not bridge.line_ids:
                raise ValidationError(_("A bridge needs indoor and outdoor component lines."))
            roles = bridge.line_ids.mapped("component_role")
            if sorted(roles) != ["indoor_unit", "outdoor_unit"]:
                raise ValidationError(_("A concealed split bridge must contain exactly one indoor and one outdoor unit."))
            if not all((bridge.source_ref, bridge.source_version, bridge.source_attachment_id)):
                raise ValidationError(_("Bridge approval requires traceable compatibility evidence."))
            bridge.line_ids._check_line()

    def action_submit(self):
        for bridge in self:
            if bridge.state != "draft":
                raise UserError(_("Only a draft bridge may be submitted."))
            bridge._check_approval()
        return super().write({"state": "submitted"})

    def action_approve(self):
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("System or designated engineering approval is required."))
        for bridge in self:
            if bridge.state != "submitted":
                raise UserError(_("Only a submitted bridge may be approved."))
            bridge._check_approval()
        return super().write({"state": "approved", "approved_by": self.env.user.id,
                              "approved_at": fields.Datetime.now()})

    def write(self, vals):
        if any(rec.state in ("approved", "retired") for rec in self):
            raise UserError(_("An approved bridge is immutable; create a new revision."))
        if "state" in vals or set(vals) & {"revision", "approved_by", "approved_at"}:
            raise UserError(_("Use the bridge approval workflow."))
        return super().write(vals)


class ComponentBridgeLine(models.Model):
    _name = "sco.hvac.product.component.bridge.line"
    _description = "HVAC Sale Component Bridge Line"
    _order = "bridge_id, component_role"
    _check_company_auto = True

    bridge_id = fields.Many2one("sco.hvac.product.component.bridge", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="bridge_id.company_id", store=True)
    component_role = fields.Selection([("indoor_unit", "Indoor Unit"), ("outdoor_unit", "Outdoor Unit")],
                                      required=True)
    component_product_id = fields.Many2one("product.product", required=True, check_company=True,
                                            ondelete="restrict")
    component_oem_spec_id = fields.Many2one("sco.hvac.oem.spec", required=True, check_company=True,
                                            ondelete="restrict")
    quantity_per_sale = fields.Float(required=True, default=1.0)
    uom_id = fields.Many2one("uom.uom", required=True)
    compatibility_ref = fields.Char(required=True)
    source_line_ref = fields.Char(required=True)

    _one_role = models.Constraint(
        "unique(bridge_id, component_role)", "Each bridge can contain one line per component role.",
    )

    def _check_line(self):
        for line in self:
            if line.quantity_per_sale <= 0 or not line.uom_id:
                raise ValidationError(_("Component quantity and unit must be positive."))
            spec = line.component_oem_spec_id
            if spec.state != "approved" or spec.product_tmpl_id != line.component_product_id.product_tmpl_id:
                raise ValidationError(_("Each component must match its approved OEM evidence."))
            if not (line.compatibility_ref or "").strip():
                raise ValidationError(_("Technical compatibility evidence is required."))
            if not line.uom_id._has_common_reference(line.component_product_id.uom_id):
                raise ValidationError(_("The component unit is incompatible with the product unit."))

    @api.constrains("component_product_id", "component_oem_spec_id", "quantity_per_sale", "uom_id",
                    "compatibility_ref", "source_line_ref")
    def _check_line_constraint(self):
        self._check_line()

    def write(self, vals):
        if any(line.bridge_id.state in ("approved", "retired") for line in self):
            raise UserError(_("An approved bridge line is immutable; create a new revision."))
        return super().write(vals)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    component_bridge_id = fields.Many2one("sco.hvac.product.component.bridge", readonly=True, copy=False)
    component_requirements_generated = fields.Boolean(readonly=True, copy=False)

    def _component_payment_eligible(self):
        self.ensure_one()
        order = self.order_id
        if not getattr(order, "require_payment", False):
            return True
        paid = getattr(order, "amount_paid", 0.0)
        return paid >= order.amount_total

    def _component_bridge(self):
        self.ensure_one()
        qualification = self.env["sco.hvac.sales.equipment.qualification"].sudo().search([
            ("product_id", "=", self.product_id.id), ("state", "=", "approved"),
            ("ac_type", "=", "concealed"),
        ], limit=1)
        return self.env["sco.hvac.product.component.bridge"].sudo().search([
            ("sales_product_id", "=", self.product_id.id), ("qualification_id", "=", qualification.id),
            ("state", "=", "approved"),
        ], limit=1)

    def action_generate_component_requirements(self, from_confirmation=False):
        for line in self:
            bridge = line._component_bridge()
            if not bridge:
                continue
            if line.order_id.state not in ("sale", "done"):
                raise UserError(_("Component requirements require a confirmed sale."))
            if not line._component_payment_eligible():
                if from_confirmation:
                    continue
                raise UserError(_("Component requirements are released after the required payment."))
            if not line.order_id.project_id or not line.order_id.fsm_location_id:
                raise UserError(_("The confirmed sale needs a project and site before component release."))
            line._sco_create_component_boq(bridge)
            line.with_context(component_bridge_write=True).write({
                "component_bridge_id": bridge.id, "component_requirements_generated": True,
            })
        return True

    def _sco_cancel_commercial_stock_moves(self):
        """The sale product is a commercial system line, not an inventory kit."""
        for line in self:
            line.move_ids.filtered(lambda move: move.state not in ("done", "cancel"))._action_cancel()

    def _sco_create_component_boq(self, bridge):
        self.ensure_one()
        BoqLine = self.env["sco.hvac.boq.line"].sudo()
        generation = "sale:%s:line:%s:bridge:%s" % (self.order_id.id, self.id, bridge.id)
        existing = BoqLine.search([("component_generation_key", "=", generation)])
        if existing:
            return existing.mapped("boq_id")[:1]
        source = bridge.source_attachment_id
        boq = self.env["sco.hvac.boq"].sudo().create({
            "name": _("Component Requirements — %(sale)s", sale=self.order_id.name),
            "company_id": self.order_id.company_id.id,
            "partner_id": self.order_id.partner_id.id,
            "location_id": self.order_id.fsm_location_id.id,
            "project_id": self.order_id.project_id.id,
            "source_sale_order_id": self.order_id.id,
            "line_ids": [(0, 0, {
                "product_id": component.component_product_id.id,
                "description": component.component_product_id.display_name,
                "quantity": self.product_uom_id._compute_quantity(
                    self.product_uom_qty * component.quantity_per_sale, component.uom_id),
                "uom_id": component.uom_id.id,
                "source_type": "documented", "source_attachment_id": source.id,
                "source_ref": bridge.source_ref, "source_version": bridge.source_version,
                "source_locator": component.source_line_ref,
                "source_document_date": fields.Date.context_today(self),
                "measurement_method": "Approved product component ratio",
                "takeoff_scope": "Sale line %s; no commercial product stock movement" % self.id,
                "component_bridge_line_id": component.id,
                "source_sale_line_id": self.id,
                "component_generation_key": generation,
            }) for component in bridge.line_ids],
        })
        return boq


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_release_component_requirements(self):
        self.mapped("order_line").filtered(lambda line: not line.display_type).action_generate_component_requirements()
        self.mapped("order_line").filtered(lambda line: line.component_bridge_id)._sco_cancel_commercial_stock_moves()
        return True

    def action_confirm(self):
        result = super().action_confirm()
        self.mapped("order_line").filtered(lambda line: not line.display_type).action_generate_component_requirements(from_confirmation=True)
        self.mapped("order_line").filtered(lambda line: line._component_bridge())._sco_cancel_commercial_stock_moves()
        return result
