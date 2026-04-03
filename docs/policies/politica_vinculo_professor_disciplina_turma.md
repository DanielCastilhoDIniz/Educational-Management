# Politica - Vinculo Professor, Disciplina e Turma

## Objetivo
Definir como professores podem ser associados a ofertas academicas.

## Regras Sugeridas
- atribuicao deve respeitar tenant, ano, periodo e turma
- o mesmo professor pode ter multiplas atribuicoes
- a politica deve decidir se uma disciplina pode ter mais de um professor simultaneo
- substituicao de professor deve preservar auditoria e vigencia
- sem atribuicao valida nao ha diario nem lancamento de notas

## Testes Recomendados
- atribuicao valida
- atribuicao fora do tenant
- professor substituto com vigencia delimitada
- professor sem atribuicao tentando registrar aula
