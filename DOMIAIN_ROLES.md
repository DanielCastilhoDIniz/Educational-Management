---

# DOMAIN_RULES.md

**Sistema de Gestão Escolar — Regras de Domínio**

---

## 0. Natureza, Autoridade e Escopo deste Documento

Este documento define as **regras centrais do domínio educacional** do Sistema de Gestão Escolar.

As regras aqui descritas:

* **não dependem** de tecnologia, banco de dados, API ou interface;
* **devem ser respeitadas** por qualquer meio de entrada no sistema (API, admin, importações, jobs, integrações);
* **têm precedência** sobre decisões técnicas e de implementação.

Em caso de divergência entre código e este documento, **o domínio prevalece**.

Este documento é a **fonte de verdade do negócio**.

---

## 1. Linguagem Ubíqua (Glossário Oficial)

Os termos abaixo possuem **significado único e não ambíguo** dentro do sistema.

### 1.1 Instituição

Entidade administrativa responsável por uma ou mais unidades escolares, com autonomia para configurar políticas pedagógicas **dentro da legislação vigente**.

### 1.2 Unidade Escolar

Estabelecimento físico ou virtual onde ocorrem atividades educacionais (escola, campus, polo).

### 1.3 Período Letivo

Intervalo de datas oficialmente definido para execução das atividades acadêmicas (ano, semestre ou módulo).

### 1.4 Turma

Agrupamento de alunos associado a:

* uma unidade escolar,
* um período letivo,
* uma estrutura curricular definida.

### 1.5 Matrícula

Vínculo acadêmico entre um aluno e uma turma em um período letivo específico.

> Matrícula **não é** o aluno
> Matrícula **não é** a turma
> Matrícula **é o estado acadêmico do aluno naquela turma e período**

A Matrícula é tratada como **Aggregate Root** do domínio acadêmico.

### 1.6 Frequência

Registro de presença ou ausência do aluno em atividades letivas oficialmente contabilizáveis.

### 1.7 Avaliação

Instrumento formal de verificação de aprendizagem, com critérios, pesos e regras definidos.

---

## 2. Princípios Fundamentais do Domínio

As regras abaixo são **invariantes globais**, válidas em todo o sistema:

1. Nenhuma atividade acadêmica ocorre fora de um **período letivo válido**.
2. Nenhuma informação acadêmica relevante existe sem **rastreabilidade temporal, institucional e de autoria**.
3. Alterações de estado acadêmico **devem ser auditáveis**.
4. Estados acadêmicos possuem **transições explícitas, limitadas e irreversíveis quando finais**.

---

## 3. Estados Acadêmicos da Matrícula

> **Nota de alinhamento (fonte de verdade × implementação)**
>
> Este documento usa linguagem ubíqua em PT-BR (ex.: **ATIVA**, **TRANCADA**).
> Na implementação, os estados são representados por um enum em inglês.
> A equivalência oficial é:
>
> - **ATIVA** ↔ `ACTIVE`
> - **TRANCADA** ↔ `SUSPENDED` *(termo técnico no código: “suspensão” / “trancamento” no negócio)*
> - **CANCELADA** ↔ `CANCELLED`
> - **CONCLUÍDA** ↔ `CONCLUDED`
>
> Sempre que houver divergência de nomenclatura, **o significado do estado (definição formal abaixo) prevalece**.

### 3.1 Estados Possíveis

Uma matrícula **sempre** se encontra em exatamente um dos estados abaixo:

- `ATIVA` (`ACTIVE`)
- `TRANCADA` (`SUSPENDED`)
- `CANCELADA` (`CANCELLED`)
- `CONCLUÍDA` (`CONCLUDED`)

### 3.2 Definições Formais

- **ATIVA** (`ACTIVE`)
  Matrícula válida para participação em aulas, avaliações e contagem de frequência.

- **TRANCADA** (`SUSPENDED`)
  Matrícula temporariamente suspensa, sem lançamento de notas ou frequência durante o período de trancamento/suspensão.

- **CANCELADA** (`CANCELLED`)
  Matrícula encerrada sem conclusão acadêmica (abandono, desistência, transferência).

- **CONCLUÍDA** (`CONCLUDED`)
  Matrícula encerrada com cumprimento dos critérios acadêmicos definidos.



---

