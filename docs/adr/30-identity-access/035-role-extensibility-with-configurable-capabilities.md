# ADR 035 - Modelo de Extensibilidade de Papeis com Capabilities Configuráveis

## Status
Proposto

## Contexto
O ADR 034 formalizou o catalogo de `Capabilities` como StrEnum estatico no dominio, derivado de um mapa `code → frozenset[Capability]` no aggregate `Role`. Essa abordagem garante rastreabilidade total (Matrix-First), tipagem estatica e zero complexidade operacional para os papeis pre-definidos da taxonomia.

No entanto, clientes do SaaS precisarao de papeis customizados para atender estruturas organizacionais especificas — por exemplo, "Supervisor Pedagogico" ou "Coordenador Financeiro" — sem depender de ciclos de desenvolvimento. O modelo atual retorna `frozenset()` vazio para qualquer `code` fora do mapa estatico, tornando papeis customizados inoperantes para autorizacao real.

O campo `level` foi deliberadamente mantido como campo livre (nao derivado de `code`) para suportar essa extensibilidade — o cliente escolhe o nivel hierarquico do papel customizado sem necessidade de desenvolvedor.

## Problema
A autonomia do cliente para criar papeis uteis e limitada pelo vinculo entre `code` e capabilities no mapa estatico. Um papel com `code` desconhecido nasce sem capabilities — inutilizavel para autorizacao — mesmo que `level` esteja correto e o papel faca sentido organizacional.

## Alternativas Avaliadas

### A — Estatico Puro (modelo atual)
Capabilities sempre derivadas do `_CAPABILITY_MAP`. Papeis customizados dependem de desenvolvedor para entrar no mapa e receber capabilities.

**Positivo:** rastreabilidade total, sem complexidade operacional, auditavel via git.
**Negativo:** zero autonomia do cliente para novos papeis funcionais.

### B — Totalmente Configuravel por Banco
Capabilities armazenadas por papel no banco, configuravel livremente pelo cliente sem restricao ao catalogo aprovado.

**Positivo:** autonomia total do cliente.
**Negativo:** autorizacao vive no banco (auditoria fragil); risco de escalada de privilegio; migrations a cada mudanca de capability; necessidade de UI complexa; catalogo de capabilities deixa de ser controlado.

### C — Meio-Termo: Templates Imutaveis + Subconjunto Configuravel *(decisao adotada)*
Papeis pre-definidos (seed) sao templates imutaveis com capabilities fixas derivadas do `_CAPABILITY_MAP`. Cliente pode criar papeis customizados escolhendo um subconjunto das capabilities ja aprovadas no catalogo (`Capability` StrEnum). Novas capabilities continuam seguindo o processo Matrix-First — fora do alcance do cliente.

**Positivo:** autonomia parcial do cliente sem abrir o catalogo de capabilities; authorization ainda auditavel — o StrEnum aprovado e o teto do que pode ser configurado.
**Negativo:** requer novo mecanismo de persistencia de capabilities por papel customizado; escopo adicional (UI de configuracao, repositorio).

## Decisão
Adotar o modelo C.

Papeis pre-definidos da taxonomia permanecem com capabilities derivadas do `_CAPABILITY_MAP` — comportamento atual inalterado.

Papeis customizados recebem um conjunto explicito de capabilities persistido no banco, escolhido pelo ator responsavel a partir do catalogo aprovado. A property `capabilities` do aggregate `Role` passa a ser:
- Para papeis pre-definidos: derivada do `_CAPABILITY_MAP` (sem mudanca)
- Para papeis customizados: lida do campo persistido `custom_capabilities`

O catalogo de capabilities (StrEnum) permanece sob controle exclusivo do desenvolvimento — nenhuma capability nova pode ser criada pelo cliente.

## Principios Mantidos

- **Matrix-First**: novas capabilities continuam exigindo linha na matriz e aprovacao antes de entrar no StrEnum
- **`has_capability()` inalterado**: interface publica de autorizacao nao muda para nenhum consumidor
- **Papeis pre-definidos imutaveis**: seed data nao e alterada; comportamento atual e o contrato de referencia
- **`level` como campo livre**: cliente atribui o nivel hierarquico do papel customizado — decisao registrada no ADR 033

## Impacto no Aggregate Role

| Elemento | Mudanca |
|---|---|
| `_CAPABILITY_MAP` | Permanece — usado apenas para papeis pre-definidos |
| `custom_capabilities` | Novo campo opcional `frozenset[Capability] \| None` — `None` para papeis do sistema |
| Property `capabilities` | Verifica `custom_capabilities` primeiro; se `None`, consulta `_CAPABILITY_MAP` |
| `create()` | Sem mudanca para papeis pre-definidos |
| Novo factory ou parametro | Para criacao de papel customizado com capabilities explicitas |

## O Que Precisa Ser Construido

- Campo `custom_capabilities` no aggregate `Role` (opcional, `frozenset[Capability] | None`)
- Coluna no modelo de persistencia (nullable, serializada como lista de strings)
- Logica no repositorio para persistir e reidratar `custom_capabilities`
- Validacao na camada de application: capabilities informadas devem pertencer ao StrEnum `Capability`
- UI ou endpoint para configuracao de papeis customizados por ator autorizado
- Capability `ROLE_CREATE` (listada como futura no ADR 034) deve ser promovida e implementada antes deste fluxo

## Consequencias

### Positivas
- Cliente cria papeis customizados uteis sem ciclo de desenvolvimento
- Catalogo de capabilities permanece auditavel e controlado pelo desenvolvimento
- Papeis pre-definidos nao sao afetados — zero regressao no comportamento atual
- `has_capability()` continua sendo a unica interface de verificacao — transparente para a camada de Application

### Negativas / Riscos
- Complexidade adicional no aggregate e no repositorio
- Risco de configuracao incorreta — papel customizado com capabilities excessivas atribuidas por ator mal-intencionado ou desinformado
- Requer UI de configuracao — escopo nao trivial
- Dois caminhos para `capabilities` (estatico vs. persistido) exigem testes de dominio para ambos os casos

## Status de Implementacao
Nao implementado. Registrado para orientar planejamento futuro.

Condicoes para promover a implementacao:
- Aggregates `Role` e `Membership` estabilizados e testados
- Capability `ROLE_CREATE` promovida de futura para ativa (ADR 034)
- UI de administracao institucional em escopo de roadmap

## Checklist de Implementacao (quando promovido)
- [ ] Adicionar `custom_capabilities: frozenset[Capability] | None` ao aggregate `Role`
- [ ] Atualizar property `capabilities`: verificar `custom_capabilities` antes do `_CAPABILITY_MAP`
- [ ] Novo factory method ou parametro em `create()` para papel customizado com capabilities explicitas
- [ ] Coluna `custom_capabilities` no modelo de persistencia (nullable, serializada como JSON array de strings)
- [ ] Validacao na application: capabilities informadas devem ser valores validos do StrEnum `Capability`
- [ ] Testes de dominio: papel customizado com capabilities corretas, papel pre-definido sem mudanca
- [ ] Testes de integracao: persistencia e reidratacao de `custom_capabilities`
- [ ] Atualizar ADR 034 referenciando este ADR na secao de decisoes futuras
- [ ] Atualizar ADR 033 com o novo campo e impacto na property `capabilities`
