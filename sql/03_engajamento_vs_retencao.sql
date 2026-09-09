-- =========================================================================
-- 03 — Engajamento no app x retenção  [FRENTE A: produto e progressão]
--
-- PERGUNTA: o engajamento digital (moedas do Universo SCCP) prevê retenção
-- entre quem NÃO vai ao estádio? Se prevê, existe uma régua de mérito
-- alternativa à presença, e ela já está sendo coletada — só não está
-- conectada à pontuação do Fiel Torcedor.
--
-- RESSALVA METODOLÓGICA (vale para todo este arquivo): em base fictícia, a
-- relação entre engajamento e retenção é uma PREMISSA do gerador, não uma
-- descoberta. O valor deste recorte é mostrar o desenho da medição e o corte
-- de decisão. Em dados reais, a mesma correlação precisaria de teste
-- controlado: quem engaja mais pode ser simplesmente quem já era mais fiel.
-- =========================================================================

SELECT
  faixa_engajamento,
  CASE WHEN jogos_comparecidos = 0 THEN 'Não vai ao estádio'
       ELSE 'Vai ao estádio' END                    AS perfil_presenca,
  COUNT(*)                                          AS socios,
  ROUND(AVG(retido_12m) * 100, 1)                   AS retencao_12m_pct,
  ROUND(AVG(meses_ativos), 1)                       AS meses_ativos_medio,
  ROUND(AVG(transacoes_parceiros), 1)               AS usos_parceiro_medio,
  ROUND(AVG(margem_m12), 2)                         AS margem_m12_media
FROM vw_socio_economia
WHERE coorte_12m_completa = 1
GROUP BY faixa_engajamento, perfil_presenca
ORDER BY perfil_presenca DESC, faixa_engajamento;
