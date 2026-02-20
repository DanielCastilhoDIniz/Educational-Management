# ADR 003 — Linguagem Ubíqua em PT-BR e Mapeamento Técnico de Estados
# ADR 003 — Ubiquitous Language in Brazilian Portuguese and Technical Mapping of States

## Status
Aprovado

## Contexto
A documentação do domínio usa termos em PT-BR (ATIVA, TRANCADA, CANCELADA, CONCLUÍDA),
enquanto a implementação utiliza um enum técnico em inglês (ACTIVE, SUSPENDED, CANCELLED, CONCLUDED).

Sem um mapeamento oficial, surgem inconsistências entre:
- documentação (fonte de verdade do negócio),
- código (representação técnica),
- UI e integrações externas.

## Decisão
Manter a **linguagem ubíqua em PT-BR** como fonte de verdade na documentação e adotar um
**mapeamento oficial** entre termos do negócio e enum técnico:

- ATIVA ↔ `ACTIVE`
- TRANCADA ↔ `SUSPENDED`
- CANCELADA ↔ `CANCELLED`
- CONCLUÍDA ↔ `CONCLUDED`

O significado do estado (definição formal) prevalece sobre a nomenclatura técnica.

## Consequências

### Positivas
- Consistência entre docs, código e UI.
- Facilita comunicação com stakeholders e usuários finais.
- Mantém domínio “limpo” sem renunciar ao padrão técnico interno.

### Negativas / Riscos
- Se alguém alterar termos do documento sem atualizar o mapeamento, cria divergência.
- Integrações externas precisam saber qual “idioma” usar (PT-BR vs enum técnico).

## Regras e Invariantes
- Documentos de domínio devem referenciar ambos quando necessário:
  - `ATIVA` (`ACTIVE`), `TRANCADA` (`SUSPENDED`), etc.
- O enum técnico é a forma persistida/intercambiada internamente.
- UI pode exibir PT-BR (linguagem ubíqua), sem alterar o core.
- Novos estados só podem ser introduzidos com:
  - definição formal no documento,
  - atualização do enum técnico,
  - atualização do mapeamento oficial.

## Plano de Implementação
- Atualizar `DOMIAIN_ROLES.md` e demais docs para incluir a equivalência oficial.
- Garantir que tabelas de transição e regras sempre mencionem PT-BR + enum técnico.
- Definir convenção para API/UI:
  - internamente usar enum técnico,
  - externamente exibir PT-BR (ou aceitar ambos, se necessário).

## Checklist de Implementação
- [ ] Inserir “Nota de alinhamento” no capítulo de Estados (docs)
- [ ] Atualizar tabelas de transição para exibir `PT-BR (ENUM)`
- [ ] Padronizar nomenclatura nos capítulos 5–10 (Matrícula, Eventos, Fronteiras)
- [ ] Documentar convenção de exposição na API (se a API expõe estado)

## Checklist de Code Review
- [ ] Estado nunca é comparado por texto “PT-BR” no core (usar enum técnico)
- [ ] Conversões PT-BR ↔ enum são centralizadas (não espalhadas)
- [ ] Logs/auditoria registram enum técnico e (opcional) rótulo PT-BR

## Checklist de Testes
- [ ] Tabelas/documentos citam corretamente o mapeamento
- [ ] Serialização/deserialização de estado não perde informação