## 4. Invariantes da Matrícula

1. Um aluno **não pode possuir mais de uma matrícula ATIVA**:

   * na mesma turma;
   * no mesmo período letivo.

2. Matrículas em estado CANCELADA (CANCELLED) ou CONCLUÍDA (CONCLUDED) são estados finais e não podem retornar ao estado ATIVA (ACTIVE).

3. Toda transição de estado deve:

   * registrar data e hora;
   * identificar o ator responsável (usuário ou sistema);
   * registrar justificativa quando exigido por política.

---

## 5. Regras de Transição de Estado

> **Escopo deste capítulo**
>
> Este capítulo define as transições de estado **no nível do Aggregate Matrícula**.
> Regras que dependem de contexto externo (Turma/Período Letivo) ou de políticas institucionais
> são tratadas como **pré-condições de Application Service** ou como **políticas configuráveis**.

### 5.1 Criação da Matrícula

A criação de uma matrícula (estado inicial `ATIVA`) exige as seguintes pré-condições **fora do aggregate**:

- o período letivo deve estar válido para matrícula (regra do domínio acadêmico/política institucional);
- a turma deve estar válida para receber alunos (regra do domínio de turmas);
- não pode existir matrícula `ATIVA` duplicada para o mesmo aluno no mesmo contexto (turma + período).

Efeitos:

- o estado inicial deve ser `ATIVA` (`ACTIVE`);
- deve ser registrado `created_at` e o ator responsável;
- deve ser gerado o evento de domínio `EnrollmentCreated` quando aplicável.

---

### 5.2 Trancamento (Suspensão) da Matrícula

**Trancamento** (linguagem do negócio) corresponde tecnicamente ao estado `SUSPENDED`.

O trancamento é permitido quando:

- a matrícula estiver `ATIVA` (`ACTIVE`).

É obrigatória justificativa formal.

Durante o trancamento:

- não há lançamento de frequência;
- não há lançamento de notas.

Efeitos:

- estado passa para `TRANCADA` (`SUSPENDED`);
- `suspended_at` torna-se obrigatório;
- `concluded_at` e `cancelled_at` devem estar vazios;
- deve ser gerado evento `EnrollmentSuspended`.

> **Política Institucional (se aplicável)**
>
> A regra “dias mínimos para trancamento” é uma **política configurável** e, quando adotada,
> deve ser verificada na camada de Application (por depender do calendário do período letivo).

---

### 5.3 Reativação da Matrícula

A reativação é permitida quando:

- a matrícula estiver `TRANCADA` (`SUSPENDED`).

É recomendável exigir justificativa (política), mas o mínimo obrigatório é registrar ator e data.

Efeitos:

- estado retorna para `ATIVA` (`ACTIVE`);
- `suspended_at` deve ser limpo;
- `concluded_at` e `cancelled_at` devem estar vazios;
- pode gerar evento `EnrollmentReactivated` (quando adotado como evento oficial do domínio).

---

### 5.4 Cancelamento da Matrícula

O cancelamento:

- pode ocorrer enquanto a matrícula **não estiver em estado final**;
- encerra definitivamente o vínculo acadêmico;
- exige justificativa formal.

Efeitos:

- estado passa para `CANCELADA` (`CANCELLED`);
- `cancelled_at` torna-se obrigatório;
- `concluded_at` e `suspended_at` devem estar vazios;
- deve ser gerado evento `EnrollmentCancelled`;
- gera registros obrigatórios para fins estatísticos e legais (ex.: Censo Escolar), conforme requisitos do produto.

---

### 5.5 Conclusão da Matrícula

A conclusão é permitida quando:

- a matrícula estiver `ATIVA` (`ACTIVE`);
- existir um **veredito de conclusão** válido (política pedagógica), com razões e exigência de justificativa quando aplicável.

A conclusão é:

- automática ao final do período quando elegível (quando existir motor de regras/rotina);
- manual e excepcional, quando autorizada por instância pedagógica;
- irreversível.

Efeitos:

- estado passa para `CONCLUÍDA` (`CONCLUDED`);
- `concluded_at` torna-se obrigatório;
- `cancelled_at` e `suspended_at` devem estar vazios;
- deve ser gerado evento `EnrollmentConcluded`.

