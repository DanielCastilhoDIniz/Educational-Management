# ADR 005 — Eventos de Domínio via Acúmulo no Aggregate e Extração (Pull)

## Status
Aprovado

## Contexto
Transições válidas do aggregate Matrícula geram eventos de domínio (ex.: matrícula trancada, cancelada, concluída).
Precisamos:

- evitar acoplamento do domínio com infraestrutura (fila, webhook, ORM, HTTP);
- garantir que eventos externos só sejam publicados quando a mudança estiver persistida;
- suportar retries sem publicar “fatos” que não foram confirmados no banco.

## Decisão
Adotar o padrão **Aggregate Event Buffer + Pull**:

1) O domínio cria e registra eventos internamente durante transições válidas;
2) O aggregate acumula esses eventos em buffer interno;
3) A Application Layer extrai eventos explicitamente ao final do caso de uso (`pull`);
4) A Infrastructure publica externamente apenas após persistência bem-sucedida.

Eventos são fatos imutáveis e não carregam lógica de negócio.

## Consequências

### Positivas
- Domínio permanece puro e testável.
- Evita “evento publicado sem commit”.
- Permite retries seguros (combinado com persistência idempotente).
- Evolui naturalmente para Outbox se necessário.

### Negativas / Riscos
- Exige disciplina na Application: sempre persistir antes de extrair/publicar.
- Se a Application esquecer de “pull”, eventos podem ficar presos (testes devem cobrir).
- Publicação externa pode falhar após commit (requer estratégia de retry/outbox se crítico).

## Regras e Invariantes
- Eventos são criados **apenas no domínio**.
- Eventos **não** são publicados pelo domínio.
- Extração é **explícita** e deve limpar o buffer do aggregate.
- A Infrastructure só publica eventos provenientes da Application, após persistência confirmada.
- Eventos oficiais do aggregate Matrícula são apenas os ligados a transições de estado (ver ADR 007).

## Plano de Implementação
- No domínio: manter buffer interno de eventos e operação de extração (“pull”).
- Na Application: padrão de fluxo:
  1) carregar aggregate
  2) executar operação de domínio
  3) persistir aggregate
  4) extrair eventos
  5) encaminhar para publisher (infra)
- Na Infra: implementar publisher (log/queue/webhook) e, se necessário, Outbox (ADR futuro).

## Checklist de Implementação
- [ ] Domínio registra eventos apenas em transições válidas
- [ ] Aggregate expõe operação de extração (`pull`) que limpa o buffer
- [ ] Application executa persistência antes do `pull`
- [ ] Publisher de infra recebe apenas eventos extraídos (não instancia eventos)
- [ ] Falhas de publicação são tratadas (retry/log) sem quebrar consistência

## Checklist de Code Review
- [ ] Domínio não conhece fila/webhook/ORM/HTTP
- [ ] Não existe publicação de evento antes do commit
- [ ] Eventos são imutáveis (sem setters/mutações)
- [ ] O buffer não “vaza” entre casos de uso (sempre limpo após pull)
- [ ] Application não cria eventos “na mão”

## Checklist de Testes
- [ ] Transição válida gera evento esperado (domínio)
- [ ] `pull` retorna eventos e limpa buffer (domínio)
- [ ] Application persiste antes de publicar (teste de fluxo)
- [ ] Falha de persistência não publica evento