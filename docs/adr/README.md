# Indice de ADRs

Este diretorio concentra os Architecture Decision Records do projeto.
Os arquivos estao organizados por tema e contexto para melhorar navegacao,
leitura incremental e manutencao das referencias cruzadas.

## Status Geral

| Status | Quantidade |
| --- | ---: |
| `Aprovado` | 13 |
| `Proposto` | 21 |
| `Implementado` | 1 |
| `Sem secao padrao de status` | 1 |

Observacao:
- o `ADR 009` ainda nao segue o template atual e precisa ter o campo `## Status` normalizado
- o template oficial de ADR fica em `docs/adr/templates/adr-template.md`

## Ordem Recomendada de Leitura

1. Fundacoes de modelagem e arquitetura
2. Contexto de matriculas (`Enrollment`)
3. Plataforma, API e concerns transversais
4. Identidade e acesso
5. Estrutura academica, reporting e expansao do dominio

## Indice Tematico

### 00 - Fundacoes

- [ADR 001 - Linguagem Ubiqua em PT-BR e Mapeamento Tecnico de Estados](00-foundations/001-Ubiquitous-languagePTbr.md) - `Aprovado`
- [ADR 003 - Eventos de Dominio via Acumulo no Aggregate e Extracao (Pull)](00-foundations/003-Domain-eventes.md) - `Aprovado`
- [ADR 004 - Camada de Dominio como Nucleo Puro do Sistema](00-foundations/004-domain-layer-core.md) - `Aprovado`
- [ADR 005 - Camada de Application como Orquestradora de Casos de Uso](00-foundations/005-application-layer-use-case-orchestration.md) - `Aprovado`
- [ADR 006 - Politicas Institucionais Configuraveis com Resolucao por Escopo e Congelamento por Periodo](00-foundations/006-Politicas.md) - `Aprovado`
- [ADR 013 - Taxonomia de Erros e Mapeamento entre Camadas](00-foundations/013-error-taxonomy-and-failure-mapping.md) - `Proposto`
- [ADR 017 - Estrategia de Testes e Gates de Qualidade](00-foundations/017-testing-strategy-and-quality-gates.md) - `Proposto`

### 10 - Enrollment

- [ADR 002 - Fronteira do Aggregate Matricula e Regras Dependentes de Contexto Externo](10-enrollment/002-Aggregate-Bondary-Enrollment.md) - `Aprovado`
- [ADR 008 - Persistencia do Aggregate Enrollment (Snapshot + Transition Log)](10-enrollment/008-enrollment-persistence.md) - `Aprovado`
- [ADR 009 - Contrato do metodo `save`](10-enrollment/009-contrato-save.md) - `Sem secao padrao de status`
- [ADR 010 - Deterministic Transition ID (UUIDv5)](10-enrollment/010-deterministic-transition-id.md) - `Aprovado`
- [ADR 012 - Contrato de Criacao de Enrollment](10-enrollment/012-create-enrollment-contract.md) - `Aprovado`
- [ADR 014 - Matriz de Estados e Timestamps do Ciclo de Vida da Matricula](10-enrollment/014-enrollment-state-matrix-and-lifecycle-timestamps.md) - `Proposto`

### 20 - Plataforma, API e Concerns Transversais

- [ADR 007 - Camada de Infrastructure como Implementadora de Ports e Efeitos Externos](20-platform-api/007-infrastructure-layer-adapters-persistence-publication.md) - `Aprovado`
- [ADR 011 - Camada de Interface HTTP como Tradutora Fina de Entrada e Saida](20-platform-api/011-interface-http-boundary.md) - `Aprovado`
- [ADR 016 - Entrega de Eventos de Dominio e Outbox](20-platform-api/016-domain-event-delivery-and-outbox.md) - `Proposto`
- [ADR 018 - Observabilidade, Auditoria e Suporte Operacional](20-platform-api/018-observability-audit-and-operational-support.md) - `Proposto`
- [ADR 019 - Multi-Tenancy e Isolamento por Instituicao](20-platform-api/019-multi-tenant-and-institution-isolation.md) - `Proposto`
- [ADR 029 - Estrategia de Entrega da API e Superficie HTTP](20-platform-api/029-api-delivery-strategy-and-http-surface.md) - `Proposto`

