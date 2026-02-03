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

### 3.1 Estados Possíveis

Uma matrícula **sempre** se encontra em exatamente um dos estados abaixo:

* `ATIVA`
* `TRANCADA`
* `CANCELADA`
* `CONCLUÍDA`

### 3.2 Definições Formais

* **ATIVA**
  Matrícula válida para participação em aulas, avaliações e contagem de frequência.

* **TRANCADA**
  Matrícula temporariamente suspensa, sem lançamento de notas ou frequência durante o período de trancamento.

* **CANCELADA**
  Matrícula encerrada sem conclusão acadêmica (abandono, desistência, transferência).

* **CONCLUÍDA**
  Matrícula encerrada com cumprimento dos critérios acadêmicos definidos.

---

## 4. Invariantes da Matrícula

1. Um aluno **não pode possuir mais de uma matrícula ATIVA**:

   * na mesma turma;
   * no mesmo período letivo.

2. Matrículas em estado `CANCELADA` ou `CONCLUÍDA` são **estados finais** e **não podem retornar** ao estado `ATIVA`.

3. Toda transição de estado deve:

   * registrar data e hora;
   * identificar o ator responsável (usuário ou sistema);
   * registrar justificativa quando exigido por política.

---

## 5. Regras de Transição de Estado

### 5.1 Criação da Matrícula

Uma matrícula só pode ser criada se:

* o período letivo estiver ATIVO;
* a turma estiver ATIVA;
* não existir matrícula ATIVA duplicada para o aluno no mesmo contexto.

---

### 5.2 Trancamento

O trancamento é permitido se:

* a matrícula estiver ATIVA;
* o número mínimo de dias letivos decorridos tiver sido atingido (parâmetro institucional).

Durante o trancamento:

* não há lançamento de frequência;
* não há lançamento de notas.

---

### 5.3 Cancelamento

O cancelamento:

* pode ocorrer a qualquer momento enquanto a matrícula não for final;
* encerra definitivamente o vínculo acadêmico;
* gera registros obrigatórios para fins estatísticos e legais (ex.: Censo Escolar).

---

### 5.4 Conclusão

Uma matrícula só pode ser concluída se:

* o período letivo estiver ENCERRADO;
* os critérios de aprovação forem atendidos.

A conclusão é:

* **automática** ao final do período quando elegível;
* **manual e excepcional**, quando autorizada por instância pedagógica;
* **irreversível**.

---

## 6. Frequência Acadêmica

### 6.1 Invariantes

1. Frequência só pode ser registrada para:

   * matrícula ATIVA;
   * turma ATIVA;
   * período letivo ATIVO.

2. O percentual mínimo de frequência:

   * é configurável por instituição;
   * **nunca pode ser inferior ao mínimo legal vigente**.

### 6.2 Reprovação por Frequência

* Frequência inferior ao mínimo **impede aprovação**, salvo exceção pedagógica formal.
* Exceções exigem:

  * justificativa documentada;
  * autorização de responsável pedagógico.

---

## 7. Avaliações, Notas e Resultado Acadêmico

### 7.1 Avaliações

* pertencem a uma turma;
* possuem pesos e critérios explícitos;
* seguem o modelo de avaliação institucional.

### 7.2 Notas

* só podem ser lançadas para matrícula ATIVA;
* só podem ser lançadas em avaliações válidas e não encerradas.

### 7.3 Média Final

A média final é calculada conforme política institucional, podendo ser:

* aritmética;
* ponderada;
* modular.

---

## 8. Aprovação, Reprovação e Recuperação

### 8.1 Aprovação

Uma matrícula é APROVADA se:

* frequência ≥ mínima **E**
* média final ≥ mínima
  **OU**
* recuperação for aprovada, quando aplicável.

### 8.2 Reprovação

Uma matrícula é REPROVADA se:

* pelo menos uma disciplina não atender aos critérios;
* e não houver recuperação válida.

---

## 9. Monitoramento de Evasão (Busca Ativa)

Alertas devem ser gerados quando ocorrer:

* faltas consecutivas acima do limite configurado;
* ausência prolongada;
* percentual crítico de faltas em período parcial.

Uma matrícula **não pode ser classificada como evasão** sem:

* registro de tentativa de contato;
* justificativa formal.

---

## 10. Eventos de Domínio

Eventos de domínio representam **fatos relevantes que já ocorreram**.

Exemplos:

* `EnrollmentCreated`
* `EnrollmentSuspended`
* `EnrollmentCancelled`
* `EnrollmentConcluded`
* `AttendanceCriticalDetected`
* `StudentEligibleForApproval`

Eventos:

* **não executam regras de negócio**
* **não tomam decisões**
* **apenas comunicam fatos consumidos por outras partes do sistema**

---

## 11. Políticas Institucionais (Configuráveis)

Não são invariantes do domínio, mas parâmetros configuráveis:

* percentual mínimo de frequência;
* nota mínima para aprovação;
* dias mínimos para trancamento;
* modelo de cálculo de média;
* progressão continuada vs. reprovação.

---

## 12. Papéis, Autorizações e Responsabilidades

### 12.1 Papéis

* **Administrador Institucional**
  Acesso total às unidades da Instituição.

* **Secretário Escolar**
  Operacionaliza matrículas, trancamentos, cancelamentos e documentos.

* **Coordenador Pedagógico**
  Autoriza exceções acadêmicas e decisões de conselho.

* **Professor**
  Lança notas e frequência apenas nas turmas em que está alocado.

### 12.2 Matriz de Autoridade (Resumo)

| Ação                   | Autoridade Mínima | Justificativa | Evento              |
| ---------------------- | ----------------- | ------------- | ------------------- |
| Criar Matrícula        | Secretário        | Não           | EnrollmentCreated   |
| Trancar Matrícula      | Secretário        | Sim           | EnrollmentSuspended |
| Cancelar Matrícula     | Secretário        | Sim           | EnrollmentCancelled |
| Concluir (Automática)  | Sistema           | Não           | EnrollmentConcluded |
| Concluir (Exceção)     | Coordenador       | Sim (Ata)     | EnrollmentConcluded |
| Alterar Nota Pós-Prazo | Coordenador       | Sim           | GradeCorrected      |

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
