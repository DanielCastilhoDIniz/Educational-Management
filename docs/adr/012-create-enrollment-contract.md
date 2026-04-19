# ADR 012 - Contrato de Criacao de Enrollment

## Status
Aprovado

## Contexto
O contrato de `save()` cobre a persistência de aggregates `Enrollment` ja
existentes, com concorrência otimista e semantica de update. A criação de
matricula e um caso de uso diferente e precisa de contrato proprio para evitar:

- uso indevido de `save()` para insert inicial
- ambiguidade sobre estado inicial e versionamento
- confusao entre snapshot inicial, evento de criacao e transicao de estado
- dependencia de pre-check como se fosse garantia final de unicidade
- taxonomia de erros inconsistente entre port, service e adapter

No estado atual do projeto, o domínio ja sabe criar a matricula, a Application
ja expoe um fluxo proprio de criacao e o port ja possui `create(...)`, mas o
adapter principal de infraestrutura ainda esta em consolidacao.

## Decisao
Adotar um contrato de criacao separado do contrato de update.

### Regras principais
1. Criacao de matricula e um caso de uso proprio.
2. O repositorio deve expor `create(enrollment)` de forma explicita e separada
   de `save()`.
3. `create(...)` recebe um aggregate `Enrollment` novo, ja validado no domínio.
4. A matricula nasce em `active`.
5. A primeira versao persistida e `1`.
6. `reactivated_at` nasce `null`.
7. A criacao persiste o snapshot inicial.
8. A criacao nao depende, neste momento, da persistencia de uma
   `StateTransition` inicial.
9. O aggregate emite `EnrollmentCreated` como evento de domínio proprio na
   criacao.
10. `institution_id` e obrigatorio e faz parte do contrato de negocio da
    criação.
11. A unicidade final da matricula e garantida na persistencia, nao por
    pre-check na Application.
12. O fluxo principal de criação nao depende de `exist_by_business_key(...)`.
13. O contrato minimo de falhas de `create(...)` e:
    - `EnrollmentDuplicationError`
    - `EnrollmentTechnicalPersistenceError`
14. `EnrollmentDuplicationError` cobre:
    - duplicidade por business key
    - colisao explicita de `id`
15. `EnrollmentTechnicalPersistenceError` cobre:
    - falhas técnicas de banco/servidor
    - falhas de integridade inesperadas nao classificadas como duplicidade
16. A classificação de duplicidade no adapter deve ser conservadora: so deve
    virar `EnrollmentDuplicationError` quando houver evidencia técnica
    suficiente.

## Contrato operacional de `create(...)`
- entrada: aggregate novo e valido
- efeito: persistência do snapshot inicial
- retorno: versão inicial persistida
- falha esperada 1: `EnrollmentDuplicationError`
- falha esperada 2: `EnrollmentTechnicalPersistenceError`

## Fluxo alvo
1. A Application recebe os dados de criação.
2. O domínio cria o aggregate via `Enrollment.create(...)`.
3. O aggregate nasce em `active`, com `version = 1`, e registra
   `EnrollmentCreated` no buffer interno.
4. A Application chama `repo.create(enrollment)`.
5. O adapter persiste o snapshot inicial.
6. Em caso de duplicidade confirmada, o adapter levanta
   `EnrollmentDuplicationError`.
7. Em caso de falha técnica ou integridade inesperada, o adapter levanta
   `EnrollmentTechnicalPersistenceError`.
8. A Application converte o resultado para o contrato externo do caso de uso.
9. A Application faz `pull_domain_events()` somente após persistência bem-
   sucedida.

## O que este ADR nao decide
- autorização do ator
- politicas externas de janela de criação
- validações cross-context de cadastro mestre
- persistência de transição inicial no log append-only
- politica de publicação/outbox do `EnrollmentCreated`

## Consequencias

### Positivas
- separa claramente criação de update
- reduz ambiguidade no repositorio
- deixa o port mais enxuto e mais contratual
- evita falsa seguranca de pre-check como garantia de unicidade
- torna `institution_id` parte explicita do contrato de negocio
- preserva a possibilidade de diagnostico mais preciso para duplicidade

### Negativas / Riscos
- exige alinhamento fino entre port, service e adapter
- exige testes de integração para validar a classificação de erro no adapter
- pode exigir revisao futura caso a criação passe a persistir transição inicial
- a confirmação técnica de duplicidade pode depender de metadados do backend
  concreto de persistencia

