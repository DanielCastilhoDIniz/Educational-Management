# Checklist - Multi-Tenancy e Autorizacao

- [ ] Toda operacao relevante conhece o tenant
- [ ] Membership institucional e exigido
- [ ] Papel e escopo foram avaliados no caso de uso
- [ ] Logs incluem `tenant_id` e `actor_id`
- [ ] Testes cobrem negacao cross-tenant
- [ ] Nenhuma query critica ignora isolamento institucional
