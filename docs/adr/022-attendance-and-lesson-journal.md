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

## Checklist de Implementacao
- [ ] Existe modelo de aula registrada com turma, disciplina, professor e data/hora
- [ ] Existe modelo padronizado de frequencia por aula e estudante/matricula
- [ ] Retificacao e auditoria de diario foram definidas
- [ ] Contratos entre diario e matricula estao formalizados
- [ ] Fechamento/retificacao de diario esta documentado

## Checklist de Code Review
- [ ] O diario permanece separado do aggregate de matricula
- [ ] Lancamento de frequencia nao depende de mutacao direta da matricula
- [ ] Toda alteracao de aula/frequencia e auditavel
- [ ] O contexto respeita tenant, periodo e escopo do professor

## Checklist de Testes
- [ ] Existem testes de registro de aula
- [ ] Existem testes de lancamento de frequencia por aula
- [ ] Existem testes de retificacao com auditoria
- [ ] Existem testes de integracao com estruturas academicas e matriculas elegiveis

## Checklist de Documentacao
- [ ] Casos de uso de registrar aula e lancar frequencia estao oficializados
- [ ] Politicas de frequencia e reposicao estao alinhadas ao ADR
- [ ] Reporting e dashboard usam o mesmo significado de frequencia

