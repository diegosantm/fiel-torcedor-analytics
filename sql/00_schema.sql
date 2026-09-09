-- =========================================================================
-- 00_schema.sql — views derivadas do Fiel Torcedor (base fictícia)
--
-- Princípio: FONTE ÚNICA DE LEITURA. Margem, tempo de vida e faixa de
-- engajamento são definidos aqui, uma única vez. Nenhuma query de análise
-- recalcula essas regras por conta própria — todas leem daqui. Isso evita o
-- defeito clássico de painel que cresce: dois números diferentes para a mesma
-- métrica, no mesmo arquivo, porque um trecho leu o campo cru e o outro leu o
-- campo tratado.
--
-- Janela da simulação: 2023-01 a 2026-08 → 44 meses, índice 0..43.
-- =========================================================================

DROP VIEW IF EXISTS vw_parametros;
CREATE VIEW vw_parametros AS
SELECT
  MAX(CASE WHEN parametro = 'custo_operacional_mes'  THEN valor END) AS custo_operacional_mes,
  MAX(CASE WHEN parametro = 'custo_conteudo_mes'     THEN valor END) AS custo_conteudo_mes,
  MAX(CASE WHEN parametro = 'margem_ingresso'        THEN valor END) AS margem_ingresso,
  MAX(CASE WHEN parametro = 'horizonte_ltv_meses'    THEN valor END) AS horizonte_ltv_meses,
  43 AS ultimo_mes_indice
FROM parametros_custo;

-- -------------------------------------------------------------------------
-- vw_socio_economia — uma linha por sócio, com a economia inteira do ciclo.
--
-- Duas leituras convivem, e a diferença entre elas é o ponto metodológico
-- central do projeto:
--
--   *_total : tudo o que o sócio gerou até o fim da janela. Enviesado por
--             tempo de casa — quem entrou em 2023 teve 44 meses para gerar
--             receita, quem entrou em julho/2026 teve 2. Serve para somar
--             o programa, NUNCA para comparar grupos.
--   *_m12   : apenas os 12 primeiros meses de cada sócio. Horizonte fixo,
--             comparável entre coortes. É o número usado em toda comparação
--             de plano, canal e região. Só é válido para quem já completou
--             12 meses de janela observável (coorte_12m_completa = 1).
-- -------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_socio_economia;
CREATE VIEW vw_socio_economia AS
WITH p AS (SELECT * FROM vw_parametros),

pag AS (
  SELECT socio_id,
         SUM(valor) AS receita_plano_total,
         SUM(CASE WHEN mes < (SELECT mes_adesao FROM socios s WHERE s.socio_id = pagamentos.socio_id) + 12
                  THEN valor ELSE 0 END) AS receita_plano_m12,
         COUNT(*) AS meses_pagos
  FROM pagamentos GROUP BY socio_id
),

ing AS (
  SELECT i.socio_id,
         SUM(i.valor * (1 - pl.desconto_ingresso)) AS receita_ingresso_total,
         SUM(CASE WHEN i.mes < s.mes_adesao + 12
                  THEN i.valor * (1 - pl.desconto_ingresso) ELSE 0 END) AS receita_ingresso_m12,
         COUNT(*)              AS ingressos_comprados,
         SUM(i.compareceu)     AS jogos_comparecidos,
         SUM(i.liberou)        AS ingressos_liberados,
         SUM(CASE WHEN i.compareceu = 0 AND i.liberou = 0 THEN 1 ELSE 0 END) AS no_shows
  FROM ingressos i
  JOIN socios s  ON s.socio_id = i.socio_id
  JOIN planos pl ON pl.plano   = s.plano
  GROUP BY i.socio_id
),

trx AS (
  SELECT t.socio_id,
         SUM(t.comissao_clube) AS comissao_parceiros_total,
         SUM(CASE WHEN t.mes < s.mes_adesao + 12 THEN t.comissao_clube ELSE 0 END) AS comissao_parceiros_m12,
         SUM(t.valor)          AS gmv_parceiros_total,
         COUNT(*)              AS transacoes_parceiros
  FROM transacoes_parceiros t
  JOIN socios s ON s.socio_id = t.socio_id
  GROUP BY t.socio_id
),

cup AS (
  SELECT c.socio_id,
         SUM(c.custo_clube) AS custo_cupom_total,
         SUM(CASE WHEN c.mes < s.mes_adesao + 12 THEN c.custo_clube ELSE 0 END) AS custo_cupom_m12,
         COUNT(*)           AS cupons_emitidos,
         SUM(c.resgatou)    AS cupons_resgatados
  FROM cupons_parceiro c
  JOIN socios s ON s.socio_id = c.socio_id
  GROUP BY c.socio_id
)

