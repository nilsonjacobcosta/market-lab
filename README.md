# market-lab

Laboratório de painéis e estudos sobre mercado financeiro: sazonalidade, ciclos econômicos e monitores de gráficos. Cada projeto fica numa pasta própria e é publicado pelo GitHub Pages.

**Site:** https://nilsonjacobcosta.github.io/market-lab/

## Projetos

| Projeto | Pasta | Status | Descrição |
|---|---|---|---|
| Rali do Midterm | [`sazonalidade/rali-midterm`](sazonalidade/rali-midterm/) | Publicado | Sazonalidade do S&P 500 no ano de eleição de meio de mandato nos EUA e nos 12 meses seguintes |
| Monitor multi-gráficos | [`monitor/`](monitor/) | Planejado | Vários gráficos de mercado na mesma tela (widgets do TradingView) |

## Estrutura

```
market-lab/
├── index.html          # página inicial com o índice dos painéis
├── sazonalidade/       # estudos de sazonalidade e ciclos
│   └── rali-midterm/
├── monitor/            # painéis de acompanhamento de mercado
└── README.md
```

## Como adicionar um novo painel

1. Crie uma pasta dentro da categoria certa (`sazonalidade/`, `monitor/` ou uma nova).
2. Coloque o painel como `index.html` dentro dela, com os dados em `data/` e um `README.md` com objetivo, fontes e limitações.
3. Adicione um card na página inicial (`index.html` da raiz) e uma linha na tabela acima.

## Princípios

- Cada número tem fonte citada e verificável.
- Dados ainda não auditados contra séries oficiais são marcados como tal.
- Opiniões de terceiros aparecem separadas dos dados.

## Aviso

Material educativo. Não é recomendação de investimento. Rentabilidade passada não garante resultado futuro.
