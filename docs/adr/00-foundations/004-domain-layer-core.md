# ADR 004 - Camada de Dominio como Nucleo Puro do Sistema

## Status
Aprovado

## Contexto
O projeto ja possui decisões importantes sobre matricula, eventos, fronteira do aggregate e persistencia.
Essas decisões estao espalhadas entre codigo, testes e ADRs especificos.

Falta registrar de forma explicita a decisao estrutural mais importante da primeira camada:
o dominio e o nucleo do sistema e a fonte de verdade para invariantes do negocio.

Sem esse registro formal, surgem riscos recorrentes:

- mover regra de negocio para framework ou adapter por conveniencia
- acoplar entidades a DTOs, ORM ou contratos da Application
- misturar erro de dominio com erro de caso de uso
- deixar pre-condicoes externas vazarem para dentro do aggregate

No contexto atual, o modulo `academic.enrollment` ja implementa:

- aggregate root `Enrollment`
- value objects (`EnrollmentState`, `StateTransition`, `ConclusionVerdict`)
- domain events
- domain errors
- invariantes de construcao, reidratacao e transicao

## Decisao
Adotar formalmente a Camada de Domain como primeira camada arquitetural e nucleo puro do sistema.

Isso significa que:

1. O dominio contem apenas conceitos de negocio:
- entidades
- value objects
- domain events
- domain errors
- invariantes e transicoes

2. O dominio nao depende de:
- Django
- ORM
- banco de dados
- HTTP
- serializacao de API
- `ApplicationResult`, `ApplicationError` ou DTOs da camada de application

3. O aggregate valida invariantes internas e executa transicoes validas.

4. O dominio pode criar eventos internamente, mas nao publica eventos externamente.

5. Regras dependentes de contexto externo permanecem fora do dominio, conforme ADR 002.

6. Persistencia, publicacao e traducao de erro ficam fora do dominio, conforme ADR 008 e ADR 003.

## Consequencias

### Positivas
- Dominio permanece puro, deterministico e altamente testavel.
- Regras criticas ficam centralizadas no aggregate e nos value objects.
- A Application pode orquestrar casos de uso sem reimplementar regra.
- Infraestrutura pode ser trocada sem reescrever o modelo central.

### Negativas / Riscos
- Exige disciplina para nao mover regra para service, serializer ou repository.
- A Application precisa traduzir erros e coordenar pre-condicoes externas.
- Algumas regras "convenientes" nao poderao ser resolvidas dentro do aggregate por dependerem de contexto externo.

## Regras e Invariantes
- Toda regra que depende apenas do estado da matricula pertence ao dominio.
- Toda transicao de estado deve ser validada pelo aggregate.
- O aggregate deve permanecer reidratavel com validacao de coerencia.
- Timestamps de dominio devem ser normalizados para UTC.
- Eventos de dominio devem ser fatos imutaveis.
- O dominio nao faz IO e nao consulta servicos externos.
- O dominio nao conhece detalhes de persistencia, transporte ou apresentacao.

## Plano de Implementacao
- Manter o pacote `src/domain/` isolado de framework e adapters.
- Preservar a validacao de invariantes em `Enrollment` e nos value objects.
- Manter testes de dominio cobrindo invariantes, transicoes e eventos.
- Fazer a Application consumir o dominio por meio de casos de uso e ports, sem reimplementar regra.
- Revisar novos modulos para seguir a mesma fronteira desde o inicio.

## Checklist de Implementacao
- [x] Aggregate root `Enrollment` modelado no dominio
- [x] Value objects do contexto de matricula modelados no dominio
- [x] Domain events definidos no dominio
- [x] Domain errors definidos no dominio
- [x] Invariantes de construcao e reidratacao implementadas
- [x] Transicoes de estado implementadas no aggregate
- [x] Dominio sem dependencia de framework
- [ ] Validacao automatica de fronteira por lint/import rules

## Checklist de Code Review
- [x] Nenhum arquivo em `src/domain/` importa `application`, `infrastructure` ou framework
- [ ] Nenhum serializer/repository/service reimplementa regra que pertence ao aggregate
- [x] Eventos continuam sendo criados apenas no dominio
- [x] O dominio continua sem IO ou acesso externo
- [x] Erros de dominio continuam separados de erros de application

## Checklist de Testes
- [x] Testes de dominio cobrem invariantes do aggregate
- [x] Testes de dominio cobrem transicoes validas e invalidas
- [x] Testes de dominio cobrem `pull_domain_events()` e `peek_domain_events()`
- [x] Testes de application verificam a orquestracao sem mover a regra para fora do dominio
- [ ] Testes automatizados de fronteira de imports entre camadas
