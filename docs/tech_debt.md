# Divida Tecnica

Registro de decisoes tecnicas conscientes que se desviam do ideal arquitetural.
Cada item deve ser revisitado quando o custo de correcao for menor que o custo de manter.

---

## TD-001 — Validacao de `from_state` em `EnrollmentReactivated`

**Arquivo:** `src/domain/academic/enrollment/events/enrollment_events.py`

**Problema:**
O evento `EnrollmentReactivated` valida `from_state == SUSPENDED` no `__post_init__`.
Essa responsabilidade pertence ao aggregate, nao ao evento.
Eventos devem ser fatos imutaveis — nao validadores de regra de negocio.

**Por que foi deixado assim:**
A validacao foi adicionada como protecao extra antes da separacao de responsabilidades
estar completamente consolidada no projeto. Nao causa bugs no comportamento atual.

**Impacto atual:**
Baixo. A regra tambem e validada no aggregate `reactivate()`.
Duplicidade de validacao, nao ausencia dela.

**Correcao sugerida:**
Remover `__post_init__` de `EnrollmentReactivated`.
Garantir que o aggregate seja o unico responsavel por essa regra.

**Quando corrigir:**
Quando houver refatoracao dos eventos de dominio ou revisao do contrato de `EnrollmentReactivated`.

---

## TD-002 — `EnrollmentLike` Protocol na camada de Application

**Arquivo:** `src/application/academic/enrollment/services/_state_change_flow.py`

**Problema:**
O Protocol `EnrollmentLike` foi criado na Application como solucao provisoria para
evitar `Any` no `cast(Enrollment, enrollment)`. Idealmente, esse Protocol deveria
viver no dominio e o port deveria tipá-lo diretamente.

**Por que foi deixado assim:**
Mover o Protocol para o dominio exigiria que o dominio conhecesse o contrato de
extracao de eventos — o que pode gerar acoplamento indesejado nesse momento.

**Impacto atual:**
Baixo. O `cast` e consciente e o comportamento e correto.

**Correcao sugerida:**
Avaliar se faz sentido expor `EnrollmentLike` como parte do contrato publico do dominio.

**Quando corrigir:**
Quando houver revisao do contrato de portas e protocolos do aggregate.
