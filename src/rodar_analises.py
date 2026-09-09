"""
rodar_analises.py — Executa todas as queries de sql/ e grava os resultados.

Saída em output/: um CSV por query e um relatorio.md com todas as tabelas em
markdown, para leitura direta no GitHub.
"""

from __future__ import annotations

import glob
import os
import sqlite3

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(RAIZ, "data", "fiel_torcedor.db")
DIR_SQL = os.path.join(RAIZ, "sql")
DIR_OUT = os.path.join(RAIZ, "output")


def cabecalho_da_query(sql: str) -> str:
    """Extrai a primeira linha de comentário significativa como título."""
    for linha in sql.splitlines():
        l = linha.strip()
        if l.startswith("--") and not set(l) <= set("- ") and "PERGUNTA" not in l:
            titulo = l.lstrip("- ").strip()
            if titulo and not titulo.startswith("="):
                return titulo
    return ""


def pergunta_da_query(sql: str) -> str:
    capturando, partes = False, []
    for linha in sql.splitlines():
        l = linha.strip().lstrip("-").strip()
        if l.startswith("PERGUNTA:"):
            capturando = True
            partes.append(l.replace("PERGUNTA:", "").strip())
            continue
        if capturando:
            if not l:
                break
            partes.append(l)
    return " ".join(partes)


def main():
    con = sqlite3.connect(DB)
    os.makedirs(DIR_OUT, exist_ok=True)

    arquivos = sorted(glob.glob(os.path.join(DIR_SQL, "*.sql")))
    arquivos = [a for a in arquivos if not os.path.basename(a).startswith("00_")]

    linhas_md = [
        "# Resultados das análises",
        "",
        "Gerado por `src/rodar_analises.py` sobre a base fictícia (SEED=42).",
        "Todos os números vêm de dados simulados: não são evidência sobre o",
        "programa real do Corinthians.",
        "",
    ]

    for caminho in arquivos:
        nome = os.path.basename(caminho).replace(".sql", "")
        with open(caminho, encoding="utf-8") as f:
            sql = f.read()

        df = pd.read_sql(sql, con)
        df.to_csv(os.path.join(DIR_OUT, f"{nome}.csv"), index=False)

        titulo = cabecalho_da_query(sql) or nome
        pergunta = pergunta_da_query(sql)

        print(f"\n{'=' * 78}\n{titulo}\n{'=' * 78}")
        print(df.to_string(index=False))

        linhas_md += [f"## {titulo}", ""]
        if pergunta:
            linhas_md += [f"**Pergunta:** {pergunta}", ""]
        linhas_md += [f"`sql/{nome}.sql`", "", df.to_markdown(index=False), ""]

    with open(os.path.join(DIR_OUT, "relatorio.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_md))

    con.close()
    print(f"\n\nCSVs e relatorio.md em {DIR_OUT}")


if __name__ == "__main__":
    main()
