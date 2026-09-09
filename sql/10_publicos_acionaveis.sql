-- =========================================================================
-- 10 — Públicos acionáveis para mídia e CRM  [FRENTE C: mídia paga]
--
-- PERGUNTA: quais listas o time de mídia deveria estar subindo como público
-- customizado esta semana, e com qual oferta?
--
-- Esta é a query que vira operação. Não descreve o passado: separa a base
-- viva de hoje em grupos que pedem ações diferentes, com o tamanho de cada
-- um, para que a decisão de investimento seja dimensionada antes de ser
-- tomada. Cada linha é uma audiência exportável.
--
-- Os cortes são heurísticos e declarados. Não é um modelo de propensão
-- treinado: é a régua simples que precede o modelo, e que já resolve boa
-- parte do problema. Um classificador treinado seria o passo seguinte, e só
-- se justifica se ganhar do baseline abaixo.
-- =========================================================================

WITH vivos AS (
  SELECT * FROM vw_socio_economia WHERE ativo = 1
),
segmentado AS (
  SELECT
    socio_id, plano, regiao, canal_aquisicao, moedas_mes, meses_ativos,
    jogos_comparecidos, transacoes_parceiros, margem_total, distancia_arena_km,
    CASE
      -- Risco: paga há tempo, parou de interagir, não vai a jogo.
      WHEN moedas_mes < 5 AND jogos_comparecidos = 0 AND meses_ativos >= 6
        THEN 'A. Risco de cancelamento'
      -- Upgrade: mora perto, engaja, já vai a jogo, mas está no plano de entrada.
      WHEN plano IN ('Fiel Digital', 'Minha Vida')
           AND distancia_arena_km <= 120 AND jogos_comparecidos >= 3 AND moedas_mes >= 15
        THEN 'B. Candidato a upgrade de plano'
      -- Remoto valioso: longe, engajado, consome parceiro. Alvo do benefício digital.
      WHEN distancia_arena_km > 120 AND moedas_mes >= 15
        THEN 'C. Remoto engajado'
      -- Remoto frio: longe, sem engajamento. Alvo de reativação de conteúdo.
      WHEN distancia_arena_km > 120
        THEN 'D. Remoto frio'
      ELSE 'E. Base estável'
    END AS segmento
  FROM vivos
)
SELECT
  segmento,
  COUNT(*)                                            AS socios,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)  AS pct_base_ativa,
  ROUND(AVG(meses_ativos), 1)                         AS meses_ativos_medio,
  ROUND(AVG(moedas_mes), 1)                           AS engajamento_medio,
  ROUND(AVG(jogos_comparecidos), 1)                   AS jogos_medio,
  ROUND(AVG(transacoes_parceiros), 1)                 AS usos_parceiro_medio,
  ROUND(AVG(margem_total), 2)                         AS margem_acumulada_media,
  ROUND(SUM(margem_total))                            AS margem_acumulada_total
FROM segmentado
GROUP BY segmento
ORDER BY segmento;
