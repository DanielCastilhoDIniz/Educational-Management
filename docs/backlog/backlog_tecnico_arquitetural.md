# Backlog Tecnico Arquitetural

## Objetivo
Consolidar num unico lugar os itens tecnicos e arquiteturais que hoje estao espalhados por ADRs, use cases, politicas e checklists.

## Como Ler
Cada item deve evoluir com:
- prioridade
- contexto
- dependencias
- criterio de pronto

## Itens Prioritarios

### 1. Auth e Membership Multi-Tenant
Prioridade: muito alta
Contexto: identidade e acesso
Criterio de pronto:
- tenant resolvido na borda
- membership institucional definido
- papel e escopo documentados

### 2. Contrato de Criacao de Matricula
Prioridade: muito alta
Contexto: matriculas
Criterio de pronto:
- caso de uso documentado
- contrato de persistencia definido
- testes previstos

### 3. Taxonomia de Erros End-to-End
Prioridade: alta
Contexto: application/interface
Criterio de pronto:
- `ErrorCodes` mapeados
- persistencia conhecida traduzida
- HTTP preparado para o contrato

### 4. API HTTP Fase 1
Prioridade: alta
Contexto: interface
Criterio de pronto:
- rotas de enrollment definidas
- payload de erro padrao definido
- presenter HTTP central definido

### 5. Read Models de Reporting
Prioridade: alta
Contexto: reporting
Criterio de pronto:
- catalogo de read models definido
- freshness documentada
- filtros principais documentados

### 6. Outbox e Eventos de Integracao
Prioridade: media/alta
Contexto: infra/operacao
Criterio de pronto:
- eventos catalogados
- envelope definido
- estrategia de entrega documentada

### 7. Exportacoes Assincronas
Prioridade: media
Contexto: reporting
Criterio de pronto:
- formato e limites definidos
- jobs assincromos previstos
- auditoria de exportacao prevista

### 8. Dashboard do Estudante
Prioridade: media
Contexto: reporting/product
Criterio de pronto:
- metricas definidas
- visibilidade documentada
- contrato HTTP previsto

### 9. Observabilidade Operacional
Prioridade: media
Contexto: operacao
Criterio de pronto:
- logs estruturados definidos
- erros e metricas principais listados
- runbooks iniciais revisados

### 10. Rastreabilidade Documento x Teste
Prioridade: media
Contexto: qualidade
Criterio de pronto:
- matriz inicial preenchida
- contratos principais ligados a testes

## Recomendacao
Esse backlog deve virar ponte entre documentacao e planejamento real de sprint/roadmap tecnico.
