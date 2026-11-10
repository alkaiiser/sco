# SCO Server Architecture Block

## Scope

This block defines the server architecture boundary for SCO as a target design and records the runtime facts that are verifiable from the existing legacy repository.

The former procurement system remains frozen legacy software. This document does not make it the SCO Platform and does not authorize production changes, server access, DNS changes, deployment, or credential handling.

## Classification

| Area | Status |
| --- | --- |
| Company identity | Owner-approved: SCO — Business Development & Systems Engineering |
| Shared SCO Platform server foundation | Target architecture; runtime not yet assigned |
| Legacy Procurement runtime | Code and deployment references verified in `alkaiiser/sco` |
| Production status | Repository documentation states production deployment is disabled |
| Staging status | Repository documents a staging edge contract; actual host state is not verified |
| Odoo, Field, Mobile, Connect, Digital Branch, Website & Store | Product boundaries approved; server runtimes not yet verified |
| Customer Extensions | Target isolation requirement; actual customer environments not verified |

## Current verified legacy runtime

The accessible repository documents this runtime shape:

- API: NestJS/Fastify application on an internal listener.
- Partner Web: Next.js application.
- Operations Web: Next.js application.
- Database: PostgreSQL with Prisma migrations and least-privilege runtime roles.
- Object storage: private S3-compatible storage for staging/production design.
- Edge: Nginx staging contract.
- Images: API, partner-web, and operations-web container images.
- Registry: GHCR references in release documentation and workflows.
- CI: GitHub Actions builds, tests, scans, recovery drills, and image checks.
- Deployment design: owner-laptop initiated SSH flow; GitHub Actions is not granted a production SSH key.
- Recovery: encrypted, signed backup artifacts and restore into clean infrastructure.

These are facts about the legacy repository's documented design, not verified facts about live infrastructure.

## Target server topology

```text
                            Public Internet
                                  |
                            DNS + TLS edge
                                  |
                         Nginx / reverse proxy
                  _________/       |        _________
                 /                 |                  \
        Website & Store       Digital Branch       Partner/Operations
                 |                 |                  |
                 +-----------------+------------------+
                                  |
                         Private API network
                  _________/       |        _________
                 /                 |                  \
          SCO Platform APIs     SCO Connect       Field/Mobile APIs
                 |                 |                  |
                 +-----------------+------------------+
                                  |
                         Private data network
                  _________/       |        _________
                 /                 |                  \
          PostgreSQL / Odoo   Object Storage      Queue/Workers
                 |                 |                  |
                 +----------- Encrypted Backups ----+
```

The target topology uses integration contracts between products. Products must not gain access to unrelated production databases merely because they share a host or network.

## Environment separation

| Environment | Purpose | Data | Deployment authority | Required boundary |
| --- | --- | --- | --- | --- |
| Development | Local engineering | Synthetic or development-only | Developer | No production credentials |
| Test/CI | Automated validation | Disposable isolated data | CI workflow | Destroy after run |
| Staging | Release and integration validation | Explicitly approved non-production data | Release owner with environment approval | Private management and data plane |
| Production | Customer service | Live customer data | Explicit production approver | Separate credentials, network, backups, and audit |

No environment may reuse credentials, storage buckets, database roles, or deployment identities from another environment.

## Network and edge contract

Target rules:

- Public DNS exposes only approved HTTPS entry points.
- TLS terminates at the approved edge.
- Nginx proxies only approved public routes.
- API, health, metrics, PostgreSQL, Docker, object storage, and management routes remain private.
- Application listeners bind to private or loopback interfaces, never directly to the public Internet.
- Security groups and host firewalls deny by default.
- Administrative access uses a dedicated identity and controlled private path.
- Host keys and certificates are pinned and rotated through an approved process.
- No dynamic trust based on unauthenticated host discovery.

