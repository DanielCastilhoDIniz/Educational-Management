# ADR 009 - Contrato do mÃ©todo `save`

## Responsabilidade
Persistir a atualizaÃ§Ã£o de uma matrÃ­cula existente usando concorrÃªncia otimista.

## Entrada
- Um aggregate `Enrollment` existente, semanticamente vÃ¡lido, contendo a versÃ£o de origem esperada para a atualizaÃ§Ã£o.

## PrÃ©-condiÃ§Ãµes
- O aggregate representa uma matrÃ­cula jÃ¡ existente
- A `version` do aggregate Ã© a versÃ£o de origem usada como condiÃ§Ã£o de concorrÃªncia
- O mÃ©todo nÃ£o realiza criaÃ§Ã£o implÃ­cita
- Garantir que haja pelo menos uma transiÃ§Ã£o persistente (requisito rastreabilidade para auditoria).

## SaÃ­da
- A nova versÃ£o persistida da matrÃ­cula

## CondiÃ§Ã£o de sucesso
A atualizaÃ§Ã£o sÃ³ pode ser concluÃ­da quando:
- O registro com o `id` informado existe no banco
- A `version` persistida atual Ã© igual Ã  `version` de origem do aggregate

## Efeitos em caso de sucesso
- Persiste o novo snapshot da matrÃ­cula
- Incrementa a versÃ£o automaticamente em 1
- Retorna a nova versÃ£o persistida

### Campos atualizados
Quando a gravaÃ§Ã£o for aceita, o repository deve persistir corretamente:
- `state`
- `concluded_at`
- `cancelled_at`
- `suspended_at`
- `reactivated_at`
- `version` nova

### Campos preservados
O repository deve manter corretamente os dados estruturais jÃ¡ existentes da matrÃ­cula, incluindo:
- `id`
- `student_id`
- `class_group_id`
- `academic_period_id`
- `created_at`

## Casos de falha

1. **Registro ausente para atualizaÃ§Ã£o**
   - O `id` informado nÃ£o existe no momento do `save`
   - Nome conceitual sugerido: `EnrollmentPersistenceNotFoundError`

2. **Conflito de concorrÃªncia**
   - O registro existe, mas a `version` persistida atual nÃ£o coincide com a `version` de origem do aggregate
   - Nome conceitual sugerido: `ConcurrencyConflictError`

3. **Erro de integridade de dados**
   - A persistÃªncia falha por violaÃ§Ã£o de constraint, referÃªncia ou outra inconsistÃªncia estrutural de dados
   - Nome conceitual sugerido: `InfrastructureError`

4. **Falha tÃ©cnica inesperada**
   - A persistÃªncia falha por motivo tÃ©cnico nÃ£o classificado nas categorias anteriores
   - Nome conceitual sugerido: `InfrastructureError`

5. **Erro de infraestrutura**
   - O aggregate foi enviado para persistÃªncia sem nenhuma transition persistÃ­vel.
   - Nome conceitual sugerido: `InfrastructureError`


## Regras tÃ©cnicas
- Incremento automÃ¡tico de versÃ£o
- Sem sobrescrita
- Sem mescla
- Sem create implÃ­cito

### EstratÃ©gia de diagnÃ³stico quando nenhuma atualizaÃ§Ã£o ocorrer
Se a tentativa de atualizaÃ§Ã£o condicional nÃ£o afetar nenhum registro:
1. Verificar se o `id` existe
2. Se nÃ£o existir, lanÃ§ar erro de registro ausente para atualizaÃ§Ã£o (`EnrollmentPersistenceNotFoundError`)
3. Se existir, lanÃ§ar erro de conflito de concorrÃªncia (`ConcurrencyConflictError`)

## NÃ£o responsabilidades
- NÃ£o criar matrÃ­cula nova
- NÃ£o aplicar regras de negÃ³cio do domÃ­nio
- NÃ£o publicar eventos externos
- NÃ£o limpar domain events
- NÃ£o resolver conflitos por merge

## Checklist de Implementacao
- [x] `save()` permanece separado de `create()`
- [x] `save()` usa `version` como versao de origem para concorrencia otimista
- [x] Snapshot e transition sao persistidos na mesma transacao
- [ ] Retry idempotente usa validacao completa do estado persistido
- [ ] Traducao de falhas de integridade e falhas inesperadas esta fechada de ponta a ponta

## Checklist de Code Review
- [x] `save()` nao realiza criacao implicita
- [x] O repositorio nao publica nem limpa eventos de dominio
- [ ] Conflito real e retry idempotente estao claramente separados no fluxo
- [ ] Violacao de contrato de entrada usa erro apropriado e nao erro tecnico generico

## Checklist de Testes
- [x] Existe teste de sucesso com incremento de versao
- [x] Existe teste de conflito de concorrencia
- [x] Existe teste de retry sem duplicar transition
- [ ] Existe teste especifico para falha de integridade sem falso sucesso

## Checklist de Documentacao
- [x] O ADR 012 deixa explicita a separacao entre criacao e `save()`
- [ ] README e guias funcionais refletem `save()` como contrato de update
- [ ] API e interfaces futuras mapeiam corretamente os erros esperados de `save()`

