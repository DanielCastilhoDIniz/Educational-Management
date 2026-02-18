
---

# ADR 002 — Deterministic Transition ID (UUIDv5)

## Status

Accepted

## Context

The `Enrollment` aggregate maintains a transition history (`StateTransition`) in the domain layer.
In the infrastructure layer, transitions are persisted in the `enrollment_transitions` table as an append-only log.

We must guarantee:

* No duplicate transition records in case of retries
* Idempotent persistence behavior
* Safe handling of transient failures (e.g., DB commit retry, network interruption)
* Structural integrity independent from application-layer safeguards

Because transitions are persisted in a relational database with a unique constraint on `transition_id`, we need a deterministic strategy to generate this identifier.

---

## Problem

If `transition_id` were generated using `uuid4()` at insertion time:

* Retries of the same logical transition would generate different IDs
* The database would accept duplicates
* The audit log would become inconsistent
* Idempotency would rely solely on application logic

We need persistence-level idempotency.

---

## Decision

We will generate `transition_id` using **UUIDv5**, which is deterministic.

The UUID will be generated from:

* A fixed namespace UUID (constant per bounded context)
* A canonical fingerprint string representing the transition fact

### Namespace Location

Defined in:

```
src/infrastructure/django/apps/academic/constants.py
```

Constant name:

```
ACADEMIC_ENROLLMENT_TRANSITION_NS
```

This namespace value:

* Is generated once
* Is hardcoded
* Must never be changed
* Is documented in this ADR

Changing this namespace would break deterministic generation and invalidate deduplication guarantees.

---

## Fingerprint Strategy

The fingerprint must be:

* Deterministic
* Canonical
* Order-stable
* Timezone-consistent

It is composed of:

* `enrollment_id`
* `action`
* `from_state`
* `to_state`
* `occurred_at` (ISO 8601, timezone-aware UTC)
* `actor_id`
* `justification` (normalized; None → empty string; trimmed)

Example conceptual format:

```
enrollment:<id>|
action:<action>|
from:<from_state>|
to:<to_state>|
at:<occurred_at_iso>|
actor:<actor_id>|
just:<normalized_justification>
```

The fingerprint must be constructed in exactly the same format for all insertions.

---

## Architectural Boundaries

* The domain layer does **not** generate `transition_id`.
* The domain remains unaware of UUIDv5 or persistence concerns.
* The infrastructure layer is responsible for:

  * Inferring `action`
  * Constructing fingerprint
  * Generating UUIDv5
  * Persisting transitions

This preserves Clean Architecture and DDD boundaries.

---

## Consequences

### Positive

* Persistence-level idempotency
* Safe retries
* Protection against duplicate audit rows
* Deterministic behavior
* Domain purity maintained

### Negative

* Namespace must never change
* Fingerprint format must remain stable
* Requires careful normalization of timestamps

---

## Invariants

* `transition_id` is unique in the database
* UUIDv5(namespace, fingerprint) must always return the same value for the same logical fact
* `occurred_at` must be timezone-aware (UTC) before fingerprint generation

---

## Related Decisions

* ADR 001 — Snapshot + Transition Log persistence strategy
* Optimistic locking using `version` field on `EnrollmentModel`

---

## Implementation Notes

* UUIDv5 generation must exist in a single helper function
* The namespace constant must not be recalculated dynamically
* All transition inserts must use this deterministic ID strategy
* The repository must treat unique violations as idempotent retries (when consistent)

---

## Final Statement

Transition persistence must be:

* Deterministic
* Idempotent
* Atomic
* Infrastructure-driven

This ADR formalizes the deterministic UUIDv5 strategy as the official mechanism for transition identity in the Academic bounded context.


