"""
gerar_base.py — Gerador da base FICTÍCIA do programa Fiel Torcedor.

IMPORTANTE
----------
Nenhum dado real do Sport Club Corinthians Paulista foi utilizado. Este script
cria um ambiente de simulação a partir de regras declaradas abaixo. Os números
produzidos NÃO são evidência sobre o programa real: servem para testar a
mecânica de decisão (quais perguntas fazer, quais métricas comparar, qual corte
usar) contra uma base cuja "verdade" é conhecida.

A estrutura dos planos, os valores de mensalidade, a pontuação por jogo, as
regras de liberação de ingresso e o benefício de cupom em parceiro foram
espelhados do que está publicado em fieltorcedor.com.br (consulta: set/2026).
Tudo o mais — volumes, custos de mídia, taxas de churn, engajamento — é
arbitrado e está declarado em PARAMS.

Semente fixa (SEED=42): rodar de novo reproduz exatamente a mesma base.
"""

from __future__ import annotations

import json
import os
from datetime import date, timedelta

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_DADOS = os.path.join(RAIZ, "data")

# --------------------------------------------------------------------------
# Janela da simulação
# --------------------------------------------------------------------------
INICIO = date(2023, 1, 1)
FIM = date(2026, 8, 31)  # último mês fechado na data do estudo
N_SOCIOS = 18_000

