# Catalogo Oficial de Politicas

## Objetivo
Consolidar em um unico documento o inventario de politicas configuraveis, operacionais e de visibilidade do produto.

## Campos Minimos por Politica
- chave
- descricao
- contexto
- escopo
- valor padrao
- se congela por periodo
- dono da politica
- casos de uso que consultam a politica

## Catalogo Inicial

### `enrollment.creation`
- contexto: matriculas
- escopo: instituicao/periodo
- congela por periodo: opcional
- dono: secretaria + administracao institucional
- casos de uso: criar matricula

### `enrollment.conclusion`
- contexto: matriculas
- escopo: instituicao/periodo
- congela por periodo: sim
- dono: coordenacao academica
- casos de uso: concluir matricula

### `attendance.rules`
- contexto: diario
- escopo: instituicao/periodo
- congela por periodo: sim
- dono: coordenacao academica
- casos de uso: lancar frequencia, relatorio de frequencia

### `grading.scheme`
- contexto: avaliacao
- escopo: instituicao/periodo/disciplina quando aplicavel
- congela por periodo: sim
- dono: coordenacao academica
- casos de uso: lancar notas, fechar periodo, boletim

### `student.dashboard.visibility`
- contexto: reporting
- escopo: instituicao
- congela por periodo: nao
- dono: administracao institucional
- casos de uso: consultar painel do estudante

### `reporting.export`
- contexto: reporting
- escopo: instituicao
- congela por periodo: nao
- dono: administracao institucional
- casos de uso: emitir relatorios e exportacoes

### `privacy.data_access`
- contexto: seguranca e dados
- escopo: instituicao/plataforma
- congela por periodo: nao
- dono: administracao institucional + compliance
- casos de uso: todos os que expoem dados sensiveis

## Recomendacao
Todo novo caso de uso relevante deve indicar explicitamente quais politicas consulta.
