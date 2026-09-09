# Resultados das análises

Gerado por `src/rodar_analises.py` sobre a base fictícia (SEED=42).
Todos os números vêm de dados simulados: não são evidência sobre o
programa real do Corinthians.

## 01 — Retenção de 12 meses por plano  [FRENTE A: produto e progressão]

**Pergunta:** o plano que não dá acesso ao estádio segura o sócio?

`sql/01_retencao_por_plano.sql`

| plano          |   socios_na_coorte |   retencao_12m_pct |   meses_ativos_medio |   cac_medio |   margem_m12_media |   ratio_margem_cac |   payback_meses |   pontos_medios_regra_atual |
|:---------------|-------------------:|-------------------:|---------------------:|------------:|-------------------:|-------------------:|----------------:|----------------------------:|
| Fiel Digital   |               4627 |               59   |                 15.2 |       25.99 |             117.32 |                4.5 |             2.7 |                         0   |
| Minha Vida     |               4440 |               84.4 |                 21.9 |       47.95 |             199.9  |                4.2 |             2.9 |                        18.4 |
| Minha História |               1976 |               90.6 |                 23.6 |       81.18 |             546.67 |                6.7 |             1.8 |                        31.6 |
| Meu Amor       |               1038 |               92.6 |                 24.3 |      159.59 |            2887.08 |               18.1 |             0.7 |                        41.8 |
| Minha Cadeira  |                441 |               95.7 |                 25.1 |      244.86 |            6805.73 |               27.8 |             0.4 |                        68.6 |

## 02 — Quantos sócios não vão ao estádio, e o que acontece com eles

**Pergunta:** qual o tamanho do público que sustenta o programa sem nunca ocupar uma cadeira, e como a regra de pontuação vigente o trata?

`sql/02_socio_sem_estadio.sql`

| perfil_presenca      |   socios |   pct_da_coorte |   retencao_12m_pct |   dist_media_km |   engajamento_app_medio |   pontos_regra_atual |   margem_m12_media |   margem_m12_total |   pct_da_margem |
|:---------------------|---------:|----------------:|-------------------:|----------------:|------------------------:|---------------------:|-------------------:|-------------------:|----------------:|
| Frequentador (4+)    |     7446 |            59.5 |               93.1 |             170 |                    22.8 |                 29.1 |            1058.81 |        7.88392e+06 |            92.7 |
| Nunca foi ao estádio |     2774 |            22.2 |               39.1 |            1539 |                    15.2 |                  0   |              98.83 |   274156           |             3.2 |
| Foi 1 a 3 vezes      |     2302 |            18.4 |               70.8 |             983 |                    18   |                  0.5 |             152.33 |   350657           |             4.1 |

## 03 — Engajamento no app x retenção  [FRENTE A: produto e progressão]

**Pergunta:** o engajamento digital (moedas do Universo SCCP) prevê retenção entre quem NÃO vai ao estádio? Se prevê, existe uma régua de mérito alternativa à presença, e ela já está sendo coletada — só não está conectada à pontuação do Fiel Torcedor.

`sql/03_engajamento_vs_retencao.sql`

| faixa_engajamento   | perfil_presenca    |   socios |   retencao_12m_pct |   meses_ativos_medio |   usos_parceiro_medio |   margem_m12_media |
|:--------------------|:-------------------|---------:|-------------------:|---------------------:|----------------------:|-------------------:|
| 1. Dormente (<5)    | Vai ao estádio     |     1424 |               83.9 |                 21.1 |                   7.9 |             825.42 |
| 2. Leve (5-15)      | Vai ao estádio     |     3816 |               86.6 |                 22.3 |                  13.4 |             776.76 |
| 3. Ativo (15-40)    | Vai ao estádio     |     3257 |               89.6 |                 23.1 |                  20.2 |             877.02 |
| 4. Intenso (40+)    | Vai ao estádio     |     1251 |               91.6 |                 24.1 |                  24.6 |             990.09 |
| 1. Dormente (<5)    | Não vai ao estádio |      637 |               36.1 |                  9.8 |                   3.7 |              84.25 |
| 2. Leve (5-15)      | Não vai ao estádio |     1242 |               36.6 |                 10.3 |                   6.1 |              96.18 |
| 3. Ativo (15-40)    | Não vai ao estádio |      704 |               43.8 |                 11.7 |                  10.1 |             110.19 |
| 4. Intenso (40+)    | Não vai ao estádio |      191 |               48.7 |                 12.2 |                  12.7 |             122.81 |

## 04 — Simulação da trilha de pontos digital  [FRENTE A: proposta]

**Pergunta:** se a pontuação passasse a reconhecer permanência e engajamento além da presença, quantos sócios sairiam do zero — e quantos frequentadores seriam ultrapassados na fila de prioridade?

`sql/04_trilha_pontos_digital.sql`