# --------------------------------------------------------------------------
# PARAMS — todas as premissas arbitradas ficam aqui, em um lugar só.
# Mudar um número aqui e rodar de novo é o experimento inteiro.
# --------------------------------------------------------------------------
PARAMS = {
    # Planos: espelhados do site oficial (set/2026).
    # mensalidade_equivalente = custo mensal para o sócio, normalizado.
    "planos": [
        # nome,             mensalidade, pontos_jogo, desc_ingresso, prioridade, garantido
        ("Fiel Digital",      14.90, 0.0,  0.00, 0, 0),
        ("Minha Vida",        24.50, 1.2,  0.25, 3, 0),
        ("Minha História",    60.00, 1.5,  0.35, 2, 0),
        ("Meu Amor",         300.00, 1.5,  0.35, 1, 0),
        ("Minha Cadeira",    700.00, 1.5,  0.00, 1, 1),
    ],
    # Mix de adesão por plano (arbitrado: base larga na entrada)
    "mix_plano": [0.34, 0.38, 0.16, 0.08, 0.04],
    # Regiões e distância típica até a Neo Química Arena
    "regioes": [
        ("Grande São Paulo", 0.52, 25),
        ("Interior de SP",   0.19, 180),
        ("Outros estados",   0.25, 900),
        ("Exterior",         0.04, 8000),
    ],
    # Peso relativo de cada plano por região (linha = região, coluna = plano).
    # Quanto mais longe, mais o Fiel Digital domina.
    "plano_por_regiao": {
        "Grande São Paulo": [0.16, 0.46, 0.22, 0.11, 0.05],
        "Interior de SP":   [0.34, 0.40, 0.15, 0.08, 0.03],
        "Outros estados":   [0.72, 0.18, 0.06, 0.03, 0.01],
        "Exterior":         [0.90, 0.06, 0.02, 0.01, 0.01],
    },
    # Canais de aquisição: participação e CAC médio (R$) com dispersão
    "canais": [
        # nome,          share, cac_medio, cac_desvio
        ("Meta Ads",      0.31,  62.0, 18.0),
        ("Google Ads",    0.22,  74.0, 22.0),
        ("TikTok Ads",    0.11,  48.0, 16.0),
        ("Orgânico/SEO",  0.16,   9.0,  4.0),
        ("Indicação",     0.09,  21.0,  8.0),
        ("Loja/Presencial", 0.11, 33.0, 12.0),
    ],
    # Plano caro custa mais para vender: multiplicador de CAC sobre o canal.
    "cac_mult_plano": {"Fiel Digital": 0.55, "Minha Vida": 1.00, "Minha História": 1.70,
                       "Meu Amor": 3.30, "Minha Cadeira": 5.20},
    # Engajamento no app Universo SCCP: moedas/mês, distribuição lognormal.
    # Sócio de plano presencial engaja um pouco mais (mais motivos de uso).
    "engaj_mu": {"Fiel Digital": 2.35, "Minha Vida": 2.60, "Minha História": 2.70,
                 "Meu Amor": 2.75, "Minha Cadeira": 2.80},
    "engaj_sigma": 0.95,
    # Churn mensal base por plano (hazard). Fiel Digital é o mais frágil:
    # não acumula ponto, não tem prioridade, não tem trilha de progressão.
    "churn_base": {"Fiel Digital": 0.062, "Minha Vida": 0.028, "Minha História": 0.020,
                   "Meu Amor": 0.013, "Minha Cadeira": 0.008},
    # Modificadores de churn
    "churn_mod_engajamento": -0.55,   # multiplicador máximo de redução p/ engajamento alto
    "churn_mod_jogo_recente": -0.40,  # ter ido a jogo nos últimos 60 dias segura
    "churn_pico_aniversario": 2.1,    # mês 12/24/36 (renovação) multiplica o hazard
    # Jogos na Neo Química Arena
    "jogos_por_ano": 31,
    "preco_medio_ingresso": 92.0,
    # Probabilidade de comprar ingresso para um jogo, por plano
    "p_compra_jogo": {"Fiel Digital": 0.04, "Minha Vida": 0.34, "Minha História": 0.42,
                      "Meu Amor": 0.55, "Minha Cadeira": 0.88},
    # Dado que comprou: comparece / libera (check-out) / não faz nada (no-show)
    "p_comparece": 0.86,
    "p_libera_se_falta": 0.55,
    # Parceiros (modelo Zé Delivery já existente no programa)
    # afin_remoto: peso relativo de uso por quem mora longe da arena.
    # >1 = categoria que funciona à distância; <1 = categoria de dia de jogo.
    "parceiros": [
        # nome,            categoria,     ticket_medio, comissao_clube, afin_remoto
        ("Zé Delivery",    "Bebidas",       78.0, 0.045, 0.75),
        ("Rede de Farmácias", "Saúde",      62.0, 0.030, 1.00),
        ("Posto de Combustível", "Mobilidade", 190.0, 0.012, 0.45),
        ("Streaming Esportivo", "Assinatura", 39.9, 0.150, 2.30),
        ("Marketplace Oficial", "E-commerce", 145.0, 0.060, 1.60),
    ],
    # Uso de parceiro por mês: função do engajamento (quem abre o app resgata)
    "p_uso_parceiro_base": 0.22,
    "p_uso_parceiro_por_engaj": 0.55,
    # --- Custos de servir (arbitrados) --------------------------------------
    # Cupom de parceiro: o programa oferece hoje 50% da mensalidade em cupom
    # no Zé Delivery para os planos pagos (fonte: site oficial, set/2026).
    "cupom_pct_mensalidade": 0.50,
    "cupom_share_clube": 0.60,        # fatia do cupom bancada pelo clube
    "cupom_resgate_base": 0.30,       # prob. de resgate para engajamento zero
    "cupom_resgate_por_engaj": 0.45,  # ganho de prob. no topo do engajamento
    "custo_operacional_mes": 4.20,    # atendimento, plataforma, meio de pagamento
    "custo_conteudo_mes": 1.80,       # produção de conteúdo e app
    "margem_ingresso": 0.70,          # margem sobre o ingresso vendido ao sócio
}

MESES_TOTAL = (FIM.year - INICIO.year) * 12 + (FIM.month - INICIO.month) + 1


def _mes_index(d: date) -> int:
    return (d.year - INICIO.year) * 12 + (d.month - INICIO.month)


def _data_do_mes(i: int) -> date:
    ano = INICIO.year + (INICIO.month - 1 + i) // 12
    mes = (INICIO.month - 1 + i) % 12 + 1
    return date(ano, mes, 1)