> **Observação importante**
>
> Regras como “período letivo ENCERRADO” são pré-condições externas ao aggregate,
> pois dependem do estado do Período Letivo.

---

### 5.6 Estados Finais e Idempotência

Estados finais:

- `CANCELADA` (`CANCELLED`)
- `CONCLUÍDA` (`CONCLUDED`)

Regras:

- transições a partir de estado final são proibidas e devem resultar em erro de domínio;
- comandos repetidos no mesmo estado final podem ser tratados como idempotentes (sem efeito), quando apropriado.

---
## 6. Frequência Acadêmica

> **Escopo e fronteira**
>
> Frequência é um subdomínio operacional que depende de:
> - Estado da Matrícula (ATIVA/TRANCADA/CANCELADA/CONCLUÍDA)
> - Estado da Turma
> - Estado do Período Letivo
>
> O Aggregate Matrícula garante apenas seu próprio estado.
> Validações que dependem de Turma/Período Letivo devem ser aplicadas na camada Application
> (ou no contexto responsável por Turmas/Períodos).

### 6.1 Invariantes (Regra de Negócio)

A frequência só pode ser registrada se, simultaneamente:

- a matrícula estiver `ATIVA`;
- a turma estiver `ATIVA`;
- o período letivo estiver `ATIVO`.

> **Observação técnica (implementação)**
>
> A verificação “matrícula ATIVA” é interna ao domínio da Matrícula.
> As verificações “turma ATIVA” e “período ATIVO” são dependências externas e devem ser garantidas pelo caso de uso.

### 6.2 Percentual Mínimo de Frequência

O percentual mínimo de frequência:

- é configurável por instituição;
- **nunca pode ser inferior ao mínimo legal vigente**.

### 6.3 Reprovação por Frequência

Frequência inferior ao mínimo:

- impede aprovação,
- salvo exceção pedagógica formal.

Exceções exigem:

- justificativa documentada;
- autorização de responsável pedagógico (ver Matriz de Autoridade).

### 6.4 Eventos derivados de Frequência (Fronteira)

Alertas como “frequência crítica” ou “ausência prolongada”:

- pertencem ao contexto de Frequência/Monitoramento;
- podem referenciar uma matrícula,
- mas **não** devem ser emitidos pelo Aggregate Matrícula.

---

## 7. Avaliações e Notas

> **Escopo e fronteira**
>
> Avaliações/Notas pertencem ao contexto de Avaliação e dependem de:
> - Estado da Matrícula
> - Calendário do Período Letivo
> - Configurações de avaliação da Turma/Disciplina
>
> O Aggregate Matrícula garante apenas seu próprio estado.
> Regras de calendário, pesos, recuperação e prazos devem ser tratadas no contexto de Avaliação
> e/ou validadas na camada Application.

### 7.1 Invariantes (Regra de Negócio)

Notas só podem ser lançadas quando:

- a matrícula estiver `ATIVA`;
- a turma estiver `ATIVA`;
- o período letivo estiver `ATIVO`;
- a avaliação estiver dentro de janela/prazo permitido.

> **Observação técnica**
>
> Apenas “matrícula ATIVA” é verificação interna ao domínio da Matrícula.
> As demais dependem de Turma/Período e calendário de avaliação.

### 7.2 Alterações e Retificações

Alterações de nota após prazo:

- exigem justificativa formal;
- exigem autoridade pedagógica conforme Matriz de Autoridade;
- devem registrar auditoria completa (quem, quando, antes/depois, motivo).

### 7.3 Eventos derivados de Avaliação (Fronteira)

Eventos como “nota corrigida”, “recuperação aplicada”, “apto para conselho”:

- pertencem ao contexto de Avaliação/Resultados;
- podem referenciar matrícula,
- mas **não** devem ser emitidos pelo Aggregate Matrícula.

---
## 8. Resultado Acadêmico e Conselho

> **Escopo e fronteira**
>
> Resultado acadêmico (aprovação/reprovação/recuperação) é uma decisão pedagógica
> derivada de notas e frequência. Depende de:
> - Regras pedagógicas configuráveis
> - Consolidação de avaliações
> - Frequência mínima
> - Decisões de conselho (quando aplicável)
>
> O Aggregate Matrícula não calcula resultado; ele apenas controla o vínculo e seu estado.

### 8.1 Invariantes (Regra de Negócio)

