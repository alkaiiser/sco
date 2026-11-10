# SCO Integration and Contract Architecture Block

## Scope

This block defines the integration boundaries between SCO products. It distinguishes intended contracts from integrations verified in the legacy repository.

No external integration is enabled, changed, or migrated by this document.

## Contract principles

1. Integrate through explicit versioned APIs, events, packages, or adapters.
2. Do not share production database tables across product boundaries.
3. Every integration has one producer, one consumer, an owner, a data classification, and a failure policy.
4. Authentication and authorization are separate decisions.
5. Customer and environment scope must be carried and validated end to end.
6. Events are immutable facts; commands are explicit requests with idempotency.
7. Breaking changes require a compatibility window and migration plan.
8. External providers are isolated behind adapters.
9. Secrets belong to the integration owner and are never copied into clients or shared packages.
10. The frozen legacy procurement system remains outside the new product graph unless an owner approves a specific adapter.

## Product authority model

| Product | Owns | May consume | Must not own |
| --- | --- | --- | --- |
| SCO Platform | Identity contracts, shared standards, integration conventions, CI/CD and observability contracts | Approved product metadata | Product-specific business data |
| SCO Odoo | ERP and business-operation records | Platform identity and approved integrations | Mobile or customer UI state |
| SCO Odoo Sectors | Sector-specific Odoo modules and rules | SCO Odoo contracts | Shared platform identity policy |
| SCO Field — By Odoo | Field workflows and distribution experience | Authorized Odoo APIs and platform identity | Direct database ownership of Odoo |
| SCO Mobile | Mobile user experience and client state | Versioned product APIs, identity, notifications | Direct customer database access |
| SCO Connect | Communication and interaction workflows | Identity, event contracts, approved provider adapters | ERP source-of-truth records |
| SCO Digital Branch | Digital branch journeys and customer interaction state | Connect, Odoo APIs, platform identity | Shared database tables with unrelated products |
| SCO Website & Store | Public acquisition, catalog, checkout, CRM handoff | Approved product and commerce APIs | Internal runtime or migration credentials |
| SCO Customer Extensions | Customer-specific behavior and adapters | Publicly supported contracts only | Other customer data or credentials |
| SCO Legacy Procurement | Frozen procurement behavior and historical data | Existing local dependencies only | Future platform ownership |

## Integration map

```text
                 +------------------+
                 |   SCO Platform   |
                 | identity/contracts|
                 +---------+--------+
                           |
       +-------------------+-------------------+
       |                   |                   |
+------v------+     +------v------+     +------v------+
| SCO Odoo    |<--->| SCO Connect |<--->| Digital     |
| ERP authority|     | interactions|     | Branch      |
+------+------+     +------+------+     +------+------+
       |              |                     |
+------v------+  +----v-----+        +-------v--------+
| Odoo Sectors|  | Field    |        | Website & Store|
+-------------+  +----------+        +----------------+
       ^              ^
       |              |
       +--------+-----+
                |
          +-----v-----+
          |   Mobile  |
          +-----------+

Customer Extensions consume approved contracts and remain isolated.
Legacy Procurement stays outside this graph.
```

The map is a target design. It does not confirm that these products or links currently exist.

## Contract types

### Synchronous API

Use for:

- authenticated reads;
- bounded commands requiring an immediate decision;
- health and capability checks.

Required properties:

- explicit version;
- timeout and retry policy;
- correlation ID;
- idempotency key for retried commands;
- authorization and tenant scope;
- structured error contract;
- rate and payload limits;
- audit event for sensitive operations.

### Asynchronous event

Use for:

- integration notifications;
- long-running work;
- fan-out to independent consumers;
- durable workflow transitions.

Required properties:

- event name and schema version;
- event ID and causation ID;
- producer and owner;
- customer/environment scope;
- ordering and delivery guarantee;
- deduplication rule;
- retention and replay policy;
- dead-letter and reconciliation path.

### Shared package

Use only for:

- stable types;
- validation schemas;
- protocol clients;
- provider-neutral interfaces;
- security-safe utilities.

Do not put customer data, database clients, deployment credentials, or product business rules into shared packages.

### Provider adapter

Use for:

