# ADR 007 - Camada de Infrastructure como Implementadora de Ports e Efeitos Externos

## Status
Aprovado

## Contexto
Com as camadas de dominio e application definidas, falta registrar formalmente a responsabilidade da camada concreta que conecta o sistema ao mundo externo.

No projeto atual, essa camada aparece em `src/infrastructure/django/` e concentra integracoes tecnicas como:

- modelos Django
- mapeadores entre ORM e dominio
- repositorios concretos
- configuracao de framework
- futura publicacao de eventos externos

Ja existem decisoes importantes relacionadas a infraestrutura:

- persistencia do aggregate `Enrollment` por snapshot + transition log (ADR 008)
- eventos de dominio acumulados no aggregate e extraidos pela application (ADR 003)
- application como guardia do fluxo do caso de uso (ADR 005)

Sem uma decisao explicita para esta camada, surgem riscos recorrentes:

- repository tomando decisao de negocio
- ORM vazando para dominio ou application
- excecoes tecnicas vazando sem traducao adequada
- publicacao de evento acontecendo antes da persistencia
- controllers, jobs ou management commands acessando banco direto sem passar pelo contrato certo

## Decisao
Adotar formalmente a Camada de Infrastructure como implementadora de ports e concentradora de efeitos externos.

Isso significa que:

1. A Infrastructure implementa detalhes concretos de:
- persistencia
- framework
- filas, webhooks ou mensageria
- configuracao tecnica
- adaptadores externos

2. A Infrastructure implementa ports definidos na Application, sem redefinir regra de negocio.

3. Repositorios concretos sao responsaveis por:
- reidratar aggregates a partir do modelo persistido
- persistir snapshot e log de transicoes dentro da estrategia definida
- respeitar transacao por caso de uso
- aplicar concorrencia otimista quando o contrato exigir

4. Erros tecnicos de banco, ORM ou integracao devem ser traduzidos para falhas tecnicas estaveis antes de chegar a camada superior.

5. Publicacao externa de eventos ocorre apenas apos persistencia bem-sucedida e sempre a partir de eventos extraidos pela Application.

6. A Infrastructure nao deve instanciar regra de negocio nem fabricar eventos de dominio "na mao".

## Consequencias

### Positivas
- Dominio e application permanecem desacoplados de framework e DB.
- Troca de adapter ou framework fica mais controlada.
- Falhas tecnicas ficam centralizadas e traduziveis.
- Persistencia e publicacao podem evoluir para outbox, retry ou outros mecanismos sem contaminar o nucleo.

### Negativas / Riscos
- Mapeamento ORM <-> dominio exige cuidado para manter reidratacao correta.
- Traducao de erro tecnico pode ficar inconsistente se cada adapter fizer de um jeito.
- Publicacao apos commit pode exigir outbox quando confiabilidade forte for necessaria.

## Regras e Invariantes
- Infrastructure nao reimplementa regra nuclear do aggregate.
- Repository nao decide se uma transicao e valida; ele apenas persiste o estado resultante.
- Persistencia de `Enrollment` deve respeitar ADR 008.
- Publicacao de eventos deve respeitar ADR 003.
- Erros tecnicos devem ser traduzidos para um contrato compreensivel pela Application.
- Nenhum adapter concreto deve ser importado pelo dominio.
- A camada pode depender de framework; as camadas internas nao.

## Plano de Implementacao
- Implementar o repository Django de matricula com reidratacao segura.
- Traduzir falhas de persistencia para tipos tecnicos estaveis.
- Garantir transacao atomica de snapshot + transitions.
- Implementar publisher de eventos externos desacoplado do dominio.
- Evoluir para outbox quando a criticidade operacional justificar.

## Checklist de Implementacao
- [x] Estrutura base de infrastructure em Django criada
- [x] Modelos ORM do contexto academico criados
- [x] Mappers do contexto academico criados
- [ ] `django_enrollment_repository` implementado por completo
- [ ] Concorrencia otimista aplicada no save do aggregate
- [ ] Traducao de falhas tecnicas para erros tipados
- [ ] Publicador de eventos externos implementado
- [ ] Estrategia de retry/outbox documentada quando aplicavel

## Checklist de Code Review
- [ ] Nenhum arquivo em `src/infrastructure/` define regra que pertence ao dominio
- [ ] Repositories implementam ports, nao contratos paralelos
- [ ] Falhas tecnicas nao vazam cruamente para interface
- [ ] Publicacao nao ocorre antes da persistencia confirmada
- [ ] Mapeamento ORM <-> dominio preserva invariantes e timestamps
- [x] Dependencias de framework nao vazam para `src/domain/` ou `src/application/`

## Checklist de Testes
- [ ] Testes de round-trip ORM -> dominio -> ORM
- [ ] Testes de save transacional com snapshot + log
- [ ] Testes de conflito de versao
- [ ] Testes de traducao de erro tecnico
- [ ] Testes garantindo que falha de persistencia nao publica eventos
- [ ] Testes de publicacao apos commit ou fluxo equivalente