O resultado acadêmico:

- deve ser calculado/registrado apenas se a matrícula estiver `ATIVA` ou em encerramento regular;
- não pode “aprovar/reprovar” matrículas `CANCELADAS` ou `CONCLUÍDAS` como se estivessem em curso.

### 8.2 Conselho e Exceções

Decisões excepcionais:

- exigem registro formal (ata);
- exigem autoridade pedagógica (Coordenador ou instância definida);
- devem ser auditáveis e rastreáveis.

### 8.3 Relação com Conclusão da Matrícula

A conclusão da matrícula (`CONCLUÍDA`) é um estado do vínculo e pode depender de:

- veredito elegível (aprovado/concluiu requisitos);
- políticas de encerramento institucional.

A validação de “veredito” pertence ao contexto pedagógico, mas a transição de estado pertence ao Aggregate Matrícula.

---

## 9. Evasão e Abandono

> **Escopo e fronteira**
>
> Evasão/abandono são classificações administrativas/pedagógicas derivadas de sinais operacionais,
> como ausência prolongada e falta de participação.
> Isso depende de dados de frequência, calendário e acompanhamento,
> e não é responsabilidade do Aggregate Matrícula por si só.

### 9.1 Regras Gerais

Um caso pode ser considerado evasão/abandono quando:

- houver ausência prolongada conforme política institucional;
- houver tentativa de contato/documentação conforme processo definido;
- houver confirmação administrativa/pedagógica conforme Matriz de Autoridade.

### 9.2 Ações possíveis

Ao confirmar evasão/abandono, ações comuns incluem:

- abertura de atendimento/registro;
- notificação de responsáveis;
- recomendação de cancelamento, quando permitido.

> O cancelamento, quando aplicado, deve seguir o Cap. 5 (transição formal para `CANCELADA`).

### 9.3 Eventos derivados de Evasão (Fronteira)

Eventos como “evasão detectada” ou “abandono confirmado”:

- pertencem ao contexto de Monitoramento/Atendimento;
- podem referenciar matrícula,
- mas não devem ser emitidos pelo Aggregate Matrícula.

---

## 10. Eventos de Domínio — Contrato Arquitetural

### 10.1 Definição

Eventos de domínio representam **fatos relevantes que já ocorreram** no negócio.
Eles:

- **não executam regras de negócio**;
- **não tomam decisões**;
- **apenas comunicam fatos** para consumo por outras partes do sistema (relatórios, integrações, automações).

Eventos **não representam intenções** (comandos). Representam consequências válidas após regras satisfeitas.

---

### 10.2 Origem, Autoridade e Dependências (Regra Arquitetural)

1) **Origem exclusiva no Domínio**
- Eventos são criados **apenas** por entidades/aggregates do domínio, no momento da transição válida.
- É proibido instanciar eventos de domínio na camada Application ou Infrastructure simulando fatos.

2) **Sem dependências técnicas**
- Eventos não dependem de framework, banco, fila, serializer, HTTP ou ORM.

3) **Imutabilidade**
- Eventos são imutáveis após criação.

---

### 10.3 Eventos Oficiais do Aggregate Matrícula (Enrollment)

Eventos oficiais emitidos pelo Aggregate Matrícula:

- `EnrollmentSuspended` (ATIVA → TRANCADA/SUSPENDED)
- `EnrollmentReactivated` (TRANCADA/SUSPENDED → ATIVA)
- `EnrollmentCancelled` (ATIVA/TRANCADA → CANCELADA/CANCELLED)
- `EnrollmentConcluded` (ATIVA → CONCLUÍDA/CONCLUDED)

> **Nota sobre `EnrollmentCreated`**
>
> `EnrollmentCreated` pode existir como evento do domínio, porém só deve ser tratado como “oficial”
> quando a criação for encapsulada por uma factory/serviço de domínio que registre o evento.
> Até lá, a criação deve ser tratada como fato auditável (log/auditoria) sem evento obrigatório.

---

### 10.4 Eventos que NÃO pertencem ao Aggregate Matrícula

Eventos como:

- `AttendanceCriticalDetected`
- `StudentEligibleForApproval`
- `GradeCorrected`

não pertencem ao Aggregate Matrícula e devem ser emitidos pelos contextos responsáveis
por frequência, avaliação/notas e resultado acadêmico, embora possam **referenciar** uma matrícula.

