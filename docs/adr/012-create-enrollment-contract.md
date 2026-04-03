# ADR 012 - Contrato de Criacao de Enrollment

## Status
Aprovado

## Contexto
O contrato atual de `save()` cobre atualizacao de aggregate existente com concorrencia otimista. O projeto ainda nao formalizou como criar uma matricula nova sem misturar criacao com update.

Sem essa decisao, surgem riscos recorrentes:

- uso indevido de `save()` para criacao
- ambiguidade sobre estado inicial e versionamento
- ausencia de regra explicita para deduplicacao e unicidade de negocio
- incerteza sobre evento inicial e trilha de auditoria

## Decisao
Adotar um contrato de criacao separado do contrato de update.

### Regras principais
1. Criacao de matricula e um caso de uso proprio.
2. O repositorio deve expor uma operacao explicita de criacao, separada de `save()`.
3. A matricula nasce no estado `active`.
4. A primeira versao persistida e `1`.
5. `reactivated_at` deve nascer `null`.
6. Criacao nao deve depender do log de `StateTransition` atual.
7. O aggregate emite `EnrollmentCreated` como evento de dominio proprio na criacao. Este evento carrega: `institution_id`, `student_id`, `class_group_id`, `academic_period_id` e `actor_id`.
8. `institution_id` e campo obrigatorio do aggregate `Enrollment` e invariante de negocio — toda matricula pertence a uma instituicao explicita.
9. A unicidade de negocio deve ser validada por politica/aplicacao antes do insert, e reforcada por constraint quando possivel.

### Contrato operacional sugerido
- entrada: aggregate novo e valido
- efeito: insert do snapshot inicial
- retorno: confirmacao de persistencia da versao `1`
- falhas esperadas: duplicidade de negocio, erro tecnico de integridade, erro tecnico inesperado

## Consequencias

### Positivas
- separa claramente criacao de update
- reduz ambiguidade no repositorio
- simplifica testes e documentacao
- evita acoplamento artificial do conceito de criacao ao log de transicoes

### Negativas / Riscos
- exige novo contrato no port de repositorio
- exige caso de uso adicional na Application
- pode exigir revisao futura se a auditoria passar a exigir evento/transicao inicial persistida

## Regras e Invariantes
- `save()` nao cria matricula implicitamente
- criacao bem-sucedida sempre persiste `version = 1`
- criacao nao aceita aggregate ja persistido
- criacao exige politicas externas resolvidas antes de chamar o dominio, quando aplicavel
- snapshot inicial deve ser coerente com a matriz de estados do aggregate

## Plano de Implementacao
- definir caso de uso `criar_matricula`
- definir politica de unicidade e janela de criacao
- criar contrato de repositorio dedicado para insert inicial
- implementar `EnrollmentCreated` no dominio com os campos definidos na regra 7
- criar testes de integracao para sucesso, duplicidade e rollback

## Checklist de Implementacao
- [ ] O caso de uso `criar_matricula` foi definido de forma explicita na camada de Application.
- [ ] O contrato de criacao esta separado do contrato de `save()` de update.
- [ ] O repositorio possui operacao explicita de criacao, sem create implicito dentro de `save()`.
- [ ] A criacao persiste um snapshot inicial valido com `version = 1`.
- [ ] O estado inicial da matricula esta documentado e coerente com o dominio.
- [ ] `created_at` e demais timestamps iniciais usam UTC de forma consistente.
- [ ] `reactivated_at` nao e preenchido na criacao inicial.
- [ ] A regra de unicidade de negocio da matricula foi definida e documentada.
- [ ] O contrato de erro para duplicidade/conflito de criacao foi definido.
- [ ] A criacao nao depende de `StateTransition` inicial sem decisao arquitetural explicita.
- [x] A decisao sobre evento de dominio de criacao foi registrada — `EnrollmentCreated` adotado.
- [ ] As responsabilidades entre Domain, Application e Infrastructure ficaram explicitas.

## Checklist de Revisao
- [ ] `save()` continua exclusivo para atualizacao de matricula existente.
- [ ] A criacao nao introduz regra de negocio indevida na Infrastructure.
- [ ] Regras externas de elegibilidade, autorizacao e politicas permanecem fora do aggregate.
- [ ] O aggregate criado nasce em estado consistente com as invariantes do dominio.
- [ ] O contrato de erros diferencia duplicidade, falha tecnica e uso invalido do metodo.
- [ ] O fluxo de criacao nao conflita com o modelo `snapshot + append-only log` vigente.
- [ ] O contrato de criacao ficou alinhado aos ADRs 005, 006, 008 e 009.

## Checklist de Testes
- [ ] Existe teste de criacao bem-sucedida com persistencia do snapshot inicial.
- [ ] Existe teste garantindo `version = 1` na criacao.
- [ ] Existe teste garantindo estado inicial correto apos reidratacao.
- [ ] Existe teste de duplicidade de negocio ou conflito de criacao.
- [ ] Existe teste para falha tecnica sem persistencia parcial.
- [ ] Existe teste garantindo que criacao nao reutiliza indevidamente o fluxo de update.
- [ ] Existe teste para evento de criacao, caso esse evento seja adotado.

## Checklist de Documentacao
- [x] O caso de uso `criar_matricula` esta documentado.
- [ ] A politica de criacao de matricula esta documentada.
- [ ] O README ou guia funcional referencia a existencia do fluxo de criacao.
- [ ] O contrato de criacao esta coerente com a futura camada API.
- [ ] A nomenclatura usada no ADR esta alinhada com a linguagem ubiqua do projeto.
