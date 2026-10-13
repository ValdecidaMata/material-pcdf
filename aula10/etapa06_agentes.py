"""
ETAPA 6 -- Os especialistas, cada um com UMA responsabilidade e SÓ as tools de que precisa.

ESQUELETO:
  ETAPA 6.1 -- criar_normas(), criar_escala(), criar_financeiro(), criar_redator()
  ETAPA 6.2 -- criar_coordenador(): usa Normas, Escala e Financeiro como TOOLS (as_tool)

As tools abaixo (PRONTAS) só repassam a chamada ao MCP Server do RH (cliente_mcp.chamar_mcp_async). Dar a cada agente
só as tools dele é o PRIVILÉGIO MÍNIMO (Etapa 9.1); o hook do 🆕 B (etapa10_governanca.py) confere isso em tempo de execução.

REFERÊNCIAS NAS AULAS
  aula4/ex03_agente_as_tool.py                         Coordenador que chama especialistas como tools    <- o mais parecido
  aula2/agente_handoff2.py                             as_tool com tool_name e tool_description
  aula4/ex02_handoff_roteamento.py                     handoff: compare (quem responde no fim?)
  aula7/exemplos/02_agentes_especializados/main.py     uma responsabilidade por agente
  aula7/agentes.py                                     ModelSettings(temperature=0) para respostas mais estáveis
  aula8/exemplos/06_excessive_agency/1_codigo_pronto/main.py   o problema de dar tools DEMAIS a um agente
"""
import json

from agents import Agent, ModelSettings, RunHooks, function_tool

from etapa05_cliente_mcp import chamar_mcp_async
from etapa04_ferramentas import cotacao_usd_brl

CONFIG = ModelSettings(temperature=0)


# ------------------------------------------------------------------ tools (PRONTAS)
@function_tool
async def consultar_normas(tema: str) -> str:
    """Regras da norma interna sobre um tema: férias, prazos, escala, abono, diária, aprovação, saúde ou dados."""
    return json.dumps(await chamar_mcp_async("consultar_normas", {"tema": tema}), ensure_ascii=False)


@function_tool
async def consultar_escala(equipe: str, inicio: str, fim: str) -> str:
    """Afastamentos da equipe que se sobrepõem ao período (AAAA-MM-DD) e o limite de afastados da regra N5."""
    return json.dumps(await chamar_mcp_async("consultar_escala", {"equipe": equipe, "inicio": inicio, "fim": fim}),
                      ensure_ascii=False)


@function_tool
async def tabela_diarias(tipo_destino: str) -> str:
    """Moeda e valor da diária para o tipo de destino: capital, interior ou exterior."""
    return json.dumps(await chamar_mcp_async("tabela_diarias", {"tipo_destino": tipo_destino}), ensure_ascii=False)


@function_tool
async def consultar_remuneracao(matricula: str) -> str:
    """[RESTRITA] Salário-base de um servidor. Só para calcular a venda de férias (N2)."""
    print(f"[tool] consultar_remuneracao({matricula}) EXECUTOU")  # o 🆕 B prova que, barrada, ela NÃO executa
    return json.dumps(await chamar_mcp_async("consultar_remuneracao", {"matricula": matricula}), ensure_ascii=False)


@function_tool
def cotacao_dolar() -> str:
    """Cotação atual do dólar em reais (USD->BRL). Devolve 'indisponível' se a API falhar: nunca invente o câmbio."""
    cotacao = cotacao_usd_brl()
    return f"{cotacao:.4f}" if cotacao else "indisponível"


# ------------------------------------------------------------------ ETAPA 6.1: especialistas
def criar_normas() -> Agent:
    # ETAPA 6.1 -- Agent(name="Normas", instructions=..., tools=[consultar_normas], model_settings=CONFIG)
    #   Responsabilidade: dizer QUAIS regras se aplicam ao pedido e explicá-las em linguagem simples.
    #   NÃO calcula valores, NÃO consulta a escala. Recebe também as violações objetivas (etapa06_regras.py) para explicá-las.
    return Agent(
        name="Normas",
        instructions=(
            "Você é o especialista em NORMAS de RH. Use consultar_normas para buscar as regras do tema do pedido "
            "(férias, prazos, abono, diária, aprovação...) e diga QUAIS regras se aplicam, citando o código (N1..N10), "
            "em linguagem simples. Você recebe também as violações objetivas já calculadas pelo sistema: NÃO as "
            "recalcule nem as contradiga, apenas explique cada uma. Não calcule valores e não consulte a escala. "
            "Responda em português, de forma breve."
        ),
        tools=[consultar_normas],
        model_settings=CONFIG,
    )


