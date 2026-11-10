# SCO Security and Access Architecture Block

## Scope

This block defines the security and access model for the SCO product portfolio and records the controls that can be required before any repository, server, or product boundary is created.

It is a design and evidence document. It does not grant access, rotate credentials, change GitHub settings, or alter production.

## Security principles

1. Default deny: access is granted only to a named identity, team, environment, and purpose.
2. Separate identities: human, CI, deployment, migration, runtime, backup, monitoring, and customer support identities are distinct.
3. Least privilege: permissions are scoped to the smallest repository, environment, data class, and operation.
4. Strong boundaries: customer, environment, product, and production data boundaries are explicit and auditable.
5. No secret material in Git: credentials, tokens, private keys, recovery keys, and customer data are never committed or logged.
6. Immutable evidence: releases, images, migrations, backups, and audit records are traceable to an approved commit or digest.
7. Recoverability: every sensitive system has an owner, backup policy, restore test, and incident path.
8. Separation of duties: code authors, reviewers, release approvers, and production operators are not one uncontrolled identity.

## Identity domains

| Identity domain | Purpose | Access boundary | Required controls |
| --- | --- | --- | --- |
| Organization owner | Organization policy and emergency administration | Organization only | Minimal membership, MFA, audited use |
| Repository team member | Code and issue work | Assigned repository/team | Team-based access, no shared accounts |
| Code owner | Review responsibility | Owned paths | CODEOWNERS and required review |
| CI identity | Build and test | Workflow permissions | Read-only by default, scoped write only for artifacts |
| Release identity | Publish approved artifacts | Registry and release environment | Protected environment, immutable tags/digests |
| Deployment identity | Promote approved artifacts | Specific environment and host path | Short-lived or rotated key, no repository admin |
| Migration identity | Schema changes | Database migration operation | Separate database role, audited execution |
| Runtime identity | Application requests | Specific service/data permissions | No ownership, no role creation, RLS where applicable |
| Backup identity | Backup and restore | Backup source/destination only | Separate keys, encryption, restore audit |
| Monitoring identity | Metrics and health | Private observability endpoints | Read-only and network restricted |
| Customer support identity | Approved support workflow | Assigned customer scope | Time-bound access and audit |

## GitHub access model

The proposed future organization should use teams rather than individual repository grants:

- Owners: organization administration and policy.
- Platform Engineering: shared standards and reusable infrastructure.
- Product teams: access only to their product repositories.
- Customer Delivery: assigned customer repositories only.
- Security Reviewers: security review and incident response.
- Release Managers: release and environment approvals.

Required GitHub controls:

- MFA for all members.
- SSO and verified domains if an organization is created and the plan supports them.
- Protected main branches.
- Pull requests for all changes.
- CODEOWNERS review for security, infrastructure, migrations, and deployment files.
- Required status checks.
- No force pushes or direct pushes to protected branches.
- Environment protection rules for staging and production.
- Separate bot identities and minimal workflow permissions.
- Audit-log review for membership, permission, secret, and environment changes.

The current account and repository permissions are verified only for the accessible personal account. No GitHub organization or organization-level team policy has been verified.

## Environment access

| Environment | Developer | CI | Release manager | Production operator | Customer support |
| --- | --- | --- | --- | --- | --- |
| Development | Own local environment | No live access | No | No | No |
| Test/CI | Disposable fixtures only | Scoped test access | No | No | No |
| Staging | Approved debugging path | Build/test and approved deployment | Approve promotion | Limited operational access | Time-bound approved access |
| Production | No default access | No direct shell or database access | Approve release | Narrow operational access | Time-bound customer-scoped access |

Production access must require a named person, reason, duration, approval, and audit trail. Emergency access expires automatically and is reviewed after use.

## Secret management

Secrets must be stored in an approved external secret manager or protected GitHub Environment, never in repository files.

Required separation:

- development secrets;
- CI/test secrets;
- staging secrets;
- production secrets;
- customer-specific secrets;
- Odoo integration secrets;
- payment and checkout secrets;
- mobile signing secrets;
- backup encryption and storage credentials;
- deployment credentials.

Rules:

- Secret names may appear in documentation; secret values may not.
- Logs, error reports, artifacts, Docker layers, and test fixtures must redact credentials.
- Credentials are rotated after suspected exposure, membership changes, or environment migration.
- Runtime services receive only their own secrets.
- Web applications never receive database, migration, or internal service credentials.
- Backup and recovery keys are held separately from application operators.
- Production secrets must not be available to pull-request workflows.

## Network and data access

- Public traffic enters only through approved TLS edge controls.
- Internal services use private network paths and authenticated service identities.
- PostgreSQL, object storage, health, metrics, admin, and Docker endpoints are private.
- Product APIs use versioned contracts and authorization checks.
- Direct cross-product database access is denied by default.
- Customer data is tagged by customer and environment.
- Tenant context is enforced in the service and database layers where applicable.
- Audit events record actor, customer scope, purpose, resource, result, and correlation identifier.
- Sensitive data is encrypted in transit and at rest according to the approved provider and key policy.

## Customer isolation

SCO Customer Extensions must be isolated across:

- source repository and team access;
- build artifacts and package dependencies;
- deployment environment and approval;
- database and storage;
- secrets and service identities;
- backups and restore scope;
- support and incident records;
- retention and offboarding.

A shared library may contain generic behavior only. Customer data, credentials, private business rules, and customer-specific deployment paths must not be placed in shared platform packages.

## Threat model

The first threat model must cover:

- compromised developer account;
- compromised CI workflow or dependency;
- leaked deployment credential;
- unauthorized customer cross-access;
- public exposure of PostgreSQL or object storage;
- mutable or substituted release image;
- malicious or unsafe Odoo integration;
- replayed webhook or integration event;
- backup theft or restore into the wrong target;
- insider misuse of support or production access;
- DNS, TLS, or reverse-proxy misconfiguration;
- mobile token theft and unauthorized API use.

For each threat, record preventive control, detection signal, response owner, recovery action, and residual risk.

## Required security evidence

Before a product or server boundary is accepted, collect:

- owner and team mapping;
- access review and MFA evidence;
- branch protection and CODEOWNERS evidence;
- environment and secret separation;
- network exposure and firewall evidence;
- database role and privilege review;
- storage policy and encryption evidence;
- dependency, secret, filesystem, and image scans;
- audit and alert coverage;
- backup and restore evidence;
- incident and offboarding procedure.

## Acceptance criteria

This block is ready for implementation planning when:

- each identity has a named owner and purpose;
- every environment has separate credentials and approval controls;
- customer access is demonstrably isolated;
- no public route reaches private data or management services;
- CI cannot access production secrets by default;
- release artifacts are immutable and traceable;
- security and recovery checks are mandatory gates;
- access reviews and incident response have owners and schedules.

## Immediate safe actions

- Maintain a role and access matrix for the future SCO organization.
- Add security, ownership, and environment requirements to repository templates.
- Collect read-only evidence from actual GitHub organization, hosting, Odoo, identity, and backup systems.
- Convert each approved exception into a dated ADR with an expiry or review condition.
