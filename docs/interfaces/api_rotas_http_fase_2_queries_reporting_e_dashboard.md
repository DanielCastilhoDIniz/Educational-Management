# API - Rotas HTTP Fase 2 (Queries, Reporting e Dashboard)

## Objetivo
Definir a segunda onda da API, orientada a consultas e saidas analiticas.

## Rotas Sugeridas

### Queries de Dominio e Leitura
- `GET /enrollments/{id}/history`
- `GET /students/{id}/report-card`
- `GET /students/{id}/dashboard`

### Reporting
- `GET /reports/attendance`
- `GET /reports/classes`
- `GET /reports/performance`

### Exportacoes
- `GET /exports/reports/attendance`
- `GET /exports/reports/classes`
- `GET /exports/reports/performance`
- `GET /exports/students/{id}/report-card`

## Regras
- queries devem expor filtros explicitos e auditaveis
- dashboards e relatorios devem informar se o dado e parcial ou oficial
- exportacoes devem refletir os mesmos filtros da tela
- grandes exportacoes podem migrar para job assincrono

## Filtros Minimos Esperados
- `school_year_id`
- `period_id`
- `class_group_id`
- `subject_id`
- `student_id`
- `date_from`
- `date_to`
- ordenacao e pagina
