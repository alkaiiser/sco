# SCO Operational Continuity and Recovery Architecture Block

## Scope

This block defines the operational model required to keep SCO products available, recoverable, supportable, and auditable.

It is a target standard. It does not access production, alter backups, change monitoring, or perform a recovery operation.

## Service ownership

Every service must have:

- business owner;
- technical owner;
- on-call or escalation owner;
- repository and artifact reference;
- environment list;
- data classification;
- dependency list;
- SLO and alert policy;
- backup and recovery owner;
- incident runbook;
- lifecycle and decommission date.

No service is production-ready without an accountable owner.

## Reliability targets

Each product and environment must define:

| Target | Meaning |
| --- | --- |
| Availability SLO | Allowed service unavailability over a stated period |
| RPO | Maximum acceptable data loss measured in time |
| RTO | Maximum acceptable recovery time |
| Recovery scope | Service, database, storage, queue, identity, and customer boundary |
| Degraded mode | Safe behavior when dependencies fail |
| Alert threshold | Signal that triggers operator action |
| Escalation | Person/team and response window |

Targets must be approved per product and customer contract. No universal value is assumed.

## Backup architecture

Backups must be:

- encrypted before leaving the source environment;
- signed or integrity-verifiable;
- stored outside the primary failure domain;
- isolated by environment and customer scope;
- protected against accidental deletion;
- retained according to legal and business requirements;
- monitored for success, freshness, size, and integrity;
- tested through restoration, not merely reported as successful.

Required backup classes:

1. PostgreSQL logical or physical backup as appropriate.
2. Object-storage metadata and objects.
3. Configuration without secret values.
4. Release manifests and artifact digests.
5. Audit and operational records where required.
6. Odoo database and filestore when Odoo is verified.
7. Customer extension state within the customer boundary.
8. Encryption-key custody and recovery procedure, stored separately from backup data.

## Recovery design

Recovery must restore into clean, isolated infrastructure before traffic is switched.

Required sequence:

1. Declare incident and freeze unsafe writes.
2. Identify the approved backup and integrity evidence.
3. Provision a clean target with the correct environment marker.
4. Restore database schema and data.
5. Restore object storage and verify referenced objects.
6. Recreate least-privilege runtime roles.
7. Apply only approved compatible migrations.
8. Start services with fresh runtime credentials.
9. Run liveness, readiness, security, tenant-isolation, and contract checks.
10. Reconcile database references, storage objects, and audit counts.
11. Validate release and configuration identity.
12. Obtain owner approval before traffic switch.
13. Record evidence, gaps, and follow-up actions.

Never restore over a populated target without an explicitly approved destructive procedure. Never run production recovery from an unreviewed shell session.

## Recovery testing

| Test | Minimum frequency | Evidence |
| --- | --- | --- |
| Backup integrity | Every backup or scheduled verification | Checksum/signature result |
| Database restore | Scheduled per RPO/RTO | Restore duration and validation |
| Object reconciliation | With database restore | Reference/object report |
| Application startup | Each release candidate | Health/readiness result |
| Tenant isolation | Each security baseline change | Cross-tenant negative tests |
| Full recovery drill | Scheduled by owner | Source destruction, clean target, traffic decision |
| Key recovery | Scheduled and after rotation | Custodian and decryption evidence |
| Customer restore | Before customer contract commitment | Customer-scoped recovery report |

The legacy repository already contains an encrypted backup and isolated recovery drill for its own runtime. This is evidence for preservation quality, not evidence that the future SCO product estate has a complete recovery system.

## Incident response

Every incident runbook must provide:

- severity levels;
- detection source;
- incident commander;
- technical lead;
- customer communication owner;
- evidence preservation rules;
- containment actions;
- credential/session revocation;
- recovery decision;
- status updates;
- post-incident review;
- corrective action owner and deadline.

Security incidents must not be debugged by copying secrets or customer data into chat, issues, logs, or temporary files.

## Monitoring and alerting

Monitor at service, host, data, and business layers:

- availability and latency;
- error rate and saturation;
- CPU, memory, disk, and container restarts;
- PostgreSQL connections, locks, replication, storage, and migrations;
- object storage availability, capacity, and failed writes;
- queue depth and retry/dead-letter volume;
- backup freshness and restore failures;
- certificate and domain expiry;
- release and dependency drift;
- authentication failures and privilege anomalies;
- customer-isolation violations;
- critical business workflow failures.

Alerts must have an owner and a runbook. Avoid alerts that cannot lead to an action.

## Capacity and maintenance

Before increasing traffic or adding a product:

- define resource budgets;
- measure baseline and peak behavior;
- set database connection and queue limits;
- test storage growth and retention;
- validate backup duration and capacity;
- plan certificate and dependency renewals;
- use maintenance windows for incompatible changes;
- retain rollback capacity;
- document scaling triggers and decision owners.

Do not use production load testing without a separately approved safe plan.

## Data lifecycle

For each data class define:

- source of truth;
- retention;
- deletion or anonymization;
- backup retention;
- legal hold;
- customer export;
- customer offboarding;
- encryption and key rotation;
- access audit;
- restore behavior.

Customer data must not remain in shared development or test environments.

## Operational evidence

The owner review package should contain:

- service catalog;
- environment matrix;
- network and data-flow diagrams;
- access review;
- release and deployment records;
- backup freshness and restore reports;
- SLO and alert definitions;
- incident runbooks;
- customer-isolation evidence;
- open risk register;
- accepted exceptions with expiry dates.

## Architecture completion gates

The SCO server architecture is ready to close when:

- current infrastructure evidence is collected read-only;
- all products have owners and runtime classifications;
- public/private boundaries are confirmed;
- identity, secrets, and customer isolation are tested;
- release and rollback paths are rehearsed in staging;
- backup and recovery meet approved RPO/RTO;
- monitoring and incident owners are active;
- unresolved risks have a named owner and target date;
- future repository creation decisions are captured as ADRs;
- legacy procurement remains preserved and separately labeled.

## Final execution boundary

After architecture closure, execution may proceed only by approved blocks:

1. establish or confirm organization and teams;
2. create repository templates and reusable CI;
3. verify Odoo and external product assets;
4. implement the first approved product boundary;
5. integrate through versioned contracts;
6. validate staging;
7. obtain separate production authorization.

This block does not authorize any of those externally impactful actions.
