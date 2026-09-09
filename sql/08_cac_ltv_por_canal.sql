-- =========================================================================
-- 08 — CAC, margem de 12 meses e payback por canal  [FRENTE C: mídia paga]
--
-- PERGUNTA: qual canal traz sócio que fica, e não só sócio que assina?
--
-- O erro clássico de leitura em mídia paga de assinatura é ranquear canal por
-- CPA. Canal barato pode estar comprando exatamente o público que cancela em
-- três meses; canal caro pode estar trazendo quem renova por anos. Só a
-- margem em horizonte fixo compara os dois de forma honesta.
--
-- Horizonte fixo de 12 meses (não margem acumulada até hoje) porque canais
-- mudam de peso ao longo do tempo: um canal que só passou a rodar em 2026
-- teria menos tempo de acúmulo e pareceria pior sem ter culpa.
-- =========================================================================

SELECT
  canal_aquisicao,
  COUNT(*)                                            AS socios,
  ROUND(AVG(cac), 2)                                  AS cac_medio,
  ROUND(AVG(margem_m12), 2)                           AS margem_m12_media,
  ROUND(AVG(margem_m12) / AVG(cac), 1)                AS ratio_margem_cac,
  ROUND(AVG(cac) / NULLIF(AVG(margem_m12) / 12.0, 0), 1) AS payback_meses,
  ROUND(AVG(retido_12m) * 100, 1)                     AS retencao_12m_pct,
  -- Mix: canal que só traz plano de entrada tem CAC baixo por composição,
  -- não por eficiência. Sem esta coluna, o ranking engana.
  ROUND(100.0 * SUM(CASE WHEN plano = 'Fiel Digital' THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                      AS pct_fiel_digital,
  ROUND(100.0 * SUM(CASE WHEN regiao <> 'Grande São Paulo' THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                      AS pct_fora_gsp,
  ROUND(SUM(cac))                                     AS investimento_total
FROM vw_socio_economia
WHERE coorte_12m_completa = 1
GROUP BY canal_aquisicao
ORDER BY ratio_margem_cac DESC;