| perfil_presenca    |   socios |   pontos_hoje |   pontos_proposta |   zerados_hoje |   zerados_proposta |   pontos_proposta_max |   acima_do_freq_mediano |   pct_acima_do_freq_mediano |
|:-------------------|---------:|--------------:|------------------:|---------------:|-------------------:|----------------------:|------------------------:|----------------------------:|
| Frequentador (4+)  |     7446 |          29.1 |              44.7 |            171 |                  0 |                 212.5 |                    3722 |                        50   |
| Vai pouco (1-3)    |     2302 |           0.5 |              13.6 |           1839 |                  0 |                 136.8 |                      74 |                         3.2 |
| Não vai ao estádio |     2774 |           0   |               8.2 |           2774 |                  0 |                  72.5 |                      22 |                         0.8 |

## 05 — O cupom que ninguém resgata  [FRENTE B: ativação de receita]

**Pergunta:** o benefício mais caro do programa (50% da mensalidade em cupom de parceiro, oferecido hoje aos planos pagos) está chegando a quem paga?

`sql/05_cupom_desperdicio.sql`

| faixa                       |   socios |   cupons_emitidos |   cupons_resgatados |   taxa_resgate_pct |   custo_cupom_total |   usos_parceiro_medio |   comissao_gerada |   retorno_por_real_de_cupom |
|:----------------------------|---------:|------------------:|--------------------:|-------------------:|--------------------:|----------------------:|------------------:|----------------------------:|
| 1. Dormente (<5)            |     1072 |             23056 |                7796 |               33.8 |    274721           |                   8   |             41852 |                        0.15 |
| 2. Leve (5-15)              |     3063 |             68906 |               32403 |               47   |         1.02756e+06 |                  13.5 |            202049 |                        0.2  |
| 3. Ativo (15-40)            |     2686 |             62359 |               39002 |               62.5 |         1.37072e+06 |                  20.3 |            262474 |                        0.19 |
| 4. Intenso (40+)            |     1074 |             25864 |               18717 |               72.4 |    718775           |                  24.7 |            128274 |                        0.18 |
| — sem cupom (regra atual) — |     4627 |                 0 |                   0 |              nan   |         0           |                  10.2 |            246424 |                      nan    |

## 06 — Clube de vantagens: onde está a receita fora do dia de jogo

**Pergunta:** qual categoria de parceiro gera receita recorrente para o clube, e qual delas alcança o sócio que não vai ao estádio?

`sql/06_parceiros_receita.sql`

| parceiro             |   transacoes |         gmv |   comissao_clube |   ticket_medio |   take_rate_pct |   pct_comissao_de_remoto |   pct_comissao_fora_gsp |
|:---------------------|-------------:|------------:|-----------------:|---------------:|----------------:|-------------------------:|------------------------:|
| Marketplace Oficial  |        41569 | 6.03141e+06 |           361885 |         145.09 |             6   |                     12   |                    47.1 |
| Streaming Esportivo  |        49843 | 1.98873e+06 |           298309 |          39.9  |            15   |                     14   |                    52.5 |
| Zé Delivery          |        29464 | 2.29978e+06 |           103489 |          78.05 |             4.5 |                      8.8 |                    35.8 |
| Rede de Farmácias    |        33244 | 2.06582e+06 |            61974 |          62.14 |             3   |                      9.6 |                    39.5 |
| Posto de Combustível |        24280 | 4.61793e+06 |            55415 |         190.19 |             1.2 |                      7   |                    29.2 |

## 07 — Cadeira vazia: no-show e uso do pool de ingressos

**Pergunta:** quanto assento pago fica vazio sem ser devolvido para revenda?

`sql/07_noshow_pool.sql`

| competicao     | demanda        |   jogos |   ingressos_socio |   presenca_pct |   liberacao_pct |   no_show_pct |   assentos_perdidos |   receita_revenda_potencial |
|:---------------|:---------------|--------:|------------------:|---------------:|----------------:|--------------:|--------------------:|----------------------------:|
| Brasileirão    | Demanda normal |      51 |             87837 |           85.8 |             7.8 |           6.4 |                5581 |                      513452 |
| Copa do Brasil | Alta demanda   |      16 |             34414 |           85.9 |             7.7 |           6.4 |                2187 |                      291746 |
| Libertadores   | Alta demanda   |      18 |             30048 |           86   |             7.7 |           6.2 |                1873 |                      249858 |
| Brasileirão    | Alta demanda   |      10 |             16164 |           86.3 |             7.4 |           6.3 |                1014 |                      135268 |
| Paulista       | Demanda normal |      13 |             21020 |           85.7 |             7.6 |           6.6 |                1396 |                      128432 |
| Paulista       | Alta demanda   |       5 |             15139 |           86   |             7.8 |           6.2 |                 933 |                      124462 |

## 08 — CAC, margem de 12 meses e payback por canal  [FRENTE C: mídia paga]

**Pergunta:** qual canal traz sócio que fica, e não só sócio que assina?

`sql/08_cac_ltv_por_canal.sql`

