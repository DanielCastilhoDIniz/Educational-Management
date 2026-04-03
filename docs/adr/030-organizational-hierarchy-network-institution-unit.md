# ADR 030 - Hierarquia Organizacional: Rede, Instituicao e Unidade Escolar

## Status
Proposto

## Contexto
A documentacao ja cobre multi-tenancy por instituicao, membership institucional e isolamento por tenant. No entanto, ainda faltava explicitar como o produto deve representar cenarios em que uma mesma organizacao controla mais de uma escola, campus ou unidade.

Em SaaS escolar, esse ponto e importante porque uma rede educacional pode:
- possuir multiplas instituicoes ou escolas
- compartilhar politicas entre unidades
- manter usuarios com acesso cross-school sob controle
- consolidar relatorios por rede, por instituicao ou por unidade

Sem uma decisao formal, surgem ambiguidades como:
- `tenant` significa escola unica ou grupo educacional inteiro
- unidade escolar e apenas um atributo ou um contexto estrutural
- o mesmo usuario pode operar em multiplas escolas da mesma rede sem duplicidade de cadastro

## Decisao
Adotar uma hierarquia organizacional explicita com tres niveis conceituais:

1. `Network` ou `EducationalGroup`
- representa a rede, mantenedora ou grupo educacional
- pode agregar uma ou mais instituicoes

2. `Institution`
- representa o tenant operacional primario do sistema
- e o escopo minimo de isolamento de dados por padrao

3. `Unit` ou `SchoolUnit`
- representa escola, campus, polo ou unidade subordinada, quando o modelo de negocio exigir
- pertence a uma `Institution`

## Regras
- o isolamento minimo continua sendo por `Institution`
- `Network` organiza governanca, consolidacao e administracao superior, mas nao elimina a necessidade de segregacao por instituicao
- `Unit` so deve existir quando houver caso de uso real para isso
- memberships podem existir no nivel de instituicao e, quando necessario, com escopo adicional por unidade
- politicas podem resolver por `Unit -> Institution -> Network`, quando fizer sentido

## Consequencias

### Positivas
- deixa claro como suportar mais de uma escola ou rede
- prepara o produto para grupos educacionais e administracao multi-escola
- reduz ambiguidade em autorizacao, relatorios e consolidacao

### Negativas / Riscos
- aumenta a complexidade do modelo organizacional
- exige cuidado para nao introduzir `Unit` sem necessidade real
- pode exigir matrices de permissao mais detalhadas

## Invariantes
- toda operacao relevante continua tenant-aware
- dados nao devem vazar entre instituicoes so porque pertencem a mesma rede
- consolidacao cross-school deve ser explicita e auditavel
- um usuario nao deve precisar de identidades duplicadas para atuar em escolas diferentes da mesma rede

## Plano de Implementacao
- documentar a hierarquia organizacional oficial do produto
- definir quando `Unit` existe de fato
- revisar membership, autorizacao e reporting com base nessa hierarquia
- alinhar read models e filtros de relatorio para suportar `network_id`, `institution_id` e `unit_id` quando aplicavel

## Checklist de Implementacao
- [ ] Existe modelo explicito para rede, instituicao e unidade escolar
- [ ] `Institution` esta confirmada como tenant operacional primario
- [ ] Membership e acesso cross-school respeitam a hierarquia organizacional
- [ ] Relatorios consolidados por rede/instituicao/unidade foram especificados
- [ ] Politicas de heranca/override por unidade foram definidas

## Checklist de Code Review
- [ ] O significado de tenant nao fica ambiguo entre rede e escola
- [ ] Usuarios nao sao duplicados desnecessariamente entre unidades da mesma rede
- [ ] Acesso cross-school so ocorre por contrato explicito e auditavel
- [ ] Multi-tenancy e hierarquia organizacional permanecem coerentes entre si

## Checklist de Testes
- [ ] Existem testes de usuario atuando em mais de uma escola da mesma rede
- [ ] Existem testes de consolidacao por rede, instituicao e unidade
- [ ] Existem testes de negacao para acesso fora da hierarquia permitida
- [ ] Existem testes para override de politicas por unidade quando aplicavel

## Checklist de Documentacao
- [ ] Caso de uso de cadastrar rede/instituicao/unidade foi oficializado
- [ ] Politica de hierarquia organizacional esta alinhada ao ADR
- [ ] ADRs 019 e 020 referenciam a mesma estrutura organizacional