## Status atual da implementação
- `Enrollment.create(...)` ja existe no domínio
- `CreateEnrollment.execute(...)` ja existe na Application
- o port ja expoe `create(enrollment)`
- `institution_id` ja e obrigatorio no service e no aggregate
- `EnrollmentCreated` ja foi adotado e ja e emitido no domínio
- o pre-check saiu do fluxo principal de criação
- o adapter principal Django ainda esta em consolidação
- a classificação conservadora de duplicidade ainda depende de observação do
  `IntegrityError` real em runtime
- o contrato textual do port ainda precisa ser lapidado para refletir esse ADR

## Regras e invariantes
- `save()` nao cria matricula implicitamente
- criação bem-sucedida sempre persiste `version = 1`
- criação exige `institution_id` valido e explicito
- criação nao depende de `StateTransition` inicial enquanto isso nao for uma
  decisao arquitetural explicita
- o snapshot inicial deve ser coerente com a matriz de estados do aggregate
- duplicidade nao deve ser inferida por heuristica fraca quando faltar
  evidencia técnica suficiente

## Plano de implementação
- consolidar o contrato do port `create(...)`
- concluir a remoção de `EnrollmentCreationError` do fluxo de criação
- manter o fluxo principal sem pre-check
- concluir o adapter principal Django para `repo.create(...)`
- investigar, em runtime, quais metadados o `IntegrityError` expoe
- implementar classificação conservadora de duplicidade
- criar testes de integração para sucesso, duplicidade e falha técnica
- alinhar documentação de caso de uso e backlog ao fluxo final

## Checklist de implementação
- [x] O caso de uso `criar_matricula` foi definido de forma explicita na camada de Application.
- [x] O contrato de criação esta separado do contrato de `save()` de update.
- [x] O port de repositorio possui operação explicita de criação.
- [x] O contrato textual do port `create(...)` foi totalmente alinhado a este ADR.
- [x] O adapter principal Django implementa completamente `repo.create(...)`.
- [x] A criação persiste o snapshot inicial valido com `version = 1` no adapter principal.
- [x] O estado inicial da matricula esta documentado e coerente com o domínio.
- [x] `created_at` e demais timestamps iniciais usam UTC de forma consistente.
- [x] `reactivated_at` nao e preenchido na criação inicial.
- [x] A criação nao depende de `StateTransition` inicial no contrato atual.
- [x] `EnrollmentCreated` foi adotado como evento de criação.
- [x] O pre-check saiu do fluxo principal de criação.
- [x] A regra conservadora de classificação da duplicidade foi implementada no adapter.

## Checklist de revisão
- [x] `save()` continua exclusivo para atualização de matricula existente.
- [x] O create nao introduz regra de negocio indevida na Infrastructure.
- [ ] Regras externas de autorização e politicas continuam fora do aggregate e seguem pendentes nos contextos apropriados.
- [x] O aggregate criado nasce em estado consistente com as invariantes do domínio.
- [ ] O contrato de erros diferencia duplicidade e falha técnica em toda a cadeia.
- [x] O fluxo de criação nao conflita com o modelo `snapshot + append-only log` vigente.
- [x] O contrato de criação ficou alinhado aos ADRs 005, 006, 008, 009 e 013.

## Checklist de testes
- [x] Existe teste de integração do adapter para criação bem-sucedida.
- [x] Existe teste garantindo `version = 1` na criação.
- [x] Existe teste garantindo estado inicial correto apos criação no domínio.
- [x] Existe teste de investigação para observar o `IntegrityError` real em colisao de `id`.
- [x] Existe teste de investigação para observar o `IntegrityError` real em duplicidade por business key.
- [x] Existe teste de duplicidade tipada no adapter apos a regra final de classificação.
- [ x] Existe teste para falha técnica sem persistencia parcial.
- [x] Existe teste garantindo que criação nao reutiliza indevidamente o fluxo de update.
- [x] Existe teste para evento `EnrollmentCreated`.

## Checklist de documentação
- [x] O caso de uso `criar_matricula` esta documentado.
- [x] A politica de criação de matricula esta documentada.
- [x] O backlog tecnico da refatoração da criação esta documentado.
- [x] A existencia do fluxo de criacao esta refletida na documentacao funcional.
- [x] O contrato de criacao esta coerente com a futura camada API.
- [x] A nomenclatura usada no ADR esta alinhada com a linguagem ubiqua do projeto.