- payments;
- messaging;
- meetings;
- storage;
- identity providers;
- CRM and external ERP bridges.

Adapters must hide provider-specific credentials and translate provider failures into a stable internal contract.

## Identity and authorization flow

1. Client authenticates with the approved identity authority.
2. The API validates token issuer, audience, expiry, and required claims.
3. The service resolves product, environment, and customer scope.
4. Authorization checks the action, resource, purpose, and tenant boundary.
5. The service calls another product using a service identity scoped to the contract.
6. The consumer validates the producer identity and schema version.
7. Sensitive actions emit an audit event with actor, customer, purpose, resource, result, and correlation ID.

Mobile and Field clients must never receive Odoo database credentials. Website and Store must never receive migration, runtime database, or internal service credentials.

## Odoo integration boundary

SCO Odoo is the proposed ERP authority for ERP-owned workflows. Before implementation:

- record the Odoo version and supported API surface;
- identify authorized environments and owners;
- define read/write ownership for every entity;
- define synchronization direction and conflict policy;
- define webhook/event authenticity and replay protection;
- define rate limits and retry behavior;
- define Odoo outage behavior;
- test against a non-production environment;
- document data retention and deletion obligations.

Direct SQL integration is prohibited by default. Any exception requires an ADR, least-privilege role, read/write scope, migration plan, and rollback evidence.

## Field and Mobile boundary

Field and Mobile are independent products:

- use versioned APIs;
- use short-lived access tokens and refresh controls;
- support offline or intermittent connectivity through explicit sync contracts;
- use idempotent commands;
- avoid storing unrestricted customer data on devices;
- encrypt local storage;
- support remote session revocation;
- define minimum supported API and app versions;
- separate development, test, staging, and store-release credentials.

## Connect and Digital Branch boundary

Connect and Digital Branch must:

- use identity and customer scope from the platform;
- expose communication events through versioned contracts;
- protect meeting/message content according to data classification;
- avoid becoming an ERP source of truth;
- define provider fallback and retry behavior;
- record consent and audit requirements;
- separate customer communication data from internal operations.

## Website and Store boundary

Website & Store must:

- keep payment and checkout credentials server-side;
- isolate public traffic from internal APIs and databases;
- use a narrow catalog and CRM contract;
- avoid direct database access to Odoo or customer systems;
- validate webhook signatures and idempotency;
- define order, payment, refund, and failure reconciliation;
- separate analytics and marketing data from operational records.

## Customer extension boundary

Customer Extensions must consume published contracts only. Each extension must declare:

- supported contract versions;
- customer scope;
- data and secrets used;
- deployment environment;
- support owner;
- test and rollback path;
- offboarding and data-retention behavior.

No extension may infer another customer's identity, access a shared customer database, or bypass platform authorization.

## Compatibility and lifecycle

- APIs and events use explicit major versions.
- Additive changes are preferred.
- Deprecation requires notice, owner, deadline, migration path, and telemetry.
- Shared packages use SemVer and changelogs.
- Odoo compatibility is recorded as a matrix by product and release.
- Mobile and Field clients have minimum supported versions.
- Events remain replayable for the documented retention window.
- Contract tests run in CI for every producer and consumer.
- Breaking changes require coordinated releases or a compatibility adapter.

## Failure and recovery

Every integration must document:

- timeout;
- retry and backoff;
- idempotency;
- circuit breaker or rate limit;
- partial success;
- compensation or reconciliation;
- dead-letter handling;
- operator alert;
- replay or restore procedure;
- customer communication path.

A product outage must not expose credentials or silently corrupt another product's source of truth.

## Evidence currently verified

The legacy repository verifies its own internal API, tenant, role, PostgreSQL, object-storage, and recovery contracts. It does not verify active Odoo, Field, Mobile, Connect, Digital Branch, Website & Store, or customer-extension repositories.

## Block acceptance criteria

This block is accepted for implementation planning when:

- each product authority is approved;
- each integration has a producer, consumer, owner, and data class;
- API/event schemas and compatibility rules are versioned;
- identity and tenant propagation are tested;
- failure, replay, and reconciliation paths are defined;
- Odoo environments and access are verified;
- customer extensions consume only approved contracts;
- contract tests are mandatory CI gates.
