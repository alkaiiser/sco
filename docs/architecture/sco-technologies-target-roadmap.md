# SCO Technologies Architecture and Delivery Roadmap

## Executive position

**SCO — Business Development & Systems Engineering** is a technology and systems engineering company developing multiple independent but integrated products.

The former SCO B2B Procurement Platform is a **legacy project frozen for one year**. It is not SCO's main platform, architectural foundation, or starting point for future products. Its existing code and history must be preserved. No deletion, rename, migration, split, or production action is authorized by this document.

The current `alkaiiser/sco` repository is therefore classified as **SCO Legacy Procurement**. It may continue to receive safety, maintenance, and preservation work, but it must not be used as evidence that Odoo, Field, Mobile, Connect, Digital Branch, or Website & Store already exist in this repository.

## Portfolio boundaries

These are logical product boundaries. They are not approved repository names.

| Product boundary | Intended responsibility | Classification |
| --- | --- | --- |
| **SCO Platform** | Shared technical standards, reusable infrastructure, security, CI/CD, identity, observability, and integration contracts | Proposed shared foundation; not identified as the current `alkaiiser/sco` repository |
| **SCO Odoo** | Main ERP and business-operations ecosystem based on Odoo Community and open-source extensions | Proposed product ecosystem; codebase not verified in accessible GitHub inventory |
| **SCO Odoo Sectors** | Specialized sector packages built on the shared Odoo ecosystem | Proposed product boundary; requires sector ownership and compatibility policy |
| **SCO Field — By Odoo** | Independent field sales and distribution product integrated with authorized SCO Odoo environments | Proposed independent product |
| **SCO Mobile** | Independent iOS/Android application platform connected to authorized Odoo environments | Proposed independent product |
| **SCO Connect** | Communication, meetings, and customer-interaction infrastructure | Proposed independent product/integration boundary |
| **SCO Digital Branch** | Independent digital-branch product integrated with SCO Connect and Odoo | Proposed independent product |
| **SCO Website & Store** | Corporate website, service catalog, checkout, CRM integration, and customer acquisition | Proposed independent product |
| **SCO Customer Extensions** | Customer-specific implementations and extensions with strict per-customer isolation | Proposed delivery boundary |
| **SCO Legacy Procurement** | Frozen B2B procurement project retained separately with preserved history | Confirmed current GitHub asset: `alkaiiser/sco` |

## Architecture model

`
                         SCO Platform
       standards · identity · security · CI/CD · contracts
            /       |        |         |          \
         Odoo   Connect   Website    Mobile     Field
          |        |         |          |          |
   Odoo Sectors  Digital Branch   CRM/Store   authorized Odoo
          |
  Customer Extensions (isolated per customer)

  Legacy Procurement: preserved separately; not a platform dependency
`

The arrows describe intended integration contracts, not current runtime connections. Every connection requires an owner, interface contract, authentication model, data classification, and recovery responsibility.

## Monorepo versus multirepo decision

### Current verified state

`alkaiiser/sco` is a pnpm workspace monorepo containing:

- `apps/api`: NestJS/Fastify API with Prisma/PostgreSQL integration.
- `apps/partner-web`: Next.js partner web application.
- `apps/operations-web`: Next.js operations web application.
- `packages/config` and `packages/contracts`: shared workspace packages.
- Dockerfiles for the three applications.
- CI for static checks, migrations, tests, security scanning, recovery, and container builds.

### Recommendation

Do not split the legacy repository as part of this architecture exercise.

Use a **platform monorepo** only for code that has all of these properties:

- shared ownership and release cadence;
- meaningful compile-time or contract-level coupling;
- coordinated security and compatibility policy;
- no customer-specific data or deployment credentials.

Use **independent repositories** for Odoo, Field, Mobile, Connect, Digital Branch, Website & Store, and customer extensions when they have independent release cadence, runtime, ownership, access controls, or data boundaries.

Use a separate repository for Odoo sector packages only when sector modules can be versioned and tested against an explicitly supported Odoo compatibility matrix.

The final split decision requires the Phase 1 inventory and Phase 2 contract review in the companion documents. Repository names must not be created merely because they appear in this proposal.

## Dependency and integration principles

1. Odoo is the business-system authority for ERP-owned workflows once its runtime and ownership are verified.
2. Mobile and Field clients must use versioned, least-privilege APIs; they must not connect directly to arbitrary customer databases.
3. Connect and Digital Branch must expose explicit integration contracts rather than sharing database tables with unrelated products.
4. Website & Store must isolate public acquisition, checkout, and CRM concerns from internal ERP credentials.
5. Customer Extensions must be isolated by repository or explicit package boundary, customer identity, data, credentials, deployment authorization, and audit trail.
6. Shared libraries must be dependency-light, documented, semver-versioned, and free of customer data.
7. The legacy procurement application must remain outside the new platform dependency graph unless an owner approves a specific integration contract.

## Phased implementation

### Phase 0 — Preserve and correct the record

- Keep `alkaiiser/sco` unchanged in role: a frozen legacy procurement asset.
- Keep its security gates, recovery evidence, and dependency maintenance healthy.
- Update repository documentation so it no longer calls the legacy project the SCO platform.
- Do not rename, migrate, split, archive, or delete it.

### Phase 1 — Read-only inventory

- Identify confirmed repositories, local codebases, Odoo instances, mobile projects, hosting, CI/CD, integrations, backups, and owners.
- Record evidence, last-known activity, runtime, data classification, and recovery path.
- Mark unknowns explicitly and avoid inferring products from names or documents.

### Phase 2 — Contract design

- Define identity, tenancy, API, events, integration, audit, observability, deployment, and recovery contracts.
- Define Odoo authorization and environment boundaries.
- Define the customer-isolation policy and approval gates.

### Phase 3 — Organization and repository foundation

- Create the SCO GitHub organization only after owner approval.
- Establish teams, least-privilege roles, repository naming, branch protection, CODEOWNERS, environments, and reusable workflows.
- Create repositories only after scope, ownership, history strategy, access model, and rollback plan are approved.

### Phase 4 — Incremental product delivery

- Start with the highest-confidence independent product boundary.
- Require independent CI, security scanning, release evidence, and recovery evidence.
- Integrate through versioned contracts; do not share production databases by convenience.

### Phase 5 — Controlled migration

- Migrate one bounded capability at a time.
- Preserve source history and provide a rollback path.
- Freeze old paths before decommissioning any duplicate.
- Decommission only with explicit owner approval and verified backup/recovery evidence.

## Approval checklist

Before the next execution phase, the owner must approve:

- SCO organization creation or use;
- product owner and technical owner for every boundary;
- repository visibility and team access;
- Odoo version and environment ownership;
- customer-isolation model;
- secrets and environment policy;
- CI, security, release, and recovery minimums;
- migration, rollback, and decommissioning plans;
- whether any existing asset may be renamed, moved, split, archived, or retired.

See:

- [Verified inventory and evidence](./sco-verified-inventory.md)
- [GitHub governance and engineering standards](./sco-github-governance.md)