The legacy repository currently documents staging hostnames `staging.sco.sa` and `operations.staging.sco.sa`, loopback application ports 3101–3103, and private health/metrics routes. Actual DNS, certificates, firewall state, and host listeners remain unverified.

## Runtime and data boundaries

### Platform services

The future SCO Platform should own:

- identity and service-to-service authentication contracts;
- reusable CI/CD workflows;
- observability and audit contracts;
- approved API and event conventions;
- image, artifact, and SBOM standards;
- backup and recovery standards.

It must not become a shared production database for unrelated products.

### Odoo

SCO Odoo should own ERP and business-operation data. Product clients and integrations must use authorized, versioned interfaces. Direct database access is prohibited for Field, Mobile, Website, Connect, and Digital Branch unless a specific security ADR approves a controlled read-only or migration use case.

### Customer Extensions

Each customer extension requires:

- separate repository or explicit package boundary;
- separate credentials and environment;
- separate database/storage scope;
- separate deployment approval;
- separate backup and restore ownership;
- auditability and offboarding procedure.

## Deployment and release boundary

The target release flow is:

1. Pull request checks pass.
2. CI builds and scans once.
3. Release artifacts are identified by commit SHA and immutable digest.
4. Registry permissions are limited to release workflows.
5. A protected environment approves deployment.
6. Migration runs with a dedicated migration identity.
7. Long-running services receive only runtime credentials.
8. Health and readiness checks run privately.
9. Traffic switches only after validation.
10. Rollback uses a previously verified immutable artifact and compatible migration strategy.

The legacy repository documents GHCR and owner-laptop deployment controls, while production deployment remains disabled. No live deployment was executed by this architecture work.

## Database and storage security

- PostgreSQL is private and is never exposed through public Nginx routes.
- Runtime roles are non-owner and least privilege.
- Migration identities are separate from runtime identities.
- Row-level security and tenant context enforce customer boundaries where applicable.
- Object storage buckets are private and environment-specific.
- Storage keys are not public URLs by default.
- Backup artifacts are encrypted, signed, integrity-checked, and restored only into clean targets.
- Backup credentials and keys remain outside Git and logs.
- Restore drills must reconcile database references with storage objects.

## Observability and operations

Every production service must provide:

- private liveness and readiness checks;
- structured logs with credential/token redaction;
- metrics behind a private monitoring path;
- request and correlation identifiers;
- audit events for identity, tenant, authorization, deployment, and data access;
- alerts for availability, error rate, saturation, backup failure, and restore failure;
- an owner and escalation path.

Operational endpoints must not be exposed through public business ingress.

## Server architecture evidence gaps

The following are still not verified and must be collected read-only:

- provider, region, host inventory, operating systems, and lifecycle;
- actual DNS records, certificates, and edge configuration;
- firewall/security-group rules and private network topology;
- running containers, images, volumes, and registry bindings;
- actual Odoo servers, versions, addons, databases, and integration accounts;
- PostgreSQL instances, replicas, roles, extensions, and storage;
- S3-compatible provider, buckets, policies, lifecycle, and encryption;
- CI runners, environment protections, deployment identities, and audit logs;
- backup destination, encryption-key ownership, retention, immutability, and restore evidence;
- monitoring, alerting, incident response, RPO/RTO, and maintenance windows;
- customer-to-environment mapping and isolation evidence.

## Block acceptance criteria

This server architecture block is ready for implementation planning when:

- every runtime has a named owner and environment;
- public and private network paths are evidenced;
- all databases and storage systems have data classifications;
- product integrations have contracts and identities;
- deployment and rollback paths are tested in staging;
- backup restore evidence meets approved RPO/RTO;
- customer isolation is verified;
- production remains protected by explicit approvals and environment gates.

## Safe next action

Collect the evidence gaps through read-only connectors, populate the runtime matrix, and produce one ADR for each approved server boundary. Do not provision, reconfigure, deploy, rotate, or migrate anything as part of inventory.
