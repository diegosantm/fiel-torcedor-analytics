-- =========================================================================
-- 11 — Tamanho do prêmio: quanto valem as três frentes
--
-- PERGUNTA: se as propostas funcionarem, o resultado paga o esforço?
--
-- Esta query NÃO prevê nada. Ela dimensiona: aplica um delta arbitrado sobre
-- a base observada e mostra a ordem de grandeza. O delta é a aposta do
-- projeto, e está escrito aqui em vez de escondido numa planilha. Quem
-- discordar do número troca o valor e roda de novo — é para isso que ele
-- está isolado no CTE `premissas`.
--
-- Os três cenários são independentes e não devem ser somados sem cuidado:
-- há sobreposição entre o sócio que seria retido pela trilha de pontos e o
-- que seria retido pelo benefício de parceiro.
-- =========================================================================

WITH premissas AS (
  SELECT
    0.08  AS delta_retencao_trilha,   -- +8 p.p. de retenção 12m no público remoto
    0.35  AS delta_resgate_cupom,     -- +35% de resgate com comunicação dirigida
    0.40  AS delta_recuperacao_noshow -- 40% dos no-shows convertidos em liberação
),

-- Cenário 1 (Frente A) — trilha de pontos digital
c1 AS (
  SELECT
    'Frente A: trilha de pontos digital'                        AS cenario,
    COUNT(*)                                                    AS publico_alvo,
    ROUND(SUM(margem_m12) )                                     AS margem_hoje,
    ROUND(SUM(margem_m12) * (1 + (SELECT delta_retencao_trilha FROM premissas)))
                                                                AS margem_cenario,
    'Retenção 12m do sócio remoto sobe ' ||
      CAST(ROUND((SELECT delta_retencao_trilha FROM premissas) * 100) AS INT) ||
      ' p.p. ao ganhar progressão sem depender de presença'      AS premissa
  FROM vw_socio_economia
  WHERE coorte_12m_completa = 1 AND jogos_comparecidos = 0
),

-- Cenário 2 (Frente B) — resgate de cupom e clube de vantagens
c2 AS (
  SELECT
    'Frente B: ativação do clube de vantagens'                  AS cenario,
    COUNT(*)                                                    AS publico_alvo,
    ROUND(SUM(comissao_parceiros_m12))                          AS margem_hoje,
    ROUND(SUM(comissao_parceiros_m12) * (1 + (SELECT delta_resgate_cupom FROM premissas)))
                                                                AS margem_cenario,
    'Comissão de parceiro cresce ' ||
      CAST(ROUND((SELECT delta_resgate_cupom FROM premissas) * 100) AS INT) ||
      '% ao elevar o resgate do cupom nas faixas de menor engajamento' AS premissa
  FROM vw_socio_economia
  WHERE coorte_12m_completa = 1
),

-- Cenário 3 (Frente B) — recuperação de assento via pool
c3 AS (
  SELECT
    'Frente B: recuperação de assento (pool)'                   AS cenario,
    COUNT(DISTINCT i.socio_id)                                  AS publico_alvo,
    0                                                           AS margem_hoje,
    ROUND(SUM(i.valor) * (SELECT delta_recuperacao_noshow FROM premissas)
          * (SELECT margem_ingresso FROM vw_parametros))         AS margem_cenario,
    'Lembrete no app converte ' ||
      CAST(ROUND((SELECT delta_recuperacao_noshow FROM premissas) * 100) AS INT) ||
      '% dos no-shows em liberação para revenda'                AS premissa
  FROM ingressos i
  WHERE i.compareceu = 0 AND i.liberou = 0
)

SELECT cenario, publico_alvo, margem_hoje, margem_cenario,
       margem_cenario - margem_hoje AS ganho_estimado, premissa FROM c1
UNION ALL SELECT cenario, publico_alvo, margem_hoje, margem_cenario,
       margem_cenario - margem_hoje, premissa FROM c2
UNION ALL SELECT cenario, publico_alvo, margem_hoje, margem_cenario,
       margem_cenario - margem_hoje, premissa FROM c3;