---

### 10.5 Payload Mínimo Obrigatório (Contrato de Interoperabilidade)

Todo evento oficial do Aggregate Matrícula deve conter, no mínimo:

- `aggregate_id` (id da matrícula)
- `actor_id` (quem realizou: usuário ou sistema)
- `from_state` (estado anterior)
- `to_state` (estado novo)
- `occurred_at` (data/hora)
- `justification` (quando aplicável)

---

### 10.6 Ordem Obrigatória (Consistência Transacional)

A emissão/publicação deve respeitar a sequência:

1. regra validada no domínio
2. estado alterado no aggregate
3. evento registrado internamente no aggregate
4. aggregate persistido com sucesso
5. eventos extraídos pelo application service
6. publicação realizada pela infraestrutura (ex.: outbox, fila, webhook, log)

É proibido publicar evento se a persistência falhar.

---

### 10.7 Extração e Não-Duplicidade

- Eventos devem ser extraídos explicitamente após o caso de uso (pull).
- Após extração, o aggregate não deve reter eventos antigos.
- Comandos idempotentes (ex.: repetir cancelamento em CANCELADA) podem resultar em “sem efeito” e “sem novo evento”.


---

## 11. Políticas Institucionais Configuráveis

> **Objetivo**
>
> Políticas institucionais são parâmetros do domínio que variam por instituição/rede/unidade
> e influenciam regras de frequência, avaliação, prazos e exceções.
>
> Elas devem ser:
> - explicitamente nomeadas;
> - versionáveis e auditáveis;
> - validadas em camada apropriada;
> - aplicadas de forma determinística.

> **Fronteira de validação**
>
> - **Domain (Aggregate Matrícula)** valida apenas invariantes internas (estado, timestamps, transições).
> - **Application / Contextos especializados** validam políticas que dependem de calendário, turma, período letivo,
>   frequência e avaliação.

---

### 11.1 Catálogo de Políticas (mínimo recomendado)

#### P01 — Frequência mínima (%)
- **Chave:** `attendance.minimum_percentage`
- **Tipo:** inteiro (0–100)
- **Padrão sugerido:** 75
- **Restrição legal:** nunca inferior ao mínimo legal vigente
- **Onde validar:** Application / Contexto de Frequência
- **Efeito:** reprovação por frequência quando abaixo do mínimo (salvo exceção formal)

#### P02 — Janela de lançamento de frequência (dias)
- **Chave:** `attendance.posting_window_days`
- **Tipo:** inteiro (>= 0)
- **Padrão sugerido:** 7
- **Onde validar:** Contexto de Frequência
- **Efeito:** impede lançamentos fora do prazo sem retificação autorizada

#### P03 — Janela de lançamento de notas (dias)
- **Chave:** `grades.posting_window_days`
- **Tipo:** inteiro (>= 0)
- **Padrão sugerido:** 7
- **Onde validar:** Contexto de Avaliação/Notas
- **Efeito:** impede lançamento/alteração de notas após prazo

#### P04 — Retificação de nota pós-prazo (permitido?)
- **Chave:** `grades.allow_late_correction`
- **Tipo:** boolean
- **Padrão sugerido:** true
- **Onde validar:** Contexto de Avaliação + Matriz de Autoridade
- **Efeito:** permite correção com justificativa e autoridade definida

#### P05 — Trancamento mínimo após início (dias)
- **Chave:** `enrollment.suspension_min_days_after_start`
- **Tipo:** inteiro (>= 0)
- **Padrão sugerido:** 0
- **Onde validar:** Application (depende de calendário do período letivo)
- **Efeito:** bloqueia trancamento antes do mínimo (quando adotado)

#### P06 — Conclusão automática ao encerrar período (habilitada?)
- **Chave:** `enrollment.auto_conclude_on_period_close`
- **Tipo:** boolean
- **Padrão sugerido:** true
- **Onde validar:** Application (rotina/scheduler) + Contexto pedagógico (veredito)
- **Efeito:** aciona rotina do Sistema para concluir matrículas elegíveis

#### P07 — Exceção pedagógica permitida (conselho)
- **Chave:** `pedagogy.allow_exceptional_approval`
- **Tipo:** boolean
- **Padrão sugerido:** true
- **Onde validar:** Contexto pedagógico + Matriz de Autoridade
- **Efeito:** permite aprovação/conclusão excepcional com ata e autoridade

