# Caso de Uso - Emitir Relatorio de Aulas Registradas

## Objetivo
Gerar uma visao das aulas registradas por professor, disciplina, turma e periodo, incluindo pendencias de diario.

## Atores
- coordenacao
- secretaria
- professor, dentro de seu escopo
- sistema

## Entrada Conceitual
- filtros por professor, turma, disciplina, periodo e datas
- criterio de ordenacao
- formato de saida
- `actor_id`

## Pre-condicoes
- ator autorizado
- filtros validos

## Fluxo Principal
1. Validar autorizacao.
2. Carregar aulas no escopo filtrado.
3. Enriquecer com status de diario e frequencia, quando aplicavel.
4. Aplicar ordenacao e agrupamentos.
5. Retornar relatorio.
