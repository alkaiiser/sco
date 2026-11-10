# SCO CI Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair every currently failing CI gate on a separate branch while preserving security boundaries and production behavior.

**Architecture:** Keep the existing CI workflow and least-privilege database model. Fix each root cause at its owning boundary: scanner configuration for a verified fixture, restore role provisioning for dump ownership, test types at their call sites, Docker workspace context in image stages, and dependency versions in the package graph.

**Tech Stack:** TypeScript, Vitest, PostgreSQL/Prisma, pnpm 10, Docker BuildKit, GitHub Actions, Gitleaks, Trivy.

**Spec:** `docs/superpowers/specs/2026-11-10-ci-repair-design.md`

## Global Constraints

- PR #2 stays unchanged and Draft.
- No production systems, live credentials, DNS, deployments, or destructive history rewriting.
- Security gates remain enabled and fail closed.
- Runtime roles remain non-superuser, non-CREATEDB, non-CREATEROLE, NOINHERIT, and NOBYPASSRLS.
- Dependency upgrades must retain frozen-lockfile reproducibility.

## Review Focus

- Historical fixture allowlist must be exact and non-global — test Gitleaks on both repository history and current files.
- Restore role ownership must be present before `pg_restore` and retain least privilege — test recovery drill and role attributes.
- Type predicates must narrow the actual UUID template-literal type — run API typecheck and the affected tests.
- Docker build context must include workspace contracts in dependency and build stages — build both web images.
- Dependency upgrades must not alter runtime behavior or weaken scanners — run tests, builds, and Trivy.

---

### Task 1: Baseline and security finding

**Files:**
- Create: `.gitleaks.toml`
- Create: `docs/superpowers/specs/2026-11-10-ci-repair-design.md`
- Create: `docs/superpowers/plans/2026-11-10-ci-repair-plan.md`

- [ ] Record the exact historical commit/path/fingerprint without printing the matched value.
- [ ] Add only a commit/path/fixture-scoped allowlist with a rationale.
- [ ] Run the repository Gitleaks script and confirm no current or historical unapproved findings.

### Task 2: Restore owner roles

**Files:**
- Modify: `apps/api/scripts/provision-runtime-role.mjs`
- Test: `apps/api/test/recovery/` and `scripts/recovery/run-local-drill.sh`

- [ ] Add a failing restore-preparation assertion for all dump owner roles.
- [ ] Provision `sco_partner_admission_gateway_owner` in `prepare-restore` with the same least-privilege flags as its migration.
- [ ] Run the recovery unit suite and isolated drill; verify restore and post-restore provisioning.

### Task 3: Type-safe H6 tests

**Files:**
- Modify: `apps/api/test/database/h6-internal-partnership-read-model.integration.test.ts`
- Modify: `apps/api/test/integration/h6-wave2-http.integration.test.ts`

- [ ] Add/adjust focused type-level regression coverage first.
- [ ] Replace invalid predicates with a UUID-compatible predicate/type and type the HTTP payload as the Fastify injection payload.
- [ ] Run API typecheck and affected integration tests.

### Task 4: Workspace-aware web images

**Files:**
- Modify: `apps/partner-web/Dockerfile`
- Modify: `apps/operations-web/Dockerfile`

- [ ] Add the contracts package manifest to dependency stages and the contracts source to build stages.
- [ ] Build both production images and verify standalone output starts as the non-root user.

### Task 5: Dependency remediation

**Files:**
- Modify: `package.json` and/or workspace manifests
- Modify: `pnpm-lock.yaml`

- [ ] Add a failing dependency/security verification for patched Fastify, Tinypool, Vite, and source-map-js versions.
- [ ] Update the minimal dependency graph to patched compatible releases.
- [ ] Run install with frozen lockfile, tests, builds, and Trivy image scan.

### Task 6: Full verification and PR

- [ ] Run all workflow-equivalent checks locally where available.
- [ ] Commit focused changes, push the repair branch, and open a separate PR without merging.
- [ ] Read the repair PR's GitHub Actions results and fix any regressions until all checks pass or an external owner-level blocker is proven.
