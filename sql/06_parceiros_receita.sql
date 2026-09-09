-- =========================================================================
-- 06 — Clube de vantagens: onde está a receita fora do dia de jogo
--      [FRENTE B: ativação de receita]
--
-- PERGUNTA: qual categoria de parceiro gera receita recorrente para o clube,
-- e qual delas alcança o sócio que não vai ao estádio?
--
-- A segunda parte importa mais que a primeira. Benefício de dia de jogo
-- (estacionamento, loja da arena, tour) é inacessível para quem mora longe.
-- Parceria de consumo cotidiano é o único benefício do programa que independe
-- de geografia — e portanto o único que pode sustentar o plano remoto.
-- =========================================================================

WITH base AS (
  SELECT
    t.parceiro,
    t.valor,
    t.comissao_clube,
    e.plano,
    e.regiao,
    CASE WHEN e.jogos_comparecidos = 0 THEN 'Não vai ao estádio'
         ELSE 'Vai ao estádio' END AS perfil_presenca
  FROM transacoes_parceiros t
  JOIN vw_socio_economia e ON e.socio_id = t.socio_id
  WHERE e.coorte_12m_completa = 1
)
SELECT
  parceiro,
  COUNT(*)                                            AS transacoes,
  ROUND(SUM(valor))                                   AS gmv,
  ROUND(SUM(comissao_clube))                          AS comissao_clube,
  ROUND(AVG(valor), 2)                                AS ticket_medio,
  ROUND(100.0 * SUM(comissao_clube) / SUM(valor), 2)  AS take_rate_pct,
  ROUND(100.0 * SUM(CASE WHEN perfil_presenca = 'Não vai ao estádio'
                         THEN comissao_clube ELSE 0 END) / SUM(comissao_clube), 1)
                                                      AS pct_comissao_de_remoto,
  ROUND(100.0 * SUM(CASE WHEN regiao <> 'Grande São Paulo'
                         THEN comissao_clube ELSE 0 END) / SUM(comissao_clube), 1)
                                                      AS pct_comissao_fora_gsp
FROM base
GROUP BY parceiro
ORDER BY comissao_clube DESC;
