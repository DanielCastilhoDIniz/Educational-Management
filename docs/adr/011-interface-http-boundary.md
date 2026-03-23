# ADR 011 - Camada de Interface HTTP como Tradutora Fina de Entrada e Saida

## Status
Aprovado

## Contexto
O projeto ainda nao expos os casos de uso de matricula por HTTP, mas essa integração e um passo natural do sistema.

Ja existe um contrato interno importante definido na Application:

- `ApplicationResult`
- `ApplicationError`
- `ErrorCodes`

Também ja existe a decisao de manter dominio e application desacoplados de framework.

Sem uma decisao explicita para a camada de interface, surgem riscos recorrentes:

- controllers ou views reimplementando regra de negocio
- excecoes de domínio virando contrato HTTP direto
- serializers conhecendo aggregate demais
- respostas HTTP inconsistentes entre endpoints
- acoplamento de Django/DRF ao domínio e a application

No estado atual do projeto, a interface HTTP ainda e uma fronteira logica. A implementacao concreta pode viver sobre Django views, DRF views/serializers ou adapters equivalentes dentro da infraestrutura.

## Decisão
Adotar formalmente a Camada de Interface HTTP como tradutora fina entre transporte HTTP e casos de uso da Application.

Isso significa que:

1. A Interface recebe entrada HTTP e a converte para os parâmetros esperados pelo caso de uso.

2. A Interface chama a Application e recebe `ApplicationResult` como contrato principal de saída.

3. A Interface converte `ApplicationResult` para resposta HTTP sem alterar regra de negocio.

4. A Interface nao conhece detalhes internos de persistência, ORM ou transição de estado além
5. Validações de formato e transporte podem ocorrer na Interface:
- campos obrigatórios do payload
- tipos primitivos
- parsing de datas
- autenticacao/autorizacao de transporte

1. Validacoes de negocio nao pertencem a Interface.

2. O mapeamento de erro para HTTP deve ser centralizado e estavel, baseado em `ErrorCodes`.

## Consequencias

### Positivas
- Endpoints ficam finos e previsiveis.
- O contrato HTTP pode evoluir sem contaminar o domínio.
- Jobs, CLI e API podem compartilhar os mesmos casos de uso da Application.
- Falhas ficam mapeadas de forma uniforme para status e payloads.

### Negativas / Riscos
- Exige disciplina para nao mover regra para serializer ou controller.
- Pode haver duplicacao de mapeamento se o contrato HTTP nao for centralizado.
- A definicao de payload de resposta precisa ser mantida coerente com o contrato da Application.

## Regras e Invariantes
- Interface nao executa regra nuclear do domínio.
- Interface nao traduz erro tecnico diretamente do domínio.
- O contrato HTTP parte de `ApplicationResult`, nao de excecoes de domínio.
- Mapeamento `ErrorCodes` -> status HTTP deve ser unificado.
- Controllers/views devem delegar a um service de application por caso de uso.
- Payloads HTTP devem ser serializaveis e independentes de classes internas do domínio.

## Mapeamento Inicial Recomendado
- `ENROLLMENT_NOT_FOUND` -> `404 Not Found`
- `JUSTIFICATION_REQUIRED` -> `400 Bad Request`
- `INVALID_STATE_TRANSITION` -> `409 Conflict`
- `ENROLLMENT_NOT_ACTIVE` -> `409 Conflict`
- `CONCLUSION_NOT_ALLOWED` -> `422 Unprocessable Entity`
- `STATE_INTEGRITY_VIOLATION` -> `500 Internal Server Error`
- `CONCURRENCY_CONFLICT` -> `409 Conflict`
- `DATA_INTEGRITY_ERROR` -> `409 Conflict`
- `UNEXPECTED_ERROR` -> `500 Internal Server Error`

## Plano de Implementacao
- Definir presenter/mapper HTTP central para `ApplicationResult`.
- Criar endpoints ou views para os casos de uso de matricula.
- Definir schema de request/response por caso de uso.
- Centralizar o mapeamento de `ErrorCodes` para status HTTP.
- Garantir que autenticacao e autorizacao de transporte nao contaminem o domínio.

## Checklist de Implementacao
- [ ] Presenter HTTP para `ApplicationResult`
- [ ] Mapeamento central de `ErrorCodes` para status HTTP
- [ ] Endpoint de cancelar matricula
- [ ] Endpoint de suspender matricula
- [ ] Endpoint de concluir matricula
- [ ] Payloads de erro padronizados
- [ ] Validacao de input de transporte separada da validacao de negocio

## Checklist de Code Review
- [ ] Views/controllers nao reimplementam regra do aggregate
- [ ] Nenhuma resposta HTTP depende de excecao de domínio como contrato primario
- [ ] Mapeamento de erro HTTP e centralizado
- [ ] Interface nao acessa ORM diretamente quando ha use case correspondente
- [ ] Payloads expostos nao vazam estruturas internas desnecessarias do domínio

## Checklist de Testes
- [ ] Testes de endpoint para sucesso, no-op e falha esperada
- [ ] Testes do presenter HTTP para cada `ErrorCodes`
- [ ] Testes de payload de erro padronizado
- [ ] Testes garantindo que controllers chamam a Application e nao o domínio direto
