# ADR 022 - Diario de Classe, Aulas e Frequencia

## Status
Proposto

## Contexto
Professores registrarao aulas, conteudos e frequencia. Esse fluxo precisa ser auditavel, temporal e coerente com turma, disciplina e periodo.

## Decisao
Adotar diario de classe como contexto proprio, separado de matricula, mas integrado a ela.

## Regras
- aula registrada deve referenciar turma, disciplina, professor e data/hora
- frequencia deve ser lancada sobre aula, estudante/matricula e situacao padronizada
- alteracoes em diario e frequencia devem ser auditaveis
- diario nao deve depender de mutacao direta do aggregate de matricula para operar no dia a dia

## Consequencias
- reduz acoplamento do ciclo diario com o ciclo de vida da matricula
- melhora rastreabilidade pedagogica
- exige contratos claros entre matricula e diario

## Plano de Implementacao
- definir modelo de aula e frequencia
- definir estados ou status de frequencia
- documentar fechamento e retificacao de diario
