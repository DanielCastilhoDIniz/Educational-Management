---

# 📘 Application Layer — Guia Norteador

## 0. Propósito deste Documento

Este documento define **como a camada de Application deve ser desenhada e utilizada** neste projeto.

A camada de Application:

* **orquestra** casos de uso (use cases);
* **não contém regras de negócio**;
* **coordena transações** entre domínio e infraestrutura;
* **expõe contratos estáveis** para camadas externas (API, jobs, integrações).

Este documento tem **autoridade arquitetural** para a camada de Application.

---

## 1. Responsabilidades da Camada de Application

### 1.1 O que a Application **faz**

* Carrega aggregates via repositórios (ports)
* Executa comandos do domínio
* Decide **quando persistir**
* Extrai Domain Events (`pull_domain_events`)
* Retorna resultados padronizados para a camada superior (**sem exceptions em fluxos esperados**)

### 1.2 O que a Application **não faz**

* Não valida regras de negócio
* Não muda estados diretamente
* Não acessa banco de dados ou ORM
* Não conhece Django, DRF, serializers ou HTTP

> **Regra de ouro:**
> Se uma regra “define o que é permitido”, ela pertence ao **domínio**.

---

## 2. Regras de Dependência (Invioláveis)

* `domain` **não depende** de `application`
* `application` **depende** de `domain`
* `infra` depende de `application` e `domain`
* `presentation` (DRF) depende de `application`

Qualquer violação desta regra é considerada **erro arquitetural**.

---

## 3. Estrutura de Pastas Recomendada

Estrutura mínima:
src/application/
services/
ports/
errors/
dto/


### 3.1 `services/`

Contém **um arquivo por caso de uso**.

Exemplo:

* `conclude_enrollment.py`
* `cancel_enrollment.py`
* `suspend_enrollment.py`

Cada arquivo define:

* **uma classe**
* **um método público**: `execute`

---

### 3.2 `ports/`

Define **interfaces (contratos)** que a infraestrutura deve implementar.

Exemplo:

* `enrollment_repository.py`

Regras:

* Nenhuma implementação concreta
* Sem ORM, SQL ou frameworks
* Apenas contratos e semântica

---

### 3.3 `errors/`

Define erros **da camada de Application** (quando houver).

Exemplo:

* `EnrollmentNotFoundError`

Regras:

* Não duplicar erros de domínio
* Não conter regras de negócio
* Expressar falhas de orquestração, IO ou contexto

> **Importante (contrato A):**
> Mesmo quando existirem erros de Application, **os services não devem lançar**.
> Eles devem converter em `ApplicationResult(success=false, error=...)`.

---

### 3.4 `dto/`

Define **objetos de entrada e saída** da Application.

Uso típico:

* padronizar retorno
* reduzir acoplamento com o domínio
* facilitar integração futura com APIs

---

## 4. Naming Convention (Padrão Obrigatório)

### 4.1 Arquivos e Classes

| Elemento       | Padrão               |
| -------------- | -------------------- |
| Arquivo        | `verbo_objeto.py`    |
| Classe         | `VerboObjetoService` |
| Método público | `execute`            |

Exemplo:

* `conclude_enrollment.py`
* `ConcludeEnrollmentService.execute(...)`

---

## 5. Contrato do Application Service

### 5.1 Inputs

* Todos os parâmetros **devem ser keyword-only**
* IDs e dados externos entram aqui
* Objetos de domínio podem ser aceitos (ex.: `verdict`)

Exemplo conceitual:

* `enrollment_id`
* `actor_id`
* `verdict`
* `occurred_at?`
* `justification?`

---

### 5.2 Output (Contrato Padronizado)

Todos os Application Services **devem retornar um resultado padronizado**: `ApplicationResult`.

#### Estrutura conceitual: `ApplicationResult`

Campos mínimos:

* `aggregate_id`
* `success` (bool)
* `changed` (bool)
* `domain_events` (lista de DomainEvent)
* `new_state` (opcional)
* `error` (opcional, quando `success=false`)

> A camada de Application **não retorna o aggregate inteiro**.

---

### 5.3 Regra de Ouro: Sem Exceptions em Fluxos Esperados (Contrato A)

Os services **não devem lançar exceções** em situações esperadas:

- aggregate não encontrado
- violação de regra de domínio
- transição inválida
- justificativa ausente
- conclusão não permitida
- pré-condições de application (quando existirem)

Em vez disso, devem retornar:

- `ApplicationResult(success=false, changed=false, domain_events=[], error=...)`

Exceções só são aceitáveis para falhas **inesperadas** (bug/infra não mapeada).
Essas falhas devem ser tratadas no adaptador superior (API), retornando `UNEXPECTED_ERROR`.

---

### 5.4 Contrato de Erro (quando `success=false`)

`error` deve conter:

- `code` (estável, para integração)
- `message` (humano)
- `details` (opcional, estruturado)

