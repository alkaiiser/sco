# AGENTS.md

## Scope

This repository is the SCO B2B Procurement Platform repository. It currently contains the platform API, partner web application, operations web application, shared packages, infrastructure examples, and related documentation.

This file governs work in this repository only. It is not an inventory or authority for SCO Mobile, SCO Field, Odoo, customer databases, servers, or other repositories.

## Safety boundaries

- Do not change production, servers, databases, backups, DNS, hosting, Docker resources, or deployment targets from this repository without an approved change request and an explicit owner.
- Do not commit secrets, credentials, private keys, access tokens, customer data, database dumps, or real environment files. Use redacted examples only.
- Treat `.env.example` as a development template; never add real values to it.
- Do not rename, transfer, archive, delete, or split this repository without a separate owner-approved decision.
- Do not infer that documentation, Compose files, systemd examples, or workflow files prove that a corresponding production resource exists.
- Preserve current agent and project workflows. Prefer additive, reviewable, reversible changes.

## Change process

1. Confirm the change belongs to this repository and does not duplicate another SCO project.
2. Create a focused branch from `main`.
3. Open a pull request with scope, evidence, tests, risk, and rollback notes.
4. Obtain review from the repository owner or an explicitly delegated owner.
5. Run the relevant checks before merge.
6. Never merge or deploy a sensitive change without the required owner approval.

## Required PR evidence

Every PR should state:

- What is changing and why.
- What is explicitly not changing.
- Tests or checks run, or why none apply.
- Security and data-impact assessment.
- Rollback or revert procedure.
- Any dependency on SCO Mobile, SCO Field, Odoo, infrastructure, hosting, or external services.

## Architecture boundary

The proposed SCO Hybrid Architecture is a coordination target, not proof of the current repository map. Any future extraction into platform, Odoo, sector, field, mobile, integration, or customer-extension repositories requires an evidence-backed ownership review and a separate approved migration plan.
