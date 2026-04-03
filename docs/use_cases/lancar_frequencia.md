# Caso de Uso - Lancar Frequencia

## Objetivo
Registrar a frequencia dos estudantes para uma aula especifica.

## Atores
- professor
- coordenacao, em fluxo de retificacao autorizado

## Entrada Conceitual
- `lesson_id`
- lista de presencas/ausencias por estudante ou matricula
- observacoes opcionais

## Pre-condicoes
- aula existe
- ator autorizado
- estudantes pertencem a turma/aula
- janela de lancamento ainda esta aberta ou ha permissao de retificacao

## Fluxo Principal
1. Validar autorizacao.
2. Carregar aula e lista de matriculas elegiveis.
3. Registrar frequencia por estudante.
4. Registrar auditoria.
5. Retornar resumo do lancamento.