| canal_aquisicao   |   socios |   cac_medio |   margem_m12_media |   ratio_margem_cac |   payback_meses |   retencao_12m_pct |   pct_fiel_digital |   pct_fora_gsp |   investimento_total |
|:------------------|---------:|------------:|-------------------:|-------------------:|----------------:|-------------------:|-------------------:|---------------:|---------------------:|
| Orgânico/SEO      |     2026 |       11.76 |             668.48 |               56.8 |             0.2 |               77.1 |               37.4 |           48.7 |                23835 |
| Indicação         |     1103 |       27.71 |             739.57 |               26.7 |             0.4 |               76.4 |               38.9 |           50.3 |                30560 |
| Loja/Presencial   |     1415 |       41.36 |             679.99 |               16.4 |             0.7 |               79.1 |               37.5 |           48.1 |                58522 |
| TikTok Ads        |     1420 |       60.59 |             651.14 |               10.7 |             1.1 |               77   |               36.3 |           47.6 |                86039 |
| Meta Ads          |     3856 |       79.26 |             676.64 |                8.5 |             1.4 |               76.1 |               37.3 |           49.2 |               305637 |
| Google Ads        |     2702 |       97.19 |             681.98 |                7   |             1.7 |               77.6 |               35.5 |           46.8 |               262609 |

## 09 — Funil de mídia paga por público geográfico  [FRENTE C: mídia paga]

**Pergunta:** a comunicação que roda para quem mora longe está vendendo um produto que essa pessoa pode usar?

`sql/09_funil_midia_geo.sql`

| canal      | publico           |   impressoes |   cliques |   ctr_pct |   adesoes |   conv_clique_adesao_pct |    cpa |   retencao_12m_pct |   margem_m12_media |   cpa_por_socio_retido |
|:-----------|:------------------|-------------:|----------:|----------:|----------:|-------------------------:|-------:|-------------------:|-------------------:|-----------------------:|
| Google Ads | Fora da Grande SP |      5360770 |    181276 |      3.38 |      1850 |                     1.02 |  75.34 |               69.8 |             453.6  |                 107.97 |
| Google Ads | Grande SP         |      9157000 |    307115 |      3.35 |      2082 |                     0.68 | 114.35 |               84.5 |             882.72 |                 135.34 |
| Meta Ads   | Fora da Grande SP |      9201168 |    115088 |      1.25 |      2715 |                     2.36 |  61    |               69.1 |             453.82 |                  88.29 |
| Meta Ads   | Grande SP         |     15336824 |    190032 |      1.24 |      2829 |                     1.49 |  97.58 |               82.9 |             892.19 |                 117.77 |
| TikTok Ads | Fora da Grande SP |      4060218 |     36281 |      0.89 |       979 |                     2.7  |  45.62 |               69.5 |             395.51 |                  65.62 |
| TikTok Ads | Grande SP         |      7100690 |     64002 |      0.9  |      1060 |                     1.66 |  73.69 |               83.7 |             883.41 |                  88    |

## 10 — Públicos acionáveis para mídia e CRM  [FRENTE C: mídia paga]

**Pergunta:** quais listas o time de mídia deveria estar subindo como público customizado esta semana, e com qual oferta?

`sql/10_publicos_acionaveis.sql`

| segmento                        |   socios |   pct_base_ativa |   meses_ativos_medio |   engajamento_medio |   jogos_medio |   usos_parceiro_medio |   margem_acumulada_media |   margem_acumulada_total |
|:--------------------------------|---------:|-----------------:|---------------------:|--------------------:|--------------:|----------------------:|-------------------------:|-------------------------:|
| A. Risco de cancelamento        |      205 |              1.7 |                 13.5 |                 3.2 |           0   |                   5   |                   151.37 |          31031           |
| B. Candidato a upgrade de plano |     1380 |             11.4 |                 22.3 |                36.8 |          17.1 |                  20.3 |                   393.09 |         542461           |
| C. Remoto engajado              |     2219 |             18.3 |                 17.3 |                38.1 |           6.1 |                  15.8 |                  1116.03 |              2.47648e+06 |
| D. Remoto frio                  |     2415 |             19.9 |                 15.6 |                 8   |           5.1 |                   8.6 |                   962.02 |              2.32327e+06 |
| E. Base estável                 |     5931 |             48.8 |                 17.3 |                19.6 |          17   |                  11.7 |                  2010.85 |              1.19264e+07 |

## 11 — Tamanho do prêmio: quanto valem as três frentes

**Pergunta:** se as propostas funcionarem, o resultado paga o esforço?

`sql/11_impacto_cenarios.sql`

| cenario                                  |   publico_alvo |   margem_hoje |   margem_cenario |   ganho_estimado | premissa                                                                                     |
|:-----------------------------------------|---------------:|--------------:|-----------------:|-----------------:|:---------------------------------------------------------------------------------------------|
| Frente A: trilha de pontos digital       |           2774 |        274156 |           296089 |            21933 | Retenção 12m do sócio remoto sobe 8 p.p. ao ganhar progressão sem depender de presença       |
| Frente B: ativação do clube de vantagens |          12522 |        464065 |           626487 |           162422 | Comissão de parceiro cresce 35% ao elevar o resgate do cupom nas faixas de menor engajamento |
| Frente B: recuperação de assento (pool)  |           6421 |             0 |           404101 |           404101 | Lembrete no app converte 40% dos no-shows em liberação para revenda                          |
