# Proposta: destravar o sócio que não vai ao estádio

Documento de recomendação. Os números citados vêm da base fictícia do projeto
e servem para dimensionar ordem de grandeza, não para prever resultado.

---

## O diagnóstico em uma frase

O programa cobra mensalidade de todo mundo e só reconhece quem aparece. Quem
mora longe paga, não pontua, não progride e cancela na primeira renovação.

Três números sustentam o diagnóstico na base simulada:

- 22% da coorte nunca foi ao estádio e retém **39%** em 12 meses.
- 2.774 sócios estão com **zero ponto** — inclusive quem tem Fiel Digital e
  comparece, porque o plano não pontua por jogo na regra vigente.
- O benefício mais caro do programa, o cupom de parceiro, tem **34% de resgate**
  entre os menos engajados. É o público que mais precisaria dele.

---

## Frente A — Progressão sem depender de presença

### O que muda

Uma trilha de pontos paralela, somada à existente, com duas fontes novas:

| Fonte | Regra proposta | Por quê |
|---|---|---|
| Permanência | 0,5 ponto por mês ininterrupto de adimplência | Recompensa fidelidade financeira, que é o que o clube precisa |
| Engajamento | 1 ponto a cada 60 moedas no Universo SCCP | O app **já coleta** isso via quiz, palpite e pesquisa; hoje não conversa com a pontuação do Fiel Torcedor |
| Teto | Parte digital limitada a 2/3 dos pontos de presença | Protege a fila de quem enche o estádio |

### O teste que decide a viabilidade

Um programa de sócio-torcedor não pode deixar o remoto passar na frente do
frequentador. Na simulação, com o teto aplicado, **0,8% do público remoto**
ultrapassaria o frequentador mediano. A hierarquia sobrevive.

Sem o teto, a proposta compraria um problema maior do que resolve. Ele não é
detalhe de implementação: é a condição para a mudança ser defensável.

### Ganho dimensionado

Cerca de R$ 22 mil em 12 meses sobre o público remoto atual, assumindo 8 pontos
percentuais de retenção. **É o menor prêmio imediato das três frentes**, e isso
é honesto dizer. O valor da Frente A não está no retorno de 12 meses: está em
remover o teto estrutural que impede a base digital de crescer. Enquanto o
plano de entrada não levar a lugar nenhum, investir em aquisição para ele é
encher um balde furado.

### Riscos

- Percepção de que "pontos digitais valem menos que ir ao jogo" — verdade, e
  deve ser comunicado assim, explicitamente, não escondido.
- Gamificação vazia: se a moeda do app for fácil demais, a trilha vira ruído.
  Exige calibração e monitoramento da distribuição, não só da média.

---

## Frente B — Ativação de receita fora do dia de jogo

### B1. Resgatar o cupom que ninguém resgata

Cupom não resgatado é o pior dos mundos: não custa caixa, não gera valor
percebido, e ainda ocupa o espaço de comunicação de um benefício que
funcionaria. Na base, o resgate vai de 34% (dormentes) a 72% (intensos).

**Ação:** comunicação dirigida por faixa de engajamento, com o cupom entregue
onde a pessoa já está, e não esperando que ela procure. Estender o benefício ao
Fiel Digital em versão proporcional, para que o plano de entrada tenha algo
tangível todo mês.

**Ganho dimensionado:** ~R$ 162 mil em 12 meses, assumindo 35% de aumento na
comissão de parceiro.

### B2. Expandir o clube de vantagens nas categorias certas

Na base, streaming e marketplace tiram 47% a 52% da comissão de fora da Grande
São Paulo. Posto de combustível, 29%. A diferença não é acaso: benefício de dia
de jogo é inacessível para quem mora longe.

**Ação:** priorizar categorias de consumo cotidiano e digital na expansão do
clube de parceiros, com meta de alcance regional, não só de volume de GMV.

### B3. Recuperar a cadeira vazia

O programa já tem o mecanismo: liberação do ingresso até 48h antes, com
manutenção de parte da pontuação e crédito. Ainda assim, na simulação 6,3% dos
ingressos de sócio viram no-show puro — nem compareceu, nem liberou.

**Ação:** lembrete ativo no app com um toque para liberar, disparado na janela
em que a liberação ainda vale pontuação.

**Ganho dimensionado:** ~R$ 404 mil de receita potencial de revenda, assumindo
40% de conversão dos no-shows. É teto, não previsão: supõe que haveria
comprador, o que é razoável em jogo de alta demanda e otimista em meio de semana.

---

## Frente C — Mídia paga que vende o produto certo

### O achado

Na base, o público de fora da Grande São Paulo converte melhor e custa menos
por adesão (CPA de R$ 45 a R$ 75 contra R$ 74 a R$ 114), mas retém 69% contra
83%. Ajustando o CPA pela retenção, a vantagem encolhe.

A leitura: a mídia está comprando barato um público que o produto não segura.
Enquanto a Frente A não existir, escalar investimento nesse público piora o
resultado em vez de melhorar.

### O erro de leitura que isso corrige

Ranquear canal por CPA é o erro clássico em mídia paga de assinatura. Canal
barato pode estar comprando exatamente quem cancela em três meses. Por isso
toda a análise usa margem em horizonte fixo, e não CPA isolado.

### Ações

1. **Separar a comunicação por geografia.** Criativo para fora da Grande São
   Paulo não deveria prometer prioridade de ingresso, setor da arena, desconto
   de estacionamento ou loja da arena — nada disso é resgatável a 900 km. Deve
   vender conteúdo, clube de vantagens e progressão.
2. **Trocar a métrica de otimização.** Levar para o gerenciador um sinal de
   qualidade pós-adesão (sócio ativo no 3º mês), não só a conversão de assinatura.
3. **Operacionalizar os públicos.** A query `10` já entrega quatro audiências
   exportáveis com tamanho e ação sugerida: risco de cancelamento, candidato a
   upgrade, remoto engajado, remoto frio.

---

## Sequência recomendada

| Ordem | Frente | Por quê |
|---|---|---|
| 1º | B1 e B3 | Pagam agora, usam mecanismos que já existem, não exigem mudança de regra |
| 2º | A | Muda regra de pontuação: precisa de decisão de produto e comunicação cuidadosa |
| 3º | C | Só faz sentido escalar aquisição depois que o produto segura o público |

Os cenários da query `11` são independentes e **não devem ser somados sem
cuidado**: há sobreposição entre o sócio que seria retido pela trilha de pontos
e o que seria retido pelo benefício de parceiro.

---

## O que eu precisaria para levar isso a sério com dado real

Está em [`metodologia.md`](metodologia.md).