### 30 - Identidade e Acesso

- [ADR 015 - Autoridade do Ator e Responsabilidade de Auditoria](30-identity-access/015-actor-authority-and-audit-responsibility.md) - `Proposto`
- [ADR 020 - Identidade, Acesso e Membership Institucional](30-identity-access/020-identity-access-and-membership.md) - `Proposto`
- [ADR 031 - Design do Aggregate Membership](30-identity-access/031-membership-aggregate-design.md) - `Proposto`
- [ADR 032 - Design do Aggregate User](30-identity-access/032-user-aggregate-design.md) - `Implementado`
- [ADR 033 - Design do Aggregate Role](30-identity-access/033-role-aggregate-design.md) - `Proposto`
- [ADR 034 - Matriz Operacional de Autorizacao com Capabilities Explicitas](30-identity-access/034-operational-authorization-matrix-and-capabilities.md) - `Aprovado`
- [ADR 035 - Modelo de Extensibilidade de Papeis com Capabilities Configuráveis](30-identity-access/035-role-extensibility-with-configurable-capabilities.md) - `Proposto`

### 40 - Estrutura Academica, Reporting e Expansao do Produto

- [ADR 021 - Estrutura Academica: Ano Letivo, Periodos, Turmas e Disciplinas](40-academic-reporting/021-academic-structure-school-year-period-class-group-subject.md) - `Proposto`
- [ADR 022 - Diario de Classe, Aulas e Frequencia](40-academic-reporting/022-attendance-and-lesson-journal.md) - `Proposto`
- [ADR 023 - Avaliacoes, Notas, Medias e Fechamento de Periodo](40-academic-reporting/023-assessment-gradebook-and-period-closing.md) - `Proposto`
- [ADR 024 - Estudantes, Responsaveis e Dados de Contato](40-academic-reporting/024-student-guardian-and-contact-data.md) - `Proposto`
- [ADR 025 - Boletim, Historicos e Registros Oficiais](40-academic-reporting/025-reporting-and-official-records.md) - `Proposto`
- [ADR 026 - Reporting, Read Models e Contratos de Consulta](40-academic-reporting/026-reporting-read-models-and-query-contracts.md) - `Proposto`
- [ADR 027 - Filtros, Ordenacao, Paginacao e Exportacao em Relatorios](40-academic-reporting/027-report-filters-exports-and-pagination.md) - `Proposto`
- [ADR 028 - Painel do Estudante e Agregacao de Metricas Academicas](40-academic-reporting/028-student-dashboard-and-metric-aggregation.md) - `Proposto`
- [ADR 030 - Hierarquia Organizacional: Rede, Instituicao e Unidade Escolar](40-academic-reporting/030-organizational-hierarchy-network-institution-unit.md) - `Proposto`

## Estrutura Atual

A taxonomia atual dos ADRs e:

```text
docs/
\--- adr/
    +--- README.md
    +--- templates/
    |    \--- adr-template.md
    +--- 00-foundations/
    +--- 10-enrollment/
    +--- 20-platform-api/
    +--- 30-identity-access/
    \--- 40-academic-reporting/
```

## Regras de Manutencao

- manter numeracao global dos ADRs, mesmo que a estrutura de pastas mude
- evitar categorias puramente orientadas a stack quando a decisao for de dominio
- atualizar links cruzados antes de qualquer mudanca fisica de arquivo
- preferir nomes consistentes no formato `NNN-slug.md`
- normalizar todos os ADRs para o template oficial antes de novas reorganizacoes