def criar_escala() -> Agent:
    # ETAPA 6.1 -- tools=[consultar_escala]. Confere a N5 e, se houver conflito, SUGERE outro período
    #   (com o mesmo número de dias, começando num dia permitido).
    return Agent(
        name="Escala",
        instructions=(
            "Você é o especialista em ESCALA (regra N5). Use consultar_escala com a equipe e o período (AAAA-MM-DD) "
            "e diga se há conflito: quantos colegas da equipe já estão afastados no período e qual o limite. "
            "Desconsidere o próprio servidor do pedido. Se houver conflito, SUGIRA outro período com o MESMO número "
            "de dias, começando DEPOIS do fim do afastamento que conflita, numa segunda, terça ou quarta-feira que não "
            "seja véspera nem antevéspera de feriado (regra N3); confira a sugestão com consultar_escala. "
            "Responda em português, de forma breve."
        ),
        tools=[consultar_escala],
        model_settings=CONFIG,
    )


def criar_financeiro() -> Agent:
    # ETAPA 6.1 -- tools=[tabela_diarias, consultar_remuneracao, cotacao_dolar].
    #   Venda de férias (N2): dias_vendidos x salario_base / 30. Diárias (N7): uma por pernoite + meia no retorno;
    #   no exterior, em USD convertido pela cotação. Mostre a conta. Câmbio indisponível -> "a calcular".
    #   É o ÚNICO agente que vê o salário.
    return Agent(
        name="Financeiro",
        instructions=(
            "Você é o especialista FINANCEIRO e calcula os valores do pedido, mostrando a conta.\n"
            "- Venda de férias (N2): SÓ neste caso consulte consultar_remuneracao (em diária NUNCA consulte o salário); valor = dias_vendidos x salario_base / 30, "
            "em reais, com 2 casas decimais. Informe só o valor da venda: NUNCA repita o salário-base na resposta.\n"
            "- Diárias (N7): consulte tabela_diarias com o tipo_destino INFORMADO no pedido (capital, interior ou exterior; cidade fora do Brasil = exterior); uma diária por dia com pernoite e MEIA "
            "diária no dia do retorno (ex.: de 08 a 11 = 3 pernoites + meia = 3,5 diárias); se receber a quantidade_diarias "
            "já calculada, use-a sem recalcular: valor = quantidade_diarias x valor_diaria. No exterior o valor é em "
            "USD: use cotacao_dolar e converta para reais; se a cotação vier 'indisponível', escreva 'a calcular'.\n"
            "- Abono (folga) não tem valor. Nunca invente valores. Responda em português, de forma breve."
        ),
        tools=[tabela_diarias, consultar_remuneracao, cotacao_dolar],
        model_settings=CONFIG,
    )


def criar_redator() -> Agent:
    # ETAPA 6.1 -- sem tools. Escreve o DESPACHO (deferimento ou indeferimento) usando SÓ os fatos recebidos:
    #   matrícula, período, decisão, regras citadas, valores e, no indeferimento, a sugestão de datas.
    #   Nunca escreve CPF nem dado de saúde (N10). Se receber um feedback (da validação ou da chefia), corrige.
    return Agent(
        name="Redator",
        instructions=(
            "Você redige o DESPACHO administrativo de um pedido de RH (férias, abono ou diária), em português formal "
            "e curto (um parágrafo, texto simples, sem markdown nem título). Use SOMENTE os fatos recebidos: matrícula, tipo, período (datas em DD/MM/AAAA), "
            "decisão, regras citadas (N1..N10), valores calculados e, no indeferimento, a sugestão de datas. "
            "Regras de forma OBRIGATÓRIAS: cite a matrícula; escreva TODAS as datas como DD/MM/AAAA (ex.: 12/07/2027, "
            "nunca '12 de julho'); termine com a frase 'Pedido DEFERIDO.' ou 'Pedido INDEFERIDO.', conforme a DECISÃO "
            "recebida. Só diga que segue para aprovação da chefia imediata se a linha DECISÃO disser isso; "
            "abono deferido e indeferimentos NÃO passam pela chefia. "
            "No INDEFERIMENTO, o motivo é EXATAMENTE a lista de VIOLAÇÕES OBJETIVAS recebida: cite cada código "
            "(ex.: N4) e explique-o; não invente outro motivo nem cite regra que não está nessa lista. "
            "NUNCA escreva CPF, CID, salário ou dado de saúde (N10). "
            "Se receber um FEEDBACK (da validação ou da chefia), reescreva o despacho corrigindo o que foi apontado."
        ),
        model_settings=CONFIG,
    )


