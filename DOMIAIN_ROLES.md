
# DOMAIN_RULES.md

**Sistema de Gestão Escolar — Regras de Domínio**

---

## 0. Natureza e Autoridade deste Documento

Este documento define as **regras de domínio** do Sistema de Gestão Escolar.

As regras aqui descritas:

* **não dependem** de tecnologia, banco de dados, API ou interface;
* **devem ser respeitadas** por qualquer meio de entrada no sistema (API, admin, importações, jobs, integrações);
* **têm precedência** sobre decisões técnicas.

Sempre que houver conflito entre código e este documento, **o documento prevalece**.

---

## 1. Linguagem Ubíqua (Glossário Oficial)

Os termos abaixo possuem **significado único e não ambíguo** dentro do sistema.

### 1.1 Instituição

Entidade administrativa responsável por uma ou mais unidades escolares, com autonomia para configurar políticas pedagógicas dentro da legislação vigente.

### 1.2 Unidade Escolar

Estabelecimento físico ou virtual onde ocorrem atividades educacionais (escola, campus, polo).

### 1.3 Período Letivo

Intervalo de datas oficialmente definido para execução de atividades acadêmicas (ano, semestre, módulo).

### 1.4 Turma

Agrupamento de alunos associado a:

* uma unidade escolar,
* um período letivo,
* uma estrutura curricular.

### 1.5 Matrícula

Vínculo acadêmico entre um aluno e uma turma em um determinado período letivo.

> Matrícula **não é** o aluno
> Matrícula **não é** a turma
> Matrícula **é o estado acadêmico do aluno naquela turma e período**

### 1.6 Frequência

Registro de presença ou ausência do aluno em atividades letivas oficialmente contabilizáveis.

### 1.7 Avaliação

Instrumento formal de verificação de aprendizagem, com peso e critérios definidos.

---

## 2. Princípios Gerais do Domínio

As regras abaixo são **invariantes globais**.

1. Nenhuma atividade acadêmica ocorre fora de um **período letivo válido**.
2. Nenhuma informação acadêmica relevante pode existir sem **rastreabilidade temporal e institucional**.
3. Alterações de estado acadêmico **devem ser auditáveis**.
4. Estados acadêmicos possuem **transições explícitas e limitadas**.

---

## 3. Estados Acadêmicos e Invariantes

### 3.1 Estados da Matrícula

Uma matrícula **sempre** se encontra em exatamente um dos estados abaixo:

* `ATIVA`
* `TRANCADA`
* `CANCELADA`
* `CONCLUÍDA`

#### Definições formais

* **ATIVA**
  Matrícula válida para participação em aulas, avaliações e frequência.

* **TRANCADA**
  Matrícula temporariamente suspensa, sem contagem de frequência ou notas durante o período de trancamento.

* **CANCELADA**
  Matrícula encerrada sem conclusão acadêmica (abandono, desistência, transferência).

* **CONCLUÍDA**
  Matrícula encerrada com cumprimento dos critérios acadêmicos definidos.

---

### 3.2 Invariantes da Matrícula

1. Um aluno **não pode possuir mais de uma matrícula ATIVA**:

   * na mesma turma;
   * no mesmo período letivo.

2. Matrículas CANCELADAS ou CONCLUÍDAS **não retornam** ao estado ATIVA.

3. Qualquer mudança de estado:

   * deve registrar data, autor e justificativa (quando aplicável).

---

## 4. Regras de Transição de Estado (Matrícula)

### 4.1 Criação

Uma matrícula **só pode ser criada** se:

* o período letivo estiver ATIVO;
* a turma estiver ATIVA;
* não existir matrícula ATIVA duplicada para o aluno no mesmo contexto.

---

### 4.2 Trancamento

O trancamento é permitido se:

* a matrícula estiver ATIVA;
* o número mínimo de dias letivos decorridos for atingido (parâmetro institucional).

Durante o trancamento:

* não há lançamento de frequência;
* não há lançamento de notas.

---

### 4.3 Cancelamento

O cancelamento:

