# Politica - Elegibilidade para Conclusao

## Objetivo
Definir se a matricula pode ser concluida com base em criterios externos ao aggregate.

## Escopo
Consumida pela Application para produzir um verdict de conclusao.

## Entradas Sugeridas
- `enrollment_id`
- desempenho academico consolidado
- bloqueios administrativos
- status do periodo letivo
- eventuais regras institucionais congeladas por periodo

## Saida Sugerida
Um `verdict` com:
- `is_allowed`
- `reasons`
- `requires_justification`

## Regras Sugeridas
- periodo deve estar encerrado, salvo excecao documentada
- nao pode haver bloqueio impeditivo de conclusao
- resultados academicos devem estar consolidados
- toda excecao institucional deve ser auditavel

## Testes Recomendados
- estudante elegivel
- estudante inelegivel por nota/frequencia
- bloqueio administrativo
- encerramento de periodo ausente
- conclusao excepcional com justificativa