#### Codes mínimos recomendados
- `ENROLLMENT_NOT_FOUND`  repo retornou None
- `JUSTIFICATION_REQUIRED` → domínio exigiu justificativa
- `INVALID_STATE_TRANSITION` → conflito com estado atual (409)
- `ENROLLMENT_NOT_ACTIVE` → conflito com estado atual (409)
- `CONCLUSION_NOT_ALLOWED` → regra/política de conclusão (422)
- `CONCURRENCY_CONFLICT` (se aplicável)
- `DATA_INTEGRITY_ERROR` (se aplicável)
- `STATE_INTEGRITY_VIOLATION` (se aplicável) → dados inconsistentes (500)
- `UNEXPECTED_ERROR` (apenas no adaptador/API)→ fallback do adaptador (500)

---

## 6. Fluxo Interno do Application Service (Sequência Obrigatória)

Todo `execute` segue **exatamente esta sequência**:

1. **Load**
   * Buscar aggregate via repository
   * Se não existir → retornar `ApplicationResult.failure(code=ENROLLMENT_NOT_FOUND)`

2. **Execute Domain Command**
   * Chamar método do aggregate
   * Capturar exceções de domínio e converter em `ApplicationResult.failure(...)`

3. **Pull Events (uma única vez)**
   * Extrair e limpar Domain Events
   * **Regra:** o service deve chamar `pull_domain_events()` no máximo uma vez por execução.

4. **Detect Change**
   * `changed = (len(domain_events) > 0)`
   * **Regra:** “mudança” no contrato da Application é definida pela existência de eventos do domínio.
     (Isso evita armadilhas futuras onde algo muda sem trocar estado.)

5. **Persist**
   * Persistir **somente se** `changed=true`
   * Persistência deve acontecer **antes** de qualquer publicação externa (a publicação é responsabilidade da infra).

6. **Return Result**
   * Sucesso com mudança: `success=true, changed=true, new_state` presente, `domain_events` presentes
   * Sucesso sem mudança: `success=true, changed=false, new_state` ausente, `domain_events=[]`
   * Falha: `success=false, changed=false, domain_events=[]`, `error` preenchido

---

## 7. Repositório (Port) — Contrato

### 7.1 Métodos mínimos

* `get_by_id(id)`
* `save(aggregate)`

### 7.2 Regras

* `get_by_id` retorna `None` se não existir
* `save` persiste o estado atual (snapshot) e histórico (quando aplicável)
* Concorrência/versionamento:
  * decisão documentada em ADR (ex.: versionamento otimista)

---

## 8. Testes da Camada de Application

### 8.1 Objetivo dos testes

* Provar o **contrato do caso de uso**
* Verificar:
  * retorno padronizado (success/changed/error)
  * persistência correta **somente quando changed=true**
  * idempotência (changed=false)
  * captura e tradução de erros de domínio
  * extração de eventos (pull uma vez)

### 8.2 O que usar

* Repositório in-memory
* Domain real
* Sem mocks de domínio

### 8.3 Casos mínimos por service

1. Caminho feliz (success=true, changed=true)
2. Aggregate não encontrado (success=false, code=ENROLLMENT_NOT_FOUND)
3. Domínio bloqueia operação (success=false, code correspondente)
4. Persistência ocorre somente quando há mudança (changed=true)
5. Eventos são extraídos uma única vez e retornados corretamente
6. Idempotência: chamada repetida retorna success=true, changed=false (quando aplicável)

---

## 9. Evolução Planejada

### 9.1 Próximos Application Services
* `CancelEnrollmentService`
* `SuspendEnrollmentService`
* `ConcludeEnrollmentService`

### 9.2 Integração futura
* DRF chamará Application Service e mapeará `ApplicationResult` para HTTP
* Infra implementará ports
* Domain permanece isolado

---

## 10. Princípios Fundamentais

* **Domínio é a autoridade**
* **Application coordena**
* **Infra executa**
* **Testes são contrato**
* **Eventos comunicam fatos**
* **Sem exceptions em fluxos esperados (Contrato A)**

---

## 11. Critério de Qualidade

Uma implementação da camada de Application é considerada correta se:

* nenhuma regra de negócio está fora do domínio
* todos os casos de uso seguem o mesmo padrão
* services retornam `ApplicationResult` em todos fluxos esperados
* persistência só ocorre quando `changed=true`
* `pull_domain_events()` é chamado no máximo uma vez por execução
* testes de aplicação passam sem mocks frágeis

---

## 12. Mapeamento Padrão `error.code` → HTTP (Contrato do Adaptador / DRF)

> **Objetivo**
>
> A camada Presentation (DRF) deve ser apenas um adaptador.
> Ela converte `ApplicationResult` em HTTP de forma **determinística** e **estável**.
>
> Regra: **o código HTTP não depende da exceção**, mas sim do `error.code`.

### 12.1 Regras gerais

