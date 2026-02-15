
---

# 🎓 School Management SaaS — Backend

Sistema de Gestão Escolar construído com foco em **arquitetura de domínio, consistência transacional e engenharia de software orientada a longo prazo**.

O projeto aplica **Domain-Driven Design (DDD)** em um contexto real do setor educacional brasileiro (Ensino Fundamental II e Ensino Médio), modelando processos acadêmicos com rigor estrutural e preocupação com escalabilidade.

---

## 🚀 Objetivo

Desenvolver uma **API backend profissional, consistente e evolutiva**, cobrindo:

* Matrículas
* Estados acadêmicos (ativa, suspensa, cancelada, concluída)
* Transições controladas
* Auditoria imutável
* Eventos de domínio
* Regras institucionais explícitas

O foco do projeto não é apenas entregar funcionalidades, mas:

* preservar invariantes de negócio,
* garantir integridade transacional,
* manter separação clara entre camadas,
* documentar decisões arquiteturais.

Este projeto segue a filosofia:

> Construir aprendendo — mas com padrões de produção.

---

## 🧠 Arquitetura

### ✔ Domain-Driven Design (DDD)

O sistema é estruturado com separação rigorosa entre:

* **Domínio** (regras puras)
* **Aplicação** (orquestração de casos de uso)
* **Infraestrutura** (Django + Postgres)
* **Interfaces** (API REST — fase posterior)

Conceitos aplicados:

* Aggregate Roots (`Enrollment`)
* Entidades e Value Objects
* Eventos de Domínio imutáveis
* Controle explícito de transições de estado
* Controle otimista de concorrência
* Tradução de erros de infraestrutura

O domínio é totalmente independente de framework.

📄 Documentação de regras: `DOMAIN_RULES.md`
📄 Decisões de persistência: `docs/adr/001-enrollment-persistence.md`

---

## 🏛 Estratégia de Persistência

### Snapshot + Log Imutável

O aggregate `Enrollment` é persistido utilizando:

* **Tabela Snapshot (`Enrollment`)**
* **Tabela Append-Only (`EnrollmentTransition`)**

Características:

* Estado atual como fonte da verdade
* Histórico completo de transições
* Auditoria com `actor_id`
* `transition_id` único para deduplicação
* Controle otimista via campo `version`
* Transação única por comando

Essa abordagem garante:

* Consistência
* Idempotência
* Integridade sob concorrência
* Evolução futura sem reescrita estrutural

---

## 🛠 Stack Tecnológica

### Backend (fase atual)

* Python 3.12+
* Django
* PostgreSQL
* Pytest
* Estrutura modular inspirada em Clean Architecture

Infraestrutura planejada:

* Docker & Docker Compose
* Separação de ambientes (local / produção)
* Configuração via variáveis de ambiente

O domínio não depende do Django.

---

## 📁 Estrutura do Projeto

```text
src/
 ├── domain/
 │   └── academic/
 │       └── enrollment/
 │           ├── entities/
 │           ├── value_objects/
 │           ├── events/
 │           └── errors/
 │
 ├── application/
 │   └── academic/
 │       └── enrollment/
 │           ├── services/
 │           ├── ports/
 │           └── errors/
 │
 ├── infrastructure/
 │   └── django/
 │        ├── config/
 │        └── apps/
 │            └── academic/
 │                └── enrollment/
 │                    ├── models/
 │                    ├── mappers/
 │                    └── repositories/
 │
 │
 ├── tests/
 |
```

### Camadas

* `domain/` → regras puras e invariantes
* `application/` → casos de uso e orquestração
* `infrastructure/` → ORM, banco, adapters
* `interfaces/` → API REST (em breve)

---

## 🧪 Testes

O projeto prioriza testes estruturais:

* Testes de domínio (100% isolados de framework)
* Testes de transição de estado
* Testes de idempotência
* Testes de controle de concorrência
* Testes de integração com PostgreSQL

Objetivo:

> Quebrar uma regra de negócio deve obrigatoriamente quebrar um teste.

---

## 📌 Status

🚧 Em desenvolvimento ativo

Fluxo de desenvolvimento:

1. Modelagem do domínio
2. Documentação da regra
3. Implementação
4. Testes
5. Integração com infraestrutura

Sem atalhos.

---

## 🎯 Próximos Passos

* Finalizar Repository com controle otimista
* Testes de integração transacionais
* Exposição via Django REST Framework
* Dockerização
* Implementação de novos casos de uso

---

## 👨‍💻 Sobre

Desenvolvido por um backend developer em transição de carreira, com sólida base em:

* Física
* Modelagem matemática
* Lógica formal
* Estruturação de sistemas complexos

Este repositório representa um processo disciplinado de construção de software de qualidade, aplicando conceitos de arquitetura em um cenário real.

---

## 📬 Contato

GitHub:
[https://github.com/DanielCastilhoDIniz](https://github.com/DanielCastilhoDIniz)

LinkedIn:
[https://www.linkedin.com/in/daniel-castilho-diniz/](https://www.linkedin.com/in/daniel-castilho-diniz/)

---

## 📄 Licença

Projeto educacional e demonstrativo.

---


