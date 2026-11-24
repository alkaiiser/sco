# SCO CI/CD and Release Architecture Block

## Scope

This block defines how SCO products are tested, secured, built, released, deployed, and rolled back. It is a target standard and does not enable deployment or change existing workflows.

The frozen legacy procurement repository keeps its current CI and release protections. Future products adopt this standard only after their repository and owner are approved.

## Delivery lifecycle

```text
Change
  |
Pull Request
  |-- ownership review
  |-- tests and type checks
  |-- contract and migration checks
  |-- secret/dependency/configuration scans
  |-- build and image scan
  |
Approved merge
  |
Release candidate
  |-- SBOM and provenance
  |-- immutable artifact digest
  |-- compatibility checks
  |
Protected environment approval
  |
Staging deployment
  |-- migration and health checks
  |-- smoke/contract/e2e tests
  |-- observability verification
  |
Production approval
  |
Production deployment
  |-- immutable digest
  |-- controlled migration
  |-- readiness and traffic validation
  |-- rollback decision window
```

## Repository pipeline baseline

Every active product repository must provide:

1. Lockfile and immutable dependency installation.
2. Formatting, linting, and static analysis.
3. Type checks and API/schema validation.
4. Unit tests.
5. Integration tests against disposable dependencies.
6. Contract tests for all producers and consumers.
7. Migration validation and backward-compatibility tests.
8. End-to-end tests where user flows require them.
9. Secret scanning with Gitleaks.
10. Dependency, filesystem, configuration, and image scanning.
11. SBOM and artifact provenance.
12. Non-root container verification where containers are used.
13. Backup/recovery tests for stateful services.
14. Generated-file and reproducibility checks.
15. Release notes and rollback evidence.

No required security or test gate may be skipped by branch, actor, or environment.

## Pull request controls

Every change must:

- target a protected branch through a pull request;
- identify the owning product and affected contracts;
- include tests or explain why none apply;
- include migration and rollback notes for schema changes;
- include security and data-impact notes;
- receive the required CODEOWNERS review;
- pass all required status checks;
- avoid secrets, customer data, mutable release tags, and unreviewed generated artifacts.

Emergency changes follow a separate documented procedure with post-incident review.

## Workflow permissions

Default workflow permissions are read-only.

Grant write permissions only to the smallest step that needs them:

- package or container publishing;
- release metadata;
- signed artifact upload;
- deployment promotion.

Pull request workflows must not access production secrets or production environments. Deployment workflows must use protected environments and separate identities.

Pin third-party actions to immutable commit SHAs. Review action updates as dependencies.

## Build reproducibility

Builds must record:

- source commit SHA;
- dependency lockfile hash;
- runtime and toolchain versions;
- build parameters;
- artifact digest;
- SBOM;
- provenance/attestation;
- test and scan results;
- owner and release timestamp.

Build the release artifact once and promote the same digest across environments. Do not rebuild different binaries for staging and production.

## Versioning

### Libraries and contracts

- Use SemVer for shared packages and public contracts.
- Publish changelogs and migration notes.
- Use major versions for breaking API/event changes.
- Keep compatibility adapters during deprecation windows.
- Record supported runtime, Odoo, mobile, Field, and client versions.

### Applications

Applications may use coordinated release versions, but every deployment remains traceable to a commit and immutable artifact digest.

### Database

- Migrations are forward-only in deployed environments.
- Expand/contract migrations are required for incompatible schema changes.
- Runtime code must remain compatible during migration rollout.
- Migration identity is separate from runtime identity.
- Backups and restore tests precede risky schema changes.

## Artifact and registry policy

- Registry packages are private by default.
- Publish only from approved release workflows.
- Use commit SHA and digest as release identity.
- Never overwrite an existing release artifact.
- Do not use `latest` in production.
- Sign images and packages where the registry supports it.
- Retain SBOM and provenance with the release record.
- Scan before publish and again before promotion.
- Restrict pull access to approved deployment identities.

## Environment promotion

| Stage | Entry criteria | Promotion evidence |
| --- | --- | --- |
| Pull Request | Checks, review, scans, contract impact | Required status checks |
| Candidate | Merged protected branch | Immutable artifact and SBOM |
| Staging | Environment approval | Deployment log, migrations, health, smoke tests |
| Production | Explicit production approval | Artifact digest, change record, rollback plan |
| Post-release | Observability stable | Error, latency, security, and business checks |

A failed staging check blocks production promotion.

## Deployment rules

- Deploy by immutable digest.
- Keep deployment identity separate from CI build identity.
- Use a dedicated migration step and identity.
- Validate environment markers before writing secrets or configuration.
- Do not pass credentials as command arguments.
- Do not print environment files or tokens.
- Verify host keys and transport endpoints.
- Keep private management paths private.
- Run readiness and smoke tests from the correct private network.
- Record who approved, what digest was deployed, and what database migration ran.

The current legacy repository documents owner-laptop initiated staging deployment and disabled production deployment. This architecture does not enable or change that behavior.

## Rollback

Every release must define:

- artifact to restore;
- application rollback procedure;
- database compatibility state;
- migration rollback or forward-fix strategy;
- storage/object compatibility;
- session and token handling;
- customer communication;
- decision owner and time window.

Do not roll back application code across an incompatible schema migration. Prefer expand/contract migrations and forward fixes.

## Security gates

The minimum release gate includes:

- Gitleaks history and current-content scan;
- dependency vulnerability scan;
- filesystem and configuration scan;
- container vulnerability and misconfiguration scan;
- actionlint and workflow permission review;
- dependency lockfile verification;
- SBOM/provenance validation;
- non-root and runtime hardening checks;
- recovery evidence for stateful services.

Security exceptions require a documented owner, reason, compensating control, expiry date, and review.

## Product-specific CI expectations

| Product | Required additional checks |
| --- | --- |
| SCO Platform | Contract compatibility, identity/security tests, reusable workflow validation |
| SCO Odoo | Odoo version matrix, addon install/upgrade, migration and access-rule tests |
| SCO Odoo Sectors | Sector matrix against supported Odoo versions and core |
| SCO Field | API contract, offline sync, tenant scope, distribution workflow tests |
| SCO Mobile | iOS/Android builds, signing separation, device/session security, API compatibility |
| SCO Connect | Provider adapter tests, webhook verification, message/meeting privacy |
| SCO Digital Branch | Journey tests, identity/consent, Connect and Odoo contract tests |
| SCO Website & Store | checkout/webhook idempotency, payment sandbox, CRM and catalog contracts |
| SCO Customer Extensions | customer-isolation tests, separate artifact/secrets, customer-specific rollback |
| SCO Legacy Procurement | Preserve existing CI, security gates, recovery drill, and frozen-project boundary |

## Release observability

Before promotion, verify:

- logs are structured and redacted;
- metrics and traces identify release SHA/digest;
- health checks are private and functional;
- alerts are routed to an owner;
- dashboards distinguish products and environments;
- audit records include deployment identity and approval;
- rollback signals and thresholds are defined.

## Acceptance criteria

This block is ready for implementation when:

- a reusable workflow baseline is approved;
- each repository has required owners and protected branches;
- environment and registry permissions are defined;
- artifact identity and provenance are mandatory;
- staging promotion is tested;
- production approval and rollback are documented;
- product-specific test matrices are owned;
- security exceptions have expiry and audit rules.
