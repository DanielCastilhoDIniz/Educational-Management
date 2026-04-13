# Relatorios Consolidados por Rede, Instituicao e Unidade

## Objetivo
Descrever como relatorios podem agregar dados em diferentes niveis organizacionais.

## Niveis de Consolidacao

### Unidade
- uso operacional local
- foco em turma, disciplina, frequencia e desempenho da unidade

### Instituicao
- consolidado tenant-wide
- foco em gestao academica e administrativa da instituicao

### Rede
- consolidado de varias instituicoes ou escolas
- foco em governanca, comparativos e visao executiva

## Regras
- todo relatorio deve explicitar o nivel de agregacao
- filtros devem indicar `network_id`, `institution_id` e `unit_id` quando aplicavel
- consolidacao por rede exige permissao ampliada
- exportacoes consolidadas devem ser auditadas

## Exemplos de Saidas
- frequencia media por unidade
- quantidade de aulas registradas por instituicao
- desempenho medio por rede
- comparativo entre escolas da mesma rede
