# Metodologia, premissas e limites

## O que é real e o que é inventado

| Real (publicado em fieltorcedor.com.br, set/2026) | Inventado (premissa do gerador) |
|---|---|
| Os cinco planos e suas mensalidades | Quantos sócios existem em cada plano |
| Pontuação base por plano (0 a 1,5 por jogo) | Taxas de churn e sua sensibilidade |
| Pontuação exige compra **mais** acesso ao jogo | Distribuição de engajamento no app |
| Pontos valem 10% do original após 12 meses | Custos de mídia, CPM, CTR e CAC |
| Liberação do ingresso até 48h antes, com crédito | Custo operacional e de conteúdo por sócio |
| Cupom de 50% da mensalidade em parceiro, só planos pagos | Quais parceiros existem e seus take rates |
| Fiel Digital sem desconto, prioridade ou pontuação | Distribuição geográfica da base |
| Setores da arena por plano | Calendário de jogos e demanda por partida |

Toda premissa vive em um único bloco `PARAMS` em `src/gerar_base.py`. Trocar um
número e rodar de novo é o experimento inteiro.

## Por que base fictícia não invalida o projeto

Ela invalida as **conclusões numéricas** — e isso está escrito em cada arquivo,
inclusive no cabeçalho do dashboard. O que ela não invalida é o que o projeto
de fato entrega: quais perguntas fazer, qual métrica compara grupos de forma
honesta, onde a leitura ingênua engana, e qual corte transforma um número em
decisão.

Há um ganho que dado real não daria: a verdade é conhecida. Dá para verificar
se o método recupera a estrutura que foi plantada, e dá para mostrar quando ele
não recupera.

## Decisões que mudam as conclusões

### 1. Bilheteria fora da margem do programa

Três razões, em ordem de peso:

1. O assento seria vendido de qualquer forma na maior parte dos jogos.
   Creditá-lo ao programa é atribuir ao sócio-torcedor uma receita preexistente.
2. O sócio compra com 25% a 35% de desconto. Por assento, o programa **reduz** a
   receita de bilheteria — contá-la como ganho inverte o sinal.
3. Sem separar, todo plano presencial vence por construção, e a pergunta do
   projeto fica respondida pela definição da métrica.

A view expõe `margem_m12_com_bilheteria` para quem quiser a visão de receita
total do torcedor. Ela existe nomeada justamente para que a escolha seja
explícita e reversível.

### 2. Coorte fechada e horizonte fixo

Toda comparação usa apenas sócios cuja janela de 12 meses terminou, e mede a
margem dos 12 primeiros meses de cada um.

Sem o filtro de coorte, quem aderiu há dois meses conta como "não churnou" e
infla a retenção. O viés não é neutro: cresce quanto mais recente for a coorte,
então favorece exatamente os grupos que cresceram no fim da janela.

Sem o horizonte fixo, a comparação vira função da data de entrada. Um canal que
só passou a rodar em 2026 pareceria pior sem ter culpa.

O botão do dashboard permite desligar a coorte, e quando desligada a tese avisa
sozinha que a retenção está inflada. Deixar desligar é melhor que esconder: a
contagem total às vezes é a pergunta certa.

### 3. Ausência não é zero

O Fiel Digital não recebe cupom pela regra atual. Somá-lo à faixa de pior
resgate transformaria ausência de benefício em desempenho ruim, que é uma
leitura diferente e leva a uma ação diferente. Ele fica em categoria própria,
nunca na faixa extrema, com o texto dizendo o que a categoria é.

### 4. Níveis de evidência em vez de booleano

"Foi ao jogo?" é raso demais. A falta se divide em liberou o ingresso (usou o
mecanismo que o programa oferece) e sumiu (nem compareceu, nem liberou). São
situações que pedem ações diferentes do clube, e a métrica precisa distinguir.

### 5. Fonte única de leitura

Margem, tempo de vida e faixa de engajamento são definidos uma vez, na view
`vw_socio_economia`. Nenhuma query e nenhum trecho de JavaScript recalcula
essas regras. O crosscheck Python × JavaScript no dashboard existe para pegar
quando isso for violado: divergência ali quase sempre significa que o filtro de
coorte foi aplicado de um lado e não do outro.

## Limites que o projeto não resolve

- **Correlação não é causa, e aqui nem correlação é.** A relação entre
  engajamento e retenção foi escrita no gerador. Em dados reais, quem engaja
  mais pode ser simplesmente quem já era mais fiel — o app seria sintoma, não
  causa. Distinguir exige teste controlado.
- **Os cenários da query 11 não são previsão.** São dimensionamento: aplicam um
  delta arbitrado sobre a base observada para mostrar ordem de grandeza. O delta
  está isolado num CTE `premissas` justamente para que quem discordar troque o
  número e rode de novo.
- **A receita de revenda do pool é teto, não expectativa.** Supõe que haveria
  comprador para cada assento liberado. Razoável em jogo de alta demanda,
  otimista em meio de semana.
- **Não há efeito de rede nem sazonalidade de desempenho em campo.** Título e
  eliminação mexem em adesão e churn de forma que o gerador não modela.
- **Os cenários se sobrepõem.** O mesmo sócio pode ser retido tanto pela trilha
  de pontos quanto pelo benefício de parceiro. Somar os três ganhos superestima.

## O que eu faria com dado real

Em ordem, e cada passo só se justifica se o anterior fechar:

1. **Confirmar o que cada campo registra de fato** com quem opera o sistema.
   Nome de campo não é significado de campo, e métrica construída sobre
   suposição de schema é a forma mais cara de errar.
2. **Reproduzir as queries 01 a 03 na base real** e ver se a estrutura se
   mantém. Se o gap de retenção entre remoto e presencial não aparecer, a
   premissa central do projeto cai e a proposta muda.
3. **Cruzar o cadastro com engajamento no app**, que hoje provavelmente vivem em
   sistemas separados. Sem esse join, a Frente A não é mensurável.
4. **Rodar um teste controlado do cupom** antes de escalar: um grupo recebe
   comunicação dirigida, outro não, e mede-se resgate e retenção. É a frente
   mais barata de testar e a que paga mais rápido.
5. **Só então** discutir modelo de propensão. A segmentação heurística da query
   `10` é o baseline; um classificador treinado só se justifica se ganhar dela.

## Reprodutibilidade

Semente fixa (`SEED = 42`). Reexecutar `src/gerar_base.py` produz exatamente a
mesma base. O dashboard carrega um carimbo de build (hash dos dados embarcados)
e reconta as linhas em runtime, acusando divergência se o HTML e o gerador
saírem de sincronia.
