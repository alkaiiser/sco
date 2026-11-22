# SCO HVAC Purchase Requirement Model R01 — Approved Design

## Intent

Add one lightweight operational model for project purchase requirements without changing sales BOQ lines, product catalogs, prices, vendors, stock, accounting, or Odoo purchase transactions.

## Approved architecture

- New model: `sco.hvac.purchase.requirement` in `sco_hvac_starter_component_bridge`.
- Every requirement belongs to one `sco.hvac.boq.line`; BOQ, project, company, BOQ state, and sales product are traceable through stored related fields.
- One BOQ line may have multiple requirements. Each requirement stores one existing purchase-enabled product, explicit quantity, compatible UoM, exact technical specification, notes, quantity-source type, and source reference.
- Requirements are editable only while their BOQ revision is draft. BOQ submission/approval seals them through the existing BOQ workflow.
- Creating a BOQ revision copies requirements to the new BOQ lines and points every copy to its prior requirement. The approved predecessor remains unchanged.
- Project aggregation is a grouped read-only view of requirement rows. Grouping keys are project, material/service kind, purchase product, UoM, and exact specification. Source rows remain available by drill-down; different specifications never share a group.
- Requirements never become sale-order lines, never affect sales quantities or totals, and never create RFQs, POs, receipts, invoices, journal entries, stock moves, products, or UoMs.

## Required fields

- `boq_line_id`: required M2O → `sco.hvac.boq.line`.
- `boq_id`, `project_id`, `company_id`, `boq_state`, `sales_product_id`: stored/read-only lineage.
- `purchase_product_id`: required M2O → existing `product.product`, restricted to `purchase_ok=True`.
- `requirement_kind`: stored/read-only `material` or `service`, derived from the selected product type.
- `quantity`: required positive float.
- `uom_id`: required M2O → `uom.uom`, compatible with the selected product.
- `technical_specification`: required Char and an exact grouping key.
- `notes`: optional Text.
- `quantity_source`: required selection: `boq`, `drawing`, `measurement`, `approved_manual`.
- `source_reference`: required Char.
- `source_attachment_id`: optional M2O → `ir.attachment`.
- `measurement_id`: optional M2O → `sco.hvac.measurement`.
- `previous_requirement_id`: read-only M2O → prior revision requirement.

## Rules

- A requirement needs a BOQ project and a draft BOQ revision.
- The product must already exist and be purchase-enabled; the UI disables quick creation.
- Quantity must be positive; UoM must be compatible with the product.
- Exact specification is mandatory so copper sizes and duct dimensions remain explicit and non-interchangeable.
- Measurement sources require `measurement_id`; drawing sources use an explicit reference and may retain the source attachment.
- No ratios, waste allowances, conversion formulas, or purchasing transactions are generated.
- Wall split is represented as one full-kit purchase product when such a governed product exists. The current Starter purchase catalog contains no such product; production use of this case remains a catalog-data blocker and no product will be invented.
- Copper length/package quantities and duct dimensions come only from the approved BOQ/project source fields entered on each requirement.
- Duct uses existing generic round spiral or square/rectangular governed catalog identity; dimensions stay in `technical_specification`.

## UI and permissions

- Separate internal list/form action and menu under HVAC Components.
- Search filters for material/service and BOQ state; group-by project, kind, product, UoM, and exact specification.
- Requirements are visible from the BOQ line internal form but are absent from customer quotations/reports.
- Sales users may manage requirements only while BOQ is draft; purchase users may read them; system administrators retain full ACL subject to immutability guards.

## Acceptance

- Unit/integration tests prove multiple requirements per sales BOQ line, validation, approval immutability, revision lineage, grouped project totals, exact-specification separation, and zero automatic purchase/stock/accounting/catalog side effects.
- Three isolated cases: full AC kit (transient test fixture because the governed purchase item is absent), copper with explicit project size/package/length details, and ready duct with dimensions only in the requirement specification.
- Upgrade and acceptance run first on an isolated clone. Production deployment is Starter-only, backed up, and contains no test business records.
