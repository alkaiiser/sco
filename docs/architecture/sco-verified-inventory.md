# SCO Verified Inventory and Evidence

## Evidence rules

This inventory separates three categories:

- **Verified**: directly observed through accessible GitHub metadata, repository files, or code search.
- **Owner-provided**: supplied as a current business decision in the architecture brief.
- **Unknown**: not verified from the available read-only access. Unknown does not mean absent.

## GitHub account and repositories

| Item | Status | Evidence and implication |
| --- | --- | --- |
| Authenticated owner | Verified | GitHub account is `alkaiiser`. |
| GitHub organization | Verified | No organization membership was returned by the accessible GitHub account query. |
| Primary repository | Verified | `alkaiiser/sco` is public, owned by `alkaiiser`, default branch `main`, and the account has Admin permission. |
| steelchfs | Verified | `alkaiiser/steelchfs` is public and owned by the account. It is out of scope for this SCO architecture work. |
| NewThem | Verified | `alkaiiser/NewThem` is private and owned by the account. It is out of scope for this SCO architecture work. |
| newTheeme | Verified | `alkaiiser/newTheeme` is public and owned by the account. It is out of scope for this SCO architecture work. |
| Additional SCO repositories | Unknown | No additional repositories were returned in the accessible owner listing. This is not proof that no local, unconnected, or inaccessible codebases exist. |

## Current sco repository

### Verified code and delivery shape

The main branch contains a pnpm workspace with:

| Path | Verified responsibility |
| --- | --- |
| `apps/api` | NestJS/Fastify API, Prisma, PostgreSQL integrations, authentication, tenant and authorization modules |
| `apps/partner-web` | Next.js partner web application |
| `apps/operations-web` | Next.js operations web application |
| `packages/config` | Shared configuration package |
| `packages/contracts` | Shared contracts package |
| `infrastructure/` | Development and infrastructure configuration |
| `.github/workflows/ci.yml` | Pull-request and main-branch CI |

The repository also contains Dockerfiles for the API and the two web applications.

### Verified CI and security controls

The CI workflow on main:

- runs on pull requests and pushes to main;
- pins Node 20 and pnpm 10.15.1;
- runs migration integrity checks, sensitive-file checks, Prisma validation, TypeScript checks, tests, and builds;
- runs actionlint, Gitleaks, and Trivy filesystem scanning;
- runs clean-PostgreSQL security tests and a full PostgreSQL suite;
- runs an encrypted backup and isolated recovery drill;
- builds and scans API, partner-web, and operations-web images;
- uses read-only repository permissions for security and recovery jobs where configured.

PR #3 repaired these gates and was merged after CI run 37 passed. The legacy repository remains the subject of preservation and maintenance, not the new SCO platform foundation.

### Verified product signals

- Procurement functionality is present in API modules, database migrations, tests, and partner/operations applications.
- The README describes the repository as SCO Platform and references the sco.sa scope; this is a repository label, not proof of the company's current product architecture.
- Search evidence showed historical Odoo and meeting-system references in documentation, but no independently verified Odoo product repository or Mobile/Field product code in the accessible GitHub inventory.
- No customer-extension repository or customer-specific deployment boundary was verified.

## Owner-approved business classification

The owner has approved that the former procurement platform has been frozen for one year. This classification supersedes older repository wording for architecture planning:

- it is legacy procurement;
- it is not SCO Platform;
- it is not the foundation for future products;
- its history and code must be preserved;
- it must remain separately identified until an owner approves another action.

## Not verified

The following require read-only access outside the current GitHub repository inventory:

- Odoo Community version, addons, databases, environments, and owners;
- Field product source and deployment targets;
- iOS/Android source, signing, stores, and release process;
- Connect, Digital Branch, Website & Store codebases and hosting;
- customer-specific code, tenancy boundaries, and contracts;
- production and staging servers, DNS, reverse proxies, registries, and deployment agents;
- backup locations, retention, encryption keys, restore ownership, and recovery evidence;
- external identity providers, CRM, payment, meeting, messaging, and observability systems.

## Inventory next actions

1. Collect read-only repository and codebase evidence from the owner or connected systems.
2. Build a product-to-runtime matrix with owner, data class, integration, release cadence, and recovery path.
3. Validate Odoo as an authorized integration boundary before designing Field, Mobile, or Digital Branch APIs.
4. Record every unknown as an issue or decision, not as a repository creation request.
