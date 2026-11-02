# Rali do Midterm — sazonalidade do S&P 500

Painel didático sobre o comportamento do S&P 500 no ciclo presidencial dos EUA. O foco é o ano de eleição de meio de mandato (midterm) e o período que vem depois dele.

**Abrir o painel:** https://nilsonjacobcosta.github.io/market-lab/sazonalidade/rali-midterm/

## Objetivo

Explicar, inclusive para iniciantes:

- como o S&P 500 se comportou em cada ano do mandato presidencial americano desde 1950;
- por que o 2º ano (midterm) costuma ser o mais fraco;
- o que aconteceu depois do fim de outubro nos 19 midterms da amostra;
- onde 2026 se encaixa nesse padrão.

## Conteúdo

| Seção | O que mostra |
|---|---|
| Resumo | Retorno médio de 12 meses após outubro (+16,6%) e os 19 de 19 casos positivos |
| Entenda em três passos | O ciclo presidencial explicado sem jargão |
| Gráfico 1 | Média e mediana por ano do ciclo |
| Gráfico 2 | Retorno a partir de outubro, por grupo (até dezembro e em 12 meses) |
| Gráfico 3 | Todos os midterms ano a ano, com 6 medidas selecionáveis |
| Outubro e novembro | Retorno médio mensal citado no vídeo |
| Simulador | Valor hipotético aplicado no fim de outubro, pior, médio e melhor caso |
| Contexto | Pregão de 30/10/2026 e as teses do autor (marcadas como opinião) |
| Cuidados e glossário | Limitações da análise e termos explicados |

## Estrutura

```
sazonalidade/rali-midterm/
├── index.html              # painel (HTML, CSS e JS num arquivo só, sem dependências)
├── data/
│   └── midterm-sp500.json  # os mesmos dados do painel, em formato reutilizável
└── README.md
```

Endereço publicado: https://nilsonjacobcosta.github.io/market-lab/sazonalidade/rali-midterm/

## Fontes

- Mundstock, Igor. *Estão prontos para o rally de Natal? Estudo de sazonalidade do mercado americano*. YouTube, canal @igormundstock, out/nov 2026. https://youtu.be/-WnbOPAx5Hc
- Para validação: FRED, Federal Reserve Bank of St. Louis, série SP500 (https://fred.stlouisfed.org/series/SP500); S&P Dow Jones Indices (https://www.spglobal.com/spdji/en/indices/equity/sp-500/).

## Limitações

- Os números vêm de um estudo gerado por IA e exibido no vídeo, sem fonte primária declarada. Ainda não foram auditados contra séries oficiais.
- A amostra tem 19 midterms. Padrões com poucos casos podem falhar.
- Os grupos "forte" (9) e "fraco" (8) somam 17 anos: 1994 e 2018 ficaram entre 0% e 5% até outubro.
- O valor de outubro de 2026 aparece como cerca de −0,6% no estudo e cerca de −0,93% na fala do autor.

## Próximos passos

- [ ] Recalcular todas as séries a partir de dados oficiais (FRED / S&P DJI) com um script versionado.
- [ ] Incluir retorno total (com dividendos) além do retorno de preço.
- [ ] Atualizar 2026 após o fechamento de novembro e dezembro.
- [ ] Revisar a literatura acadêmica sobre o ciclo presidencial e citá-la no painel.

## Aviso

Material educativo. Não é recomendação de investimento. Rentabilidade passada não garante resultado futuro.
