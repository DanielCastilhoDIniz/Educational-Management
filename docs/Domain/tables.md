
---

## Passo 3 — Tabela formal de transições

A seguir está a tabela que eu recomendo você adotar **como documento oficial do aggregate** (pode virar um `docs/domain/enrollment_transitions.md`).

> **Legenda curta**
>
> * “Permitido?” = o domínio aceita a intenção
> * “Efeito” = muda estado? (sim/não)
> * “Justificativa” = exigida pelo domínio (não por UI)
> * “Evento” = qual Domain Event é registrado se houver mudança

### A) Ação: **CONCLUIR** (`conclude`)

| Estado atual          |                           Permitido? | Efeito | Estado novo           | Justificativa                                | Observação                                                         | Evento              |
| --------------------- | -----------------------------------: | -----: | --------------------- | -------------------------------------------- | ------------------------------------------------------------------ | ------------------- |
| ACTIVE (ATIVA)        |                                    ✅ |      ✅ | CONCLUDED (CONCLUÍDA) | Depende do `verdict.requires_justification`  | Requer `verdict.is_allowed=True`; se não, erro                     | EnrollmentConcluded |
| SUSPENDED (TRANCADA)  |                                    ❌ |      ❌ | —                     | —                                            | “Só ATIVA pode concluir” → `EnrollmentNotActiveError`              | —                   |
| CANCELLED (CANCELADA) | ❌ *(ou idempotente, escolha abaixo)* |      ❌ | —                     | —                                            | Estado final. Eu recomendo **rejeitar** concluir após cancelamento | —                   |
| CONCLUDED (CONCLUÍDA) |                                    ✅ |      ❌ | CONCLUDED             | —                                            | **Idempotente** (retorna sem alterar)                              | —                   |

**Decisão que você precisa assumir aqui:**

* Para **CANCELLED**, você quer:

  * **rejeitar** concluir (mais coerente), ou
  * tornar idempotente (menos comum).
    Como o seu `conclude` já faz idempotência apenas para CONCLUDED, a escolha mais consistente é: **CANCELLED → rejeita**.

---

### B) Ação: **CANCELAR** (`cancel`)

| Estado atual          |             Permitido? | Efeito | Estado novo           | Justificativa         | Observação                                                                 | Evento              |
| --------------------- | ---------------------: | -----: | --------------------- | --------------------- | -------------------------------------------------------------------------- | ------------------- |
| ACTIVE (ATIVA)        |                      ✅ |      ✅ | CANCELLED (CANCELADA) | **Sim (normalmente)** | Cancelamento costuma exigir motivo (administrativo/pedagógico/solicitação) | EnrollmentCancelled |
| SUSPENDED (TRANCADA)  |                      ✅ |      ✅ | CANCELLED             | **Sim (normalmente)** | Cancelar uma matrícula trancada é comum                                    | EnrollmentCancelled |
| CANCELLED (CANCELADA) |                      ✅ |      ❌ | CANCELLED             | —                     | **Idempotente** (recomendado para robustez)                                | —                   |
| CONCLUDED (CONCLUÍDA) | ❌ *(ou erro de final)* |      ❌ | —                     | —                     | Estado final acadêmico. Recomendação: rejeitar cancelar concluída          | —                   |

📌 Aqui você vai precisar definir:

* Cancelamento exige justificativa sempre?
  No seu modelo de erro existe `JustificationRequiredError` , então faz sentido que **cancel** também possa exigir justificativa por política (igual ao conclude).
  A gente pode modelar isso como: “cancel recebe um *veredito de cancelamento*” no futuro, mas por ora você pode começar com regra simples: **cancelamento exige justificativa não vazia**.

---

### C) Ação: **TRANCAR / SUSPENDER** (`suspend`)

| Estado atual          | Permitido? | Efeito | Estado novo          | Justificativa         | Observação                                                                   | Evento              |
| --------------------- | ---------: | -----: | -------------------- | --------------------- | ---------------------------------------------------------------------------- | ------------------- |
| ACTIVE (ATIVA)        |          ✅ |      ✅ | SUSPENDED (TRANCADA) | **Sim (normalmente)** | Trancamento geralmente precisa motivo (financeiro, disciplinar, solicitação) | EnrollmentSuspended |
| SUSPENDED (TRANCADA)  |          ✅ |      ❌ | SUSPENDED            | —                     | **Idempotente** (já está trancada)                                           | —                   |
| CANCELLED (CANCELADA) |          ❌ |      ❌ | —                    | —                     | Estado final                                                                 | —                   |
| CONCLUDED (CONCLUÍDA) |          ❌ |      ❌ | —                    | —                     | Estado final                                                                 | —                   |

📌 Observação sênior:
Você ainda não tem ação de “reativar / destrancar”. Isso é uma decisão de negócio. Se existir no futuro, vira uma quarta ação (`resume()`), com regra “SUSPENDED → ACTIVE”.

---



