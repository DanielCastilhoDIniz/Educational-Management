# Mapeamento HTTP e Codigos de Erro

## Objetivo
Preparar uma ponte operacional entre contratos de Application e a futura camada HTTP.

## Estrutura Recomendada
Para cada rota futura documentar:
- metodo HTTP
- recurso
- filtros ou payload
- codigo de sucesso
- codigos de erro esperados
- `ErrorCodes` correspondentes
- requisitos de autorizacao

## Exemplos Conceituais
- `POST /enrollments` -> criar matricula
- `POST /enrollments/{id}/suspend` -> suspender matricula
- `GET /students/{id}/dashboard` -> painel do estudante
- `GET /reports/attendance` -> relatorio de frequencia
- `GET /reports/classes` -> relatorio de aulas registradas
- `GET /reports/performance` -> relatorio de desempenho
- `GET /students/{id}/report-card` -> boletim

## Recomendacao
O mapeamento deve preservar:
- semantica de erro da Application
- tenant e escopo do ator
- filtros serializaveis e auditaveis
