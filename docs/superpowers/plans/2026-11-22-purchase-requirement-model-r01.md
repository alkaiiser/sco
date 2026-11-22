# SCO HVAC Purchase Requirement Model R01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an independently reviewed, revision-safe purchase-requirement layer from sales BOQ lines to existing purchase products and projects without creating purchasing transactions or changing catalogs.

**Architecture:** `sco.hvac.purchase.requirement` is owned by `sco_hvac_starter_component_bridge`, linked to one BOQ line, and governed by the parent BOQ revision state. A project list groups stored requirement rows by existing product, UoM, kind, and exact specification while retaining each source row. BOQ revision creation copies requirements with explicit predecessor lineage.

**Tech Stack:** Odoo 19 Community ORM/XML views/security, PostgreSQL, Odoo `TransactionCase`, Arabic/English translatable UI.

**Spec:** `docs/superpowers/specs/2026-11-22-purchase-requirement-model-r01-design.md`

## Global Constraints

- Work only on `sco_hvac_starter`; do not change Basic, Plus, Premium, or Projects.
- Do not change product names, flags, prices, costs, vendors, UoMs, or catalog records.
- Do not create products, RFQs, purchase orders, receipts, invoices, journal entries, stock moves, or BoMs.
- Do not generate consumption ratios, waste allowances, copper formulas, or duct manufacturing.
- Duct identity remains round spiral or square/rectangular; dimensions belong in the requirement specification.
- Every quantity keeps its BOQ-line and source reference.
- No test business records may be created in production.

## Review Focus

- Approved/superseded BOQs must reject create, write, and unlink of requirements; covered in Task 2 immutability tests.
- BOQ revision copying must preserve all source/specification values and predecessor lineage exactly once; covered in Task 3.
- Equal products with different exact specifications must never aggregate together; covered in Task 4.
- Product/UoM mismatch, non-purchase products, missing project, and non-positive quantities must fail without side effects; covered in Task 2.
- Quotation totals/lines and purchase, stock, accounting, product, and UoM counts must be unchanged by requirements; covered in Task 5.

---

### Task 1: Source-control the deployed bridge baseline and add failing model tests

**Files:**
- Create: `sco_hvac_starter_component_bridge/**` from the deployed `19.0.1.0.2` module baseline.
- Create: `sco_hvac_starter_component_bridge/tests/test_purchase_requirement.py`
- Modify: `sco_hvac_starter_component_bridge/tests/__init__.py`

**Interfaces:**
- Consumes: deployed module source at `/srv/sco-hvac-tier-source/releases/starter-commercial-r30-quick-study-20261121/sco_hvac_starter_component_bridge`.
- Produces: source-controlled baseline plus failing tests for model `sco.hvac.purchase.requirement` and `sco.hvac.boq.line.purchase_requirement_ids`.

- [ ] Copy the deployed module into the isolated worktree and verify every baseline file is byte-identical before feature edits.
- [ ] Add `test_model_fields_and_multiple_requirements_per_boq_line` asserting the approved field names, relations, and two requirements on one draft BOQ line.
- [ ] Run the module test and confirm failure because `sco.hvac.purchase.requirement` is absent.
- [ ] Commit the imported baseline and failing test separately so the deployed starting point remains auditable.

### Task 2: Implement requirement identity, validation, and immutability

**Files:**
- Create: `sco_hvac_starter_component_bridge/models/purchase_requirement.py`
- Modify: `sco_hvac_starter_component_bridge/models/__init__.py`
- Modify: `sco_hvac_starter_component_bridge/models/boq_bridge.py`
- Modify: `sco_hvac_starter_component_bridge/__manifest__.py`
- Test: `sco_hvac_starter_component_bridge/tests/test_purchase_requirement.py`

**Interfaces:**
- Consumes: `sco.hvac.boq.line` and existing BOQ state/revision workflow.
- Produces: model `sco.hvac.purchase.requirement`, inverse field `purchase_requirement_ids`, guards `_check_requirement_values`, and BOQ-state write protection.

- [ ] Add failing tests for positive quantity, purchase-enabled product, compatible UoM, required project/specification/source, measurement-source linkage, and material/service classification.
- [ ] Add failing tests proving create/write/unlink work only for draft BOQ revisions and approved records are immutable.
- [ ] Implement the exact fields and constraints from the approved design; use `models.Constraint` where identity is SQL-safe and Python constraints for cross-model validation.
- [ ] Override `create`, `write`, and `unlink` to enforce draft-only mutation without bypassing normal ACLs.
- [ ] Bump the module version from `19.0.1.0.2` to `19.0.1.1.0`.
- [ ] Run the focused tests and confirm all Task 2 tests pass.
- [ ] Commit the model and tests.

### Task 3: Copy requirements through BOQ revisions with immutable lineage

**Files:**
- Modify: `sco_hvac_starter_component_bridge/models/boq_bridge.py`
- Test: `sco_hvac_starter_component_bridge/tests/test_purchase_requirement.py`

**Interfaces:**
- Consumes: `StarterBOQLine._revision_values()` and `purchase_requirement_ids` from Task 2.
- Produces: nested revision values and `previous_requirement_id` lineage on each copied requirement.

- [ ] Add `test_boq_revision_copies_requirements_and_preserves_predecessor` with two requirements and exact source/specification assertions.
- [ ] Run it and confirm failure because revision values omit requirements.
- [ ] Extend `_revision_values()` via `super()` to include one nested copy command per requirement and set `previous_requirement_id` to the predecessor.
- [ ] Add a regression assertion that a second revision points to the immediately previous requirement and never edits older rows.
- [ ] Run focused revision and BOQ workflow tests.
- [ ] Commit revision-lineage support.

