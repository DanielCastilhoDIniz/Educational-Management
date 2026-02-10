# 📌 Contexto

<!--
Explique brevemente o que motivou este PR.
Qual problema de negócio, regra ou evolução do domínio está sendo tratada?
-->

---

## 🎯 Objetivo do PR

<!--
O que este PR pretende alcançar?
Ex.: introduzir novo comando de domínio, refinar regra existente, preparar camada de aplicação, etc.
-->

---

## 🧠 Impacto no Domínio (DDD)

### Aggregate(s) afetado(s)
- [ ] Enrollment
- [ ] Outro(s): _______________________

### Regra(s) de negócio envolvida(s)
<!--
Descreva a(s) regra(s) de forma declarativa.
Ex.: "Uma matrícula concluída não pode ser suspensa."
-->

### Invariantes
<!--
Liste invariantes criadas, reforçadas ou verificadas neste PR.
-->

---

## 🔁 Transições de Estado (se aplicável)

| Estado Atual | Ação | Novo Estado | Permitido? | Observações |
| ------------ | ---- | ----------- | ---------- | ----------- |
|              |      |             |            |             |

---

## 📣 Eventos de Domínio

- [ ] Evento(s) novo(s)
- [ ] Evento(s) existente(s) alterado(s)
- [ ] Nenhum

### Lista de eventos
<!--
Ex.: EnrollmentConcluded, EnrollmentCancelled, etc.
-->

---

## 🧪 Testes

### Testes adicionados / alterados
- [ ] Testes de sucesso
- [ ] Testes de erro / regra de negócio
- [ ] Testes de idempotência
- [ ] Guards de eventos
- [ ] Contratos de erro

### Observações sobre cobertura
<!--
Ex.: "Cobertura mantida em 100% no domínio."
-->

---

## ⚠️ Riscos e Pontos de Atenção

<!--
Existe algum comportamento sensível?
Alguma decisão que mereça revisão futura?
-->

---

## 📎 Checklist (obrigatório)

- [ ] Regras de negócio estão **somente no domínio**
- [ ] Nenhuma regra foi duplicada na aplicação ou infra
- [ ] Testes refletem as regras descritas
- [ ] Todos os testes passaram no CI
- [ ] Não há efeitos colaterais em falhas

---

## 🧭 Próximos Passos (opcional)

<!--
O que naturalmente vem depois deste PR?
-->

---

## 📝 Changelog (quando aplicável)

> **Preencher somente se este PR tiver alguma das labels abaixo:**
> `feature`, `bug`, `breaking-change`

### Tipo de entrada
- [ ] Added
- [ ] Changed
- [ ] Fixed
- [ ] Removed
- [ ] Deprecated

### Linha para o CHANGELOG.md
<!--
Escreva UMA linha clara, em inglês ou português técnico,
no formato usado no CHANGELOG.md.

Exemplos:
- (domain) Added explicit guards for enrollment state transitions.
- (application) Added EnrollmentApplicationService with in-memory repository.
- (domain) Fixed invalid cancellation from CONCLUDED state.
- (domain) Removed deprecated enrollment transition.
-->