# --------------------------------------------------------------------------
# 1. Planos
# --------------------------------------------------------------------------
def gerar_planos() -> pd.DataFrame:
    linhas = []
    for i, (nome, mens, pts, desc, prio, gar) in enumerate(PARAMS["planos"], start=1):
        linhas.append({
            "plano_id": i,
            "plano": nome,
            "mensalidade": mens,
            "pontos_por_jogo": pts,
            "desconto_ingresso": desc,
            "prioridade_compra": prio,
            "ingresso_garantido": gar,
            "acessa_arena": 0 if nome == "Fiel Digital" else 1,
        })
    return pd.DataFrame(linhas)


# --------------------------------------------------------------------------
# 2. Jogos na Neo Química Arena
# --------------------------------------------------------------------------
COMPETICOES = [("Brasileirão", 0.55), ("Libertadores", 0.16),
               ("Copa do Brasil", 0.13), ("Paulista", 0.16)]


def gerar_jogos() -> pd.DataFrame:
    n_dias = (FIM - INICIO).days
    n_jogos = int(PARAMS["jogos_por_ano"] * n_dias / 365)
    dias = np.sort(rng.choice(np.arange(n_dias), size=n_jogos, replace=False))
    nomes = [c[0] for c in COMPETICOES]
    pesos = [c[1] for c in COMPETICOES]
    comp = rng.choice(nomes, size=n_jogos, p=pesos)
    # Jogo "grande" = Libertadores/Copa do Brasil ou clássico sorteado
    classico = rng.random(n_jogos) < 0.18
    linhas = []
    for i, (d, c, cl) in enumerate(zip(dias, comp, classico), start=1):
        data = INICIO + timedelta(days=int(d))
        alta_demanda = int(c in ("Libertadores", "Copa do Brasil") or cl)
        linhas.append({
            "jogo_id": i,
            "data": data.isoformat(),
            "competicao": c,
            "classico": int(cl),
            "alta_demanda": alta_demanda,
            "preco_base": round(PARAMS["preco_medio_ingresso"] * (1.45 if alta_demanda else 1.0), 2),
        })
    return pd.DataFrame(linhas)


# --------------------------------------------------------------------------
# 3. Sócios — adesão, plano, região, canal, engajamento, ciclo de vida
# --------------------------------------------------------------------------
def gerar_socios(planos: pd.DataFrame) -> pd.DataFrame:
    nomes_planos = [p[0] for p in PARAMS["planos"]]
    regioes = [r[0] for r in PARAMS["regioes"]]
    p_regiao = np.array([r[1] for r in PARAMS["regioes"]])
    dist_base = {r[0]: r[2] for r in PARAMS["regioes"]}
    canais = [c[0] for c in PARAMS["canais"]]
    p_canal = np.array([c[1] for c in PARAMS["canais"]])
    cac_med = {c[0]: c[2] for c in PARAMS["canais"]}
    cac_dp = {c[0]: c[3] for c in PARAMS["canais"]}

    # Adesões crescem levemente ao longo do tempo (base em expansão)
    peso_mes = np.linspace(0.75, 1.35, MESES_TOTAL)
    peso_mes = peso_mes / peso_mes.sum()
    mes_adesao = rng.choice(np.arange(MESES_TOTAL), size=N_SOCIOS, p=peso_mes)

    regiao = rng.choice(regioes, size=N_SOCIOS, p=p_regiao / p_regiao.sum())
    canal = rng.choice(canais, size=N_SOCIOS, p=p_canal / p_canal.sum())

    plano = np.empty(N_SOCIOS, dtype=object)
    for r in regioes:
        mask = regiao == r
        pesos = np.array(PARAMS["plano_por_regiao"][r], dtype=float)
        plano[mask] = rng.choice(nomes_planos, size=mask.sum(), p=pesos / pesos.sum())

    # Engajamento: moedas/mês no app Universo SCCP
    mu = np.array([PARAMS["engaj_mu"][p] for p in plano])
    moedas_mes = rng.lognormal(mean=mu, sigma=PARAMS["engaj_sigma"])
    moedas_mes = np.clip(moedas_mes, 0, 400)

    # Distância até a arena (dispersa dentro da região)
    dist = np.array([dist_base[r] for r in regiao], dtype=float)
    dist = np.clip(dist * rng.lognormal(0, 0.35, N_SOCIOS), 2, 12000)

    cac = np.array([max(3.0, rng.normal(cac_med[c], cac_dp[c])) for c in canal])
    cac = cac * np.array([PARAMS["cac_mult_plano"][p] for p in plano])

    df = pd.DataFrame({
        "socio_id": np.arange(1, N_SOCIOS + 1),
        "mes_adesao": mes_adesao,
        "data_adesao": [_data_do_mes(int(m)).isoformat() for m in mes_adesao],
        "plano": plano,
        "regiao": regiao,
        "distancia_arena_km": np.round(dist, 1),
        "canal_aquisicao": canal,
        "cac": np.round(cac, 2),
        "moedas_mes": np.round(moedas_mes, 1),
    })
    df = df.merge(planos[["plano_id", "plano", "mensalidade", "pontos_por_jogo"]], on="plano")
    return df.sort_values("socio_id").reset_index(drop=True)


