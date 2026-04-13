# School Management SaaS Backend

Backend for a multi-tenant school management system built around explicit domain modeling, stable application contracts, and long-term maintainability.

The architecture follows DDD and Clean Architecture principles, with bounded contexts progressively implemented and documented before coding begins.

## Goals

- Model each business context with explicit state machines and invariants.
- Keep domain rules isolated from framework concerns.
- Expose stable application-layer results for expected failures.
- Preserve auditability through transition records and domain events.
- Support multi-tenancy with logical isolation (Phase 1) and institutional role separation.

---

## Bounded Contexts

### `academic.enrollment` — Implemented

The most mature context. Covers the full enrollment lifecycle.

**Domain:**
- `Enrollment` aggregate root with states: `ACTIVE`, `SUSPENDED`, `CANCELLED`, `CONCLUDED`
- Command methods: `cancel`, `suspend`, `conclude`, `reactivate`
- Lifecycle timestamps, immutable domain events, transition history via `StateTransition`
- `ConclusionVerdict` value object with invariant validation

**Application:**
- Use cases: `cancel`, `suspend`, `conclude`, `reactivate`, `create`
- Stable `ApplicationResult` output contract
- `ApplicationError` (now in `application/shared/`)
- Domain-to-application error mapping, common state-change flow helper
- Optimistic concurrency conflict handling

**Infrastructure:**
- Django models and migrations for enrollment snapshot + append-only transition log
- Deterministic `transition_id` for retry-safe deduplication
- `DjangoEnrollmentRepository` with transactional save and optimistic concurrency
- Integration tests for repository success, retry, conflict, rollback, and rehydration

---

### `identity` — Documented, not yet implemented

Identity and Access context covering User lifecycle and institutional membership.

**Documented (ADRs + use cases):**
- `User` aggregate — global identity with `LegalIdentity` VO, `guardian_id`, 4-state machine (`PENDING → ACTIVE → SUSPENDED → INACTIVE`)
- `Membership` aggregate — institutional link with `registration_code`, role assignment, state machine (`SUSPENDED → ACTIVE → SUSPENDED → INACTIVE`)
- `Role` aggregate — `SYSTEM` and `CUSTOM` roles

**Use cases documented:**
- `CadastrarUsuario`, `AtivarUsuario`, `SuspenderUsuario`, `DesbloquearUsuario`, `EncerrarUsuario`
- `VincularUsuarioAInstituicaoEPapel`, `AtivarMembership`, `SuspenderMembership`, `EncerrarMembership`

**Scaffold created** at `src/domain/identity/`, `src/application/identity/`, `src/infrastructure/django/apps/identity/`

---

### `organization` — Planned

Institution and Course context. Dependency for Membership use cases.
Represented in the authorization matrix; ADR and use cases not yet written.

---

## Actor Hierarchy

Defined in `docs/policies/politica_autorizacao_e_matriz_de_atores.md`:

| Level | Role | Scope |
| :--- | :--- | :--- |
| 0 | `administrador_plataforma` | Cross-tenant (is_superuser) |
| 1 | `direcao_estrategica` | Institutional governance |
| 1 | `gestao_financeira` | Financial control (Phase 2 full scope) |
| 2 | `secretaria`, `coordenacao`, `suporte_adm` | Operational |
| 3 | `professor` | Course-scoped |
| 4 | `estudante`, `responsavel` | Self-service |

---

## Architecture

```
src/
  domain/
    academic/enrollment/        # implemented
    identity/user/              # scaffold only
  application/
    shared/                     # ApplicationError, SharedErrorCodes
    academic/enrollment/        # implemented
    identity/user/              # scaffold only
  infrastructure/django/
    apps/academic/              # implemented
    apps/identity/              # scaffold only
tests/
  domain/
  application/
docs/
  adr/                          # ADR trail (001-013, 019, 020, 031, 032)
  use_cases/                    # use case documents
  policies/                     # authorization policy and actor matrix
```

---

## Shared Kernel

`application/shared/` contains cross-context contracts:

- `ApplicationError` — stable error DTO used by all application services
- `SharedErrorCodes` — cross-context error codes (`AUTHZ_*`, `UNEXPECTED_ERROR`)

---

## Architecture Decisions (ADR Trail)

| ADR | Topic |
| :--- | :--- |
| 001 | Ubiquitous language |
| 002 | Enrollment aggregate boundary |
| 003 | Domain events |
| 004 | Domain layer core |
| 005 | Application layer use-case orchestration |
| 006 | Policy boundary and external rules |
| 007 | Infrastructure adapters, persistence, publication |
| 008 | Enrollment persistence strategy |
| 009 | `save()` contract |
| 010 | Deterministic transition identity |
| 011 | Interface/API boundary |
| 012 | Enrollment creation flow |
| 013 | Error taxonomy and failure mapping |
| 019 | Multi-tenancy and institution isolation |
| 020 | User/Membership separation (Identity & Access) |
| 031 | Membership aggregate design |
| 032 | User aggregate design |

---

## Development Setup

Python target: `3.12+`

```bash
python -m pip install -r requirements/requirements_dev.txt
```

## Running Tests

```bash
python -m pytest
python -m pytest --cov=src --cov-report=term-missing
```

Pytest is configured via `pytest.ini` with `testpaths = tests` and `pythonpath = src`.

## Linting

```bash
ruff check .
```

---

## Current Status

- Enrollment context fully implemented and tested
- Identity & Access context fully documented (ADRs, use cases, authorization policy)
- Shared application contracts extracted (`ApplicationError`, `SharedErrorCodes`)
- Identity scaffold created, ready for domain implementation

## Next Steps

1. Implement `User` domain (value objects, aggregate, errors, events)
2. Implement `Role` aggregate
3. Document and implement `Organization` context (Institution, Course)
4. Implement `Membership` domain and use cases end-to-end

---

## About

Study and portfolio project with production-style design goals: explicit modeling, layered architecture, stable contracts, test-driven business rules.

## License

Educational and demonstrative project.
