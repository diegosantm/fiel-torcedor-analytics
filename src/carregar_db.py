"""
carregar_db.py — Carrega os CSVs gerados para um SQLite e aplica o schema.

Executa sql/00_schema.sql depois da carga, que cria as views derivadas usadas
por todas as análises. As views são a fonte única de leitura: nenhuma query de
análise recalcula margem ou tempo de vida por conta própria.
"""

from __future__ import annotations

import os
import sqlite3

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_DADOS = os.path.join(RAIZ, "data")
DIR_SQL = os.path.join(RAIZ, "sql")
DB = os.path.join(DIR_DADOS, "fiel_torcedor.db")

TABELAS = {
    "planos": "planos.csv",
    "socios": "socios.csv",
    "jogos": "jogos.csv",
    "pagamentos": "pagamentos.csv",
    "ingressos": "ingressos.csv",
    "transacoes_parceiros": "transacoes_parceiros.csv",
    "cupons_parceiro": "cupons_parceiro.csv",
    "campanhas_midia": "campanhas_midia.csv",
    "parametros_custo": "parametros_custo.csv",
}


def main():
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)

    for tabela, arquivo in TABELAS.items():
        caminho = os.path.join(DIR_DADOS, arquivo)
        df = pd.read_csv(caminho)
        df.to_sql(tabela, con, index=False)
        print(f"  {tabela:<24} {len(df):>8,} linhas")

    # Índices nas chaves usadas em JOIN e filtro
    cur = con.cursor()
    for ddl in [
        "CREATE INDEX ix_pag_socio ON pagamentos(socio_id)",
        "CREATE INDEX ix_ing_socio ON ingressos(socio_id)",
        "CREATE INDEX ix_trx_socio ON transacoes_parceiros(socio_id)",
        "CREATE INDEX ix_cup_socio ON cupons_parceiro(socio_id)",
        "CREATE INDEX ix_socios_plano ON socios(plano)",
        "CREATE UNIQUE INDEX ix_socios_id ON socios(socio_id)",
    ]:
        cur.execute(ddl)

    with open(os.path.join(DIR_SQL, "00_schema.sql"), encoding="utf-8") as f:
        con.executescript(f.read())
    con.commit()

    n = cur.execute("SELECT COUNT(*) FROM vw_socio_economia").fetchone()[0]
    print(f"\nSchema aplicado. vw_socio_economia: {n:,} linhas")
    print(f"Banco em {DB}")
    con.close()


if __name__ == "__main__":
    main()
