
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
* Retorna resultados padronizados para a camada superior

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

```
src/application/
  services/
  ports/
  errors/
  dto/
```

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

Define erros **da camada de Application**.

Exemplo:

* `EnrollmentNotFoundError`

Regras:

* Não duplicar erros de domínio
* Não conter regras de negócio
* Expressar falhas de orquestração, IO ou contexto

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

Todos os Application Services **devem retornar um resultado padronizado**.

#### Estrutura conceitual: `ApplicationResult`

Campos mínimos:

* `aggregate_id`
* `changed` (bool)
* `events` (lista de DomainEvent)
* `new_state` (opcional)

> A camada de Application **não retorna o aggregate inteiro**.

---

## 6. Fluxo Interno do Application Service

Todo `execute` segue **exatamente esta sequência**:

1. **Load**

   * Buscar aggregate via repository
   * Se não existir → erro de Application

2. **Snapshot**

   * Capturar estado mínimo antes da operação

3. **Execute Domain Command**

   * Chamar método do aggregate
   * Propagar exceções de domínio

4. **Detect Change**

   * Verificar se houve mudança real de estado

5. **Persist**

   * Persistir **somente se houve mudança**

6. **Pull Events**

   * Extrair e limpar Domain Events

7. **Return Result**

   * Retornar `ApplicationResult`

---

## 7. Repositório (Port) — Contrato

### 7.1 Métodos mínimos

* `get_by_id(id)`
* `save(aggregate)`

### 7.2 Regras

* `get_by_id` retorna `None` se não existir
* `save` persiste o estado atual
* Concorrência/versionamento:

  * decisão documentada
  * implementação futura

---

## 8. Testes da Camada de Application

### 8.1 Objetivo dos testes

* Provar o **contrato do caso de uso**
* Verificar:

  * persistência correta
  * idempotência
  * propagação de erros
  * extração de eventos

### 8.2 O que usar

* Repositório in-memory
* Domain real
* Sem mocks de domínio

### 8.3 Casos mínimos por service

1. Caminho feliz
2. Aggregate não encontrado
3. Domínio bloqueia operação
4. Persistência ocorre somente quando há mudança
5. Eventos são extraídos corretamente

---

## 9. Evolução Planejada

### 9.1 Próximos Application Services

* `CancelEnrollmentService`
* `SuspendEnrollmentService`

### 9.2 Integração futura

* DRF chamará Application Service
* Infra implementará ports
* Domain permanece isolado

---

## 10. Princípios Fundamentais

* **Domínio é a autoridade**
* **Application coordena**
* **Infra executa**
* **Testes são contrato**
* **Eventos comunicam fatos**

---

## 11. Critério de Qualidade

Uma implementação da camada de Application é considerada correta se:

* nenhuma regra de negócio está fora do domínio
* todos os casos de uso seguem o mesmo padrão
* testes de aplicação passam sem mocks frágeis
* mudanças no domínio quebram testes de aplicação (quando esperado)

---

