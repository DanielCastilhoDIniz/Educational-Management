# ADR 027 - Filtros, Ordenacao, Paginacao e Exportacao em Relatorios

## Status
Proposto

## Contexto
Relatorios de frequencia, aulas e desempenho exigirao grande variacao de filtros e formatos de saida. Sem padrao, a API e a interface tendem a ficar inconsistentes.

## Decisao
Padronizar o contrato de filtros e exportacoes para relatorios e dashboards.

## Regras
- filtros comuns devem ser reutilizados entre relatorios
- filtros devem ser explicitamente serializaveis e auditaveis
- ordenacao deve ser declarada no contrato
- exportacao deve refletir os mesmos filtros e ordenacao aplicados na tela
- paginacao deve existir para listas grandes, mesmo quando houver exportacao total em fluxo separado

## Consequencias
- reduz ambiguidade na interface
- facilita teste de consistencia entre tela e exportacao
- exige catalogo de filtros e contrato de metadados

## Plano de Implementacao
- definir DTO base de filtros para reporting
- definir contratos de exportacao assincroma ou sincrona, conforme volume
- documentar limites, formatos e regras de ordenacao

## Checklist de Implementacao
- [ ] Filtros comuns de reporting foram padronizados
- [ ] Contrato de ordenacao e paginacao foi definido para listas grandes
- [ ] Exportacao reaproveita os mesmos filtros da tela
- [ ] Metadados de exportacao e nomeacao de arquivos foram definidos
- [ ] Fluxos sincronos/assincronos de exportacao foram separados quando necessario

## Checklist de Code Review
- [ ] Exportacao nao ignora filtros e ordenacao selecionados pelo usuario
- [ ] Nao existem consultas ilimitadas sem paginacao ou fluxo async explicito
- [ ] Filtros sao serializaveis e auditaveis
- [ ] Ordenacao e validada e nao fica implicita

## Checklist de Testes
- [ ] Existem testes para equivalencia entre tela e exportacao
- [ ] Existem testes de paginacao estavel
- [ ] Existem testes para filtros invalidos ou combinacoes proibidas
- [ ] Existem testes de metadados de exportacao

## Checklist de Documentacao
- [ ] Matriz oficial de filtros por relatorio foi publicada
- [ ] Especificacao de exportacoes esta alinhada ao ADR
- [ ] API futura documenta query params e limites de exportacao

