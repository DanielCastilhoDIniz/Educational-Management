


┌─────────────┐
│   ACTIVE    │
│ (ativa)     │
└─────┬───────┘
      │ conclude()
      │ verdict.is_allowed == True
      ▼
┌─────────────┐
│ CONCLUDED   │◄───────────────┐
│ (final)     │                │
└─────────────┘                │
                               │
          (idempotência)       │
                               │
        conclude()             │
        em CONCLUDED           │
        → no-op                │
                    ┌──────────────────────────┐
                    │ ConcludeEnrollmentService│
                    └────────────┬─────────────┘
                                 │  execute(...)
                                 ▼
                    ┌──────────────────────────┐
                    │ EnrollmentRepository     │
                    │ get_by_id(enrollment_id)│
                    └────────────┬─────────────┘
                                 │
                            None │ Enrollment
                                 │

                    EnrollmentNotFoundError
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ Enrollment (Aggregate)   │
                    │ conclude(...)            │
                    └────────────┬─────────────┘
                                 │
                         ┌───────┴────────┐
                         │                │
                     idempotente       mudança
                     (no-op)            real
                         │                │
                        nts = []     pull_domain_events()
                     changed=False   changed=True
                     save ❌         save ✅
                         │                │
                         └───────┬────────┘
                                 │
                                 ▼
                     ┌──────────────────────────┐
                     │ ApplicationResult        │
                     │ changed / events / state │
                     └──────────────────────────┘
