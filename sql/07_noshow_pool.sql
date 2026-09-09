-- =========================================================================
-- 07 — Cadeira vazia: no-show e uso do pool de ingressos
--      [FRENTE B: ativação de receita]
--
-- PERGUNTA: quanto assento pago fica vazio sem ser devolvido para revenda?
--
-- A regra do programa já prevê a devolução (check-out até 48h antes, com
-- manutenção de parte da pontuação e crédito). Quem não comparece e não
-- libera produz a pior combinação possível: cadeira vazia na TV, ingresso
-- que não pôde ser revendido e um sócio que pagou por nada.
--
-- NÍVEIS DE EVIDÊNCIA, não booleano: "não foi" é raso demais. As três saídas
-- (compareceu / liberou / sumiu) exigem ações diferentes do clube.
-- =========================================================================

WITH por_jogo AS (
  SELECT
    j.jogo_id,
    j.data,
    j.competicao,
    j.alta_demanda,
    COUNT(*)                                            AS ingressos_vendidos_socio,
    SUM(i.compareceu)                                   AS compareceram,
    SUM(i.liberou)                                      AS liberaram,
    SUM(CASE WHEN i.compareceu = 0 AND i.liberou = 0 THEN 1 ELSE 0 END) AS no_show,
    SUM(CASE WHEN i.compareceu = 0 AND i.liberou = 0 THEN i.valor ELSE 0 END) AS valor_parado
  FROM ingressos i
  JOIN jogos j ON j.jogo_id = i.jogo_id
  GROUP BY j.jogo_id
)
SELECT
  competicao,
  CASE alta_demanda WHEN 1 THEN 'Alta demanda' ELSE 'Demanda normal' END AS demanda,
  COUNT(*)                                              AS jogos,
  SUM(ingressos_vendidos_socio)                         AS ingressos_socio,
  ROUND(100.0 * SUM(compareceram) / SUM(ingressos_vendidos_socio), 1) AS presenca_pct,
  ROUND(100.0 * SUM(liberaram)   / SUM(ingressos_vendidos_socio), 1) AS liberacao_pct,
  ROUND(100.0 * SUM(no_show)     / SUM(ingressos_vendidos_socio), 1) AS no_show_pct,
  SUM(no_show)                                          AS assentos_perdidos,
  -- Receita potencial de revenda: assento que sumiu, avaliado ao preço do
  -- jogo. É teto, não previsão — supõe que haveria comprador, o que é
  -- razoável em alta demanda e otimista em jogo de meio de semana.
  ROUND(SUM(valor_parado))                              AS receita_revenda_potencial
FROM por_jogo
GROUP BY competicao, alta_demanda
ORDER BY receita_revenda_potencial DESC;
