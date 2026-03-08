# ADR 003 - Linguagem Ubiqua em PT-BR e Mapeamento Tecnico de Estados

## Status
Aprovado

## Contexto
A documentacao do dominio usa termos em PT-BR (`ATIVA`, `TRANCADA`, `CANCELADA`, `CONCLUIDA`), enquanto a implementacao utiliza um enum tecnico em ingles (`ACTIVE`, `SUSPENDED`, `CANCELLED`, `CONCLUDED`).

Sem um mapeamento oficial, surgem inconsistencias entre documentacao, codigo e interfaces externas.

## Decisao
Manter a linguagem ubiqua em PT-BR como fonte de verdade na documentacao e adotar um mapeamento oficial entre termos de negocio e enum tecnico:

- `ATIVA` <-> `ACTIVE`
- `TRANCADA` <-> `SUSPENDED`
- `CANCELADA` <-> `CANCELLED`
- `CONCLUIDA` <-> `CONCLUDED`

O significado do estado prevalece sobre a nomenclatura tecnica.

## Consequencias

### Positivas
- consistencia entre docs, codigo e UI
- melhor comunicacao com stakeholders
- preserva linguagem de negocio sem perder padrao tecnico interno

### Negativas / Riscos
- alterar a documentacao sem atualizar o mapeamento cria divergencia
- integracoes externas precisam saber qual representacao usar

## Regras e Invariantes
- documentos de dominio devem referenciar ambos quando necessario
- o enum tecnico e a forma persistida/intercambiada internamente
- UI pode exibir PT-BR sem alterar o core
- novos estados exigem definicao formal, atualizacao do enum e do mapeamento

## Plano de Implementacao
- atualizar `DOMIAIN_ROLES.md` e demais docs com a equivalencia oficial
- garantir que regras e transicoes mencionem PT-BR + enum tecnico
- definir convencao para API/UI:
  - internamente usar enum tecnico
  - externamente exibir PT-BR ou aceitar ambos, se necessario

## Checklist de Implementacao
- [x] Inserir "Nota de alinhamento" no capitulo de Estados
- [x] Atualizar tabelas e regras de transicao para exibir `PT-BR (ENUM)`
- [ ] Padronizar nomenclatura nos capitulos 5-10 (Matricula, Eventos, Fronteiras)
- [ ] Documentar convencao de exposicao na API (se a API expuser estado)

## Checklist de Code Review
- [x] Estado nunca e comparado por texto PT-BR no core (usar enum tecnico)
- [ ] Conversoes `PT-BR <-> enum` sao centralizadas
- [ ] Logs/auditoria registram enum tecnico e, opcionalmente, rotulo PT-BR

## Checklist de Testes
- [ ] Tabelas/documentos citam corretamente o mapeamento
- [ ] Serializacao/deserializacao de estado nao perde informacao
