# ADR 006 - Politicas Institucionais Configuraveis com Resolucao por Escopo e Congelamento por Periodo

## Status
Aprovado

## Contexto
Regras de frequencia, prazos, trancamento minimo, correcao de nota e excecoes pedagogicas variam por instituicao/unidade e podem gerar inconsistencias se forem alteradas durante o periodo letivo.

Precisamos:

- permitir variacao por escopo
- tornar a aplicacao deterministica e auditavel
- evitar retroatividade indevida

## Decisao
Adotar politicas configuraveis com:

1. resolucao deterministica por escopo
2. congelamento por periodo letivo quando aplicavel
3. auditoria obrigatoria

A validacao dessas politicas ocorre na Application Layer ou nos contextos especializados, nao no aggregate Matricula.

## Consequencias

### Positivas
- regras previsiveis e reproduziveis
- auditoria e conformidade facilitadas
- evita comportamento divergente entre turmas/unidades
- facilita multi-tenant e crescimento do produto

### Negativas / Riscos
- implementacao exige resolucao consistente e cache com invalidacao
- congelamento por periodo aumenta carga de gestao
- mudancas tardias podem exigir migracao/justificativa institucional

## Regras e Invariantes
- resolucao sempre usa a ordem `Periodo -> Unidade -> Instituicao`
- ausencia total de configuracao cai no padrao documentado
- mudancas devem ser auditaveis
- cache so com invalidacao segura
- politicas que habilitam excecoes devem respeitar a matriz de autoridade

## Plano de Implementacao
- definir catalogo de politicas com chave, tipo, padrao, restricao legal, camada de validacao e efeito
- implementar armazenamento por escopo
- implementar resolucao deterministica e cache seguro
- registrar auditoria de alteracoes
- documentar quais casos de uso consultam quais politicas

## Checklist de Implementacao
- [ ] Catalogo de politicas completo (chave/tipo/padrao/limites/camada/efeito)
- [ ] Armazenamento por escopo (instituicao/unidade/periodo)
- [ ] Resolucao deterministica (`Periodo -> Unidade -> Instituicao`)
- [ ] Congelamento por periodo (quando aplicavel)
- [ ] Auditoria de alteracoes (ator, data/hora, antes/depois, justificativa)
- [ ] Cache com invalidacao apos mudanca
- [ ] Matriz de Autoridade aplicada para politicas de excecao

## Checklist de Code Review
- [ ] Nao ha "if magico" hardcoded substituindo politica configuravel
- [ ] Resolucao e centralizada (nao duplicada em varios services)
- [ ] Cache nao retorna valor antigo apos alteracao
- [ ] Mudancas geram trilha de auditoria completa
- [x] Politicas nao sao validadas dentro do aggregate Matricula (ADR 002)

## Checklist de Testes
- [ ] Resolucao por escopo retorna o valor correto em todos os cenarios
- [ ] Congelamento por periodo impede retroatividade
- [ ] Alteracao gera auditoria (antes/depois)
- [ ] Cache invalida corretamente
- [ ] Casos de uso consultam politicas corretas (teste de fluxo)
