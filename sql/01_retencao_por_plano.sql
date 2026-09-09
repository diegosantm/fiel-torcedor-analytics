-- =========================================================================
-- 01 — Retenção de 12 meses por plano  [FRENTE A: produto e progressão]
--
-- PERGUNTA: o plano que não dá acesso ao estádio segura o sócio?
--
-- DISCIPLINA DE COORTE: só entram sócios cuja janela de 12 meses já fechou.
-- Sem esse filtro, quem aderiu há dois meses conta como "não churnou" e
-- infla a retenção de todo mundo — o viés cresce quanto mais recente for a
-- coorte, então a comparação entre planos ficaria enviesada a favor de
-- quem cresceu mais rápido no fim da janela.
-- =========================================================================

SELECT
  plano,
  COUNT(*)                                            AS socios_na_coorte,
  ROUND(AVG(retido_12m) * 100, 1)                     AS retencao_12m_pct,
  ROUND(AVG(meses_ativos), 1)                         AS meses_ativos_medio,
  ROUND(AVG(cac), 2)                                  AS cac_medio,
  ROUND(AVG(margem_m12), 2)                           AS margem_m12_media,
  ROUND(AVG(margem_m12) / AVG(cac), 1)                AS ratio_margem_cac,
  -- Meses até pagar o CAC, pela margem média mensal dos 12 primeiros meses
  ROUND(AVG(cac) / NULLIF(AVG(margem_m12) / 12.0, 0), 1) AS payback_meses,
  ROUND(AVG(pontos_regra_atual), 1)                   AS pontos_medios_regra_atual
FROM vw_socio_economia
WHERE coorte_12m_completa = 1
GROUP BY plano
ORDER BY retencao_12m_pct;
