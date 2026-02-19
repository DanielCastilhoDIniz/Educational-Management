
# 📘 DDD_GUIDE.md
## Domain-Driven Design — Guia Prático para Consulta e Aplicação

Este documento resume os **conceitos essenciais de Domain-Driven Design (DDD)** e descreve **um fluxo prático de aplicação**, voltado para projetos backend reais (como APIs com Django/DRF).

O foco é **entender quando e por que usar cada conceito**, não apenas o “o que”.

---

## 1. O que é DDD (em uma frase)

**Domain-Driven Design é uma abordagem de desenvolvimento de software que coloca o domínio do negócio no centro do sistema, tratando código como uma expressão explícita das regras e conceitos do negócio.**

DDD não é:
- framework
- arquitetura fechada
- padrão obrigatório

DDD é:
- **uma forma de pensar**
- **uma disciplina de modelagem**
- **uma linguagem compartilhada entre código e negócio**

---

## 2. Princípios Fundamentais do DDD

### 2.1 O Domínio vem antes da Tecnologia
- Banco de dados, API, filas e frameworks são **detalhes**
- Regras de negócio são **a essência**

> Se a regra muda, o código deve mudar facilmente.

---

### 2.2 Linguagem Ubíqua
- O mesmo termo deve significar a mesma coisa:
  - no código
  - na documentação
  - nas conversas

Exemplo:
- “Matrícula” não é aluno, nem turma
- “Conclusão” é um estado final, irreversível

📌 **Se o nome é confuso, o modelo está errado.**

---

### 2.3 Modelagem Explícita
DDD prefere:
- regras claras
- estados explícitos
- transições controladas

em vez de:
- flags soltas
- ifs espalhados
- regras implícitas

---

## 3. Blocos Fundamentais do DDD

### 3.1 Entidade
Objeto que:
- possui **identidade**
- muda ao longo do tempo
- é distinguível mesmo com atributos iguais

Exemplo:
- `Enrollment` (Matrícula)

📌 Identidade importa mais que atributos.

---

### 3.2 Value Object
Objeto que:
- **não tem identidade**
- é definido apenas por seus valores
- é imutável

Exemplos:
- `EnrollmentState`
- `StateTransition`
- `ConclusionVerdict`

📌 Se dois objetos com os mesmos valores são indistinguíveis → Value Object.

---

### 3.3 Aggregate
Conjunto de entidades e value objects que:
- mantém **invariantes consistentes**
- é modificado como uma **unidade**
- tem um único ponto de entrada

Exemplo:
- Aggregate: `Enrollment`
- Dentro dele:
  - estado
  - transições
  - regras de conclusão, cancelamento, suspensão

📌 **Fora do aggregate não se mexe no estado interno.**

---

### 3.4 Aggregate Root
É a entidade principal do aggregate.

Responsabilidades:
- proteger invariantes
- expor comportamentos válidos
- emitir eventos de domínio

Exemplo:
- `Enrollment` é o Aggregate Root

---

### 3.5 Domain Event
Representa **um fato que já aconteceu** no domínio.

Características:
- imutável
- não executa lógica
- apenas comunica

Exemplos:
- `EnrollmentConcluded`
- `EnrollmentCancelled`

📌 Evento não pergunta “posso?”, ele afirma “aconteceu”.

---

### 3.6 Erros de Domínio
Representam **violações de regras do negócio**, não falhas técnicas.

Exemplos:
- `EnrollmentNotActiveError`
- `InvalidStateTransitionError`

📌 Erros de domínio **fazem parte do modelo**, não são exceções genéricas.

---

## 4. O que NÃO é DDD (erros comuns)

❌ CRUD-centric design
❌ Entidades anêmicas
❌ Regras espalhadas em views/serializers
❌ Validar tudo só no banco
❌ Confundir autorização com regra de negócio

---

## 5. Separação de Camadas (Visão Prática)

### 5.1 Camada de Domínio
Contém:
- entidades
- value objects
- aggregates
- eventos
- erros de domínio

Não contém:
- Django
- DRF
- ORM
- HTTP
- serializers

---

### 5.2 Camada de Aplicação
Responsável por:
- orquestrar casos de uso
- chamar métodos do domínio
- persistir aggregates
- publicar eventos

Exemplo:
- `ConcludeEnrollmentService`

---

### 5.3 Infraestrutura
Responsável por:
- banco de dados
- ORM
- filas
- APIs
- frameworks

📌 Infraestrutura **serve o domínio**, não o contrário.

---

## 6. Fluxo Prático de Aplicação do DDD (Passo a Passo)

### Passo 1 — Entender o Domínio
- Converse (ou simule conversas)
- Identifique regras reais
- Escreva em linguagem natural

📄 Resultado: rascunho do `DOMAIN_RULES.md`

---

### Passo 2 — Definir Linguagem Ubíqua
- Nomeie conceitos
- Elimine ambiguidades
- Trave os significados

📄 Resultado: seção de glossário

---

### Passo 3 — Identificar Aggregates
Pergunte:
- Onde as regras precisam ser consistentes?
- O que muda junto?

📌 No seu caso:
- Matrícula é o centro das regras → Aggregate Root

---

### Passo 4 — Definir Estados e Invariantes
- Estados possíveis
- Estados finais
- O que nunca pode acontecer

📄 Resultado: enum + invariantes documentadas

---

### Passo 5 — Criar Comportamentos (não setters)
- `conclude()`
- `cancel()`
- `suspend()`

Cada método:
- valida regras
- muda estado
- registra transição
- emite evento

---

### Passo 6 — Modelar Eventos de Domínio
Para cada fato relevante:
- crie um evento
- valide consistência estrutural
- não coloque lógica nele

---

### Passo 7 — Criar Erros de Domínio
Para cada regra violada:
- crie um erro semântico
- evite `ValueError`, `Exception` genérica

---

### Passo 8 — Orquestrar na Application Layer
- carregar aggregate
- chamar método
- salvar
- publicar eventos

---

### Passo 9 — Testar pelo Domínio
- testar sem banco
- testar transições
- testar erros

📌 Se o domínio estiver correto, o resto fica fácil.

---

## 7. Checklist Mental (para o dia a dia)

Antes de escrever código, pergunte:
- Isso é regra de negócio?
- Isso muda o estado do domínio?
- Quem é o Aggregate Root?
- Esse erro é técnico ou de domínio?
- Esse evento representa um fato real?

---

## 8. Conclusão

DDD não é sobre complexidade.
É sobre **clareza, intenção e sustentabilidade**.

Você não aplica DDD “por completo” de uma vez.
Você **evolui o modelo conforme aprende o domínio**.

> Um bom modelo hoje é melhor que um modelo perfeito nunca entregue.

---

## 9. Referência Interna
Este guia é complementar ao:
- `DOMAIN_RULES.md`
- modelagem do Aggregate `Enrollment`
- eventos e erros de domínio do projeto

```

---





