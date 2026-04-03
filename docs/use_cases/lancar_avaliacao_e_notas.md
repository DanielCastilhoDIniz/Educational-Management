# Caso de Uso - Lancar Avaliacao e Notas

## Objetivo
Criar uma avaliacao dentro do regime vigente e registrar notas dos estudantes.

## Atores
- professor
- coordenacao, quando aplicavel

## Entrada Conceitual
- `teacher_assignment_id`
- tipo/nome da avaliacao
- peso ou regra equivalente
- lista de notas por estudante

## Pre-condicoes
- atribuicao professor-disciplina-turma existe
- ator autorizado
- regime avaliativo do periodo permite a avaliacao
- janela de lancamento esta aberta ou ha permissao de retificacao

## Fluxo Principal
1. Validar autorizacao e regime avaliativo.
2. Criar avaliacao.
3. Registrar notas.
4. Registrar auditoria.
5. Retornar resumo do lancamento.