#### P08 — Critério de evasão/abandono (dias de ausência)
- **Chave:** `dropout.absence_days_threshold`
- **Tipo:** inteiro (>= 0)
- **Padrão sugerido:** 15
- **Onde validar:** Contexto de Monitoramento/Frequência
- **Efeito:** sinaliza caso para atendimento; não cancela automaticamente matrícula

---

### 11.2 Regras de Auditoria e Mudança de Políticas

- Toda alteração de política deve registrar:
  - quem alterou (ator)
  - quando (timestamp)
  - valor anterior e valor novo
  - justificativa (quando aplicável)
- Mudanças devem ser aplicadas de forma determinística:
  - se a instituição exigir, políticas podem ser “congeladas” por período letivo (evita retroatividade indevida).

---

### 11.3 Relação com Matriz de Autoridade

Políticas que habilitam exceções (ex.: retificação pós-prazo, aprovação excepcional):

- exigem justificativa documentada;
- exigem autoridade mínima conforme Cap. 12.2;
- devem produzir trilha de auditoria completa.

### 11.4 Tabela de Implementação das Políticas (Contrato Operacional)

> **Hierarquia sugerida de escopo**
>
> 1) Instituição/Rede (padrão global)
> 2) Unidade (override)
> 3) Período Letivo (congelamento/versão por ciclo)
>
> A resolução final deve ser determinística: o escopo mais específico prevalece.

| Política (Chave)                               | Escopo Recom.        | Armazenamento (conceito)                | Quem consulta (use cases/contextos)                              | Quem pode alterar (autoridade mínima) | Versão / Congelamento | Efeito no domínio (resumo) |
| ---------------------------------------------- | -------------------- | --------------------------------------- | ---------------------------------------------------------------- | ------------------------------------- | ---------------------- | -------------------------- |
| `attendance.minimum_percentage`                | Instituição/Unidade  | Configuração institucional              | Frequência: registrar, calcular situação                         | Administrador Institucional           | Congelar por período   | Define mínimo de aprovação por frequência |
| `attendance.posting_window_days`               | Unidade/Período      | Configuração + calendário do período    | Frequência: lançamento/retificação                               | Administrador Institucional           | Congelar por período   | Bloqueia lançamento fora da janela |
| `grades.posting_window_days`                   | Unidade/Período      | Configuração + calendário do período    | Avaliação/Notas: lançamento/retificação                           | Administrador Institucional           | Congelar por período   | Bloqueia lançamento fora da janela |
| `grades.allow_late_correction`                 | Unidade/Período      | Configuração institucional              | Avaliação/Notas: correção pós-prazo                               | Administrador Institucional           | Congelar por período   | Habilita correção com justificativa e autoridade |
| `enrollment.suspension_min_days_after_start`   | Período              | Configuração do período (calendário)    | Matrícula: trancar (Application)                                  | Administrador Institucional           | Por período            | Impede trancar antes do mínimo |
| `enrollment.auto_conclude_on_period_close`     | Período              | Configuração do período + agendamento   | Rotina do Sistema: concluir elegíveis                              | Administrador Institucional           | Por período            | Habilita job automático de conclusão |
| `pedagogy.allow_exceptional_approval`          | Instituição/Período  | Configuração pedagógica institucional   | Conselho/Resultado: exceções                                      | Administrador + Coordenação*          | Congelar por período   | Permite aprovação/conclusão excepcional com ata |
| `dropout.absence_days_threshold`               | Unidade/Período      | Configuração + regras de monitoramento  | Monitoramento/Evasão: detecção e abertura de caso                 | Administrador Institucional           | Congelar por período   | Dispara sinalização; não cancela matrícula |

\* Quando política impactar decisão pedagógica, recomenda-se exigir coautoria/validação da Coordenação.

---

### 11.5 Resolução, Cache e Auditoria (Regras Operacionais)

**Resolução de valores**
- Ao consultar uma política, o sistema deve resolver na ordem:
  1) valor específico do Período Letivo (se existir)
  2) override da Unidade (se existir)
  3) padrão da Instituição/Rede
- Em caso de ausência total, aplicar padrão definido no catálogo.

