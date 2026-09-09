-- =========================================================================
-- 02 — Quantos sócios não vão ao estádio, e o que acontece com eles
--      [FRENTE A: produto e progressão]
--
-- PERGUNTA: qual o tamanho do público que sustenta o programa sem nunca
-- ocupar uma cadeira, e como a regra de pontuação vigente o trata?
--
-- Pela regra atual, pontua-se por compra + acesso ao jogo. Quem não vai ao
-- estádio acumula zero ponto, independentemente de há quanto tempo paga.
-- Sem ponto não há prioridade, e sem prioridade não há progressão: a régua
-- de mérito do programa não enxerga esse sócio.
--
-- A classificação abaixo é COMPORTAMENTAL (foi ou não foi a jogo na janela),
-- não contratual (qual plano assinou). Um Minha Vida que nunca compareceu
-- é, na prática, um sócio remoto pagando por um benefício que não usa.
-- =========================================================================

WITH classificado AS (
  SELECT
    CASE WHEN jogos_comparecidos = 0 THEN 'Nunca foi ao estádio'
         WHEN jogos_comparecidos <= 3 THEN 'Foi 1 a 3 vezes'
         ELSE 'Frequentador (4+)' END               AS perfil_presenca,
    *
  FROM vw_socio_economia
  WHERE coorte_12m_completa = 1
)
SELECT
  perfil_presenca,
  COUNT(*)                                          AS socios,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_da_coorte,
  ROUND(AVG(retido_12m) * 100, 1)                   AS retencao_12m_pct,
  ROUND(AVG(distancia_arena_km))                    AS dist_media_km,
  ROUND(AVG(moedas_mes), 1)                         AS engajamento_app_medio,
  ROUND(AVG(pontos_regra_atual), 1)                 AS pontos_regra_atual,
  ROUND(AVG(margem_m12), 2)                         AS margem_m12_media,
  ROUND(SUM(margem_m12))                            AS margem_m12_total,
  ROUND(100.0 * SUM(margem_m12) / SUM(SUM(margem_m12)) OVER (), 1) AS pct_da_margem
FROM classificado
GROUP BY perfil_presenca
ORDER BY socios DESC;
