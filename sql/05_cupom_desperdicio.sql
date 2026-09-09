-- =========================================================================
-- 05 — O cupom que ninguém resgata  [FRENTE B: ativação de receita]
--
-- PERGUNTA: o benefício mais caro do programa (50% da mensalidade em cupom
-- de parceiro, oferecido hoje aos planos pagos) está chegando a quem paga?
--
-- Um cupom não resgatado é o pior dos mundos em programa de fidelidade: não
-- custa caixa, mas também não gera valor percebido, e ainda ocupa o espaço
-- de comunicação de um benefício que funcionaria. Medir taxa de resgate por
-- faixa de engajamento diz se o problema é a oferta ou a entrega da oferta.
--
-- "SEM MEDIDA" NÃO É ZERO: o Fiel Digital não recebe cupom pela regra atual,
-- então ele não é um caso de resgate baixo — é ausência de benefício. Fica
-- em linha própria, nunca somado à faixa de pior desempenho.
-- =========================================================================

SELECT
  CASE WHEN plano = 'Fiel Digital' THEN '— sem cupom (regra atual) —'
       ELSE faixa_engajamento END                    AS faixa,
  COUNT(*)                                           AS socios,
  SUM(cupons_emitidos)                               AS cupons_emitidos,
  SUM(cupons_resgatados)                             AS cupons_resgatados,
  CASE WHEN SUM(cupons_emitidos) = 0 THEN NULL
       ELSE ROUND(100.0 * SUM(cupons_resgatados) / SUM(cupons_emitidos), 1)
  END                                                AS taxa_resgate_pct,
  ROUND(SUM(custo_cupom_total))                      AS custo_cupom_total,
  ROUND(AVG(transacoes_parceiros), 1)                AS usos_parceiro_medio,
  ROUND(SUM(comissao_parceiros_total))               AS comissao_gerada,
  -- Retorno do benefício: cada real de cupom bancado pelo clube volta em
  -- quanto de comissão de parceiro?
  CASE WHEN SUM(custo_cupom_total) = 0 THEN NULL
       ELSE ROUND(SUM(comissao_parceiros_total) / SUM(custo_cupom_total), 2)
  END                                                AS retorno_por_real_de_cupom
FROM vw_socio_economia
WHERE coorte_12m_completa = 1
GROUP BY faixa
ORDER BY faixa;
