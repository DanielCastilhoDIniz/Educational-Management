# ADR 005 - Camada de Application como Orquestradora de Casos de Uso

## Status
Aprovado

## Contexto
Com a camada de dominio ja definida como nucleo puro do sistema, falta registrar formalmente a responsabilidade da camada seguinte.

No contexto atual do modulo `academic.enrollment`, a Application ja executa papeis importantes:

- carrega o aggregate pelo port de repositorio
- executa comandos de dominio
- traduz erros de dominio para um contrato estavel de aplicacao
- trata falhas previstas sem usar excecoes como contrato primario
- garante a ordem correta entre persistencia e limpeza/publicacao de eventos

Sem essa decisao explicita, surgem desvios recorrentes:

- service de application reimplementando regra que pertence ao aggregate
- controller, serializer ou adapter decidindo comportamento de caso de uso
- mistura entre erro de dominio, erro de infraestrutura e erro de API
- drenagem de eventos antes da persistencia
- contratos de retorno instaveis entre casos de uso

## Decisao
Adotar formalmente a Camada de Application como orquestradora de casos de uso e guardia do contrato externo do modulo.

Isso significa que:

1. A Application coordena o fluxo do caso de uso:
- carregar aggregate
- validar pre-condicoes externas
- executar operacao de dominio
- persistir aggregate
- limpar/extrair eventos conforme o contrato arquitetural
- retornar um resultado estavel para a camada superior

2. A Application nao redefine invariantes internas do aggregate.

3. Falhas esperadas devem retornar um contrato estavel, e nao ser propagadas como excecao para a camada chamadora.

4. O contrato padrao da camada e:
- `ApplicationResult` para sucesso, no-op e falha esperada
- `ApplicationError` para erro serializavel e estavel
- `ErrorCodes` como identificadores de maquina

5. A traducao de erros de dominio para erros de application acontece nesta camada.

6. Pre-condicoes dependentes de contexto externo pertencem a esta camada ou a ports/policies por ela consultados, conforme ADR 002.

7. A Application deve preservar o contrato de eventos definido no ADR 003:
- nao drenar eventos antes de persistir
- manter eventos disponiveis no aggregate se a persistencia falhar
- limpar o buffer apenas apos persistencia bem-sucedida

## Consequencias

### Positivas
- Casos de uso ficam previsiveis e uniformes.
- A camada superior recebe um contrato estavel e facil de mapear para HTTP, jobs ou CLI.
- O dominio permanece puro e a infraestrutura continua substituivel.
- Falhas de fluxo e inconsistencias ficam centralizadas e testaveis.

### Negativas / Riscos
- Exige disciplina para nao transformar a Application em deposito de regra de negocio.
- Pode haver duplicacao entre services se o fluxo comum nao for extraido.
- Erros de infraestrutura precisam ser traduzidos corretamente para nao vazar excecoes indevidas.

## Regras e Invariantes
- Application Service nao faz regra nuclear do aggregate.
- Application Service pode validar pre-condicoes externas antes de chamar o dominio.
- Falhas esperadas retornam `ApplicationResult(success=False)`.
- `changed=True` implica eventos nao vazios e `new_state` preenchido.
- Persistencia ocorre antes da limpeza do buffer de eventos.
- Falha de persistencia nao pode consumir eventos pendentes do aggregate.
- A camada superior nao deve depender de excecoes de dominio como contrato normal.

## Plano de Implementacao
- Padronizar os services do contexto de matricula sobre o mesmo fluxo de orquestracao.
- Manter helpers compartilhados para builders de resultado e finalizacao de mudanca de estado.
- Evoluir o port de repositorio para falhas tipadas de persistencia.
- Introduzir ports de autorizacao e politica para pre-condicoes externas.
- Expandir o mesmo contrato para novos casos de uso do contexto.

## Checklist de Implementacao
- [x] `ApplicationResult` definido como contrato estavel de saida
- [x] `ApplicationError` definido como payload serializavel de falha
- [x] `ErrorCodes` definidos para falhas esperadas
- [x] Mapper de erro de dominio para application implementado
- [x] Services de `cancel`, `suspend` e `conclude` alinhados ao mesmo fluxo
- [x] Persistencia ocorre antes da limpeza do buffer de eventos
- [x] Inconsistencias de estado/evento retornam `STATE_INTEGRITY_VIOLATION`
- [ ] Falhas de persistencia tipadas (`CONCURRENCY_CONFLICT`, `DATA_INTEGRITY_ERROR`)
- [ ] Ports de autorizacao e politica externa
- [x] Service de `reactivate` na Application

## Checklist de Code Review
- [x] Services nao reimplementam invariantes do aggregate
- [x] Erros de dominio sao traduzidos na Application, nao na infra ou na API
- [x] Nenhum service drena eventos antes de persistir
- [x] Falhas esperadas retornam `ApplicationResult`, nao excecao
- [ ] Pre-condicoes externas ficam em ports/policies ou services, nao no dominio
- [x] Fluxos repetidos usam helper comum quando isso reduz divergencia real

## Checklist de Testes
- [x] Testes de application cobrem sucesso, no-op e falha esperada
- [x] Testes de application cobrem falha de persistencia sem perda de eventos
- [x] Testes de application cobrem inconsistencias entre mudanca de estado e eventos
- [x] Testes de application validam o contrato de `ApplicationResult`
- [x] Testes cobrindo mapeamento completo de erros de dominio para application
- [ ] Testes cobrindo pre-condicoes externas por ports/policies
