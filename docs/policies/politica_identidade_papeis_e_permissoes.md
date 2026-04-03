# Politica - Identidade, Papeis e Permissoes

## Objetivo
Definir como usuarios recebem papeis e como esses papeis habilitam casos de uso.

## Regras Sugeridas
- papel e escopo pertencem ao membership institucional
- permissao deve ser avaliada por caso de uso e escopo
- service accounts exigem trilha de auditoria reforcada
- remocao de papel deve ter efeito previsivel e auditavel
- papeis compostos devem ser documentados explicitamente

## Testes Recomendados
- usuario com papel correto executa caso de uso
- usuario sem membership e negado
- usuario com membership em outro tenant e negado
- service account tem trilha de autoria identificavel
