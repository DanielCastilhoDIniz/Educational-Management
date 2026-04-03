# Guia da Camada API HTTP

## Objetivo
Definir como a camada API deve ser organizada para permanecer coerente com DDD, Application como orquestradora e infraestrutura desacoplada.

## Principios
- a API e uma borda de transporte
- a API nao implementa regra de negocio
- a API traduz input/output e contexto de autenticacao
- a API chama comandos e queries explicitos
- a API nao conhece detalhes internos de aggregate alem do necessario para montar payloads seriais

## Estrutura Recomendada

### Request Layer
Responsavel por:
- parse de JSON, querystring e path params
- validacao de formato
- normalizacao de tipos primitivos
- extracao de tenant e ator autenticado

### API Handler / View
Responsavel por:
- compor parametros do caso de uso
- chamar command/query correspondente
- delegar o mapeamento da resposta para presenter HTTP

### HTTP Presenter / Mapper
Responsavel por:
- transformar `ApplicationResult` ou DTO de query em payload HTTP
- padronizar sucesso, erro, metadados e envelopes

## Regras de Ouro
- nenhuma view deve chamar aggregate direto
- nenhuma view deve acessar ORM direto quando existir Application/query apropriado
- a camada HTTP nao deve conhecer `InfrastructureError` como contrato primario
- serializers/pydantic/forms/validators de transporte nao devem carregar regra institucional ou de dominio

## Recomendacao de Pastas Futuras
- `src/interface/http/...` como camada dedicada
- modulos separados por contexto e por command/query
- presenter central para erros e envelopes