**Cache**
- É permitido cache de leitura, desde que:
  - invalidado imediatamente após alteração;
  - auditável (é possível saber qual valor estava vigente).

**Auditoria**
Toda alteração deve registrar:
- ator (quem alterou)
- data/hora
- escopo afetado (instituição/unidade/período)
- valor anterior e valor novo
- justificativa (quando aplicável)
---

## 12. Papéis, Autorizações e Responsabilidades

### 12.1 Papéis

> **Regra geral**
>
> Autorizações são concedidas por **papel** e limitadas por **escopo** (Unidade/Turma/Período Letivo),
> respeitando o princípio do privilégio mínimo.
> Toda ação relevante deve registrar **autor**, **data/hora** e, quando exigido, **justificativa**.

* **Administrador Institucional**
  - Possui autoridade para configurar políticas institucionais (parâmetros) e administrar usuários e permissões.
  - Pode auditar operações e corrigir configurações.
  - **Não substitui** o Coordenador em decisões pedagógicas formais (exceções acadêmicas).

* **Secretário Escolar**
  - Responsável por operações administrativas do ciclo de matrícula, incluindo:
    - criar matrícula, trancar/suspender, reativar e cancelar (quando permitido pela matriz de autoridade).
  - Deve registrar justificativa nas ações em que ela é obrigatória.
  - Não pode autorizar exceções pedagógicas (ex.: conclusão excepcional) sem validação do responsável pedagógico.

* **Coordenador Pedagógico**
  - Responsável por decisões pedagógicas e exceções acadêmicas, incluindo:
    - conclusão excepcional (com ata/registro formal);
    - validação de exceções em frequência/avaliação quando previstas em política.
  - Atua como instância de decisão em casos de conflito acadêmico.

* **Professor**
  - Pode lançar frequência e notas **apenas** nas turmas em que está alocado.
  - Não pode alterar estado da matrícula (criar/trancar/reativar/cancelar/concluir), salvo se política institucional definir exceções explícitas.

* **Sistema (Ator Técnico)**
  - Representa rotinas automáticas, jobs e processos agendados autorizados pela instituição.
  - Pode executar ações automáticas previstas, como “Concluir (Automática)”, desde que:
    - a regra/política aplicável seja satisfeita;
    - a ação seja auditável (registro de data/hora e autoria como `Sistema`).
  - O Sistema **não** executa exceções pedagógicas que exijam autoridade humana (ex.: conclusão excepcional).


### 12.2 Matriz de Autoridade (Resumo)

| Ação                      | Autoridade Mínima | Justificativa | Evento                   |
| ------------------------- | ----------------- | ------------- | ------------------------ |
| Criar Matrícula           | Secretário        | Não           | EnrollmentCreated*       |
| Trancar Matrícula         | Secretário        | Sim           | EnrollmentSuspended      |
| Reativar Matrícula        | Secretário        | Sim           | EnrollmentReactivated    |
| Cancelar Matrícula        | Secretário        | Sim           | EnrollmentCancelled      |
| Concluir (Automática)     | Sistema           | Não**         | EnrollmentConcluded      |
| Concluir (Exceção)        | Coordenador       | Sim (Ata)     | EnrollmentConcluded      |
| Alterar Nota Pós-Prazo    | Coordenador       | Sim           | GradeCorrected***        |

\* `EnrollmentCreated` só deve ser considerado **evento oficial** quando a criação de matrícula for encapsulada por factory/serviço que registre evento; caso contrário, tratar como fato auditável sem evento.

\** A conclusão pode exigir justificativa conforme veredito/política pedagógica aplicada.

\*** `GradeCorrected` não pertence ao Aggregate Matrícula; deve ser emitido pelo contexto responsável por notas/avaliações.

---

## 13. Multi-tenancy e Segurança de Escopo

* **Isolamento por Unidade:** usuários não acessam dados de outras unidades sem vínculo explícito.
* **Princípio do Privilégio Mínimo:** acesso restrito ao necessário.
* **Auditoria de Acesso:** leituras de dados sensíveis devem ser auditadas.

---

## 14. Evolução e Governança

* Toda alteração neste documento:

  * deve ser versionada;
  * deve gerar impacto explícito em testes de domínio.
* Regras novas **não podem contradizer invariantes existentes**.

---
