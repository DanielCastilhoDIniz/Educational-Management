# ADR 003 - Eventos de Dominio via Acumulo no Aggregate e Extracao (Pull)

## Status
Aprovado

## Contexto
Transicoes validas do aggregate Matricula geram eventos de dominio. Precisamos:

- evitar acoplamento do dominio com fila, webhook, ORM ou HTTP
- garantir que eventos externos so sejam publicados quando a mudanca estiver persistida
- suportar retries sem publicar fatos nao confirmados

## Decisao
Adotar o padrao `Aggregate Event Buffer + Pull`:

1. o dominio cria e registra eventos internamente durante transicoes validas
2. o aggregate acumula esses eventos em buffer interno
3. a Application extrai eventos explicitamente ao final do caso de uso
4. a Infrastructure publica externamente apenas apos persistencia bem-sucedida

Eventos sao fatos imutaveis e nao carregam logica de negocio.

## Consequencias

### Positivas
- dominio permanece puro e testavel
- evita evento publicado sem commit
- permite retries seguros
- evolui naturalmente para Outbox

### Negativas / Riscos
- exige disciplina na Application
- se a Application esquecer de fazer `pull`, eventos podem ficar presos
- publicacao externa pode falhar apos commit

## Regras e Invariantes
- eventos sao criados apenas no dominio
- eventos nao sao publicados pelo dominio
- a extracao e explicita e deve limpar o buffer do aggregate
- a Infrastructure so publica eventos provenientes da Application
- eventos oficiais da Matricula sao os ligados a transicoes de estado

## Plano de Implementacao
- no dominio: manter buffer interno e operacao de `pull`
- na Application: carregar, executar dominio, persistir, extrair, encaminhar ao publisher
- na Infra: implementar publisher e, se necessario, Outbox

## Checklist de Implementacao
- [x] Dominio registra eventos apenas em transicoes validas
- [x] Aggregate expoe operacao de extracao (`pull`) que limpa o buffer
- [x] Application executa persistencia antes do `pull`
- [ ] Publisher de infra recebe apenas eventos extraidos (nao instancia eventos)
- [ ] Falhas de publicacao sao tratadas (retry/log) sem quebrar consistencia

## Checklist de Code Review
- [x] Dominio nao conhece fila/webhook/ORM/HTTP
- [ ] Nao existe publicacao de evento antes do commit
- [x] Eventos sao imutaveis (sem setters/mutacoes)
- [x] O buffer nao vaza entre casos de uso (sempre limpo apos pull)
- [x] Application nao cria eventos "na mao"

## Checklist de Testes
- [x] Transicao valida gera evento esperado (dominio)
- [x] `pull` retorna eventos e limpa buffer (dominio)
- [ ] Application persiste antes de publicar (teste de fluxo)
- [x] Falha de persistencia nao publica evento
