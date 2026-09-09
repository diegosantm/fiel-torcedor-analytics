-- =========================================================================
-- 04 — Simulação da trilha de pontos digital  [FRENTE A: proposta]
--
-- PERGUNTA: se a pontuação passasse a reconhecer permanência e engajamento
-- além da presença, quantos sócios sairiam do zero — e quantos frequentadores
-- seriam ultrapassados na fila de prioridade?
--
-- A segunda parte da pergunta é a que decide se a proposta é viável. Um
-- programa de sócio-torcedor não pode desidratar a prioridade de quem enche
-- o estádio: se o remoto passar na frente do frequentador, a mudança compra
-- um problema maior do que resolve.
--
-- REGRA SIMULADA (proposta, não vigente):
--   pontos_presenca   = jogos comparecidos x pontos do plano          (mantida)
--   pontos_permanencia = 0,5 por mês ininterrupto de adimplência       (nova)
--   pontos_engajamento = 1 ponto a cada 60 moedas acumuladas no app    (nova)
--   teto digital       = pontos digitais não podem passar de 40% do total,
--                        para preservar a hierarquia de quem comparece
-- =========================================================================

WITH proposta AS (
  SELECT
    socio_id, plano, regiao, jogos_comparecidos, meses_ativos, moedas_mes,
    retido_12m, margem_m12,
    pontos_regra_atual,
    0.5 * meses_ativos                                   AS pts_permanencia_bruto,
    (moedas_mes * meses_ativos) / 60.0                   AS pts_engajamento_bruto
  FROM vw_socio_economia
  WHERE coorte_12m_completa = 1
),
com_teto AS (
  SELECT *,
    -- Teto: a parte digital fica limitada a 2/3 dos pontos de presença
    -- (o que equivale a no máximo 40% do total), exceto para quem tem zero
    -- presença, onde a trilha digital é a única fonte.
    CASE WHEN pontos_regra_atual = 0
         THEN pts_permanencia_bruto + pts_engajamento_bruto
         ELSE MIN(pts_permanencia_bruto + pts_engajamento_bruto,
                  pontos_regra_atual * 0.667) END        AS pts_digitais
  FROM proposta
),
final AS (
  SELECT *, pontos_regra_atual + pts_digitais AS pontos_proposta FROM com_teto
),
-- Mediana de pontos do frequentador na regra proposta. É o piso que a
-- trilha digital não pode atropelar: se muita gente remota passar disso,
-- a fila de prioridade deixou de refletir quem enche o estádio.
mediana_freq AS (
  SELECT pontos_proposta AS corte
  FROM final WHERE jogos_comparecidos >= 4
  ORDER BY pontos_proposta
  LIMIT 1 OFFSET (SELECT COUNT(*) / 2 FROM final WHERE jogos_comparecidos >= 4)
)
SELECT
  CASE WHEN jogos_comparecidos = 0 THEN 'Não vai ao estádio'
       WHEN jogos_comparecidos <= 3 THEN 'Vai pouco (1-3)'
       ELSE 'Frequentador (4+)' END                      AS perfil_presenca,
  COUNT(*)                                               AS socios,
  ROUND(AVG(pontos_regra_atual), 1)                      AS pontos_hoje,
  ROUND(AVG(pontos_proposta), 1)                         AS pontos_proposta,
  SUM(CASE WHEN pontos_regra_atual = 0 THEN 1 ELSE 0 END)     AS zerados_hoje,
  SUM(CASE WHEN pontos_proposta = 0 THEN 1 ELSE 0 END)        AS zerados_proposta,
  ROUND(MAX(pontos_proposta), 1)                         AS pontos_proposta_max,
  -- TESTE DA HIERARQUIA: quantos deste grupo passariam do frequentador
  -- mediano. Para os grupos remotos, este número precisa ser baixo — se não
  -- for, o teto está frouxo e a proposta desidrata quem vai ao estádio.
  SUM(CASE WHEN pontos_proposta > (SELECT corte FROM mediana_freq)
           THEN 1 ELSE 0 END)                            AS acima_do_freq_mediano,
  ROUND(100.0 * SUM(CASE WHEN pontos_proposta > (SELECT corte FROM mediana_freq)
           THEN 1 ELSE 0 END) / COUNT(*), 1)             AS pct_acima_do_freq_mediano
FROM final
GROUP BY perfil_presenca
ORDER BY pontos_proposta DESC;
