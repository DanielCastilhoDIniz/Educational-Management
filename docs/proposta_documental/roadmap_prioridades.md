# Roadmap de Prioridades da Documentacao

## Objetivo
Sequenciar a adocao da documentacao proposta em ondas pequenas, reduzindo risco e retrabalho tanto no modulo de matricula quanto no SaaS escolar como um todo.

## Fase 1 - Fundacao SaaS
Prioridade muito alta porque sustenta todo o restante.

- validar visao de produto SaaS
- validar mapa de bounded contexts
- validar ADR 019 sobre multi-tenancy
- validar ADR 020 sobre identidade e membership institucional
- validar politica de isolamento institucional
- validar politica de papeis e permissoes

## Fase 2 - Fundacao Academica
Prioridade alta porque estrutura os dados mestres do produto.

- validar ADR 021 sobre ano letivo, periodos, turmas e disciplinas
- validar ADR 024 sobre estudantes, responsaveis e contatos
- validar casos de uso de cadastro institucional e academico
- validar politicas de ano letivo, turmas e contatos

## Fase 3 - Matricula e Ciclo de Vida
Prioridade alta porque consolida o contexto ja mais maduro do projeto.

- validar ADR 012 sobre criacao de matricula
- validar ADR 013 sobre taxonomia de erros
- validar ADR 014 sobre matriz de estados e timestamps
- validar casos de uso de matricula
- validar politicas de criacao, conclusao, suspensao, reativacao e cancelamento

## Fase 4 - Diario, Frequencia e Avaliacao
Prioridade alta porque representa a operacao escolar recorrente.

- validar ADR 022 sobre diario e frequencia
- validar ADR 023 sobre avaliacoes, notas e fechamento
- validar casos de uso de registrar aula, lancar frequencia e lancar notas
- validar politicas de frequencia, vinculo professor-disciplina-turma e regime avaliativo

## Fase 5 - Reporting, Boletins e Painel do Estudante
Prioridade media/alta porque transforma operacao em visibilidade gerencial e experiencia de usuario.

- validar ADR 025 sobre registros e saidas oficiais
- validar ADR 026 sobre read models e contratos de consulta
- validar ADR 027 sobre filtros, paginacao e exportacao
- validar ADR 028 sobre painel do estudante e agregacao de metricas
- validar catalogo de relatorios, matriz de filtros e dicionario de metricas
- validar casos de uso de emitir relatorios, emitir boletim oficial e consultar painel do estudante
- validar politicas de relatorios, emissao de boletim e visibilidade do painel

## Fase 6 - Camada API HTTP
Prioridade media/alta porque transforma os contratos internos em superficie de integracao externa ou remota.

- validar ADR 029 sobre estrategia de entrega da API
- validar guia da camada API HTTP
- validar autenticacao, membership e tenant context na borda
- validar rotas fase 1 de enrollment
- validar rotas fase 2 de queries, reporting e dashboard
- validar payload de erro, presenters e versionamento
- adotar checklist da camada API

## Fase 7 - Operacao, Eventos e Qualidade
Prioridade media porque sustenta confiabilidade em escala.

- validar ADR 015 sobre atores e auditoria
- validar ADR 016 sobre eventos e outbox
- validar ADR 017 sobre estrategia de testes
- validar ADR 018 sobre observabilidade e suporte operacional
- adotar checklists de PR, CI, seguranca, release e API

## Fase 8 - Consolidar e Promover
Transformar o pacote proposto em trilha oficial.

- promover documentos aprovados para `docs/adr`, `docs/use_cases` e areas definitivas
- consolidar redundancias com ADRs existentes
- remover documentos rejeitados ou absorvidos
- atualizar README principal com os contratos aprovados

## Criterios de Sucesso
- cada contexto principal possui dono conceitual e documentacao minima
- casos de uso centrais do SaaS possuem contrato documentado
- politicas institucionais chave estao explicitadas
- multi-tenancy e autorizacao deixam de ser suposicoes implicitas
- relatorios e dashboards passam a ter contrato tao claro quanto os fluxos transacionais
- a API nasce coerente com Application, tenancy e ErrorCodes
- o modulo de matricula se encaixa naturalmente no restante do produto
- checklists passam a ser usados em PRs, CI e releases
