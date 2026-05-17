# ADR 021 - Estrutura Academica: Ano Letivo, Periodos, Turmas e Disciplinas

## Status
Proposto

## Contexto
Cada instituicao podera escolher a quantidade de periodos por ano letivo, a estrutura de turmas e, possivelmente, a forma de associar disciplinas e professores.

## Decisao
Modelar a estrutura academica como configuravel por instituicao, mas com contratos explicitos.

## Regras
- ano letivo pertence a uma instituicao
- ano letivo contem um ou mais periodos
- turma pertence a um ano letivo e normalmente a um periodo ou conjunto de periodos, conforme politica institucional
- disciplinas pertencem ao catalogo institucional
- a oferta academica deve explicitar relacao entre turma, disciplina e professor quando houver diario ou avaliacao

## Consequencias
- prepara suporte a instituicoes com calendarios diferentes
- reduz hardcode de quantidade fixa de periodos ou avaliacoes
- exige politicas claras para fechamento e consolidacao

## Plano de Implementacao
- definir modelo conceitual de ano/periodo/turma/disciplina
- formalizar chaves de negocio e constraints
- documentar como matricula se ancora nessa estrutura

## Checklist de Implementacao
- [ ] Existe modelo conceitual e tecnico de ano letivo, periodo, turma e disciplina
- [ ] A quantidade de periodos por instituicao e configuravel
- [ ] Oferta academica explicita relacao entre turma, disciplina e professor
- [ ] Chaves de negocio e constraints foram definidas por instituicao/ano
- [ ] Matricula se ancora formalmente nessa estrutura academica

## Checklist de Code Review
- [ ] Nao ha numero fixo de periodos hardcoded no codigo
- [ ] Turma nao existe fora do contexto institucional/ano letivo
- [ ] Dependencias entre matricula, diario e avaliacao usam contratos claros
- [ ] Politicas variaveis ficam fora dos aggregates estruturais

## Checklist de Testes
- [ ] Existem testes para instituicoes com quantidades diferentes de periodos
- [ ] Existem testes de consistencia entre turma, periodo e ano letivo
- [ ] Existem testes de ancoragem da matricula na estrutura academica
- [ ] Existem testes para associacao de professor a disciplina/turma

## Checklist de Documentacao
- [ ] Casos de uso de ano letivo, periodos e turmas foram oficializados
- [ ] Politicas de estrutura academica estao alinhadas ao ADR
- [ ] Mapa de contextos explicita dependencias com matricula, diario e avaliacao

