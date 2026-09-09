-- =========================================================================
-- 09 — Funil de mídia paga por público geográfico  [FRENTE C: mídia paga]
--
-- PERGUNTA: a comunicação que roda para quem mora longe está vendendo um
-- produto que essa pessoa pode usar?
--
-- Praticamente todo benefício destacado na comunicação do programa depende
-- de estar em São Paulo: prioridade de ingresso, setor da arena, desconto de
-- estacionamento, loja da arena, tour. Para o público de fora, a oferta
-- carrega uma promessa que ele não consegue resgatar — e isso deveria
-- aparecer como pior conversão de clique e pior retenção pós-adesão.
--
-- Esta query cruza a entrega de mídia (nível campanha) com o desfecho do
-- sócio (nível pessoa), que é o ponto onde a maioria dos relatórios de mídia
-- para porque o gerenciador não enxerga o que aconteceu depois da conversão.
-- =========================================================================

WITH midia AS (
  SELECT
    canal,
    publico,
    SUM(custo)      AS custo,
    SUM(impressoes) AS impressoes,
    SUM(cliques)    AS cliques,
    SUM(adesoes)    AS adesoes
  FROM campanhas_midia
  GROUP BY canal, publico
),
desfecho AS (
  SELECT
    canal_aquisicao AS canal,
    CASE WHEN regiao <> 'Grande São Paulo' THEN 'Fora da Grande SP' ELSE 'Grande SP' END AS publico,
    COUNT(*)                        AS socios_coorte,
    AVG(retido_12m)                 AS retencao,
    AVG(margem_m12)                 AS margem_m12
  FROM vw_socio_economia
  WHERE coorte_12m_completa = 1
    AND canal_aquisicao IN ('Meta Ads', 'Google Ads', 'TikTok Ads')
  GROUP BY canal, publico
)
SELECT
  m.canal,
  m.publico,
  m.impressoes,
  m.cliques,
  ROUND(100.0 * m.cliques / m.impressoes, 2)          AS ctr_pct,
  m.adesoes,
  ROUND(100.0 * m.adesoes / m.cliques, 2)             AS conv_clique_adesao_pct,
  ROUND(m.custo / m.adesoes, 2)                       AS cpa,
  ROUND(d.retencao * 100, 1)                          AS retencao_12m_pct,
  ROUND(d.margem_m12, 2)                              AS margem_m12_media,
  -- CPA ajustado pela retenção: quanto custa um sócio que sobrevive a
  -- 12 meses, e não apenas um cadastro criado.
  ROUND(m.custo / (m.adesoes * d.retencao), 2)        AS cpa_por_socio_retido
FROM midia m
JOIN desfecho d ON d.canal = m.canal AND d.publico = m.publico
ORDER BY m.canal, m.publico;
