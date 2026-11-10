# SCO Technologies Target Roadmap

## Status

This document is a proposed target structure for the SCO technology portfolio. It is not an inventory of confirmed repositories, deployed systems, or existing products.

The current `alkaiiser/sco` repository remains the active SCO B2B Procurement Platform. No repository is renamed, transferred, created, or split by this document.

## Proposed portfolio boundaries

| Proposed boundary | Intended responsibility | Current status |
| --- | --- | --- |
| `sco-platform` | Shared platform capabilities, infrastructure standards, delivery controls, and deployment contracts | Current `alkaiiser/sco` is the platform starting point |
| `sco-odoo-core` | Shared Odoo modules, integrations, and technical conventions | Proposed; requires an Odoo inventory |
| `sco-odoo-sectors` | Sector-specific Odoo packages kept separate from shared core | Proposed; requires domain ownership |
| `sco-field` | Field sales and distribution product boundaries | Proposed; requires product and deployment inventory |
| `sco-mobile` | SCO mobile applications and mobile-specific services | Proposed; requires application inventory |
| `sco-connect` | Digital branch, integration, and external communication contracts | Proposed; requires interface inventory |
| `sco-customer-extensions` | Isolated customer customizations with per-customer access boundaries | Proposed; requires tenancy and ownership policy |

## Principles

1. `sco-platform` is the system of record for shared platform contracts, security gates, and delivery standards.
2. Odoo, Field, Mobile, Connect, and customer extensions must not be inferred from the current `sco` repository without verified evidence.
3. Customer extensions must remain isolated by customer, data boundary, credentials, and deployment authorization.
4. Shared code belongs in a shared boundary only when ownership, release responsibility, and compatibility policy are explicit.
5. Production systems, live credentials, DNS, and existing deployments are outside the scope of repository restructuring.
6. A proposed repository name is not authorization to create or move a repository.

## Phased path

### Phase 0: Confirm the current boundary

- Keep `alkaiiser/sco` focused on the B2B Procurement Platform.
- Keep the repository security gates, recovery drills, and dependency maintenance green.
- Record verified ownership and runtime boundaries before any portfolio change.

### Phase 1: Inventory

- Build a read-only inventory of confirmed Odoo, Field, Mobile, Connect, hosting, and backup assets.
- Identify owners, source repositories, environments, data classifications, integrations, and recovery responsibilities.
- Record unknowns explicitly; do not fill gaps with assumptions.

### Phase 2: Define contracts

- Define API, event, identity, tenancy, audit, observability, and deployment contracts.
- Decide which contracts are platform-owned and which are product-owned.
- Define the approval gates for customer-specific code and production access.

### Phase 3: Select repository boundaries

- Compare the inventory with the proposed boundaries.
- Create or split repositories only after owners approve the boundary, history strategy, access model, CI policy, and rollback plan.
- Preserve `alkaiiser/sco` history and production safety during any future migration.

### Phase 4: Incremental delivery

- Move one bounded capability at a time.
- Require independent CI, security scanning, ownership metadata, and recovery evidence for each new boundary.
- Do not merge or deploy a split solely because a target repository name exists.

## Approval gates

Before creating or splitting any repository, obtain explicit owner approval for:

- the confirmed scope and owning team;
- repository visibility and collaborator access;
- customer and production data boundaries;
- secrets and credential rotation plan;
- CI, security, backup, and recovery requirements;
- migration, rollback, and decommissioning plans.

## Current decision

Adopt this structure as a planning model only. Continue development in `alkaiiser/sco` until the Phase 1 inventory and Phase 2 contracts are reviewed and approved. Leave PR #2 deferred as previously agreed.