# ------------------------------------------------------------------ ETAPA 6.2: coordenador
def criar_coordenador(hooks: RunHooks | None = None, tools_extras: list | None = None) -> Agent:
    # ETAPA 6.2 -- Agent(name="Coordenador", instructions=..., tools=[
    #       criar_normas().as_tool(tool_name="parecer_normas", tool_description=..., hooks=hooks,
    #                              failure_error_function=None),
    #       criar_escala().as_tool(tool_name="parecer_escala", ..., hooks=hooks, failure_error_function=None),
    #       criar_financeiro().as_tool(tool_name="parecer_financeiro", ..., hooks=hooks, failure_error_function=None),
    #       *(tools_extras or [])])
    #   O Coordenador decide QUAIS especialistas consultar (abono não precisa do Financeiro) e junta os pareceres.
    #   hooks=hooks nas as_tool faz o hook do 🆕 B enxergar também as tools DENTRO de cada especialista.
    #   failure_error_function=None: sem isso, um erro dentro do especialista (inclusive o bloqueio do 🆕 B) vira só
    #   um texto de erro para o Coordenador, que segue em frente. Com None, o erro interrompe a execução.
    #   tools_extras serve só para o teste do 🆕 B (dar de propósito consultar_remuneracao ao Coordenador).
    #   Referência: aula4/ex03_agente_as_tool.py
    return Agent(
        name="Coordenador",
        instructions=(
            "Você coordena a análise de um pedido de RH e consulta especialistas (tools) para montar um PARECER.\n"
            "- parecer_normas: sempre (quais regras se aplicam e explicação das violações objetivas).\n"
            "- parecer_escala: OBRIGATÓRIO em férias e em abono (conflito na equipe, regra N5); em diária não.\n"
            "- parecer_financeiro: OBRIGATÓRIO quando dias_vendidos > 0 (venda de férias) e em TODA diária; "
            "nos outros casos (férias sem venda, abono) NÃO consulte. "
            "Abono não tem valor: não consulte o Financeiro.\n"
            "Repasse a cada especialista os dados de que ele precisa (matrícula, equipe, tipo, datas AAAA-MM-DD, "
            "dias vendidos e, na diária, o destino, o tipo_destino e a quantidade_diarias EXATAMENTE como vieram). As violações objetivas recebidas são definitivas: não as contradiga. "
            "Junte os pareceres num texto curto: decisão sugerida (deferir ou indeferir), regras, valores e, se houver "
            "conflito, a sugestão de datas. Nunca informe salário."
        ),
        tools=[
            criar_normas().as_tool(
                tool_name="parecer_normas",
                tool_description="Especialista em normas: quais regras N1..N10 se aplicam ao pedido e por quê.",
                hooks=hooks, failure_error_function=None),
            criar_escala().as_tool(
                tool_name="parecer_escala",
                tool_description="Especialista em escala: conflito de afastamentos na equipe (N5) e sugestão de datas.",
                hooks=hooks, failure_error_function=None),
            criar_financeiro().as_tool(
                tool_name="parecer_financeiro",
                tool_description="Especialista financeiro: valor da venda de férias (N2) ou das diárias (N7).",
                hooks=hooks, failure_error_function=None),
            *(tools_extras or []),
        ],
        model_settings=CONFIG,
    )
