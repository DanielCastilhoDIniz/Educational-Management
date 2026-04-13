# Arquitetura Alvo por Contexto

## Objetivo
Conectar a visão arquitetural do SaaS aos contextos de negocio, deixando claro o que cada contexto deve conter para sair da documentação e virar implementação coordenada.

## Estrutura de Leitura Recomendada por Contexto
Para cada contexto responder:
- qual problema de negocio ele resolve
- qual aggregate ou raiz principal existe ou existira
- quais comandos principais existem
- quais queries principais existem
- quais politicas externas consulta
- quais ports precisa
- quais adapters de infra precisa
- quais eventos pode publicar
- quais read models pode exigir

## Contexto: Identidade e Acesso

### Objetivo
Resolver autenticacao, usuario global, membership institucional, papeis e escopos.

### Nucleo esperado
- `User`
- `Membership`
- `Role` (System Roles e Custom Roles)
- regras de papel e escopo

### Comandos
- cadastrar usuario
- vincular usuario a instituicao
- alterar papel/escopo
- desativar membership

### Queries
- obter contexto do ator autenticado
- listar memberships do usuario

### Adapters esperados
- auth provider
- repositorio de usuarios/memberships
- adapter HTTP auth

## Contexto: Cadastro Academico

### Objetivo
Manter dados mestres escolares.

### Nucleo esperado
- estudante
- responsavel
- professor
- disciplina
- ano letivo
- periodo
- turma
- atribuicao docente

### Comandos
- cadastrar estudante
- cadastrar responsavel
- cadastrar professor
- criar ano letivo e periodos
- criar turma
- associar professor a disciplina e turma

### Queries
- consulta de estudante, turma, disciplina, atribuicoes

### Adapters esperados
- repositorios cadastrais
- policies institucionais
- queries de consulta administrativa

## Contexto: Matriculas

### Objetivo
Controlar o vinculo academico do estudante e seu ciclo de vida.

### Nucleo esperado
- aggregate `Enrollment`

### Comandos
- criar matricula
- suspender
- reativar
- cancelar
- concluir

### Queries
- consultar matricula por id
- listar historico da matricula

### Politicas
- criacao
- conclusao
- justificativa
- timestamps

### Adapters esperados
- repositorio de enrollment
- API HTTP fase 1
- publisher/outbox futuro

## Contexto: Diario de Classe

### Objetivo
Registrar aulas ministradas e frequencia.

### Nucleo esperado
- aula registrada
- frequencia por aula e estudante/matricula

### Comandos
- registrar aula
- lancar frequencia
- retificar frequencia

### Queries
- aulas registradas
- pendencias de diario
- relatorio de frequencia

### Politicas
- frequencia
- janela de lancamento
- retificacao

## Contexto: Avaliacao e Boletim

### Objetivo
Registrar avaliacoes, notas, medias e consolidacao por periodo.

### Nucleo esperado
- avaliacao
- nota
- consolidado de periodo

### Comandos
- lancar avaliacao e notas
- fechar periodo
- emitir boletim oficial

### Queries
- consultar boletim
- relatorio de desempenho por disciplina

### Politicas
- regime avaliativo
- formula de media
- emissao oficial

## Contexto: Reporting e Painel do Estudante

### Objetivo
Entregar visoes de leitura, relatorios e dashboards.

### Nucleo esperado
- read models
- contratos de query
- metricas documentadas

### Queries
- relatorio de frequencia
- relatorio de aulas registradas
- relatorio de desempenho
- painel do estudante

### Politicas
- filtros
- visibilidade
- status parcial/oficial
- exportacao

## Contexto: Auditoria e Operacao

### Objetivo
Sustentar suporte, rastreabilidade e operacao segura.

### Nucleo esperado
- logs estruturados
- eventos catalogados
- runbooks
- rastreabilidade documento x teste

### Saidas
- trilha de auditoria
- diagnostico de incidente
- suporte a compliance

## Recomendacao Final
Todo contexto que entrar em implementacao deve preencher pelo menos uma versao minima desta estrutura antes de ganhar codigo significativo.
