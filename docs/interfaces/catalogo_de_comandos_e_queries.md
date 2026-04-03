# Catalogo de Comandos e Queries

## Objetivo
Mapear os principais comandos e consultas do produto para facilitar contrato de API, testes e observabilidade.

## Comandos Principais
- criar matricula
- suspender matricula
- reativar matricula
- cancelar matricula
- concluir matricula
- cadastrar estudante
- cadastrar responsavel
- cadastrar professor
- criar turma
- registrar aula
- lancar frequencia
- lancar avaliacao e notas
- fechar periodo
- emitir boletim oficial

## Queries Principais
- consultar matricula por id
- listar historico de matricula
- consultar boletim do estudante
- consultar painel do estudante
- emitir relatorio de frequencia
- emitir relatorio de aulas registradas
- emitir relatorio de desempenho por disciplina

## Campos Minimos por Item do Catalogo
- nome
- tipo (`command` ou `query`)
- contexto
- entrada conceitual
- resultado esperado
- erros esperados
- politicas consultadas
- eventos disparados, quando houver
