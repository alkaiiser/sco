# SCO Phase 1 Inventory Register

## Purpose

This register is the working record for the first architecture phase: identify real assets, owners, runtimes, data boundaries, integrations, and recovery responsibilities before creating or splitting repositories.

It is read-only inventory work. It does not authorize repository creation, migration, deployment, credential changes, or production access.

## Status vocabulary

- **Verified**: observed from accessible GitHub metadata or repository content.
- **Owner-approved**: explicitly approved by the company owner.
- **Pending evidence**: a named question requiring read-only evidence.
- **Blocked**: evidence requires a connector or access path not currently available.

## Company and architecture decisions

| Item | Status | Record |
| --- | --- | --- |
| Company identity | Owner-approved | SCO — Business Development & Systems Engineering |
| Future platform boundary | Owner-approved | SCO Platform is the shared technical foundation; it is not assumed to be the current procurement repository |
| Legacy classification | Owner-approved | Former B2B Procurement Platform is frozen for one year and retained separately |
| Current procurement repository | Verified | `alkaiiser/sco` is the existing public repository and is classified as SCO Legacy Procurement |
| Future product portfolio | Owner-approved logical boundaries | Odoo, Odoo Sectors, Field — By Odoo, Mobile, Connect, Digital Branch, Website & Store, and Customer Extensions |
| Repository names | Pending evidence | Logical boundaries are not automatic repository names |

## GitHub inventory

| Asset | Evidence | Owner/access | Visibility | Runtime/release facts | Next evidence |
| --- | --- | --- | --- | --- | --- |
| `alkaiiser/sco` | GitHub repository metadata and main branch | `alkaiiser`; Admin access verified | Public | pnpm workspace; API, two web apps, shared packages; CI, Docker, PostgreSQL recovery | Confirm legacy support owner and freeze policy |
| `alkaiiser/steelchfs` | GitHub repository metadata | `alkaiiser`; Admin access verified | Public | Not inspected further; explicitly out of SCO architecture scope | None unless owner reopens scope |
| `alkaiiser/NewThem` | GitHub repository metadata | `alkaiiser`; Admin access verified | Private | Not inspected further; explicitly out of SCO architecture scope | None unless owner reopens scope |
| `alkaiiser/newTheeme` | GitHub repository metadata | `alkaiiser`; Admin access verified | Public | Not inspected further; explicitly out of SCO architecture scope | None unless owner reopens scope |
| SCO GitHub organization | Account organization query | No organization membership returned | Not applicable | No organization-level teams or policies verified | Owner decision whether/when to create or use an organization |

## Legacy Procurement repository facts

The accessible main branch verifies:

- `apps/api` is a NestJS/Fastify API using Prisma and PostgreSQL.
- `apps/partner-web` and `apps/operations-web` are Next.js applications.
- `packages/config` and `packages/contracts` are workspace packages.
- CI runs static/build checks, migration checks, tests, Gitleaks, Trivy, security gates, recovery drills, and three container builds.
- The repository contains procurement-oriented modules, migrations, tests, and partner/operations flows.
- The repository has Docker build definitions and a pnpm lockfile.
- No Odoo, Mobile, or Field product repository was verified in the accessible GitHub owner listing.

These facts describe the legacy asset. They do not establish the future SCO Platform or any future product boundary.

## Product asset register

| Logical product | Source repository | Runtime | Data | Integrations | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| SCO Platform | Not yet assigned | Not verified | Not verified | Identity, CI/CD, security, contracts | Not assigned | Pending evidence |
| SCO Odoo | Not verified | Not verified | ERP/business data | Odoo environments, identity, integrations | Not assigned | Blocked on external inventory |
| SCO Odoo Sectors | Not verified | Not verified | Sector business data | SCO Odoo | Not assigned | Blocked on Odoo inventory |
| SCO Field — By Odoo | Not verified | Not verified | Field operations/customer data | Authorized Odoo APIs | Not assigned | Blocked on product inventory |
| SCO Mobile | Not verified | iOS/Android code not found in accessible inventory | Not verified | Versioned APIs, identity, Odoo | Not assigned | Blocked on product inventory |
| SCO Connect | Not verified | Not verified | Interaction and communication data | Identity, messaging/meeting providers | Not assigned | Blocked on external inventory |
| SCO Digital Branch | Not verified | Not verified | Customer interaction data | Connect, Odoo, identity | Not assigned | Blocked on product inventory |
| SCO Website & Store | Not verified | Not verified | Public, CRM, commerce data | CRM, payment, Odoo, Connect | Not assigned | Blocked on product inventory |
| SCO Customer Extensions | Not verified | Per-customer runtime not verified | Customer-isolated data | Approved public contracts | Not assigned | Blocked on customer inventory |
| SCO Legacy Procurement | `alkaiiser/sco` | Verified: Node/Nest/Fastify, PostgreSQL, Docker | Verified: tenant and procurement data | Existing repository contracts | Legacy owner not assigned | Frozen and preserved |

## External read-only evidence queue

The following evidence must be collected through the appropriate connected systems without changing state:

1. Odoo installations, versions, addons, databases, environments, owners, and integration credentials by reference only.
2. Field source repositories, build pipelines, package registries, deployment targets, and API dependencies.
3. Mobile source repositories, bundle identifiers, signing ownership, stores, release channels, and backend endpoints.
4. Connect and Digital Branch codebases, providers, event flows, identity model, and data retention.
5. Website & Store source, hosting, checkout provider, CRM, analytics, and deployment path.
6. Customer extension repositories, customer identifiers, access teams, data stores, environments, and offboarding rules.
7. Servers, containers, registries, DNS, reverse proxies, CI runners, and environment ownership.
8. Backup schedules, storage locations, encryption ownership, retention, restore tests, and incident runbooks.

## Integration boundary worksheet

For each verified integration, record:

| Field | Required value |
| --- | --- |
| Producer and consumer | Named product/repository |
| Interface | Versioned API, event, package, or adapter |
| Authentication | Identity provider, credential class, rotation owner |
| Data classification | Public, internal, confidential, customer-isolated, regulated |
| Tenant boundary | Tenant/customer scope and enforcement point |
| Failure behavior | Timeout, retry, idempotency, dead-letter or compensation |
| Observability | Logs, metrics, traces, audit events |
| Release compatibility | Supported versions and deprecation window |
| Recovery | Backup owner, restore procedure, RPO/RTO evidence |

## Phase 1 exit criteria

Phase 1 is complete when:

- every logical product has an evidence status and named owner;
- every existing codebase has a repository or storage reference;
- every integration has a producer, consumer, contract, identity, and data class;
- every production runtime has an environment owner and recovery path;
- customer-specific boundaries are verified;
- unknowns are converted into explicit issues or owner decisions;
- no repository restructuring is proposed solely from a name or assumption.

## Immediate work items

- Obtain read-only access to the external systems named in the evidence queue.
- Populate the product asset register from evidence.
- Create one ADR per approved repository boundary.
- Select the first product boundary only after its owner, runtime, contracts, and recovery evidence are known.
