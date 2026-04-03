# ADR 029 - Estrategia de Entrega da API e Superficie HTTP

## Status
Proposto

## Contexto
O projeto ja possui uma diretriz aprovada para a camada HTTP como tradutora fina, mas ainda falta uma estrategia operacional para colocar a API no ar em fases, sem desalinhar DDD, Application Layer e multi-tenancy.

## Decisao
Adotar uma entrega incremental da API HTTP com as seguintes regras:

1. A primeira API publica ou interna deve nascer sobre os casos de uso mais maduros do contexto `academic.enrollment`.
2. A camada HTTP continua sendo fina, sem regra de negocio, sem acesso direto a ORM quando houver caso de uso correspondente e sem recalculo de invariantes do dominio.
3. A autenticacao e o contexto de tenant devem ser resolvidos na borda e traduzidos para a Application.
4. Rotas de comando e rotas de consulta devem ser tratadas de forma diferente:
- comandos chamam services da Application
- consultas podem chamar queries/read models dedicados
5. Reporting, boletins e dashboard nao devem ser implementados como leitura improvisada dos aggregates transacionais se houver impacto relevante de performance ou consistencia.

## Fases Sugeridas

### Fase 1 - Enrollment API
- criar matricula
- consultar matricula
- suspender
- reativar
- cancelar
- concluir

### Fase 2 - Queries de leitura
- historico da matricula
- boletim
- painel do estudante

### Fase 3 - Reporting e exportacoes
- frequencia
- aulas registradas
- desempenho por disciplina
- exportacoes

## Consequencias

### Positivas
- reduz risco de abrir uma API grande demais cedo
- aproveita o contexto mais maduro do projeto
- preserva a separacao entre command side e query side

### Negativas / Riscos
- exige disciplina para nao pular direto para reporting pesado sem read models prontos
- exige padronizacao de autenticacao, membership e mapeamento de erros antes de ampliar a superficie HTTP

## Invariantes
- HTTP nao substitui a Application como orquestradora
- a API deve ser tenant-aware desde a primeira rota
- `ErrorCodes` continuam sendo a base do contrato de falha esperado
- a borda deve validar transporte, nao regra de negocio nuclear

## Plano de Implementacao
- definir guia da camada API
- definir autenticacao e contexto de tenant
- definir payload de erro padrao
- publicar rotas fase 1 de enrollment
- depois ampliar para queries e reporting