SELECT
  s.socio_id,
  s.plano,
  s.plano_id,
  s.regiao,
  s.distancia_arena_km,
  s.canal_aquisicao,
  s.data_adesao,
  s.mes_adesao,
  s.mes_saida,
  s.ativo,
  s.meses_ativos,
  ROUND(s.cac, 2)                                    AS cac,
  s.moedas_mes,
  pl.pontos_por_jogo,
  pl.acessa_arena,

  -- Faixa de engajamento: cortes fixos, declarados uma vez, usados em todo
  -- lugar. Sem quartil dinâmico — quartil muda de significado a cada filtro.
  CASE WHEN s.moedas_mes <  5  THEN '1. Dormente (<5)'
       WHEN s.moedas_mes < 15  THEN '2. Leve (5-15)'
       WHEN s.moedas_mes < 40  THEN '3. Ativo (15-40)'
       ELSE                         '4. Intenso (40+)' END AS faixa_engajamento,

  -- Elegibilidade de coorte: só quem teve 12 meses inteiros de janela.
  CASE WHEN s.mes_adesao + 12 <= (SELECT ultimo_mes_indice + 1 FROM p)
       THEN 1 ELSE 0 END                             AS coorte_12m_completa,
  CASE WHEN s.ativo = 1 OR (s.mes_saida - s.mes_adesao) >= 12
       THEN 1 ELSE 0 END                             AS retido_12m,

  -- Receita
  ROUND(COALESCE(pag.receita_plano_total, 0), 2)     AS receita_plano_total,
  ROUND(COALESCE(pag.receita_plano_m12, 0), 2)       AS receita_plano_m12,
  ROUND(COALESCE(ing.receita_ingresso_total, 0) * (SELECT margem_ingresso FROM p), 2)
                                                     AS margem_ingresso_total,
  ROUND(COALESCE(ing.receita_ingresso_m12, 0) * (SELECT margem_ingresso FROM p), 2)
                                                     AS margem_ingresso_m12,
  ROUND(COALESCE(trx.comissao_parceiros_total, 0), 2) AS comissao_parceiros_total,
  ROUND(COALESCE(trx.comissao_parceiros_m12, 0), 2)  AS comissao_parceiros_m12,
  ROUND(COALESCE(trx.gmv_parceiros_total, 0), 2)     AS gmv_parceiros_total,

  -- Custo de servir
  ROUND(COALESCE(cup.custo_cupom_total, 0), 2)       AS custo_cupom_total,
  ROUND(COALESCE(cup.custo_cupom_m12, 0), 2)         AS custo_cupom_m12,
  ROUND(s.meses_ativos * ((SELECT custo_operacional_mes FROM p) + (SELECT custo_conteudo_mes FROM p)), 2)
                                                     AS custo_servir_total,
  ROUND(MIN(s.meses_ativos, 12) * ((SELECT custo_operacional_mes FROM p) + (SELECT custo_conteudo_mes FROM p)), 2)
                                                     AS custo_servir_m12,

  -- -----------------------------------------------------------------------
  -- MARGEM DO PROGRAMA — a única definição de margem usada nas comparações.
  --
  -- A margem de bilheteria fica DE FORA de propósito. Três razões:
  --   1. O assento seria vendido de qualquer forma na maior parte dos jogos;
  --      creditá-lo ao programa é atribuir ao sócio-torcedor uma receita que
  --      já existia.
  --   2. O sócio compra com desconto de 25% a 35%. Por assento, o programa
  --      REDUZ a receita de bilheteria — contá-la como ganho inverte o sinal.
  --   3. Sem separar, todo plano presencial parece melhor por construção, e
  --      a pergunta do projeto (quanto vale o sócio que não vai ao estádio)
  --      fica respondida pela definição da métrica, não pelos dados.
  --
  -- A versão com bilheteria existe logo abaixo, nomeada, para quem quiser a
  -- visão de receita total do torcedor.
  -- -----------------------------------------------------------------------
  ROUND(
      COALESCE(pag.receita_plano_total, 0)
    + COALESCE(trx.comissao_parceiros_total, 0)
    - COALESCE(cup.custo_cupom_total, 0)
    - s.meses_ativos * ((SELECT custo_operacional_mes FROM p) + (SELECT custo_conteudo_mes FROM p))
  , 2)                                               AS margem_total,

  ROUND(
      COALESCE(pag.receita_plano_m12, 0)
    + COALESCE(trx.comissao_parceiros_m12, 0)
    - COALESCE(cup.custo_cupom_m12, 0)
    - MIN(s.meses_ativos, 12) * ((SELECT custo_operacional_mes FROM p) + (SELECT custo_conteudo_mes FROM p))
  , 2)                                               AS margem_m12,

  -- Visão alternativa, com bilheteria incluída. Use com a ressalva acima.
  ROUND(
      COALESCE(pag.receita_plano_m12, 0)
    + COALESCE(ing.receita_ingresso_m12, 0) * (SELECT margem_ingresso FROM p)
    + COALESCE(trx.comissao_parceiros_m12, 0)
    - COALESCE(cup.custo_cupom_m12, 0)
    - MIN(s.meses_ativos, 12) * ((SELECT custo_operacional_mes FROM p) + (SELECT custo_conteudo_mes FROM p))
  , 2)                                               AS margem_m12_com_bilheteria,

  -- Comportamento
  COALESCE(ing.ingressos_comprados, 0)               AS ingressos_comprados,
  COALESCE(ing.jogos_comparecidos, 0)                AS jogos_comparecidos,
  COALESCE(ing.ingressos_liberados, 0)               AS ingressos_liberados,
  COALESCE(ing.no_shows, 0)                          AS no_shows,
  COALESCE(trx.transacoes_parceiros, 0)              AS transacoes_parceiros,
  COALESCE(cup.cupons_emitidos, 0)                   AS cupons_emitidos,
  COALESCE(cup.cupons_resgatados, 0)                 AS cupons_resgatados,

  -- Pontuação acumulada pela regra vigente: só pontua quem vai ao jogo.
  -- É a métrica que o projeto questiona.
  ROUND(COALESCE(ing.jogos_comparecidos, 0) * pl.pontos_por_jogo, 1) AS pontos_regra_atual

FROM socios s
JOIN planos pl ON pl.plano = s.plano
LEFT JOIN pag ON pag.socio_id = s.socio_id
LEFT JOIN ing ON ing.socio_id = s.socio_id
LEFT JOIN trx ON trx.socio_id = s.socio_id
LEFT JOIN cup ON cup.socio_id = s.socio_id;
