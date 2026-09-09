"""
gerar_dashboard.py — Monta o dashboard HTML de arquivo único.

Divisão de trabalho:
  Python  → lê o banco, aplica as regras, roda os casos-teste, calcula o
            crosscheck e achata a base em arrays.
  JavaScript → filtra, agrega e desenha. Nenhum agregado é pré-calculado:
            todo número na tela é função pura do subconjunto filtrado.

O Chart.js vai embutido no arquivo. O HTML final abre com duplo clique, sem
servidor e sem rede.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, "data", "fiel_torcedor.db")
DIR_DASH = os.path.join(RAIZ, "dashboard")
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template_dashboard.html")
CHARTJS = os.path.join(RAIZ, "vendor", "chart.umd.js")

# Cortes de faixa de engajamento — os mesmos do schema SQL. Duplicar aqui
# seria criar fonte paralela, então o valor vem do banco via a view.
COLUNAS = [
    "socio_id", "plano", "regiao", "canal_aquisicao", "faixa_engajamento",
    "coorte_12m_completa", "retido_12m", "ativo", "cac", "margem_m12",
    "margem_total", "moedas_mes", "jogos_comparecidos", "pontos_regra_atual",
    "meses_ativos", "distancia_arena_km", "mes_adesao", "comissao_parceiros_m12",
    "custo_cupom_total", "cupons_emitidos", "cupons_resgatados", "no_shows",
    "ingressos_liberados", "transacoes_parceiros",
]


def carregar() -> pd.DataFrame:
    con = sqlite3.connect(DB)
    df = pd.read_sql(f"SELECT {', '.join(COLUNAS)} FROM vw_socio_economia", con)
    con.close()

    # Perfil de presença: classificação comportamental, derivada uma vez.
    df["perfil_presenca"] = pd.cut(
        df["jogos_comparecidos"], bins=[-1, 0, 3, 10**9],
        labels=["Nunca foi ao estádio", "Foi 1 a 3 vezes", "Frequentador (4+)"],
    ).astype(str)
    return df


def casos_teste(df: pd.DataFrame) -> list[dict]:
    """Casos com o esperado calculado à mão, fora do código que produz o número."""
    casos = []

    # 1. Fiel Digital nunca pontua pela regra vigente (pontos_por_jogo = 0),
    #    mesmo quando o sócio comparece a jogos comprados na venda geral.
    fd = df[df["plano"] == "Fiel Digital"]
    casos.append({
        "caso": "Fiel Digital tem pontuação zero pela regra vigente",
        "esperado": "0",
        "obtido": f"{fd['pontos_regra_atual'].max():.0f}",
        "ok": bool(fd["pontos_regra_atual"].max() == 0),
    })

    # 2. Ninguém pode ter comparecido a mais jogos do que ocorreram enquanto
    #    era sócio. A primeira versão deste teste usava uma heurística ("no
    #    máximo 3 jogos por mês de vida") e falhou em 3 sócios do plano Minha
    #    Cadeira. A investigação mostrou que o erro era do teste, não da base:
    #    o calendário simulado tem meses com até 7 jogos. O teste passou a
    #    contar os jogos que de fato ocorreram na janela de cada sócio.
    con = sqlite3.connect(DB)
    jogos_mes = pd.read_sql(
        "SELECT CAST((CAST(strftime('%Y', data) AS INT) - 2023) * 12 + "
        "CAST(strftime('%m', data) AS INT) - 1 AS INT) AS mes, COUNT(*) AS n "
        "FROM jogos GROUP BY mes", con)
    con.close()
    por_mes = dict(zip(jogos_mes["mes"], jogos_mes["n"]))
    disponiveis = [
        sum(por_mes.get(m, 0) for m in range(int(a), int(a) + int(v)))
        for a, v in zip(df["mes_adesao"], df["meses_ativos"])
    ]
    impossivel = int((df["jogos_comparecidos"] > pd.Series(disponiveis, index=df.index)).sum())
    casos.append({
        "caso": "Ninguém comparece a mais jogos do que ocorreram em sua janela",
        "esperado": "0 sócios",
        "obtido": f"{impossivel} sócios",
        "ok": impossivel == 0,
    })

    # 3. Cupom só existe para plano pago — é a regra atual do programa.
    cup_fd = int(df.loc[df["plano"] == "Fiel Digital", "cupons_emitidos"].sum())
    casos.append({
        "caso": "Fiel Digital não recebe cupom de parceiro",
        "esperado": "0 cupons",
        "obtido": f"{cup_fd} cupons",
        "ok": cup_fd == 0,
    })

    # 4. Resgatados nunca excede emitidos.
    excede = int((df["cupons_resgatados"] > df["cupons_emitidos"]).sum())
    casos.append({
        "caso": "Cupons resgatados nunca superam os emitidos",
        "esperado": "0 sócios",
        "obtido": f"{excede} sócios",
        "ok": excede == 0,
    })

    # 5. Coorte fechada: quem aderiu depois do mês 32 não pode entrar na
    #    comparação de 12 meses (a janela vai até o mês 43).
    vazou = int(((df["coorte_12m_completa"] == 1) & (df["mes_adesao"] > 32)).sum())
    casos.append({
        "caso": "Coorte de 12 meses exclui adesões sem janela completa",
        "esperado": "0 sócios",
        "obtido": f"{vazou} sócios",
        "ok": vazou == 0,
    })

    # 6. Sócio ativo não tem mês de saída.
    inconsistente = int(((df["ativo"] == 1) & (df["meses_ativos"] <= 0)).sum())
    casos.append({
        "caso": "Sócio ativo tem ao menos um mês de vida",
        "esperado": "0 sócios",
        "obtido": f"{inconsistente} sócios",
        "ok": inconsistente == 0,
    })
    return casos


def crosscheck(df: pd.DataFrame) -> list[dict]:
    """Números que o Python calcula aqui e o JavaScript recalcula no navegador.

    O ponto do crosscheck não é conferir aritmética — é conferir que as duas
    implementações partem da mesma definição. Divergência aqui quase sempre
    significa que o filtro de coorte foi aplicado em um lado e não no outro.
    """
    c = df[df["coorte_12m_completa"] == 1]
    linhas = [
        {"metrica": "Sócios na coorte de 12 meses", "python": f"{len(c):,}"},
        {"metrica": "Retenção 12m da coorte (%)",
         "python": f"{c['retido_12m'].mean() * 100:.1f}"},
        {"metrica": "Margem M12 média (R$)", "python": f"{c['margem_m12'].mean():.2f}"},
        {"metrica": "CAC médio (R$)", "python": f"{c['cac'].mean():.2f}"},
        {"metrica": "Sócios com zero ponto (regra atual)",
         "python": f"{int((c['pontos_regra_atual'] == 0).sum()):,}"},
        {"metrica": "Retenção 12m do Fiel Digital (%)",
         "python": f"{c.loc[c['plano'] == 'Fiel Digital', 'retido_12m'].mean() * 100:.1f}"},
    ]
    return linhas


def achatar(df: pd.DataFrame) -> dict:
    """Base linha a linha, em arrays de inteiros e índices."""
    dims = {
        "plano": sorted(df["plano"].unique(), key=lambda p: [
            "Fiel Digital", "Minha Vida", "Minha História", "Meu Amor", "Minha Cadeira"].index(p)),
        "regiao": sorted(df["regiao"].unique()),
        "canal": sorted(df["canal_aquisicao"].unique()),
        "engajamento": sorted(df["faixa_engajamento"].unique()),
        "presenca": ["Nunca foi ao estádio", "Foi 1 a 3 vezes", "Frequentador (4+)"],
    }
    ix = {k: {v: i for i, v in enumerate(vs)} for k, vs in dims.items()}

    linhas = []
    for r in df.itertuples(index=False):
        linhas.append([
            ix["plano"][r.plano],
            ix["regiao"][r.regiao],
            ix["canal"][r.canal_aquisicao],
            ix["engajamento"][r.faixa_engajamento],
            ix["presenca"][r.perfil_presenca],
            int(r.coorte_12m_completa),
            int(r.retido_12m),
            int(r.ativo),
            round(float(r.cac), 1),
            round(float(r.margem_m12), 1),
            round(float(r.margem_total), 1),
            round(float(r.moedas_mes), 1),
            int(r.jogos_comparecidos),
            round(float(r.pontos_regra_atual), 1),
            int(r.meses_ativos),
            int(r.distancia_arena_km),
            int(r.socio_id),
            round(float(r.comissao_parceiros_m12), 1),
            int(r.cupons_emitidos),
            int(r.cupons_resgatados),
            int(r.no_shows),
            int(r.ingressos_liberados),
            int(r.transacoes_parceiros),
        ])

    return {"dims": dims, "socios": linhas}


def main():
    df = carregar()
    dados = achatar(df)
    dados["testes"] = casos_teste(df)
    dados["crosscheck"] = crosscheck(df)
    dados["meta"] = {
        "n": len(df),
        "coorte": int((df["coorte_12m_completa"] == 1).sum()),
        "janela": "jan/2023 a ago/2026",
    }

    payload = json.dumps(dados, separators=(",", ":"), ensure_ascii=False)
    # Carimbo de build: identifica a linha de dados que gerou esta página.
    # O próprio carimbo não entra no hash, para não criar circularidade.
    dados["meta"]["fp"] = hashlib.sha256(payload.encode()).hexdigest()[:8]
    payload = json.dumps(dados, separators=(",", ":"), ensure_ascii=False)

    with open(TEMPLATE, encoding="utf-8") as f:
        html = f.read()
    with open(CHARTJS, encoding="utf-8") as f:
        chartjs = f.read()

    html = html.replace("/*__CHARTJS__*/", chartjs)
    html = html.replace('"__DATA__"', payload)

    os.makedirs(DIR_DASH, exist_ok=True)
    saida = os.path.join(DIR_DASH, "dashboard-fiel-torcedor.html")
    with open(saida, "w", encoding="utf-8") as f:
        f.write(html)

    kb = os.path.getsize(saida) / 1024
    print(f"Dashboard gerado: {saida}  ({kb:,.0f} KB)")
    print(f"  sócios embarcados: {len(df):,}")
    print(f"  carimbo de build:  {dados['meta']['fp']}")
    falhas = [t for t in dados["testes"] if not t["ok"]]
    print(f"  casos-teste:       {len(dados['testes']) - len(falhas)}/{len(dados['testes'])} OK")
    if falhas:
        for t in falhas:
            print(f"    FALHOU: {t['caso']}")


if __name__ == "__main__":
    main()