### Task 4: Add internal project aggregation UI without persisted aggregate records

**Files:**
- Modify: `sco_hvac_starter_component_bridge/models/purchase_requirement.py`
- Create: `sco_hvac_starter_component_bridge/models/project_project.py`
- Modify: `sco_hvac_starter_component_bridge/models/__init__.py`
- Modify: `sco_hvac_starter_component_bridge/views/component_bridge_views.xml`
- Modify: `sco_hvac_starter_component_bridge/security/ir.model.access.csv`
- Create: `sco_hvac_starter_component_bridge/security/purchase_requirement_rules.xml`
- Modify: `sco_hvac_starter_component_bridge/__manifest__.py`
- Test: `sco_hvac_starter_component_bridge/tests/test_purchase_requirement.py`

**Interfaces:**
- Consumes: stored requirement fields from Task 2.
- Produces: internal list/form/search action, project smart action, company record rule, and grouping by project/kind/product/UoM/exact specification.

- [ ] Add failing aggregation tests: identical keys sum quantity; different specification, UoM, product, project, or kind remains separate; source rows remain individually readable.
- [ ] Add failing XML/ACL tests proving purchase users can read, sales users can manage draft requirements, quick product creation is disabled, and customer sale views/reports are not inherited.
- [ ] Implement a project action returning the requirement list with project domain and grouped context; do not create aggregate records.
- [ ] Add list/form/search views and BOQ-line internal one2many; keep requirement fields out of sale-order views and reports.
- [ ] Add ACLs and allowed-company record rule.
- [ ] Run model, view, and access tests.
- [ ] Commit UI/security/aggregation support.

### Task 5: Prove the three acceptance cases and zero business side effects

**Files:**
- Create: `sco_hvac_starter_component_bridge/tests/test_purchase_requirement_acceptance.py`
- Modify: `sco_hvac_starter_component_bridge/tests/__init__.py`

**Interfaces:**
- Consumes: model, revision, and project UI behavior from Tasks 2–4.
- Produces: isolated acceptance evidence for full kit, copper, ready duct, quotation isolation, and no transactions/catalog mutation.

- [ ] Implement `test_wall_split_full_kit_requirement_is_one_explicit_item` using a transient test-only purchase product; assert no ratio or component expansion and no PO.
- [ ] Implement `test_copper_requirement_keeps_project_size_package_and_length_source` using an existing copper catalog identity in the cloned database; all length/package details are explicit test source values, not formulas.
- [ ] Implement `test_ready_duct_dimensions_stay_in_specification` using the existing generic round spiral product; assert no product creation and different dimensions do not aggregate.
- [ ] Add a quotation-isolation test asserting BOQ line count, sale-order line products, quantities, and total are identical with and without requirements.
- [ ] Snapshot and compare counts/fingerprints for product templates, UoMs, purchase orders/lines, stock pickings/moves/quants, account moves/lines, and BoMs before and after each scenario.
- [ ] Run the complete module tests and record IDs created inside the rolled-back test transaction where available.
- [ ] Commit acceptance tests.

### Task 6: Build and verify an isolated Starter release

**Files:**
- Create: `evidence/SCO-HVAC-PURCHASE-REQUIREMENT-MODEL-R01/` test logs, baselines, and source fingerprints.

**Interfaces:**
- Consumes: source-controlled module version `19.0.1.1.0`.
- Produces: isolated release directory and test database results; no production mutation.

- [ ] Create a new release directory from the current Starter release and overlay only the changed bridge module.
- [ ] Create a database/filestore clone named for `purchase_requirement_r01_test_20261122` and an isolated config/port.
- [ ] Upgrade only `sco_hvac_starter_component_bridge` in the clone and run `--test-enable --test-tags /sco_hvac_starter_component_bridge --stop-after-init`.
- [ ] Run a clean-install module test database to prove dependencies and security load from zero.
- [ ] Compare cloned pre/post protected catalog fingerprints and transaction counts; expected product/UoM/PO/stock/accounting/BoM changes are zero outside rolled-back test fixtures.
- [ ] Record the real catalog blocker: no purchase-enabled full wall-split kit product exists; do not create or reflag one.

### Task 7: Deploy Starter-only and issue the acceptance report

**Files:**
- Create: `evidence/SCO-HVAC-PURCHASE-REQUIREMENT-MODEL-R01/SCO-HVAC-PURCHASE-REQUIREMENT-MODEL-R01-REPORT.md`
- Create: evidence CSV/log/checksum files in the same directory.

**Interfaces:**
- Consumes: passing isolated release from Task 6.
- Produces: Starter-only deployed schema/UI plus evidence; no production test business records.

- [ ] Back up `sco_hvac_starter` database and filestore and fingerprint sales/purchase catalogs plus financial/stock transaction counts.
- [ ] Point only `/etc/sco-odoo-hvac-starter.conf` to the new release, upgrade only the bridge module, and restart only the Starter service.
- [ ] Verify registry fields, views, ACLs, module version, and empty production requirement table immediately after upgrade.
- [ ] Re-run protected fingerprints and transaction counts; require exact match for catalogs, prices, vendors, UoMs, purchase/stock/accounting/BoM records.
- [ ] Record model/field relationships, code files and source hash, isolated three-case results and record references, catalog/transaction proofs, and the full-kit catalog blocker.
- [ ] Run final verification and stop without creating operational requirements, POs, receipts, invoices, or moving data to other tiers.
