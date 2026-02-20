# ADR 006 — Políticas Institucionais Configuráveis com Resolução por Escopo e Congelamento por Período

## Status
Aprovado

## Contexto
Regras de frequência, prazos, trancamento mínimo, correções de nota e exceções pedagógicas variam por
instituição/unidade e podem gerar inconsistência se forem alteradas durante o período letivo.

Precisamos:

- permitir variação por escopo (instituição, unidade, período letivo);
- tornar a aplicação determinística e auditável;
- evitar retroatividade indevida (mudança “no meio do jogo”).

## Decisão
Adotar políticas configuráveis com:

1) **Resolução determinística por escopo**
- Período Letivo (mais específico)
- Unidade
- Instituição/Rede (padrão)

2) **Congelamento por Período Letivo quando aplicável**
- políticas relevantes podem ser “fixadas” por período, evitando retroatividade.

3) **Auditoria obrigatória**
- toda mudança deve registrar ator, data/hora, escopo, valor anterior/novo e justificativa quando aplicável.

A validação dessas políticas ocorre na Application Layer ou nos contextos especializados (não no aggregate Matrícula),
conforme ADR 004.

## Consequências

### Positivas
- Regras previsíveis e reproduzíveis (determinismo).
- Auditoria e conformidade facilitadas.
- Evita comportamento divergente entre turmas/unidades.
- Facilita multi-tenant e crescimento do produto.

### Negativas / Riscos
- Implementação exige resolução consistente e cache com invalidação.
- Congelamento por período aumenta carga de gestão (versões por ciclo).
- Mudanças tardias podem exigir migração/justificativa institucional.

## Regras e Invariantes
- Resolução sempre usa a ordem: Período → Unidade → Instituição.
- Ausência total de configuração cai no padrão documentado do catálogo.
- Mudanças devem ser auditáveis.
- Cache permitido apenas com invalidação segura após alteração.
- Políticas que habilitam exceções devem respeitar Matriz de Autoridade (Cap. 12.2).

## Plano de Implementação
- Definir catálogo de políticas (Cap. 11) com:
  - chave, tipo, padrão, restrição legal, camada de validação, efeito
- Implementar armazenamento conceitual por escopo (instituição/unidade/período).
- Implementar resolução determinística e cache seguro.
- Registrar auditoria de alterações.
- Documentar quais casos de uso consultam quais políticas (Tabela de Implementação do Cap. 11).

## Checklist de Implementação
- [ ] Catálogo de políticas completo (chave/tipo/padrão/limites/camada/efeito)
- [ ] Armazenamento por escopo (instituição/unidade/período)
- [ ] Resolução determinística (Período → Unidade → Instituição)
- [ ] Congelamento por período (quando aplicável)
- [ ] Auditoria de alterações (ator, data/hora, antes/depois, justificativa)
- [ ] Cache com invalidação após mudança
- [ ] Matriz de Autoridade aplicada para políticas de exceção

## Checklist de Code Review
- [ ] Não há “if mágico” hardcoded substituindo política configurável
- [ ] Resolução é centralizada (não duplicada em vários serviços)
- [ ] Cache não retorna valor antigo após alteração
- [ ] Mudanças geram trilha de auditoria completa
- [ ] Políticas não são validadas dentro do aggregate Matrícula (ADR 004)

## Checklist de Testes
- [ ] Resolução por escopo retorna o valor correto em todos cenários
- [ ] Congelamento por período impede retroatividade
- [ ] Alteração gera auditoria (antes/depois)
- [ ] Cache invalida corretamente
- [ ] Casos de uso consultam políticas corretas (teste de fluxo)