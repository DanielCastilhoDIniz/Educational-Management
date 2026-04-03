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
