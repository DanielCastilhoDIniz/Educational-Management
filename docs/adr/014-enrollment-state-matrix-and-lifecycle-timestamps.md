# ADR 014 - Matriz de Estados e Timestamps do Ciclo de Vida da Matricula

## Status
Proposto

## Contexto
O aggregate ja possui estados e timestamps de ciclo de vida, mas o projeto ainda se beneficia de uma definicao documental unica para reidratacao, persistencia e testes.

## Decisao
Adotar uma matriz de estados explicita para `Enrollment`.

## Matriz Proposta

### `active`
Campos obrigatorios:
- `created_at`

Campos permitidos:
- `reactivated_at` pode ser `null` ou preenchido

Campos proibidos:
- `concluded_at`
- `cancelled_at`
- `suspended_at`

Interpretacao:
- `reactivated_at = null` indica matricula ativa sem reativacao registrada
- `reactivated_at != null` indica que o estado ativo atual foi alcancado por reativacao

### `suspended`
Campos obrigatorios:
- `created_at`
- `suspended_at`

Campos proibidos:
- `concluded_at`
- `cancelled_at`
- `reactivated_at`

### `cancelled`
Campos obrigatorios:
- `created_at`
- `cancelled_at`

Campos proibidos:
- `concluded_at`
- `suspended_at`
- `reactivated_at`

### `concluded`
Campos obrigatorios:
- `created_at`
- `concluded_at`

Campos proibidos:
- `cancelled_at`
- `suspended_at`
- `reactivated_at`

## Transicoes Permitidas
- `active -> suspended`
- `active -> cancelled`
- `active -> concluded`
- `suspended -> active`
- `suspended -> cancelled`

## Transicoes Proibidas
- qualquer transicao a partir de `cancelled`
- qualquer transicao a partir de `concluded`
- `active -> active` como mudanca de negocio
- `suspended -> concluded` sem reativacao, salvo decisao futura explicitamente documentada

## Regras de Persistencia
- o snapshot deve respeitar a matriz acima
- o `state` do snapshot deve coincidir com o `to_state` da ultima transicao persistida, quando houver transicoes
- `reactivated_at` deve ser limpo ao sair de `active`
- criacao inicial deve nascer com `reactivated_at = null`

## Plano de Implementacao
- alinhar aggregate, mapper e modelos ORM a esta matriz
- criar testes especificos para round-trip de cada estado
- validar coerencia snapshot x ultima transicao