def simular_ciclo_de_vida(socios: pd.DataFrame, jogos: pd.DataFrame):
    """Mês a mês: churn, pagamento, uso de parceiro. Retorna eventos e o fim de cada sócio."""
    jogos_por_mes = {}
    for _, j in jogos.iterrows():
        d = date.fromisoformat(j["data"])
        jogos_por_mes.setdefault(_mes_index(d), []).append(j)

    # normaliza engajamento em 0..1 para modular churn e uso de parceiro
    q = socios["moedas_mes"].rank(pct=True).to_numpy()

    parceiros = PARAMS["parceiros"]
    p_nomes = [p[0] for p in parceiros]
    p_ticket = {p[0]: p[2] for p in parceiros}
    p_com = {p[0]: p[3] for p in parceiros}
    p_afin = np.array([p[4] for p in parceiros], dtype=float)

    pagamentos, ingressos, transacoes, cupons = [], [], [], []
    mes_saida = np.full(len(socios), -1, dtype=int)

    plano_arr = socios["plano"].to_numpy()
    mens_arr = socios["mensalidade"].to_numpy()
    adesao_arr = socios["mes_adesao"].to_numpy()
    dist_arr = socios["distancia_arena_km"].to_numpy()
    id_arr = socios["socio_id"].to_numpy()

    p_compra = PARAMS["p_compra_jogo"]
    churn_base = PARAMS["churn_base"]

    for idx in range(len(socios)):
        plano = plano_arr[idx]
        mens = mens_arr[idx]
        m0 = int(adesao_arr[idx])
        eng = q[idx]
        dist = dist_arr[idx]
        sid = int(id_arr[idx])
        ult_jogo = -99

        # Mix de parceiros deste sócio: quanto mais longe da arena, mais peso
        # às categorias que funcionam à distância (streaming, e-commerce) e
        # menos às de dia de jogo (combustível, bebida para o pré-jogo).
        remoto = 1.0 / (1.0 + np.exp(-(dist - 150.0) / 90.0))  # 0 perto, 1 longe
        pesos_parc = p_afin ** remoto
        pesos_parc = pesos_parc / pesos_parc.sum()

        for m in range(m0, MESES_TOTAL):
            tenure = m - m0
            # --- pagamento do mês
            pagamentos.append((sid, m, round(float(mens), 2)))

            # --- cupom de parceiro (só planos pagos, conforme regra do programa)
            if plano != "Fiel Digital":
                valor_cupom = float(mens) * PARAMS["cupom_pct_mensalidade"]
                p_resg = PARAMS["cupom_resgate_base"] + PARAMS["cupom_resgate_por_engaj"] * eng
                resgatou = int(rng.random() < min(p_resg, 0.95))
                cupons.append((sid, m, round(valor_cupom, 2), resgatou,
                               round(valor_cupom * PARAMS["cupom_share_clube"], 2) if resgatou else 0.0))

            # --- ingressos dos jogos do mês
            for j in jogos_por_mes.get(m, []):
                pc = p_compra[plano]
                # distância reduz a probabilidade de comprar; alta demanda aumenta
                fator_dist = float(np.exp(-dist / 260.0))
                pc = pc * (0.25 + 0.75 * fator_dist) * (1.25 if j["alta_demanda"] else 1.0)
                if rng.random() < min(pc, 0.95):
                    compareceu = rng.random() < PARAMS["p_comparece"]
                    if compareceu:
                        liberou = 0
                        ult_jogo = m
                    else:
                        liberou = int(rng.random() < PARAMS["p_libera_se_falta"])
                    ingressos.append((sid, int(j["jogo_id"]), m, round(float(j["preco_base"]), 2),
                                      int(compareceu), liberou))

            # --- uso de parceiros no mês
            p_uso = PARAMS["p_uso_parceiro_base"] + PARAMS["p_uso_parceiro_por_engaj"] * eng
            n_usos = rng.poisson(p_uso * 1.4)
            for _ in range(int(n_usos)):
                pn = p_nomes[int(rng.choice(len(p_nomes), p=pesos_parc))]
                valor = float(max(8.0, rng.normal(p_ticket[pn], p_ticket[pn] * 0.35)))
                transacoes.append((sid, pn, m, round(valor, 2),
                                   round(valor * p_com[pn], 2)))

            # --- churn no fim do mês
            h = churn_base[plano]
            h *= (1 + PARAMS["churn_mod_engajamento"] * eng)
            if m - ult_jogo <= 2:
                h *= (1 + PARAMS["churn_mod_jogo_recente"])
            if tenure > 0 and tenure % 12 == 0:
                h *= PARAMS["churn_pico_aniversario"]
            if rng.random() < h:
                mes_saida[idx] = m
                break

    df_pag = pd.DataFrame(pagamentos, columns=["socio_id", "mes", "valor"])
    df_ing = pd.DataFrame(ingressos, columns=["socio_id", "jogo_id", "mes", "valor",
                                              "compareceu", "liberou"])
    df_trx = pd.DataFrame(transacoes, columns=["socio_id", "parceiro", "mes", "valor",
                                               "comissao_clube"])
    df_cup = pd.DataFrame(cupons, columns=["socio_id", "mes", "valor_cupom",
                                           "resgatou", "custo_clube"])
    return df_pag, df_ing, df_trx, df_cup, mes_saida


