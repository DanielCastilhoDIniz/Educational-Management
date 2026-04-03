# Caso de Uso - Emitir Relatorio de Frequencia

## Objetivo
Gerar uma visao filtravel e exportavel da frequencia de estudantes por turma, disciplina, periodo ou intervalo de datas.

## Atores
- secretaria
- coordenacao
- professor, dentro de seu escopo
- sistema

## Entrada Conceitual
- filtros institucionais e academicos
- filtro de intervalo de datas
- criterio de ordenacao
- formato de saida
- `actor_id`

## Pre-condicoes
- ator autorizado
- filtros validos
- escopo academico existente

## Fluxo Principal
1. Validar autorizacao e filtros.
2. Resolver o escopo do relatorio.
3. Carregar dados de frequencia consolidados ou parciais.
4. Aplicar agregacoes e ordenacao.
5. Retornar relatorio em tela ou formato exportavel.

## Saidas Esperadas
- percentual de frequencia
- total de faltas
- recorte por disciplina/turma/periodo
- identificacao de dado parcial ou oficial
