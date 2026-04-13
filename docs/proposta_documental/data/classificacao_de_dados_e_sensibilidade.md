# Classificacao de Dados e Sensibilidade

## Objetivo
Classificar dados do produto por sensibilidade, visibilidade e exigencia de auditoria.

## Classes Sugeridas

### Publico Institucional
Exemplos:
- nome da instituicao
- catalogo de disciplinas sem dados pessoais

### Interno Operacional
Exemplos:
- identificador de turma
- calendario academico
- status de diario

### Pessoal
Exemplos:
- nome do estudante
- nome do responsavel
- contato de professor

### Sensivel Operacional
Exemplos:
- frequencia individual
- notas individuais
- boletim
- historico escolar
- justificativas de cancelamento/suspensao quando exponham situacao sensivel

## Campos Relevantes por Tipo
- dado
- classificacao
- quem pode ver
- quem pode exportar
- se exige auditoria de acesso
- prazo de retencao

## Recomendacao
Logs e exportacoes nao devem vazar dados pessoais ou sensiveis sem necessidade explicita e autorizacao adequada.