- Se `success=true` e `changed=true` → **200 OK** (ou 201 Created quando fizer sentido)
- Se `success=true` e `changed=false` → **200 OK** (ou 204 No Content se endpoint for comando puro)
- Se `success=false` → usar a tabela abaixo

### 12.2 Tabela de mapeamento

| `error.code`                | HTTP | Quando usar (semântica) |
| --------------------------- | ---- | ------------------------ |
| `ENROLLMENT_NOT_FOUND`      | 404  | Aggregate não existe     |
| `JUSTIFICATION_REQUIRED`    | 422  | Falta dado obrigatório para ação válida (justificativa) |
| `INVALID_STATE_TRANSITION`  | 409  | Conflito de estado (ação não compatível com estado atual) |
| `ENROLLMENT_NOT_ACTIVE`     | 409  | Conflito de estado (pré-condição interna: precisa estar ATIVA) |
| `CONCLUSION_NOT_ALLOWED`    | 422  | Regra de domínio impede conclusão (veredito/política) |
| `STATE_INTEGRITY_VIOLATION` | 500  | Violação de invariantes (erro grave: dados inconsistentes) |
| `CONCURRENCY_CONFLICT`      | 409  | Controle otimista falhou (versão divergente) |
| `DATA_INTEGRITY_ERROR`      | 500  | Infra detectou inconsistência estrutural (FK/constraints) |
| `UNEXPECTED_ERROR`          | 500  | Fallback do adaptador para falhas não mapeadas |

> **Nota**
>
> - **409 Conflict** é usado para “estado atual não permite a intenção” (conflito com o recurso).
> - **422 Unprocessable Entity** é usado para “inputs válidos em forma, mas insuficientes/inadequados ao domínio”.

### 12.3 Payload de erro HTTP (padrão)

Quando `success=false`, o adaptador deve responder com um payload estável:

* details inclui aggregate_id, action, current_state como padrão. al

- `error.code`
- `error.message`
- `error.details` (se existir)
- `aggregate_id` (se aplicável)

Exemplo conceitual:

```json
{
  "success": false,
  "aggregate_id": "enr-123",
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "message": "Cannot conclude enrollment from CANCELLED state.",
    "details": {
      "from_state": "CANCELLED",
      "to_state": "CONCLUDED"
    }
  }
}
```


### 12.4 Checklist do Adaptador (DRF)

 Nunca chamar domínio diretamente

 Sempre chamar Application Service

 Nunca depender de try/except para mapear regra (usar ApplicationResult)

 success=false sempre retorna error.code/message

 HTTP status vem apenas do error.code

 Não vazar stacktrace em responses


 ### 12.5 Contrato de Mapeamento — DomainError → ErrorCodes (Application)

A camada de Application captura `DomainError` (e subclasses) e converte para `ApplicationError`
usando `ErrorCodes` como contrato público estável.

> Regra: **não vazar exceções** para camadas superiores (Contrato A).
> Sempre retornar `ApplicationResult(success=false, ...)`.

#### Tabela de mapeamento

| Exceção de Domínio (DomainError)         | `ErrorCodes`                    | HTTP (padrão) | Significado |
| ---------------------------------------- | ------------------------------- | ------------- | ----------- |
| `InvalidStateTransitionError`            | `INVALID_STATE_TRANSITION`      | 409           | Ação incompatível com o estado atual |
| `IrreversibleStateError`                 | `INVALID_STATE_TRANSITION`      | 409           | Tentativa de sair de estado final / irreversível |
| `EnrollmentAlreadyFinalError`            | `INVALID_STATE_TRANSITION`      | 409           | Aggregate em estado final não pode ser modificado |
| `EnrollmentNotActiveError`               | `ENROLLMENT_NOT_ACTIVE`         | 409           | Operação exige matrícula ATIVA |
| `JustificationRequiredError`             | `JUSTIFICATION_REQUIRED`        | 422           | Campo obrigatório ausente (justificativa) |
| `ConclusionNotAllowedError`              | `CONCLUSION_NOT_ALLOWED`        | 422           | Critérios pedagógicos/institucionais impedem conclusão |
| Qualquer outro `DomainError` (raro)      | `STATE_INTEGRITY_VIOLATION`*    | 500           | Invariante violada / inconsistência grave |

\* Se for claramente um erro inesperado de infraestrutura/bug não classificado, o adaptador pode usar `UNEXPECTED_ERROR` (500). Preferir `STATE_INTEGRITY_VIOLATION` quando a origem for o domínio.

#### Regras para `details`

- `ApplicationError.details` deve preservar o máximo possível de `DomainError.details` quando existir.
- É permitido acrescentar contexto de orquestração:
  - `enrollment_id` (sempre que disponível)
  - `current_state`
  - `action` (ex.: `"cancel"`, `"suspend"`, `"conclude"`)
- Não incluir stack traces, dados sensíveis ou detalhes internos de infraestrutura.

---