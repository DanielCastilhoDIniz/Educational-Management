# ADR 015 - Autoridade do Ator e Responsabilidade de Auditoria

## Status
Proposto

## Contexto
Toda mudanca de estado de matricula possui `actor_id`, mas o projeto ainda nao formalizou quem pode executar qual acao, como distinguir atores humanos de sistema e qual trilha de auditoria minima precisa ser preservada.

## Decisao
Adotar uma matriz de autoridade e auditoria explicita na Application Layer.

## Regras
1. O dominio recebe `actor_id`, mas nao decide autorizacao.
2. Autorizacao e responsabilidade pertencem a Application e a policies/ports externos.
3. Toda mudanca de estado deve registrar:
- `actor_id`
- tipo de ator
- acao executada
- instante efetivo
- justificativa quando aplicavel
4. Deve existir distincao minima entre:
- ator humano autenticado
- ator de sistema
- ator administrativo de suporte
5. A execucao automatica deve identificar claramente o job/processo responsavel.

## Consequencias

### Positivas
- melhor rastreabilidade
- base mais segura para suporte e compliance
- menos ambiguidade em operacoes automaticas

### Negativas / Riscos
- exige modelagem de contexto de autenticacao e service accounts
- aumenta trabalho de integracao na camada de interface

## Invariantes
- nenhuma transicao de estado sem `actor_id`
- justificativa obrigatoria deve chegar auditavel
- a Application deve falhar cedo quando o ator nao estiver autorizado
- a auditoria nao deve depender apenas de log textual

## Plano de Implementacao
- definir matriz de atores por caso de uso
- criar policy/port de autorizacao
- propagar metadados de ator para logs e eventos
- documentar responsabilidades de suporte operacional
