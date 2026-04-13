# Catalogo de Read Models para Reporting

## Objetivo
Listar as estruturas de leitura que podem sustentar relatorios, boletins e dashboards sem sobrecarregar os modelos transacionais.

## Read Models Sugeridos

### `student_dashboard_view`
Suporta:
- painel do estudante
- resumo de desempenho por disciplina
- resumo de frequencia por periodo

### `attendance_report_view`
Suporta:
- relatorio de frequencia por estudante/turma/disciplina
- identificacao de estudantes abaixo do limite

### `lesson_registry_report_view`
Suporta:
- relatorio de aulas registradas
- pendencias de diario e frequencia

### `performance_by_subject_view`
Suporta:
- relatorio de desempenho por disciplina
- comparativos por periodo

### `official_report_card_view`
Suporta:
- emissao de boletim oficial
- consulta de boletim consolidado

## Campos Minimos por Read Model
- nome
- fontes transacionais
- granularidade
- filtros suportados
- status de freshness
- se sustenta dado parcial ou oficial
