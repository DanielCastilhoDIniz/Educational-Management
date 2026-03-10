# ADR 001 - Persistencia do Aggregate Enrollment (Snapshot + Transition Log)

## Status
Aprovado

## Contexto
Precisamos persistir o aggregate `Enrollment` garantindo integridade de reidratacao, auditoria imutavel das mudancas e consistencia transacional entre o estado atual e o historico de transicoes.

O dominio emite eventos durante transicoes validas, e a publicacao externa deve ocorrer apenas apos persistencia bem-sucedida, sem acoplar o dominio a infraestrutura.

## Decisao
Adotar a estrategia `Snapshot + Log Append-Only`:

- `Enrollment` (snapshot) armazena o estado atual da matricula
- `EnrollmentTransition` (log) armazena transicoes como fatos imutaveis
- persistencia deve ser transacional: `1 caso de uso = 1 transacao`
- concorrencia por versionamento otimista no snapshot
- deduplicacao de transicoes por `transition_id` deterministico, conforme ADR 002

## Consequencias

### Positivas
- consultas rapidas por estado atual
- historico completo e auditavel
- dominio permanece puro e testavel
- base segura para publicar eventos apos persistencia

### Negativas / Riscos
- repository precisa implementar reidratacao de snapshot + log
- crescimento do log pode exigir otimizacoes futuras
- exige disciplina: o log e append-only

## Regras e Invariantes
- `EnrollmentTransition` e append-only
- `transition_id` e unique e deterministico
- `actor_id` e obrigatorio
- todos os timestamps devem estar em UTC
- `Enrollment.state` deve coincidir com o `to_state` da ultima transicao, quando houver transicoes

## Plano de Implementação
- modelar tabelas `Enrollment` e `EnrollmentTransition` com constraints e indices
- implementar repository transacional (`get_by_id` + `save`)
- traduzir erros do banco em erros de infra
- criar testes de integracao para round-trip, retry, concorrencia e rollback

## Checklist de Implementacao
- [x] Modelar `Enrollment` (snapshot) com `version` e timestamps (`created_at`, `updated_at`, `*_at`)
- [ ] Criar constraints de coerência por estado (timestamps obrigatórios/proibidos)
- [ ] Criar indices: `state`, `student_id`, e compostos conforme consulta
- [x] Modelar `EnrollmentTransition` (append-only)
- [x] Garantir `transition_id` unique (ADR 002)
- [x] Garantir `actor_id` obrigatorio
- [x] Definir FK `enrollment_id` com `ON DELETE PROTECT`
- [ ] Implementar `get_by_id` (snapshot + transitions) com reidratacao segura
- [ ] Implementar `save` transacional (snapshot + novas transitions)
- [ ] Aplicar controle otimista por `version`
- [ ] Implementar traducao de erros de DB (unique, FK, concorrencia)

## Checklist de Code Review
- [x] O dominio nao depende de ORM/DB
- [ ] O log e realmente append-only (sem update/delete)
- [ ] `save` insere apenas transitions novas
- [ ] `save` e atomico (ou tudo persiste, ou nada)
- [ ] Eventos so sao publicados apos commit (via pull na Application)
- [ ] Concorrencia otimista esta coberta por testes

## Checklist de Testes
- [ ] Persistir -> reidratar -> objetos equivalentes (round-trip)
- [ ] No-op nao cria transition
- [ ] Retry nao duplica transition (unique `transition_id`)
- [ ] Conflito de versao falha corretamente
- [ ] Rollback mantem snapshot/log consistentes
