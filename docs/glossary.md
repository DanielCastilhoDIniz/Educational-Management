
---

# 📘 Dicionário de Conceitos — Linguagem Ubíqua

## 🔹 Identificadores e rastreabilidade

### **`aggregate_id`**

* **Camada:** Application / Domain
* **Significado:** Identificador único do aggregate afetado pelo caso de uso.
* **Uso:** Rastreamento de eventos, logs e resultados.
* **Exemplo:** ID da matrícula (`Enrollment.id`).

---

### **`enrollment_id`**

* **Camada:** Application
* **Significado:** Identificador externo usado para localizar um aggregate `Enrollment`.
* **Uso:** Entrada de casos de uso (ex.: concluir matrícula).
* **Observação:** Após o load, vira `aggregate_id`.

---

### **`id: str`**

* **Camada:** Domain
* **Significado:** Identificador único interno de uma entidade ou aggregate.
* **Uso:** Identidade do objeto no domínio.
* **Exemplo:** `Enrollment.id`.

---

### **`actor_id: str`**

* **Camada:** Domain / Application
* **Significado:** Identificador de quem executou a ação.
* **Uso:** Auditoria, eventos de domínio, rastreabilidade.
* **Exemplo:** usuário, sistema, administrador.

---

## 🔹 Estado e transições

### **`state`**

* **Camada:** Domain
* **Significado:** Estado atual do aggregate.
* **Uso:** Base para validação de transições e invariantes.

---

### **`current_state`**

* **Camada:** Domain (erros/eventos)
* **Significado:** Estado em que o aggregate se encontra no momento da tentativa.
* **Uso:** Mensagens de erro e eventos.

---

### **`new_state`**

* **Camada:** Application
* **Significado:** Estado final após execução bem-sucedida de um caso de uso.
* **Uso:** Retorno padronizado para API/UI.
* **Observação:** Não expõe o aggregate completo.

---

### **`from_state`**

* **Camada:** Domain Event
* **Significado:** Estado anterior à transição.
* **Uso:** Eventos de domínio para histórico e auditoria.

---

### **`to_state`**

* **Camada:** Domain Event
* **Significado:** Estado resultante da transição.
* **Uso:** Consistência e validação de eventos.

---

### **Estados possíveis (`EnrollmentState`)**

* **`ACTIVE = 'active'`**
  Matrícula válida e em andamento.
* **`SUSPENDED = 'suspended'`**
  Matrícula temporariamente interrompida.
* **`CONCLUDED = 'concluded'`**
  Matrícula finalizada com sucesso (estado final).
* **`CANCELLED = 'cancelled'`**
  Matrícula encerrada antes da conclusão (estado final).

---

## 🔹 Temporalidade

### **`created_at: datetime`**

* **Camada:** Domain
* **Significado:** Momento de criação do aggregate.
* **Uso:** Auditoria e histórico.

---

### **`occurred_at`**

* **Camada:** Domain / Event
* **Significado:** Momento exato em que a ação ocorreu no mundo real.
* **Uso:** Eventos de domínio, replay, integrações.
* **Regra:** Preferencialmente UTC.

---

### **`concluded_at`**

* **Camada:** Domain
* **Significado:** Timestamp da conclusão da matrícula.
* **Invariante:** Obrigatório se `state == CONCLUDED`.

---

### **`cancelled_at`**

* **Camada:** Domain
* **Significado:** Timestamp do cancelamento.
* **Invariante:** Obrigatório se `state == CANCELLED`.

---

### **`suspended_at`**

* **Camada:** Domain
* **Significado:** Timestamp da suspensão.
* **Invariante:** Obrigatório se `state == SUSPENDED`.

---

## 🔹 Regras, decisões e validações

### **`changed`**

* **Camada:** Application
* **Significado:** Indica se o aggregate sofreu mudança real.
* **Uso:** Idempotência, persistência condicional, publicação de eventos.

---

### **`events`**

* **Camada:** Domain → Application
* **Significado:** Lista de fatos imutáveis ocorridos durante o caso de uso.
* **Uso:** Publicação, logging, integrações.
* **Regra:** Se `changed == False`, deve ser vazio.

---

### **`transitions`**

* **Camada:** Domain
* **Significado:** Conjunto de mudanças de estado permitidas.
* **Uso:** Validação de regras de negócio.

---

### **`is_allowed`**

* **Camada:** Domain (Value Object)
* **Significado:** Indica se uma ação é permitida segundo política de negócio.
* **Uso:** Decisões como `verdict`.

---

### **`reasons`**

* **Camada:** Domain (Value Object)
* **Significado:** Justificativas ou fundamentos de uma decisão.
* **Uso:** Auditoria e explicabilidade.

---

### **`requires_justification`**

* **Camada:** Domain (Value Object)
* **Significado:** Indica se uma ação exige justificativa explícita.
* **Uso:** Validação antes de transições sensíveis.

---

### **`justification`**

* **Camada:** Domain
* **Significado:** Texto explicando o motivo da ação.
* **Uso:** Obrigatório quando `requires_justification == True`.

---

## 🔹 Estrutura do Aggregate Enrollment

### **`student_id`**

* **Camada:** Domain
* **Significado:** Identificador do aluno vinculado à matrícula.

---

### **`class_group_id`**

* **Camada:** Domain
* **Significado:** Identificador da turma à qual a matrícula pertence.

---

### **`academic_period_id`**

* **Camada:** Domain
* **Significado:** Identificador do período letivo (ano/semestre).

---

## 🔹 Erros e contratos de erro

### **`code`**

* **Camada:** Domain Error
* **Significado:** Identificador estável do erro.
* **Uso:** Tradução, logging, testes.

---

### **`message`**

* **Camada:** Domain/Application Error
* **Significado:** Descrição humana do erro.
* **Uso:** Logs, API, debugging.

---

### **`details`**

* **Camada:** Domain Error
* **Significado:** Dados estruturados adicionais sobre o erro.
* **Uso:** Diagnóstico e explicação.

---

### **`required_state`**

* **Camada:** Domain Error
* **Significado:** Estado necessário para executar uma ação.
* **Uso:** Erros de transição inválida.

---

### **`attempted_action`**

* **Camada:** Domain Error
* **Significado:** Ação que o usuário tentou executar.
* **Uso:** Mensagens claras e auditoria.

---

### **`allowed_from_states`**

* **Camada:** Domain Error
* **Significado:** Estados a partir dos quais a ação é permitida.
* **Uso:** Explicação de falhas de regra.

---

### **`forbidden_reason`**

* **Camada:** Domain Error / Policy
* **Significado:** Motivo pelo qual a ação foi bloqueada.
* **Uso:** Transparência e justificativa do sistema.

---

## 🔹 Utilidades técnicas

### **`default_factory`**

* **Camada:** Técnica (dataclasses)
* **Significado:** Função usada para criar valores padrão mutáveis.
* **Uso:** Evitar estado compartilhado (ex.: listas).

---

## 🎯 Observação final (importante)

Este dicionário **não é só documentação**. Ele é:

* referência para testes
* base para API
* linguagem comum entre domínio, aplicação e infra
* material excelente para explicar o projeto em entrevista técnica

