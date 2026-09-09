# Fiel Torcedor: quanto vale o sócio que não vai ao estádio

Projeto de análise de dados e performance de mídia paga aplicado a um programa
de sócio-torcedor. Base fictícia, pipeline reprodutível, dashboard interativo.

> **Nenhum dado real do Sport Club Corinthians Paulista foi utilizado.**
> A estrutura de planos, mensalidades, pontuação e a regra do cupom de parceiro
> reproduzem o que está publicado em [fieltorcedor.com.br](https://www.fieltorcedor.com.br)
> (consulta em setembro de 2026). Volumes, custos de mídia, taxas de churn e
> engajamento são premissas declaradas no gerador. Os números **não são
> evidência sobre o programa real**: o que o projeto entrega é o desenho da
> medição e o corte de decisão, testados contra uma base cuja verdade é conhecida.

---

## O problema

A régua de mérito do Fiel Torcedor é a presença. Pontua-se por compra mais
acesso ao jogo, e a pontuação define a prioridade na fila de ingressos. Quem
mora longe da Neo Química Arena paga todo mês e nunca sai do zero.

O programa já reconhece esse público: o plano **Fiel Digital** (R$ 14,90) é
descrito no próprio site como a opção para quem mora fora de São Paulo. Mas ele
não dá desconto de ingresso, não dá prioridade, não pontua e não recebe o cupom
de parceiro que os planos pagos recebem. É um plano de entrada que não leva a
lugar nenhum.

**A pergunta do projeto:** quanto vale destravar a progressão de quem sustenta
o programa sem nunca ocupar uma cadeira, e o que precisa mudar para isso não
desidratar quem enche o estádio?

## As três frentes

| Frente | Pergunta | Queries |
|---|---|---|
| **A. Produto e progressão** | Existe régua de mérito alternativa à presença, e ela já está sendo coletada? | `01`, `02`, `03`, `04` |
| **B. Ativação de receita** | O benefício mais caro chega a quem paga por ele, e quanto assento pago vira cadeira vazia? | `05`, `06`, `07` |
| **C. Mídia paga e dados** | Qual canal traz sócio que fica, e a comunicação vende um produto que o público remoto consegue usar? | `08`, `09`, `10` |
| Fechamento | O resultado paga o esforço? | `11` |

## O que a base mostra

Coorte de 12.522 sócios com janela de 12 meses fechada.

- **Retenção de 12 meses:** 59% no Fiel Digital contra 84% a 96% nos planos
  presenciais. Quem nunca foi ao estádio é 22% da coorte e retém 39%.
- **Zero ponto:** 2.774 sócios pagam há meses e não progridem. Inclui todo o
  Fiel Digital, que não pontua nem quando comparece, porque o plano tem
  pontuação zero por jogo na regra vigente.
- **Trilha de pontos simulada:** tira todos esses sócios do zero, e apenas 0,8%
  deles passaria do frequentador mediano. A hierarquia da fila sobrevive.
- **Cupom de parceiro:** 34% de resgate na faixa dormente contra 72% na
  intensa. O benefício mais caro do programa é o que menos chega a quem
  precisa ser reativado.
- **Alcance por categoria:** streaming e marketplace tiram 47% a 52% da
  comissão de fora da Grande São Paulo; posto de combustível, 29%. Parceria de
  consumo cotidiano é o único benefício que independe de geografia.
- **Mídia paga:** o público de fora converte melhor e custa menos por adesão,
  mas retém 69% contra 83% da Grande São Paulo. O CPA favorece um público que
  o produto não segura.

## Três decisões metodológicas

Estas decisões mudam as conclusões, então estão declaradas em vez de embutidas.

**1. A bilheteria fica fora da margem do programa.** O assento seria vendido de
qualquer forma na maior parte dos jogos, e o sócio ainda compra com 25% a 35%
de desconto — por assento, o programa *reduz* a receita de bilheteria. Incluí-la
faria todo plano presencial vencer por construção, respondendo a pergunta do
projeto pela definição da métrica em vez de pelos dados. A versão com
bilheteria existe na view, nomeada, para quem quiser a visão de receita total.

**2. Toda comparação roda em coorte fechada e horizonte fixo.** Só entram
sócios cuja janela de 12 meses terminou, e a margem considerada é a dos 12
primeiros meses de cada um. Sem isso, quem aderiu em 2023 teve 44 meses para
acumular receita e quem aderiu em julho teve dois: a comparação entre planos
viraria função da data de entrada.

**3. A relação entre engajamento e retenção é premissa, não descoberta.** Em
base fictícia ela foi escrita no gerador. O valor do recorte é o desenho da
medição. Em dados reais exigiria teste controlado, porque quem engaja mais
pode ser simplesmente quem já era mais fiel.

## Um teste que pegou um erro meu

O caso-teste "ninguém comparece a mais jogos do que o calendário permite"
falhou em 3 sócios. A investigação mostrou que o erro era do teste: eu havia
arbitrado "no máximo 3 jogos por mês de vida", e o calendário simulado tem
meses com até 7 jogos. O teste foi reescrito para contar os jogos que de fato
ocorreram na janela de cada sócio. Fica registrado porque é o comportamento
que o teste deveria ter: disparar contra a suposição, não contra o dado.

## Como rodar

```bash
pip install pandas numpy tabulate
python src/gerar_base.py        # gera os CSVs (SEED=42, reprodutível)
python src/carregar_db.py       # carrega no SQLite e aplica o schema
python src/rodar_analises.py    # roda as 11 queries → output/
python src/gerar_dashboard.py   # monta o dashboard HTML de arquivo único
```

O dashboard abre com duplo clique. Não precisa de servidor nem de rede: o
Chart.js vai embutido no arquivo.

## Estrutura

```
├── src/
│   ├── gerar_base.py           # gerador da base fictícia, premissas em PARAMS
│   ├── carregar_db.py          # carga no SQLite + schema
│   ├── rodar_analises.py       # executa as queries, exporta CSV e relatório
│   ├── gerar_dashboard.py      # casos-teste, crosscheck e build do HTML
│   └── template_dashboard.html # template com placeholders __DATA__ e __CHARTJS__
├── sql/
│   ├── 00_schema.sql           # views derivadas — fonte única de leitura
│   └── 01..11_*.sql            # uma query por pergunta de negócio
├── data/                       # CSVs e banco (gerados)
├── output/                     # resultados + relatorio.md
├── dashboard/                  # HTML de arquivo único
└── docs/
    ├── proposta.md             # as três frentes, com ações e riscos
    └── metodologia.md          # premissas, limites e o que faria com dado real
```

## Arquitetura do dashboard

Regra que sustenta tudo: nenhum agregado é pré-calculado. Todo número na tela é
função pura do subconjunto filtrado.

- A base viaja **linha a linha**, 18.000 sócios como arrays de inteiros e
  índices de categoria. O navegador não consegue recortar o que não tem.
- Um `state`, um predicado `passes(r)`, um `render()` que refaz a tela inteira.
- `openDrill(titulo, linhas)` genérico: qualquer KPI, barra ou linha de tabela
  abre a base que gerou o número, com quem saiu antes no topo.
- Seção de validação com casos-teste, crosscheck Python × JavaScript e as
  regras aplicadas em texto numerado.
- A tese no topo é gerada do recorte: muda com o filtro e avisa sozinha quando
  a coorte está desligada ou quando boa parte do recorte não recebe cupom.

## Verificação

```bash
node verificar_dashboard.js
```

Extrai o script do HTML gerado, stuba `document` e `Chart`, e roda asserções
sobre `passes()`, `render()`, a partição dos segmentos, o `openDrill` e o
crosscheck. Confere também por texto a regra de CSS `.modal-bg[hidden]`, que
nenhum teste headless pega e que quebra o modal inteiro se faltar.

## Licença

Código sob MIT. Chart.js em `vendor/` sob licença própria (MIT), incluída.
Marcas e nomes do Sport Club Corinthians Paulista pertencem ao clube e são
citados apenas para contextualizar o estudo.
