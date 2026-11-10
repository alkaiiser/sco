# SCO GitHub Governance and Engineering Standards

## Scope

These standards are recommendations for the future SCO engineering portfolio. They do not create a GitHub organization, change repository access, or alter production. They apply only after the owner approves the organization and repository boundaries.

## Proposed organization structure

Recommended organization: `sco-technologies`, subject to availability and owner approval.

| Team | Scope | Default access |
| --- | --- | --- |
| SCO Owners | Company-wide architecture, repository administration, security exceptions, production approvals | Organization owner or tightly limited admin |
| Platform Engineering | Shared libraries, CI/CD, identity, observability, integration contracts | Maintain on platform repositories; read on products |
| Odoo Engineering | SCO Odoo core and approved open-source extensions | Maintain on Odoo repositories |
| Sector Product Teams | Sector packages and sector-specific tests | Write or maintain only for assigned sectors |
| Field Engineering | SCO Field — By Odoo | Maintain on Field repositories; read contract dependencies |
| Mobile Engineering | SCO Mobile, mobile CI, release signing workflows | Maintain on Mobile repositories; no broad production secrets |
| Connect Engineering | SCO Connect and interaction infrastructure | Maintain on Connect repositories |
| Digital Branch | SCO Digital Branch | Maintain on Digital Branch repositories |
| Website & Commerce | Website, catalog, checkout, CRM integration | Maintain on Website & Store repositories |
| Customer Delivery | Approved customer extensions | Access only to assigned customer repositories |
| Security Reviewers | Security review and incident response | Read by default; write only for security controls |
| Release Managers | Release approvals and environment promotion | Deployment approval without broad source administration |

Use team-based access instead of individual grants. Customer teams must never inherit access to another customer's repository or environment.

## Naming conventions

Use lowercase kebab-case repository names with a stable product prefix:

- `sco-platform` for shared standards and reusable platform components;
- `sco-odoo` and `sco-odoo-sectors` for the ERP ecosystem;
- `sco-field`, `sco-mobile`, `sco-connect`, and `sco-digital-branch` for independent products;
- `sco-website-store` for public acquisition and commerce;
- `sco-customer-<customer-key>` for isolated customer work;
- `sco-legacy-procurement` only if an owner later approves a rename; the current `alkaiiser/sco` name and history must remain untouched for now.

Names are proposals, not authorization.

## Ownership and repository controls

Every active repository should have:

- CODEOWNERS covering application, infrastructure, security, migrations, and deployment files;
- a README defining scope, runtime, data class, owners, support channel, and local verification;
- an AGENTS.md or equivalent contribution boundary;
- an OWNERS.md with business and technical owners;
- a threat model and data-flow diagram;
- an ADR directory for decisions and reversals;
- a release and recovery runbook;
- issue templates for bug, security, architecture, and operational incidents.

Recommended branch controls:

- protect main;
- require pull requests and at least one code-owner review;
- require all security, test, build, and migration checks;
- require linear history or an approved merge strategy;
- disable force pushes and branch deletion on protected branches;
- require signed commits if the team's signing workflow supports it;
- use separate environments and approvals for staging and production.

## CI/CD baseline

Every repository should use a reusable, pinned workflow baseline:

1. immutable dependency installation and lockfile verification;
2. formatting, linting, and type checks;
3. unit, integration, contract, and end-to-end tests as applicable;
4. migration validation and backward-compatibility checks;
5. secret scanning with Gitleaks;
6. dependency and filesystem/image scanning with Trivy or an approved equivalent;
7. SBOM generation and artifact provenance;
8. container non-root verification and image scanning;
9. signed, immutable release artifacts;
10. deployment approval gates and rollback verification.

No workflow may bypass a security gate, print secrets, deploy from an unreviewed branch, or use mutable production image tags as the release identity.

## Versioning and compatibility

- Use SemVer for shared libraries and externally consumed contracts.
- Pin production lockfiles and review dependency updates through pull requests.
- Maintain compatibility matrices for Odoo versions, mobile API versions, Field clients, Connect adapters, and Digital Branch consumers.
- Version APIs and events explicitly; deprecate before removal.
- Keep database migrations forward-only in deployed environments and test rollback or restore procedures separately.
- Publish release notes with security, compatibility, migration, and rollback information.
- Never place customer-specific dependencies in a shared library without an explicit isolation review.

## Secrets and production boundaries

- Store secrets only in approved GitHub Environments or an external secret manager.
- Separate development, test, staging, and production credentials and databases.
- Use short-lived credentials where supported and rotate after exposure or personnel changes.
- Keep deployment identities separate from repository administration.
- Require environment protection reviewers for production.
- Restrict production access by team, environment, network, and audit trail.
- Do not copy customer secrets into issue comments, logs, fixtures, images, or repository files.
- Customer repositories and environments must have separate secrets, database roles, storage, backups, and incident scope.

## Customer isolation

Each customer extension must define:

- customer identifier and owning team;
- repository or package boundary;
- source, artifact, and deployment access;
- database and storage isolation;
- separate credentials and rotation schedule;
- audit and support ownership;
- backup and restore scope;
- offboarding and data-retention policy.

Shared platform contracts may be reused. Customer data, credentials, and deployment permissions may not be shared by default.

## Documentation and decisions

Use ADRs for:

- monorepo or multirepo selection;
- Odoo authority and integration contracts;
- identity and tenancy;
- event and API compatibility;
- customer isolation;
- deployment and rollback;
- backup and recovery;
- security exceptions.

Each ADR should state context, decision, alternatives, consequences, owner, date, and review trigger. Superseded ADRs remain in history.

## Repository responsibility matrix

| Boundary | Primary responsibility | Shared dependencies | Required release owner |
| --- | --- | --- | --- |
| SCO Platform | Standards, identity, CI/CD, security, contracts | None or approved platform libraries | Platform Engineering |
| SCO Odoo | ERP and business operations | Platform identity and contracts | Odoo Engineering |
| SCO Odoo Sectors | Sector modules and compatibility | SCO Odoo | Sector Product Team |
| SCO Field | Field sales and distribution | Odoo APIs, platform identity | Field Engineering |
| SCO Mobile | Mobile clients and release channels | Versioned APIs, identity | Mobile Engineering |
| SCO Connect | Communication and interaction services | Identity, events, observability | Connect Engineering |
| SCO Digital Branch | Digital branch product | Connect, Odoo APIs, platform contracts | Digital Branch |
| SCO Website & Store | Public web, catalog, checkout, CRM | Connect, Odoo APIs, payment provider | Website & Commerce |
| SCO Customer Extensions | Isolated customer delivery | Approved public contracts only | Customer Delivery |
| SCO Legacy Procurement | Frozen historical procurement system | Its existing runtime only | Explicit legacy owner |

## Exit criteria for architecture phase

The proposal is ready for implementation planning only when:

- all product owners are named;
- the Phase 1 inventory is evidenced;
- the target GitHub organization and team model are approved;
- repository boundaries have written ADRs;
- security, CI/CD, release, and recovery baselines are accepted;
- customer isolation and production access are approved;
- the migration and rollback plan is rehearsed for the first boundary.

