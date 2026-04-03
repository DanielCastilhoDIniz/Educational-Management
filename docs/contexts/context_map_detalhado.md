# Context Map Detalhado do SaaS Escolar

## Objetivo
Explicitar como os contextos principais se relacionam, dependem uns dos outros e compartilham contratos.

## Contextos e Relacoes

### Identidade e Acesso
Fornece:
- autenticacao
- usuario global
- membership institucional
- contexto de ator autenticado

Consumido por:
- todos os demais contextos

### Organizacao Institucional
Fornece:
- instituicao
- configuracoes institucionais
- parametros de tenant
- calendario academico basico

Consumido por:
- cadastro academico
- matriculas
- diario
- avaliacao
- reporting

### Cadastro Academico
Fornece:
- estudantes
- responsaveis
- professores
- disciplinas
- ano letivo
- periodos
- turmas
- atribuicoes docentes

Consumido por:
- matriculas
- diario
- avaliacao
- reporting

### Matriculas
Fornece:
- vinculo academico do estudante
- estado da matricula
- historico de transicoes

Consumido por:
- diario
- avaliacao
- boletim
- painel do estudante

### Diario de Classe
Fornece:
- aulas registradas
- frequencia
- status de diario

Consumido por:
- avaliacao e consolidacao
- relatorios de frequencia
- painel do estudante

### Avaliacao e Boletim
Fornece:
- avaliacoes
- notas
- medias
- consolidado por periodo
- insumos para boletim

Consumido por:
- boletim oficial
- painel do estudante
- relatorios gerenciais

### Reporting e Analytics
Consome de:
- diario
- avaliacao
- matriculas
- cadastro academico

Entrega:
- relatorios operacionais
- relatorios gerenciais
- boletins
- dashboards

### Auditoria e Operacao
Observa:
- todos os contextos

Entrega:
- trilha de auditoria
- suporte operacional
- logs e metricas

## Recomendacoes de Integracao
- comandos cruzando contextos devem ser orquestrados pela Application
- consultas de reporting podem usar read models dedicados
- eventos de dominio devem ser catalogados por contexto
- shared kernel deve ser minimo e explicitamente documentado