# --------------------------------------------------------------------------
# 4. Campanhas de mídia paga (nível campanha/mês — o que sai do gerenciador)
# --------------------------------------------------------------------------
def gerar_campanhas(socios: pd.DataFrame) -> pd.DataFrame:
    """Reconstrói investimento e entrega a partir das adesões pagas já simuladas.

    O CAC de cada sócio é a verdade; a campanha agrega. CTR e CPM são arbitrados
    por canal para que impressões e cliques sejam coerentes com o custo.
    """
    pagos = socios[socios["canal_aquisicao"].isin(["Meta Ads", "Google Ads", "TikTok Ads"])]
    cpm = {"Meta Ads": 18.0, "Google Ads": 26.0, "TikTok Ads": 11.0}
    ctr = {"Meta Ads": 0.0125, "Google Ads": 0.0340, "TikTok Ads": 0.0090}

    linhas = []
    grp = pagos.groupby(["canal_aquisicao", "mes_adesao", "regiao", "plano"])
    for (canal, mes, regiao, plano), g in grp:
        custo = float(g["cac"].sum())
        adesoes = len(g)
        impressoes = int(custo / cpm[canal] * 1000)
        cliques = int(impressoes * ctr[canal] * float(rng.normal(1.0, 0.10)))
        cliques = max(cliques, adesoes)
        publico = "Fora da Grande SP" if regiao != "Grande São Paulo" else "Grande SP"
        linhas.append({
            "canal": canal,
            "mes": int(mes),
            "data_ref": _data_do_mes(int(mes)).isoformat(),
            "publico": publico,
            "regiao": regiao,
            "plano_alvo": plano,
            "custo": round(custo, 2),
            "impressoes": impressoes,
            "cliques": cliques,
            "adesoes": adesoes,
        })
    return pd.DataFrame(linhas)


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------
def main():
    print("Gerando base fictícia do Fiel Torcedor (SEED=%d)..." % SEED)
    planos = gerar_planos()
    jogos = gerar_jogos()
    socios = gerar_socios(planos)
    pag, ing, trx, cup, mes_saida = simular_ciclo_de_vida(socios, jogos)

    socios["mes_saida"] = mes_saida
    socios["ativo"] = (socios["mes_saida"] < 0).astype(int)
    socios["data_saida"] = [
        _data_do_mes(int(m)).isoformat() if m >= 0 else None for m in socios["mes_saida"]
    ]
    socios["meses_ativos"] = np.where(
        socios["mes_saida"] < 0,
        MESES_TOTAL - socios["mes_adesao"],
        socios["mes_saida"] - socios["mes_adesao"] + 1,
    )

    os.makedirs(DIR_DADOS, exist_ok=True)
    planos.to_csv(f"{DIR_DADOS}/planos.csv", index=False)
    jogos.to_csv(f"{DIR_DADOS}/jogos.csv", index=False)
    socios.to_csv(f"{DIR_DADOS}/socios.csv", index=False)
    pag.to_csv(f"{DIR_DADOS}/pagamentos.csv", index=False)
    ing.to_csv(f"{DIR_DADOS}/ingressos.csv", index=False)
    trx.to_csv(f"{DIR_DADOS}/transacoes_parceiros.csv", index=False)
    cup.to_csv(f"{DIR_DADOS}/cupons_parceiro.csv", index=False)
    camp = gerar_campanhas(socios)
    camp.to_csv(f"{DIR_DADOS}/campanhas_midia.csv", index=False)

    # Tabela de custos: vive no banco para que o SQL possa fazer JOIN nela
    # em vez de esconder número mágico dentro da query.
    pd.DataFrame([
        ("custo_operacional_mes", PARAMS["custo_operacional_mes"],
         "Atendimento, plataforma e meio de pagamento por sócio ativo/mês"),
        ("custo_conteudo_mes", PARAMS["custo_conteudo_mes"],
         "Produção de conteúdo exclusivo e app, por sócio ativo/mês"),
        ("margem_ingresso", PARAMS["margem_ingresso"],
         "Margem sobre o ingresso vendido ao sócio, após custo de matchday"),
        ("cupom_share_clube", PARAMS["cupom_share_clube"],
         "Fatia do cupom de parceiro bancada pelo clube"),
        ("horizonte_ltv_meses", 12.0,
         "Horizonte fixo de LTV usado nas comparações de coorte"),
    ], columns=["parametro", "valor", "descricao"]).to_csv(
        f"{DIR_DADOS}/parametros_custo.csv", index=False)

    meta = {
        "seed": SEED,
        "gerado_em_janela": [INICIO.isoformat(), FIM.isoformat()],
        "meses": MESES_TOTAL,
        "n_socios": int(len(socios)),
        "n_jogos": int(len(jogos)),
        "n_pagamentos": int(len(pag)),
        "n_ingressos": int(len(ing)),
        "n_transacoes_parceiros": int(len(trx)),
        "n_cupons": int(len(cup)),
        "n_linhas_campanha": int(len(camp)),
        "params": {k: v for k, v in PARAMS.items()},
    }
    with open(f"{DIR_DADOS}/_metadados.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2, default=str)

    print(f"  sócios .................. {len(socios):>8,}")
    print(f"  jogos ................... {len(jogos):>8,}")
    print(f"  pagamentos .............. {len(pag):>8,}")
    print(f"  ingressos ............... {len(ing):>8,}")
    print(f"  transações parceiros .... {len(trx):>8,}")
    print(f"  cupons emitidos ......... {len(cup):>8,}")
    print(f"  linhas de campanha ...... {len(camp):>8,}")
    print(f"  ativos no fim da janela . {int(socios['ativo'].sum()):>8,}")
    print(f"CSV em {DIR_DADOS}")


if __name__ == "__main__":
    main()
