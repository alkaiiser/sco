# SCO CI Repair Design

## Intent

Restore the repository's existing CI contract without changing production behavior, deployment targets, live credentials, or PR #2. The repair must make the security, recovery, typecheck, container-build, dependency, and full-test gates pass on a separate reviewable PR.

## Goals

- Keep secret scanning enabled and document the verified historical test fixture without exposing its value.
- Make isolated PostgreSQL backup restore recreate every least-privilege owner role required by the dump, including `sco_partner_admission_gateway_owner`.
- Resolve the reported TypeScript errors with type-safe test code.
- Make both web Docker builds include the workspace contracts package.
- Upgrade vulnerable direct/transitive dependencies to patched compatible versions and rescan the API image.
- Verify the complete CI workflow and preserve security policies.

## Non-goals and constraints

- No production servers, databases, DNS, deployments, live credentials, or history rewriting.
- No disabling or weakening of Gitleaks, Trivy, migrations, recovery, or test gates.
- PR #2 remains unchanged and Draft.
- The repair branch is `ci/repair-all-failures-2026-11-10` and will be proposed as a separate PR.

## Approach

The repair uses the smallest repository-local changes: narrow Gitleaks configuration for a proven non-secret historical fixture; a single shared restore-role declaration used by restore preparation; precise TypeScript predicates and payload types; complete workspace package copying in web images; and lockfile dependency updates constrained by existing package APIs. Each change is verified locally where tooling exists and then by the authoritative GitHub Actions run.

## Security decision

The Gitleaks finding is in a removed historical test file, in an `idempotencyKey` request fixture, with no environment/credential source or external service use. It is not a credential. The value remains redacted in all reports. A fingerprint/path/commit-scoped allowlist is preferable to deleting history or weakening the scanner globally. Any future evidence that it is real requires owner-led rotation, which is outside this change.

## Acceptance

All required jobs in the repair PR's CI run complete successfully, including recovery restore, TypeScript, web/API image builds, Gitleaks, Trivy, migrations, and the full test suites.
