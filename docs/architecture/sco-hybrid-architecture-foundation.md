# SCO Hybrid Architecture Foundation

## Status

This is a reviewable governance baseline for `alkaiiser/sco`. It does not change runtime behavior, deployment, permissions, repository visibility, branch protection, or external infrastructure.

## Verified boundary

As of 2026-11-10:

- The authenticated GitHub account is `alkaiiser`.
- `alkaiiser/sco` is public, unarchived, and uses `main` as its default branch.
- The repository describes itself as the SCO B2B Procurement Platform.
- The visible repository scope includes the API, partner web, operations web, shared packages, infrastructure examples, and CI/CD documentation.
- Production deployment is documented as disabled.
- No conclusion about Odoo 19, SCO Mobile, SCO Field, customer databases, servers, backups, or DNS is established by this repository alone.
- The proposed organization `sco-technologies` and proposed repository split are targets for assessment, not existing resources or approved migrations.

## Governance baseline

- All changes use focused branches and pull requests.
- Repository scope must be checked before adding code, moving projects, or creating a new repository.
- Secrets and customer data never enter source control or documentation.
- Production, hosting, databases, backups, DNS, Docker resources, and CI/CD settings remain outside this documentation-only change.
- Ownership must be explicit before a sensitive change is approved.
- A migration requires an evidence-backed inventory, an affected-project owner, tests, a rollback plan, and a separately approved change window.
- No repository transfer, rename, archive, deletion, visibility change, or organization creation is authorized by this document.

## Proposed future map

The following are proposed boundaries only:

- `sco-platform`: shared platform and operational tooling.
- `sco-odoo-core`: reusable Odoo extensions.
- `sco-odoo-sectors`: sector packages.
- `sco-field`: field product.
- `sco-mobile`: mobile product.
- `sco-connect`: integrations.
- `sco-customer-extensions`: isolated customer customizations.

Before creating or moving anything, compare these names with all accessible accounts, organizations, agent workspaces, and project owners. The current `sco` repository must not be treated as a duplicate-free substitute for that inventory.

## Follow-up work requiring separate approval

1. Complete read-only inventory of accessible GitHub accounts and organizations.
2. Identify the actual owners and locations of Mobile, Field, Odoo, hosting, servers, databases, backups, and domains.
3. Complete a secret and sensitive-data review of current and historical public content; rotate any confirmed exposed credential through its owner.
4. Review repository settings, branch protection, collaborators, Actions, and deployment targets without changing them.
5. Select one pilot migration only after the affected owner approves scope, tests, timing, and rollback.

## Rollback

This PR is documentation-only. Reverting the PR removes the governance baseline and leaves application behavior and external systems unchanged.
