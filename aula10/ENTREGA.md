# Entrega: Assistente de Gestão de Pessoas

**Aluno(s):**
**Até onde chegou:** ( ) Marco mínimo (Etapa 6)  ( ) Marco completo (Etapa 9)  ( ) Etapas 10–11
**Opcionais e bônus feitos:** ( ) 🆕 A  ( ) 🆕 B  ( ) 🆕 C  ( ) Outro: ______

## Etapa 0: quem verifica cada regra?

| Regra | Tema | Quem verifica (função Python / agente / humano) | Por quê | Onde foi implementada (preencha na Etapa 11) |
|---|---|---|---|---|
| N1 | férias | Função Python | É conta: comparar dias com `saldo_ferias_dias`, contar períodos (≤ 3) e checar o mínimo de 5 dias. Resultado exato e determinístico, sem interpretação. | |
| N2 | férias | Função Python | É conta: dias vendidos ≤ 10, gozados + vendidos ≤ saldo e valor = `salario_base / 30`. Valor em dinheiro não pode depender do LLM (o salário é dado restrito). | |
| N3 | férias | Função Python (+ API/cache de feriados) | É calendário: ver se o início cai numa quinta/sexta ou nos 2 dias antes de um feriado. Basta o dia da semana e a lista de feriados. | |
| N4 | prazos | Função Python | É conta de datas: diferença entre a data do pedido e o início (30 dias, 2 dias úteis ou 10 dias, conforme o tipo). | |
| N5 | escala | Função Python | É conta: afastados da equipe que se sobrepõem ao período vs. limite `max(1, floor(30% da equipe))`, sem contar o próprio servidor. (O agente de escala só **sugere** outro período; quem decide se há conflito é o código.) | |
| N6 | abono | Função Python | É conta/calendário: 1 dia útil, não é fim de semana nem feriado, e `abonos_restantes` > 0. | |
| N7 | diária | Função Python (+ API de cotação) | É conta: 1 diária por pernoite + ½ no retorno × valor de `diarias.csv`; no exterior, × cotação do USD do dia. O agente financeiro pode explicar, mas o número vem da função. | |
| N8 | aprovação | Humano (chefia imediata) | Deferir férias/diária é **decisão de alguém** com responsabilidade, não conta nem interpretação: o fluxo pausa e espera a chefia. A parte objetiva (abono dispensa chefia; quem aprova é a chefia do cadastro e nunca o próprio servidor) é checada em Python no servidor MCP. | |
| N9 | saúde | Função Python (guardrail de entrada, regex) + agente classificador de apoio | A parte objetiva (CID, laudo) é pega por regex **antes** de qualquer agente ver o texto: dado de saúde não pode nem chegar ao LLM. Como nem todo pedido de saúde tem CID ("estou com depressão"), o classificador de escopo (agente) cobre o que a regex não pega. O pedido é bloqueado e orientado à junta médica. | |
| N10 | dados | Função Python (guardrail de saída) | Antes de registrar, o despacho passa por uma validação determinística (regex de CPF/CID). Não se confia só na instrução do agente redator: a checagem final tem que ser garantida, não provável. | |

## Etapa 11: os 12 casos

Compare **caminho e estado**, não o texto do despacho.

| Caso | Caminho percorrido | Resultado (bloqueado / pediu dados / triagem humana / indeferido / pausou na chefia / registrado + protocolo) | Bateu com o esperado? |
|---|---|---|---|
| C1_abono_simples | | | |
| C2_ferias_com_venda | | | |
| C3_dado_de_saude | | | |
| C4_fora_do_escopo | | | |
| C5_sem_matricula | | | |
| C6_conflito_de_escala | | | |
| C7_autoaprovacao | | | |
| C8_idempotencia | | | |
| C9_divergencia | | | |
| C10_zona_cinzenta | | | |
| C11_diaria_exterior | | | |
| C12_inicio_proibido | | | |

## O grafo

```mermaid
%% cole aqui a saída de: python etapa07_grafo.py --mermaid
```

## Etapa 4 (pronta): o que eu entendi

- Diferença entre a saída online e a offline:
- Por que a espera do retry dobra a cada tentativa:
- Por que o protocolo é um hash dos campos (e não um número sequencial):
- O que aconteceria sem o cache de feriados:

## Observabilidade (C2)

- Onde o tempo foi gasto:
- Tokens totais: ___

## Opcionais (preencha só os que fez)

- 🆕 A: votos e decisão do C9: ___ ; tempo dos 3 extratores em paralelo ___ s, em sequência ___ s
- 🆕 B: saída do `python etapa06_linear.py --governanca`:
- 🆕 C: caminho do C10 com a triagem humana (sim e não):

## Reflexão (até 3 linhas cada)

1. Quem decide o caminho no seu sistema: o LLM, o grafo, as regras ou um humano? Dê um exemplo de cada.
2. Se o guardrail de entrada falhar, o que ainda impede uma autoaprovação?
3. Por que o nó da chefia não pode gravar nada antes do `interrupt()`?
4. Qual dado veio do **MCP**, qual de **API externa** e qual de **tool local**? Por que essa divisão?
5. O que você mudaria para colocar este sistema em produção?
6. (Só se fez) 🆕 A: votar triplica o custo da extração. Em que pedidos vale a pena?
7. (Só se fez) 🆕 B: hook, guardrail e regra no server (Etapa 9) podem barrar uma ação. Qual a diferença de **onde** cada um atua?
8. (Só se fez) 🆕 C: o que muda quando o humano decide a **entrada** em vez da **saída**? Quem é consultado em cada pausa?

## De onde veio cada parte

| Arquivo / trecho | Exemplo das aulas em que me baseei | O que precisei adaptar |
|---|---|---|
| | | |
