
---

# 📄 ADR 001 — Persistência do Aggregate Enrollment

## Status

Aprovado — base para implementação da Infraestrutura (Django ORM + Postgres).

---

## 1. Objetivo

Persistir o aggregate **Enrollment** garantindo:

* Reidratação íntegra do estado
* Auditoria imutável das mudanças
* Separação clara entre Domínio e Infra
* Atomicidade entre snapshot e log
* Proteção contra concorrência e duplicação

---

## 2. Estratégia de Persistência

### Escolha: Snapshot + Log Append-Only

* A tabela **Enrollment** armazena o estado atual (snapshot).
* A tabela **EnrollmentTransition** armazena as mudanças de estado como fatos imutáveis.

### Justificativa

* Permite consultas rápidas por estado.
* Preserva histórico completo.
* Evita complexidade prematura de event sourcing.
* Alinha-se com o domínio já modelado (state + timestamps + transitions).

---

## 3. Modelo de Dados

### 3.1. Tabela: Enrollment (Snapshot)

Campos:

* id (gerado pela aplicação)
* student_id
* class_group_id
* academic_period_id
* state
* created_at (imutável)
* updated_at (técnico)
* concluded_at (nullable)
* cancelled_at (nullable)
* suspended_at (nullable)
* version (controle otimista de concorrência)

Índices:

* student_id
* state
* (academic_period_id, state) — opcional conforme necessidade

Constraints:

* CHECK/enum para state
* nullability coerente

Política:

* Snapshot é a fonte da verdade do estado atual.
* updated_at só muda quando há alteração real (changed=True).

---

### 3.2. Tabela: EnrollmentTransition (Log Imutável)

Campos:

* id (PK)
* transition_id (Unique)
* enrollment_id (FK)
* occurred_at (TIMESTAMP WITH TIME ZONE)
* action
* from_state
* to_state
* justification (TEXT nullable)
* actor_id (obrigatório)

Índices:

* enrollment_id
* (enrollment_id, occurred_at)
* actor_id (opcional)

Foreign Key:

* ON DELETE PROTECT

Política:

* Append-only (não editar, não deletar)
* transition_id garante deduplicação robusta
* actor_id obrigatório (usar "system" para rotinas)

---

## 4. Consistência e Transações

Regra:

> 1 comando de Application Service = 1 transação DB

Dentro da transação:

1. Atualizar snapshot (se changed=True)
2. Inserir novas transitions
3. Commit

Se qualquer operação falhar → rollback total.

---

## 5. Controle de Concorrência

Estratégia: Controle Otimista

* Campo `version` no snapshot.
* Save falha se a versão no banco for diferente da carregada.

Alternativa válida: usar `updated_at` como token de concorrência.

Erro traduzido como: `ConcurrencyConflictError`.

---

## 6. Fonte do Tempo

* Todos timestamps são UTC.
* occurred_at nasce no domínio (ou Application Service).
* Banco pode ter default como fallback, não como regra primária.

---

## 7. Fonte do Estado Atual

* O estado atual é definido pelo snapshot.
* Transitions são auditoria.
* Invariante de persistência:

  * state do snapshot deve coincidir com o `to_state` da última transition (quando existir).

---

## 8. Responsabilidade do Repositório

### get_by_id(id)

* Busca snapshot.
* Busca transitions ordenadas por occurred_at.
* Reidrata aggregate completo.

### save(enrollment)

* Se changed=False → não atualiza snapshot nem cria transitions.
* Se changed=True → atualiza snapshot + insere novas transitions.
* Opera dentro de transação.
* Traduz erros de DB em erros de infra específicos.

---

## 9. Política de Delete

* Delete físico proibido.
* ON DELETE PROTECT.
* Evolução futura: soft delete com deleted_at.

---

## 10. Tradução de Erros

Infra não propaga erros crus do ORM.

Mapeamentos esperados:

* IntegrityError (unique) → DuplicateTransitionError
* Versão divergente → ConcurrencyConflictError
* FK violada → DataIntegrityError

---

## 11. Estratégia de Crescimento

MVP:

* get_by_id carrega todas transitions.

Evolução futura:

* Carregar parcial para decisões
* Repositório de consulta separado para auditoria pesada

---

# ✅ CHECKLIST DE IMPLEMENTAÇÃO (Infra)

## Fase 1 — Modelagem e Migrations

[ ] Criar modelo ORM Enrollment
[ ] Adicionar campo version (ou política definida)
[ ] Definir constraints de state
[ ] Criar índices estratégicos

[ ] Criar modelo EnrollmentTransition
[ ] Adicionar transition_id unique
[ ] Definir FK com ON DELETE PROTECT
[ ] Criar índices por enrollment_id e occurred_at
[ ] Garantir actor_id obrigatório

[ ] Gerar migrations
[ ] Aplicar no Postgres
[ ] Validar estrutura via inspeção do banco

---

## Fase 2 — Implementação do Repository

[ ] Implementar get_by_id
[ ] Implementar reidratação completa (snapshot + history)
[ ] Garantir ordenação das transitions

[ ] Implementar save com transação
[ ] Atualizar snapshot somente quando changed=True
[ ] Inserir apenas novas transitions
[ ] Garantir controle otimista
[ ] Traduzir erros de banco

---

## Fase 3 — Testes de Integração

### Repository

[ ] Round-trip: salvar e reidratar igual
[ ] Inserir múltiplas transitions corretamente
[ ] No-op não cria transition
[ ] Unique impede duplicação
[ ] Concurrency gera erro esperado
[ ] Rollback mantém consistência

### Application + DB

[ ] conclude persiste snapshot e transition
[ ] cancel idem
[ ] suspend idem
[ ] idempotência preservada
[ ] timestamps coerentes

---

## Fase 4 — Critério de “Infra Concluída”

[ ] Todas as operações funcionam com Postgres real
[ ] Não há duplicação de transitions
[ ] Transação protege consistência
[ ] Concurrency control testado
[ ] Logs de auditoria confiáveis

---