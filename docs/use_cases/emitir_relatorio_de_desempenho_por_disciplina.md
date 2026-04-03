# Caso de Uso - Emitir Relatorio de Desempenho por Disciplina

## Objetivo
Gerar um relatorio analitico do desempenho dos estudantes por disciplina, incluindo notas, medias e situacoes de risco.

## Atores
- coordenacao
- secretaria
- professor, quando permitido
- sistema

## Entrada Conceitual
- filtros por periodo, turma, disciplina e estudante
- criterio de ordenacao
- formato de saida
- `actor_id`

## Pre-condicoes
- ator autorizado
- regime avaliativo resolvido para o recorte

## Fluxo Principal
1. Validar autorizacao.
2. Carregar notas e medias no recorte selecionado.
3. Aplicar agrupamentos por disciplina ou estudante.
4. Identificar situacoes abaixo da media ou pendencias.
5. Retornar relatorio filtrado e exportavel.
