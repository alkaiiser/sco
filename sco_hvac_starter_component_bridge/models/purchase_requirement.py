import math

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


REQUIREMENT_REVISION_CONTEXT_KEY = "_sco_purchase_requirement_revision"
REQUIREMENT_REVISION_TOKEN = object()


class PurchaseRequirement(models.Model):
    _name = "sco.hvac.purchase.requirement"
    _description = "SCO HVAC Purchase Requirement"
    _order = "project_id, boq_id, boq_line_id, id"
    _rec_name = "purchase_product_id"
    _check_company_auto = True

    boq_line_id = fields.Many2one(
        "sco.hvac.boq.line",
        required=True,
        index=True,
        ondelete="restrict",
        check_company=True,
    )
    boq_id = fields.Many2one(related="boq_line_id.boq_id", store=True, index=True)
    project_id = fields.Many2one(related="boq_id.project_id", store=True, index=True)
    company_id = fields.Many2one(related="boq_id.company_id", store=True, index=True)
    boq_state = fields.Selection(related="boq_id.state", store=True, index=True)
    sales_product_id = fields.Many2one(related="boq_line_id.product_id", store=True, index=True)

    purchase_product_id = fields.Many2one(
        "product.product",
        required=True,
        index=True,
        ondelete="restrict",
        check_company=True,
        domain="[('purchase_ok', '=', True)]",
    )
    requirement_kind = fields.Selection(
        [("material", "Material"), ("service", "Purchased Service")],
        compute="_compute_requirement_kind",
        store=True,
        index=True,
    )
    quantity = fields.Float(required=True)
    uom_id = fields.Many2one("uom.uom", required=True, ondelete="restrict")
    technical_specification = fields.Char(required=True, index=True)
    notes = fields.Text()
    quantity_source = fields.Selection(
        [
            ("boq", "BOQ"),
            ("drawing", "Drawing"),
            ("measurement", "Measurement"),
            ("approved_manual", "Approved Manual Input"),
        ],
        required=True,
        index=True,
    )
    source_reference = fields.Char(required=True)
    source_attachment_id = fields.Many2one("ir.attachment", ondelete="restrict")
    measurement_id = fields.Many2one(
        "sco.hvac.measurement",
        check_company=True,
        ondelete="restrict",
    )
    previous_requirement_id = fields.Many2one(
        "sco.hvac.purchase.requirement",
        readonly=True,
        copy=False,
        index=True,
        ondelete="restrict",
    )

    _previous_requirement_uniq = models.Constraint(
        "unique(previous_requirement_id)",
        "A purchase requirement can have only one direct next revision.",
    )

    @api.depends("purchase_product_id.type")
    def _compute_requirement_kind(self):
        for requirement in self:
            requirement.requirement_kind = (
                "service" if requirement.purchase_product_id.type == "service" else "material"
            )

    def _revision_values(self):
        self.ensure_one()
        return {
            "purchase_product_id": self.purchase_product_id.id,
            "quantity": self.quantity,
            "uom_id": self.uom_id.id,
            "technical_specification": self.technical_specification,
            "notes": self.notes,
            "quantity_source": self.quantity_source,
            "source_reference": self.source_reference,
            "source_attachment_id": self.source_attachment_id.id,
            "measurement_id": self.measurement_id.id,
            "previous_requirement_id": self.id,
        }

    @api.constrains(
        "boq_line_id",
        "purchase_product_id",
        "quantity",
        "uom_id",
        "technical_specification",
        "quantity_source",
        "source_reference",
        "source_attachment_id",
        "measurement_id",
    )
    def _check_requirement_values(self):
        for requirement in self:
            if not requirement.project_id:
                raise ValidationError(_("A purchase requirement needs an approved BOQ project link."))
            if not requirement.purchase_product_id.purchase_ok:
                raise ValidationError(_("A purchase requirement must use a purchase-enabled product."))
            if not math.isfinite(requirement.quantity) or requirement.quantity <= 0:
                raise ValidationError(_("Purchase requirement quantity must be positive."))
            if not requirement.uom_id._has_common_reference(requirement.purchase_product_id.uom_id):
                raise ValidationError(_("The requirement unit must be compatible with the purchase product."))
            if not (requirement.technical_specification or "").strip():
                raise ValidationError(_("An exact technical specification is required."))
            if not (requirement.source_reference or "").strip():
                raise ValidationError(_("A quantity source reference is required."))
            if requirement.quantity_source == "measurement" and not requirement.measurement_id:
                raise ValidationError(_("A measurement-sourced requirement must identify its measurement."))
            measurement = requirement.measurement_id
            if measurement:
                if measurement.company_id != requirement.company_id:
                    raise ValidationError(_("The measurement belongs to another company."))
                if measurement.state != "engineering_approved":
                    raise ValidationError(_("A measurement source must be engineering-approved."))
                source_project = (
                    measurement.project_document_id.project_id
                    or measurement.study_id.project_id
                )
                if not source_project or source_project != requirement.project_id:
                    raise ValidationError(_("The measurement source belongs to another project."))
                source_site = (
                    measurement.project_document_id.site_id
                    or measurement.study_id.site_id
                )
                if source_site and source_site != requirement.boq_id.location_id:
                    raise ValidationError(_("The measurement source belongs to another project site."))
            attachment = requirement.source_attachment_id
            if attachment and attachment.company_id and attachment.company_id != requirement.company_id:
                raise ValidationError(_("The requirement source attachment belongs to another company."))

    @api.model_create_multi
    def create(self, vals_list):
        internal_revision = (
            self.env.context.get(REQUIREMENT_REVISION_CONTEXT_KEY)
            is REQUIREMENT_REVISION_TOKEN
        )
        for values in vals_list:
            if values.get("previous_requirement_id") and not internal_revision:
                raise UserError(_("Requirement revision lineage is assigned by the BOQ workflow."))
            line = self.env["sco.hvac.boq.line"].browse(values.get("boq_line_id")).exists()
            if not line or line.boq_id.state != "draft":
                raise UserError(_("Purchase requirements may be added only to a draft BOQ revision."))
        requirements = super().create(vals_list)
        requirements._check_revision_lineage()
        return requirements

    def _check_revision_lineage(self):
        for requirement in self.filtered("previous_requirement_id"):
            previous = requirement.previous_requirement_id
            current_origin = requirement.boq_line_id.origin_line_id or requirement.boq_line_id
            previous_origin = previous.boq_line_id.origin_line_id or previous.boq_line_id
            if (
                requirement.boq_id.previous_id != previous.boq_id
                or requirement.company_id != previous.company_id
                or requirement.project_id != previous.project_id
                or current_origin != previous_origin
            ):
                raise ValidationError(_(
                    "A requirement revision must follow the same BOQ line, company, and project."
                ))

    def write(self, vals):
        if any(requirement.boq_state != "draft" for requirement in self):
            raise UserError(_("Approved purchase requirements are immutable; create a BOQ revision."))
        if "boq_line_id" in vals:
            raise UserError(_("A purchase requirement cannot move to another BOQ line."))
        if "previous_requirement_id" in vals:
            raise UserError(_("Requirement revision lineage is assigned by the BOQ workflow."))
        return super().write(vals)

    def unlink(self):
        if any(requirement.boq_state != "draft" for requirement in self):
            raise UserError(_("Approved purchase requirements are immutable; create a BOQ revision."))
        return super().unlink()
