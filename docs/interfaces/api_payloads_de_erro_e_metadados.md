# API - Payloads de Erro e Metadados

## Objetivo
Padronizar o envelope de erro e os metadados de resposta da futura API HTTP.

## Envelope de Erro Sugerido
Campos minimos:
- `code`
- `message`
- `details`
- `correlation_id`
- `timestamp`

## Regras
- `code` deve derivar de `ErrorCodes` ou de erro de transporte claramente separado
- `message` deve ser estavel e apropriada ao cliente
- `details` nao deve vazar stack trace ou detalhe sensivel de infraestrutura
- `correlation_id` deve permitir rastrear a request

## Metadados de Sucesso Sugeridos
- `request_id` ou `correlation_id`
- `tenant_id`, quando apropriado
- `changed`, para comandos
- `data_status` (`partial` ou `official`), para relatorios/boletins/dashboard
- `generated_at` ou `updated_at`, para consultas analiticas

## Paginacao
Quando houver listas grandes:
- `page`
- `page_size`
- `total_items`
- `total_pages`
- `sort`
- `filters`
