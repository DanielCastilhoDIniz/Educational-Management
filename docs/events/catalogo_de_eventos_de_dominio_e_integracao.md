# Catalogo de Eventos de Dominio e Integracao

## Objetivo
Consolidar os eventos relevantes do produto, seus produtores e consumidores esperados.

## Campos Minimos por Evento
- nome do evento
- contexto produtor
- quando ocorre
- aggregate ou entidade associada
- payload conceitual
- chave de idempotencia
- consumidores esperados
- tipo (`dominio`, `integracao`, `outbox`)

## Catalogo Inicial Sugerido
- `EnrollmentSuspended`
- `EnrollmentReactivated`
- `EnrollmentCancelled`
- `EnrollmentConcluded`
- `EnrollmentCreated`, se adotado
- `LessonRegistered`
- `AttendancePosted`
- `AssessmentPublished`
- `PeriodClosed`
- `ReportCardIssued`

## Recomendacao
Eventos de integracao devem ser derivados de contratos claros e nao de leitura oportunista de tabelas.
