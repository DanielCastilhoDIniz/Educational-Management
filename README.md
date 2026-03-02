# School Management SaaS Backend

Backend for a school management system built around explicit domain modeling, stable application contracts, and long-term maintainability.

The current implementation is centered on the academic enrollment context, with a DDD-oriented structure and tests focused on business invariants.

## Goals

- Model academic enrollment lifecycle with explicit state transitions.
- Keep domain rules isolated from framework concerns.
- Expose stable application-layer results for expected failures.
- Preserve auditability through transition records and domain events.
- Prepare the codebase for Django/PostgreSQL adapters without coupling the core model to infrastructure.

## Current Scope

The most mature module today is `academic.enrollment`.

Implemented in the domain layer:

- `Enrollment` aggregate root
- enrollment states: `active`, `suspended`, `cancelled`, `concluded`
- command methods: `cancel`, `suspend`, `conclude`, `reactivate`
- immutable domain events
- transition history via `StateTransition`
- invariant validation on construction and rehydration

Implemented in the application layer:

- use cases for `cancel`, `suspend`, and `conclude`
- stable `ApplicationResult` output contract
- `ApplicationError` + `ErrorCodes`
- domain-to-application error mapping
- common state change flow helper to keep orchestration consistent

Not implemented yet:

- real persistence adapter with optimistic concurrency
- typed persistence failures mapped to `CONCURRENCY_CONFLICT` / `DATA_INTEGRITY_ERROR`
- authorization and policy ports for actor roles and institutional rules
- API layer
- application service for `reactivate`

## Architecture

The codebase follows a layered structure:

- `domain/`: business rules, invariants, entities, value objects, domain events
- `application/`: use-case orchestration, ports, DTOs, error translation
- `infrastructure/`: framework and persistence adapters
- `tests/`: application and domain tests

The domain is framework-independent.

## Enrollment Contracts

### Domain

The aggregate enforces:

- valid state normalization
- datetime normalization to UTC
- required and forbidden timestamps by state
- idempotent behavior for repeated final-state operations where applicable
- event emission only through aggregate transitions

### Application

Application services return `ApplicationResult` instead of raising for expected failures.

Possible outcomes:

- success with change: `changed=True`, `domain_events` not empty, `new_state` present
- success with no-op: `changed=False`, no events
- failure: `success=False`, `error` present

The current orchestration rule is:

1. Load aggregate
2. Execute domain command
3. Snapshot pending events
4. Persist aggregate
5. Clear pending events
6. Return `ApplicationResult`

This keeps events available if persistence fails, because the buffer is not drained before `save()`.

## Project Structure

```text
src/
  domain/
    academic/
      enrollment/
        entities/
        errors/
        events/
        value_objects/
  application/
    academic/
      enrollment/
        dto/
        errors/
        ports/
        services/
  infrastructure/
tests/
  domain/
    academic/
      enrollment/
  application/
docs/
```

## Main References

- domain rules: `DOMIAIN_ROLES.md`
- persistence decisions: `docs/adr/001-enrollment-persistence.md`

## Development Setup

Python target: `3.12+`

Install development dependencies:

```bash
python -m pip install -r requirements/requirements_dev.txt
```

## Running Tests

Run all tests:

```bash
python -m pytest
```

Run with coverage:

```bash
python -m pytest --cov=src --cov-report=term-missing
```

Pytest is configured via [`pytest.ini`](d:/TI/School_management/Education_manegment/pytest.ini) with:

- `testpaths = tests`
- `pythonpath = src`

## Linting

Ruff is configured in [`pyproject.toml`](d:/TI/School_management/Education_manegment/pyproject.toml).

Run lint:

```bash
ruff check .
```

## Current Status

Current state of the enrollment module:

- domain model implemented and covered by focused unit tests
- application services aligned to a stable result contract
- error payloads standardized between domain and application
- common state-change orchestration extracted to reduce duplication

The code is ready for the next phase: persistence adapters, authorization/policy ports, and API exposure.

## Next Steps

- implement repository adapter with optimistic concurrency
- map infrastructure failures to typed application errors
- introduce actor context and authorization/policy ports
- add application service for enrollment reactivation
- expose use cases through Django/DRF

## About

This repository is a study and portfolio project with production-style design goals:

- explicit modeling
- layered architecture
- stable contracts
- test-driven business rules

## License

Educational and demonstrative project.
