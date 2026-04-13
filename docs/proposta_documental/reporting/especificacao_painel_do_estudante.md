# Especificacao do Painel do Estudante

## Objetivo
Descrever uma tela/painel para o estudante acompanhar seu desempenho academico e situacao escolar ao longo do ano letivo.

## Publico-Alvo
- estudante autenticado
- responsavel, quando a politica de visibilidade permitir

## Blocos Principais do Painel

### Visao Geral
- nome do estudante
- turma atual
- periodo selecionado
- resumo de frequencia acumulada
- resumo de media global, se fizer sentido institucional

### Desempenho por Disciplina
- disciplina
- media atual
- ultima nota lancada
- situacao atual em relacao a meta/media
- tendencia do desempenho no periodo

### Frequencia
- percentual por disciplina
- total de faltas no periodo
- alertas de risco por baixa frequencia
- recorte por intervalo de datas

### Atividade Academica Recente
- ultimas aulas registradas
- ultimas avaliacoes com nota publicada
- pendencias ou proximas entregas, se o produto suportar

## Filtros Sugeridos
- ano letivo
- periodo
- disciplina
- intervalo de datas

## Regras de Visibilidade
- estudante ve apenas seus dados
- responsavel ve apenas estudantes vinculados
- dados oficiais e parciais devem ser identificados claramente
- metricas derivadas de periodo fechado devem indicar data de consolidacao

## Requisitos Nao Funcionais
- carregamento rapido para filtros comuns
- contratos de consulta read-only
- exportacao opcional dos dados visiveis, se permitido
- trilha de auditoria para acessos sensiveis, quando necessario