* pode ocorrer a qualquer momento;
* encerra definitivamente a matrícula;
* gera registro para fins estatísticos e legais (ex: Censo Escolar).

---

### 4.4 Conclusão

Uma matrícula **só pode ser concluída** se:

* o período letivo estiver ENCERRADO;
* os critérios de aprovação forem atendidos.

Conclusão é:

* **automática** ao final do período, quando elegível;
* **irreversível**.

---

## 5. Frequência Acadêmica

### 5.1 Invariantes

1. Frequência só pode ser registrada para:

   * matrícula ATIVA;
   * turma ATIVA;
   * período letivo ATIVO.

2. O percentual mínimo de frequência é:

   * configurável por instituição;
   * nunca inferior ao mínimo legal vigente.

---

### 5.2 Regras de Reprovação por Frequência

* Frequência inferior ao mínimo:

  * **impede aprovação**, salvo exceção pedagógica formalmente registrada.
* Exceções exigem:

  * justificativa;
  * responsável pedagógico autorizado.

---

## 6. Avaliações e Notas

### 6.1 Regras Gerais

1. Avaliações:

   * pertencem a uma turma;
   * possuem peso e critérios explícitos.

2. Notas:

   * só podem ser lançadas para matrícula ATIVA;
   * só podem ser lançadas em avaliações válidas e não encerradas.

---

### 6.2 Média Final

A média final:

* é calculada conforme política institucional;
* pode ser:

  * aritmética,
  * ponderada,
  * modular.

---

## 7. Aprovação, Reprovação e Recuperação

### 7.1 Aprovação

Uma matrícula é considerada APROVADA se:

* frequência ≥ mínima **E**
* média final ≥ mínima **OU**
* recuperação aprovada (se aplicável).

---

### 7.2 Reprovação

Uma matrícula é REPROVADA se:

* pelo menos uma disciplina não atingir os critérios;
* e não houver recuperação válida.

---

## 8. Monitoramento de Evasão (Busca Ativa)

Eventos de alerta são gerados quando ocorre:

* faltas consecutivas acima do limite configurado;
* ausência prolongada;
* percentual crítico de faltas em período parcial.

A matrícula **não pode** ser marcada como evasão sem:

* registro de tentativa de contato;
* justificativa formal.

---

## 9. Eventos de Domínio (Obrigatórios)

Exemplos de eventos relevantes:

* `MatriculaCriada`
* `MatriculaTrancada`
* `MatriculaCancelada`
* `MatriculaConcluida`
* `FrequenciaCriticaDetectada`
* `AlunoElegivelParaAprovacao`

Eventos:

* **não executam lógica de negócio**
* **informam que algo relevante ocorreu**

---

## 10. Configurações Institucionais (Políticas)

Os seguintes parâmetros **não são regras fixas**, mas políticas configuráveis:

* percentual mínimo de frequência;
* nota mínima para aprovação;
* dias mínimos para trancamento;
* modelo de média;
* progressão continuada vs reprovação.

---

## 11. Fora do Escopo do Domínio

Este documento **não define**:

* códigos HTTP;
* nomes de endpoints;
* formatos de payload;
* jobs, filas ou notificações técnicas;
* layout de boletins.

Esses pertencem às camadas de **aplicação e infraestrutura**.

---

## 12. Evolução e Governança

* Toda alteração neste documento:

  * deve ser versionada;
  * deve gerar impacto explícito em testes de domínio.
* Regras novas **não podem contradizer invariantes existentes**.

---


Ação  	    Autoridade        Mínima	Justificativa Exigida?	Evento Gerado
Criar       Matrícula	        Secretário	    Não	            EnrollmentCreated
Trancar     Matrícula	        Secretário	    Sim	            EnrollmentSuspended
Cancelar    Matrícula	        Secretário	    Sim	            EnrollmentCancelled
Concluir    (Regular)	        Sistema (Auto)	Não	            EnrollmentConcluded
Concluir    (Exceção)	        Coordenador	    Sim             (Ata de Conselho)	EnrollmentConcluded
Alterar     Nota (Pós-prazo)	Coordenador	    Sim	            GradeCorrected