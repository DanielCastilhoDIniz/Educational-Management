# Checklist - Persistencia e Migracoes

- [ ] Snapshot e log continuam coerentes
- [ ] Constraints e indices foram revisados
- [ ] O contrato de concorrencia continua valido
- [ ] Migracao e reversivel ou o risco foi documentado
- [ ] Round-trip de reidratacao foi testado
- [ ] Retry idempotente foi testado quando aplicavel
- [ ] Falhas de integridade foram traduzidas corretamente
- [ ] Nao ha update/delete indevido em log append-only
