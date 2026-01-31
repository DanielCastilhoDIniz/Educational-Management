
```
docs/use_cases/concluir_matricula.md
```

---

# Caso de Uso — Concluir Matrícula

## 1. Nome

**Concluir Matrícula**

---

## 2. Objetivo

Encerrar formalmente uma matrícula com o status **CONCLUÍDA** quando o estudante estiver **elegível**, consolidando o resultado acadêmico do período letivo e habilitando a emissão de registros oficiais (histórico, certificados, indicadores institucionais).

A conclusão representa o **encerramento definitivo** do vínculo acadêmico do aluno com a turma e o período letivo correspondente.

---

## 3. Atores

* **Secretaria** — execução manual, em casos autorizados.
* **Sistema** — execução automática ao final do período letivo.

> Observação: autorização e controle de acesso são responsabilidades da camada de aplicação.

---

## 4. Comando (Entrada Conceitual)

**ConcluirMatricula**

Parâmetros conceituais:

* `matricula_id` — identificador único da matrícula
* `actor_id` — usuário responsável ou identificador do sistema
* `justificativa` — obrigatória quando a conclusão ocorrer fora do fluxo padrão

---

## 5. Pré-condições (Regras de Domínio)

A matrícula **só pode ser concluída** se **todas** as condições abaixo forem verdadeiras:

1. A matrícula encontra-se no estado **ATIVA**
2. O período letivo associado encontra-se **ENCERRADO**
3. A matrícula é considerada **elegível academicamente**, conforme política institucional vigente
4. Não existem **bloqueios administrativos** aplicáveis à conclusão, conforme políticas institucionais

> As regras de elegibilidade acadêmica e bloqueios administrativos são definidas no `DOMAIN_RULES.md`.

---

## 6. Fluxo Principal

1. Recuperar a matrícula a partir do identificador informado
2. Validar todas as pré-condições de domínio
3. Aplicar a transição de estado **ATIVA → CONCLUÍDA**
4. Registrar:

   * data da conclusão
   * ator responsável
   * justificativa, quando aplicável
5. Persistir a alteração
6. Publicar o evento de domínio **MatriculaConcluida**

---

## 7. Fluxos Alternativos / Exceções

| Situação Detectada                     | Comportamento                                   |
| -------------------------------------- | ----------------------------------------------- |
| Período letivo não encerrado           | Rejeitar a conclusão                            |
| Matrícula não elegível academicamente  | Rejeitar a conclusão                            |
| Bloqueio administrativo identificado   | Rejeitar a conclusão                            |
| Matrícula já concluída                 | Tratar como idempotente (sucesso sem alteração) |
| Matrícula em estado diferente de ATIVA | Rejeitar por estado inválido                    |

---

## 8. Evento de Domínio

### **MatriculaConcluida**

Evento publicado quando a matrícula é concluída com sucesso.

Dados mínimos do evento:

* `matricula_id`
* `occurred_at`
* `actor_id`
* `status_anterior`
* `status_novo`

> O evento comunica **o fato ocorrido**, não executa lógica de negócio e não carrega dados sensíveis.

---

## 9. Regras de Domínio Aplicadas

* `DOMAIN_RULES.md#transicoes-de-matricula`
* `DOMAIN_RULES.md#elegibilidade-academica`
* `DOMAIN_RULES.md#bloqueios-administrativos`
* `DOMAIN_RULES.md#conclusao-de-matricula`

---

## 10. Pós-condições

Após a execução bem-sucedida deste caso de uso:

* A matrícula encontra-se no estado **CONCLUÍDA**
* A transição é **irreversível**
* O evento de domínio foi publicado para consumo por outros componentes do sistema

---

## 11. Observações de Design

* Este caso de uso **não define**:

  * protocolos de transporte
  * formatos de resposta
  * códigos HTTP
  * mecanismos de execução automática
* Detalhes técnicos pertencem às camadas de aplicação e infraestrutura.

---
