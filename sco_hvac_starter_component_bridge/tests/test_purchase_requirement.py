import base64

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestPurchaseRequirement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "R01 Purchase Requirement Customer"})
        cls.location = cls.env["fsm.location"].create({
            "name": "R01 Purchase Requirement Site",
            "owner_id": cls.partner.id,
        })
        cls.project = cls.env["project.project"].create({
            "name": "R01 Purchase Requirement Project",
            "partner_id": cls.partner.id,
            "company_id": cls.env.company.id,
        })
        cls.sales_product = cls.env["product.product"].create({
            "name": "R01 Sales Fixture",
            "sale_ok": True,
            "purchase_ok": False,
            "type": "service",
        })
        cls.purchase_product = cls.env["product.product"].create({
            "name": "R01 Purchase Fixture",
            "sale_ok": False,
            "purchase_ok": True,
            "type": "consu",
            "is_storable": True,
        })
        cls.purchase_service = cls.env["product.product"].create({
            "name": "R01 Purchased Service Fixture",
            "sale_ok": False,
            "purchase_ok": True,
            "type": "service",
        })
        cls.non_purchase_product = cls.env["product.product"].create({
            "name": "R01 Non Purchase Fixture",
            "sale_ok": True,
            "purchase_ok": False,
            "type": "consu",
        })
        cls.kg_uom = cls.env.ref("uom.product_uom_kgm")

    def _new_boq_line(self, project=True, complete_source=False):
        boq = self.env["sco.hvac.boq"].create({
            "name": "R01 BOQ",
            "partner_id": self.partner.id,
            "location_id": self.location.id,
            "project_id": self.project.id if project else False,
        })
        values = {
            "boq_id": boq.id,
            "product_id": self.sales_product.id,
            "description": "R01 customer-facing BOQ line",
            "quantity": 1.0,
            "uom_id": self.sales_product.uom_id.id,
            "source_type": "documented",
            "source_ref": "R01-BOQ",
            "source_version": "1",
            "source_locator": "L1",
        }
        if complete_source:
            attachment = self.env["ir.attachment"].sudo().create({
                "name": "r01-source.pdf",
                "type": "binary",
                "datas": base64.b64encode(b"R01 approved BOQ source"),
                "mimetype": "application/pdf",
                "company_id": self.env.company.id,
            })
            values.update({
                "source_attachment_id": attachment.id,
                "source_document_date": fields.Date.today(),
                "measurement_method": "Approved explicit test quantity",
                "takeoff_scope": "R01 isolated acceptance fixture",
            })
        return self.env["sco.hvac.boq.line"].create(values)

    def _requirement_values(self, boq_line, **overrides):
        values = {
            "boq_line_id": boq_line.id,
            "purchase_product_id": self.purchase_product.id,
            "quantity": 2.0,
            "uom_id": self.purchase_product.uom_id.id,
            "technical_specification": "Specification A",
            "quantity_source": "boq",
            "source_reference": "R01-BOQ-L1-A",
        }
        values.update(overrides)
        return values

    def _sql_measurement(self, *, company, project, state="engineering_approved"):
        study = self.env["sco.hvac.sales.study"].with_company(company).create({
            "name": "R01 measurement source study",
            "company_id": company.id,
            "partner_id": self.partner.id,
            "project_id": project.id,
            "default_ac_type": "wall_split",
            "rating_condition": "t3",
        })
        self.env.cr.execute(
            """
            INSERT INTO sco_hvac_measurement
                (uid, company_id, study_id, source_kind, drawing_number,
                 drawing_issue, page_number, measurement_type, uom_id, state,
                 prepared_by, quantity, create_uid, write_uid, create_date, write_date)
            VALUES
                (%s, %s, %s, 'pdf', 'R01-MEAS', 'A', 1, 'length', %s, %s,
                 %s, 1.0, %s, %s, NOW(), NOW())
            RETURNING id
            """,
            (
                f"r01-measurement-{company.id}-{project.id}-{state}",
                company.id,
                study.id,
                self.env.ref("uom.product_uom_meter").id,
                state,
                self.env.user.id,
                self.env.user.id,
                self.env.user.id,
            ),
        )
        return self.env["sco.hvac.measurement"].browse(self.env.cr.fetchone()[0])

    def test_model_fields_and_multiple_requirements_per_boq_line(self):
        self.assertIn("sco.hvac.purchase.requirement", self.env)
        Requirement = self.env["sco.hvac.purchase.requirement"]
        expected_fields = {
            "boq_line_id", "boq_id", "project_id", "company_id", "boq_state",
            "sales_product_id", "purchase_product_id", "requirement_kind", "quantity",
            "uom_id", "technical_specification", "notes", "quantity_source",
            "source_reference", "source_attachment_id", "measurement_id",
            "previous_requirement_id",
        }
        self.assertFalse(expected_fields - set(Requirement._fields))
        self.assertIn("purchase_requirement_ids", self.env["sco.hvac.boq.line"]._fields)
        boq_line = self._new_boq_line()
        requirements = Requirement.create([
            self._requirement_values(boq_line),
            self._requirement_values(
                boq_line,
                quantity=3.0,
                technical_specification="Specification B",
                quantity_source="approved_manual",
                source_reference="R01-MANUAL-L1-B",
            ),
        ])
        self.assertEqual(len(requirements), 2)
        self.assertEqual(boq_line.purchase_requirement_ids, requirements)
        self.assertEqual(requirements.mapped("project_id"), self.project)
        self.assertEqual(requirements.mapped("sales_product_id"), self.sales_product)

    def test_requirement_rejects_invalid_identity_quantity_and_uom(self):
        Requirement = self.env["sco.hvac.purchase.requirement"]
        boq_line = self._new_boq_line()
        invalid_values = [
            self._requirement_values(boq_line, quantity=0.0),
            self._requirement_values(boq_line, quantity=float("nan")),
            self._requirement_values(boq_line, quantity=float("inf")),
            self._requirement_values(boq_line, purchase_product_id=self.non_purchase_product.id),
            self._requirement_values(boq_line, uom_id=self.kg_uom.id),
            self._requirement_values(boq_line, technical_specification=""),
            self._requirement_values(boq_line, source_reference=""),
            self._requirement_values(
                boq_line,
                quantity_source="measurement",
                source_reference="R01-MEASUREMENT-MISSING",
            ),
        ]
        for values in invalid_values:
            with self.subTest(values=values), self.assertRaises(ValidationError):
                Requirement.create(values)
        no_project_line = self._new_boq_line(project=False)
        with self.assertRaises(ValidationError):
            Requirement.create(self._requirement_values(no_project_line))

    def test_measurement_source_must_be_approved_and_match_project_company(self):
        Requirement = self.env["sco.hvac.purchase.requirement"]
        line = self._new_boq_line()
        other_project = self.env["project.project"].create({
            "name": "R01 Other Measurement Project",
            "partner_id": self.partner.id,
            "company_id": self.env.company.id,
        })
        draft_measurement = self._sql_measurement(
            company=self.env.company,
            project=self.project,
            state="draft",
        )
        unrelated_measurement = self._sql_measurement(
            company=self.env.company,
            project=other_project,
        )
        approved_measurement = self._sql_measurement(
            company=self.env.company,
            project=self.project,
        )
        for measurement in (draft_measurement, unrelated_measurement):
            with self.subTest(measurement=measurement), self.assertRaises(ValidationError):
                Requirement.create(self._requirement_values(
                    line,
                    quantity_source="measurement",
                    source_reference="R01-MEASUREMENT",
                    measurement_id=measurement.id,
                ))
        valid = Requirement.create(self._requirement_values(
            line,
            quantity_source="measurement",
            source_reference="R01-MEASUREMENT-APPROVED",
            measurement_id=approved_measurement.id,
        ))
        self.assertEqual(valid.measurement_id, approved_measurement)
        self.assertTrue(Requirement._fields["measurement_id"].check_company)

    def test_requirement_classifies_material_and_purchased_service(self):
        Requirement = self.env["sco.hvac.purchase.requirement"]
        boq_line = self._new_boq_line()
        material = Requirement.create(self._requirement_values(boq_line))
        service = Requirement.create(self._requirement_values(
            boq_line,
            purchase_product_id=self.purchase_service.id,
            uom_id=self.purchase_service.uom_id.id,
            technical_specification="Purchased installation service",
            source_reference="R01-SERVICE",
        ))
        self.assertEqual(material.requirement_kind, "material")
        self.assertEqual(service.requirement_kind, "service")

    def test_approved_requirements_reject_create_write_and_unlink(self):
        Requirement = self.env["sco.hvac.purchase.requirement"]
        boq_line = self._new_boq_line(complete_source=True)
        requirement = Requirement.create(self._requirement_values(boq_line))
        boq = boq_line.boq_id
        reviewer_group = self.env.ref("sco_hvac_starter_boq.group_boq_reviewer")
        reviewer = self.env["res.users"].create({
            "name": "R01 Independent BOQ Reviewer",
            "login": "r01-independent-boq-reviewer@example.invalid",
            "group_ids": [(6, 0, [reviewer_group.id])],
        })
        boq.action_submit()
        boq.with_user(reviewer).action_approve()
        self.assertEqual(requirement.boq_state, "approved")
        with self.assertRaises(UserError):
            requirement.write({"quantity": 3.0})
        with self.assertRaises(UserError):
            requirement.unlink()
        with self.assertRaises(UserError):
            Requirement.create(self._requirement_values(boq_line, source_reference="R01-LATE"))

    def test_boq_revision_copies_requirements_and_preserves_predecessor(self):
        Requirement = self.env["sco.hvac.purchase.requirement"]
        original_line = self._new_boq_line(complete_source=True)
        original_requirements = Requirement.create([
            self._requirement_values(original_line),
            self._requirement_values(
                original_line,
                purchase_product_id=self.purchase_service.id,
                uom_id=self.purchase_service.uom_id.id,
                quantity=1.0,
                technical_specification="Purchased specialist service",
                quantity_source="approved_manual",
                source_reference="R01-SERVICE-REVISION",
                notes="Retain this note across revisions",
            ),
        ])
        reviewer_group = self.env.ref("sco_hvac_starter_boq.group_boq_reviewer")
        reviewer = self.env["res.users"].create({
            "name": "R01 Revision Reviewer",
            "login": "r01-revision-reviewer@example.invalid",
            "group_ids": [(6, 0, [reviewer_group.id])],
        })
        original_line.boq_id.action_submit()
        original_line.boq_id.with_user(reviewer).action_approve()

        action = original_line.boq_id.action_new_revision()
        revision = self.env["sco.hvac.boq"].browse(action["res_id"])
        revision_requirements = revision.line_ids.purchase_requirement_ids

        self.assertEqual(revision.previous_id, original_line.boq_id)
        self.assertEqual(revision.state, "draft")
        self.assertEqual(len(revision_requirements), 2)
        self.assertEqual(
            revision_requirements.mapped("previous_requirement_id"),
            original_requirements,
        )
        self.assertEqual(
            revision_requirements.mapped("purchase_product_id"),
            original_requirements.mapped("purchase_product_id"),
        )
        self.assertEqual(
            revision_requirements.mapped("source_reference"),
            original_requirements.mapped("source_reference"),
        )
        self.assertEqual(
            revision_requirements.filtered(lambda item: item.notes).notes,
            "Retain this note across revisions",
        )
        self.assertEqual(original_requirements.mapped("boq_state"), ["approved", "approved"])

        revision.action_submit()
        revision.with_user(reviewer).action_approve()
        second_action = revision.action_new_revision()
        second_revision = self.env["sco.hvac.boq"].browse(second_action["res_id"])
        second_requirements = second_revision.line_ids.purchase_requirement_ids
        self.assertEqual(
            second_requirements.mapped("previous_requirement_id"),
            revision_requirements,
        )
        self.assertFalse(
            second_requirements.filtered(
                lambda item: item.previous_requirement_id in original_requirements
            )
        )

    def test_revision_lineage_cannot_be_forged_or_moved(self):
        Requirement = self.env["sco.hvac.purchase.requirement"]
        first_line = self._new_boq_line()
        second_line = self._new_boq_line()
        predecessor = Requirement.create(self._requirement_values(first_line))
        with self.assertRaises(UserError):
            Requirement.create(self._requirement_values(
                second_line,
                previous_requirement_id=predecessor.id,
            ))
        with self.assertRaises(UserError):
            predecessor.write({"boq_line_id": second_line.id})

    def test_project_aggregation_action_keeps_original_boq_sources(self):
        Requirement = self.env["sco.hvac.purchase.requirement"]
        first_line = self._new_boq_line()
        second_line = self._new_boq_line()
        requirements = Requirement.create([
            self._requirement_values(first_line, quantity=2.0, source_reference="R01-PROJECT-A"),
            self._requirement_values(
                second_line,
                quantity=3.0,
                technical_specification="Specification B",
                source_reference="R01-PROJECT-B",
            ),
            self._requirement_values(
                self._new_boq_line(),
                quantity=4.0,
                source_reference="R01-PROJECT-C",
            ),
        ])

        self.assertEqual(self.project.purchase_requirement_count, 3)
        action = self.project.action_open_purchase_requirements()
        self.assertEqual(action["res_model"], "sco.hvac.purchase.requirement")
        self.assertEqual(action["domain"], [("project_id", "=", self.project.id)])
        self.assertEqual(action["context"]["search_default_group_by_purchase_product"], 1)
        self.assertEqual(action["context"]["search_default_group_by_kind"], 2)
        self.assertEqual(action["context"]["search_default_group_by_specification"], 3)
        grouped = Requirement._read_group(
            [("id", "in", requirements.ids)],
            [
                "purchase_product_id",
                "requirement_kind",
                "technical_specification",
                "uom_id",
            ],
            ["quantity:sum"],
        )
        self.assertEqual(len(grouped), 2)
        self.assertEqual(sorted(item[4] for item in grouped), [3.0, 6.0])
        self.assertEqual(len(requirements.mapped("boq_line_id")), 3)
        self.assertEqual(
            requirements.mapped("source_reference"),
            ["R01-PROJECT-A", "R01-PROJECT-B", "R01-PROJECT-C"],
        )

    def test_security_and_internal_views(self):
        Requirement = self.env["sco.hvac.purchase.requirement"]
        line = self._new_boq_line()
        requirement = Requirement.create(self._requirement_values(line))
        sales_user = self.env["res.users"].create({
            "name": "R01 Sales Requirement Editor",
            "login": "r01-sales-requirement-editor@example.invalid",
            "group_ids": [(6, 0, [self.env.ref("sales_team.group_sale_salesman").id])],
        })
        purchase_user = self.env["res.users"].create({
            "name": "R01 Purchase Requirement Reader",
            "login": "r01-purchase-requirement-reader@example.invalid",
            "group_ids": [(6, 0, [self.env.ref("purchase.group_purchase_user").id])],
        })
        portal_user = self.env["res.users"].create({
            "name": "R01 Portal Customer",
            "login": "r01-portal-customer@example.invalid",
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
        })

        internal_user = self.env["res.users"].create({
            "name": "R01 Unprivileged Internal User",
            "login": "r01-unprivileged-internal@example.invalid",
            "group_ids": [(6, 0, [self.env.ref("base.group_user").id])],
        })

        requirement.with_user(sales_user).write({"notes": "Reviewed by sales"})
        sales_boq = self.env["sco.hvac.boq"].with_user(sales_user).create({
            "name": "R01 Sales-Owned BOQ",
            "partner_id": self.partner.id,
            "location_id": self.location.id,
            "project_id": self.project.id,
        })
        sales_line = self.env["sco.hvac.boq.line"].with_user(sales_user).create({
            "boq_id": sales_boq.id,
            "product_id": self.sales_product.id,
            "description": "R01 sales-owned line",
            "quantity": 1.0,
            "uom_id": self.sales_product.uom_id.id,
            "source_type": "documented",
            "source_ref": "R01-SALES",
            "source_version": "1",
            "source_locator": "L1",
        })
        sales_created = Requirement.with_user(sales_user).create(
            self._requirement_values(sales_line, source_reference="R01-SALES-CREATE")
        )
        sales_created.with_user(sales_user).unlink()
        requirement.with_user(purchase_user).check_access("read")
        with self.assertRaises(AccessError):
            requirement.with_user(purchase_user).write({"notes": "Purchase attempted edit"})
        with self.assertRaises(AccessError):
            requirement.with_user(portal_user).check_access("read")
        with self.assertRaises(AccessError):
            requirement.with_user(internal_user).check_access("read")

        list_view = self.env.ref(
            "sco_hvac_starter_component_bridge.view_purchase_requirement_list"
        )
        form_view = self.env.ref(
            "sco_hvac_starter_component_bridge.view_purchase_requirement_form"
        )
        boq_view = self.env.ref(
            "sco_hvac_starter_component_bridge.view_boq_form_purchase_requirements"
        )
        project_view = self.env.ref(
            "sco_hvac_starter_component_bridge.view_project_form_purchase_requirements"
        )
        self.assertEqual(list_view.model, "sco.hvac.purchase.requirement")
        self.assertEqual(form_view.model, "sco.hvac.purchase.requirement")
        self.assertEqual(boq_view.inherit_id, self.env.ref("sco_hvac_starter_boq.view_boq_form"))
        self.assertEqual(project_view.inherit_id, self.env.ref("project.edit_project"))
        self.assertNotIn("sale.order", (list_view | form_view | boq_view | project_view).mapped("model"))
        readonly_list = self.env.ref(
            "sco_hvac_starter_component_bridge.view_project_purchase_requirement_list"
        )
        readonly_form = self.env.ref(
            "sco_hvac_starter_component_bridge.view_project_purchase_requirement_form"
        )
        self.assertIn('create="0"', readonly_list.arch_db)
        self.assertIn('edit="0"', readonly_list.arch_db)
        self.assertIn('delete="0"', readonly_list.arch_db)
        self.assertIn('create="0"', readonly_form.arch_db)
        project_action = self.project.action_open_purchase_requirements()
        self.assertEqual(project_action["views"][0], (readonly_list.id, "list"))
        self.assertEqual(project_action["views"][1], (readonly_form.id, "form"))

    def test_company_rule_isolates_requirements(self):
        Requirement = self.env["sco.hvac.purchase.requirement"]
        own_requirement = Requirement.create(self._requirement_values(self._new_boq_line()))
        other_company = self.env["res.company"].create({"name": "R01 Other Company"})
        other_partner = self.env["res.partner"].create({"name": "R01 Other Company Customer"})
        other_location = self.env["fsm.location"].with_company(other_company).create({
            "name": "R01 Other Company Site",
            "owner_id": other_partner.id,
            "company_id": other_company.id,
        })
        other_project = self.env["project.project"].with_company(other_company).create({
            "name": "R01 Other Company Project",
            "partner_id": other_partner.id,
            "company_id": other_company.id,
        })
        other_boq = self.env["sco.hvac.boq"].with_company(other_company).create({
            "name": "R01 Other Company BOQ",
            "company_id": other_company.id,
            "partner_id": other_partner.id,
            "location_id": other_location.id,
            "project_id": other_project.id,
        })
        other_line = self.env["sco.hvac.boq.line"].with_company(other_company).create({
            "boq_id": other_boq.id,
            "product_id": self.sales_product.id,
            "description": "R01 other company line",
            "quantity": 1.0,
            "uom_id": self.sales_product.uom_id.id,
            "source_type": "documented",
            "source_ref": "R01-OTHER",
            "source_version": "1",
            "source_locator": "L1",
        })
        other_requirement = Requirement.with_company(other_company).create(
            self._requirement_values(other_line, source_reference="R01-OTHER-COMPANY")
        )
        sales_user = self.env["res.users"].create({
            "name": "R01 Company-Limited Sales User",
            "login": "r01-company-limited-sales@example.invalid",
            "company_id": self.env.company.id,
            "company_ids": [(6, 0, [self.env.company.id])],
            "group_ids": [(6, 0, [self.env.ref("sales_team.group_sale_salesman").id])],
        })
        visible = Requirement.with_user(sales_user).search([
            ("id", "in", (own_requirement | other_requirement).ids),
        ])
        self.assertEqual(visible, own_requirement)

    def test_acceptance_full_kit_copper_and_ready_duct_are_internal_only(self):
        sales_products = self.env["product.product"].create([
            {
                "name": "R01 TEST ONLY - مكيف سبليت جداري",
                "sale_ok": True,
                "purchase_ok": False,
                "type": "service",
            },
            {
                "name": "R01 TEST ONLY - تمديد نحاس",
                "sale_ok": True,
                "purchase_ok": False,
                "type": "service",
            },
            {
                "name": "R01 TEST ONLY - دكت دائري سبايرل",
                "sale_ok": True,
                "purchase_ok": False,
                "type": "service",
            },
        ])
        purchase_products = self.env["product.product"].create([
            {
                "name": "R01 TEST ONLY - طقم مكيف كامل",
                "sale_ok": False,
                "purchase_ok": True,
                "type": "consu",
            },
            {
                "name": "R01 TEST ONLY - لفة نحاس 3/8 بوصة 15م",
                "sale_ok": False,
                "purchase_ok": True,
                "type": "consu",
            },
            {
                "name": "R01 TEST ONLY - دكت دائري سبايرل جاهز",
                "sale_ok": False,
                "purchase_ok": True,
                "type": "consu",
            },
        ])
        attachment = self.env["ir.attachment"].sudo().create({
            "name": "r01-acceptance-source.pdf",
            "type": "binary",
            "datas": base64.b64encode(b"R01 full kit copper duct acceptance source"),
            "mimetype": "application/pdf",
            "company_id": self.env.company.id,
        })
        boq = self.env["sco.hvac.boq"].create({
            "name": "R01 ACCEPTANCE BOQ",
            "partner_id": self.partner.id,
            "location_id": self.location.id,
            "project_id": self.project.id,
        })
        lines = self.env["sco.hvac.boq.line"].create([
            {
                "boq_id": boq.id,
                "product_id": sales_product.id,
                "description": sales_product.name,
                "quantity": quantity,
                "uom_id": sales_product.uom_id.id,
                "source_type": "documented",
                "source_attachment_id": attachment.id,
                "source_ref": source_ref,
                "source_version": "1",
                "source_locator": source_ref,
                "source_document_date": fields.Date.today(),
                "measurement_method": "Approved project takeoff",
                "takeoff_scope": "R01 isolated acceptance fixture",
            }
            for sales_product, quantity, source_ref in zip(
                sales_products,
                (1.0, 30.0, 42.0),
                ("AC-KIT-01", "COPPER-LENGTH-01", "DUCT-DIM-01"),
            )
        ])
        before = {
            "products": self.env["product.product"].search_count([]),
            "product_templates": self.env["product.template"].search_count([]),
            "uoms": self.env["uom.uom"].search_count([]),
            "purchase_orders": self.env["purchase.order"].search_count([]),
            "purchase_lines": self.env["purchase.order.line"].search_count([]),
            "pickings": self.env["stock.picking"].search_count([]),
            "stock_moves": self.env["stock.move"].search_count([]),
            "stock_quants": self.env["stock.quant"].search_count([]),
            "moves": self.env["account.move"].search_count([]),
            "move_lines": self.env["account.move.line"].search_count([]),
        }

        requirements = self.env["sco.hvac.purchase.requirement"].create([
            {
                "boq_line_id": line.id,
                "purchase_product_id": purchase_product.id,
                "quantity": quantity,
                "uom_id": purchase_product.uom_id.id,
                "technical_specification": specification,
                "quantity_source": quantity_source,
                "source_reference": source_reference,
                "notes": note,
            }
            for line, purchase_product, quantity, specification, quantity_source, source_reference, note in zip(
                lines,
                purchase_products,
                (7.0, 2.0, 9.0),
                (
                    "طقم شراء كامل مطابق لاعتماد المشروع",
                    "مقاس 3/8 بوصة؛ طول المشروع المعتمد 30م",
                    "دكت دائري سبايرل جاهز؛ القطر والسماكة وفق DUCT-DIM-01",
                ),
                ("boq", "drawing", "drawing"),
                ("AC-KIT-01", "COPPER-LENGTH-01", "DUCT-DIM-01"),
                (
                    "منتج شراء واحد للطقم الكامل",
                    "لا توجد وصفة استهلاك أو نسبة هالك مفترضة",
                    "الأبعاد محفوظة في المواصفة دون إنشاء منتج لكل قطر",
                ),
            )
        ])

        self.assertEqual(len(requirements), 3)
        self.assertEqual(requirements.mapped("boq_line_id"), lines)
        self.assertEqual(self.env["product.product"].search_count([]), before["products"])
        self.assertEqual(
            self.env["product.template"].search_count([]), before["product_templates"]
        )
        self.assertEqual(self.env["uom.uom"].search_count([]), before["uoms"])
        self.assertEqual(self.env["purchase.order"].search_count([]), before["purchase_orders"])

        reviewer = self.env["res.users"].create({
            "name": "R01 Acceptance Reviewer",
            "login": "r01-acceptance-reviewer@example.invalid",
            "group_ids": [(6, 0, [self.env.ref("sco_hvac_starter_boq.group_boq_reviewer").id])],
        })
        boq.action_submit()
        boq.with_user(reviewer).action_approve()
        sale_action = boq.action_create_quotation()
        order = self.env["sale.order"].browse(sale_action["res_id"])

        self.assertEqual(order.order_line.mapped("product_id"), sales_products)
        self.assertEqual(order.order_line.mapped("product_uom_qty"), [1.0, 30.0, 42.0])
        self.assertEqual(order.order_line.mapped("price_unit"), [0.0, 0.0, 0.0])
        self.assertEqual(order.order_line.mapped("price_subtotal"), [0.0, 0.0, 0.0])
        for order_line, sales_product in zip(order.order_line, sales_products):
            expected_taxes = sales_product.taxes_id.filtered(
                lambda tax: tax.company_id in (False, order.company_id)
            )
            self.assertEqual(order_line.tax_ids, expected_taxes)
        self.assertFalse(order.order_line.filtered(lambda item: item.product_id in purchase_products))
        self.assertEqual(order.amount_total, 0.0)
        repeated_action = boq.action_create_quotation()
        self.assertEqual(repeated_action["res_id"], order.id)
        self.assertEqual(
            self.env["sco.hvac.purchase.requirement"].search_count([
                ("boq_id", "=", boq.id),
            ]),
            3,
        )
        self.assertEqual(self.env["purchase.order"].search_count([]), before["purchase_orders"])
        self.assertEqual(
            self.env["purchase.order.line"].search_count([]), before["purchase_lines"]
        )
        self.assertEqual(self.env["stock.picking"].search_count([]), before["pickings"])
        self.assertEqual(self.env["stock.move"].search_count([]), before["stock_moves"])
        self.assertEqual(self.env["stock.quant"].search_count([]), before["stock_quants"])
        self.assertEqual(self.env["account.move"].search_count([]), before["moves"])
        self.assertEqual(self.env["account.move.line"].search_count([]), before["move_lines"])

    def test_cloned_catalog_copper_and_duct_identities_are_usable(self):
        copper_sale = self.env["product.product"].search([
            ("name", "=", "تمديد نحاس مولر أمريكي"),
            ("sale_ok", "=", True),
        ], limit=1)
        copper_purchase = self.env["product.product"].search([
            ("name", "=", "لفة نحاس مولر أمريكي 3/8 بوصة — 15م"),
            ("purchase_ok", "=", True),
        ], limit=1)
        duct_sale = self.env["product.product"].search([
            ("name", "=", "مجاري هواء دكت دائري"),
            ("sale_ok", "=", True),
        ], limit=1)
        duct_purchase = self.env["product.product"].search([
            ("name", "=", "دكت دائري سبايرل مجلفن جاهز — حسب مواصفات المشروع"),
            ("purchase_ok", "=", True),
        ], limit=1)
        if not all((copper_sale, copper_purchase, duct_sale, duct_purchase)):
            self.skipTest("Starter catalog identities are unavailable in this clean database")

        product_count = self.env["product.product"].search_count([])
        copper_line = self._new_boq_line()
        duct_line = self._new_boq_line()
        copper_line.product_id = copper_sale
        duct_line.product_id = duct_sale
        requirements = self.env["sco.hvac.purchase.requirement"].create([
            self._requirement_values(
                copper_line,
                purchase_product_id=copper_purchase.id,
                uom_id=copper_purchase.uom_id.id,
                quantity=2.0,
                technical_specification="3/8 بوصة؛ لفتان × 15م؛ طول المشروع 30م",
                quantity_source="drawing",
                source_reference="CATALOG-COPPER-30M",
            ),
            self._requirement_values(
                duct_line,
                purchase_product_id=duct_purchase.id,
                uom_id=duct_purchase.uom_id.id,
                quantity=42.0,
                technical_specification="دائري سبايرل جاهز؛ الأبعاد حسب DUCT-DIM-42",
                quantity_source="drawing",
                source_reference="CATALOG-DUCT-42",
            ),
        ])
        self.assertEqual(requirements.mapped("purchase_product_id"), copper_purchase | duct_purchase)
        self.assertEqual(self.env["product.product"].search_count([]), product_count)
