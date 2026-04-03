# API - Rotas HTTP Fase 1 (Enrollment)

## Objetivo
Definir a primeira superficie HTTP do produto sobre o contexto mais maduro: matricula.

## Rotas Prioritarias

### `POST /enrollments`
Caso de uso:
- criar matricula

### `GET /enrollments/{id}`
Caso de uso:
- consultar matricula por id

### `POST /enrollments/{id}/suspend`
Caso de uso:
- suspender matricula

### `POST /enrollments/{id}/reactivate`
Caso de uso:
- reativar matricula

### `POST /enrollments/{id}/cancel`
Caso de uso:
- cancelar matricula

### `POST /enrollments/{id}/conclude`
Caso de uso:
- concluir matricula

## Payloads de Entrada Conceituais

### Criar Matricula
- `student_id`
- `class_group_id`
- `academic_period_id`
- `occurred_at`, quando fizer sentido

### Suspender / Reativar / Cancelar
- `justification`
- `occurred_at`, opcional

### Concluir
- `verdict` ou parametros necessarios para o verdict
- `justification`, quando exigida
- `occurred_at`, opcional

## Respostas de Sucesso
- payload serializavel
- identificador do aggregate
- estado atual
- `changed`
- metadados minimos do caso de uso

## Erros Esperados
- `404` para nao encontrado
- `400` para payload invalido de transporte
- `403` para falta de permissao
- `409` para conflito de estado ou concorrencia
- `422` para negocio inelegivel quando aplicavel
- `500` para falha tecnica inesperada
