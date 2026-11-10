# market-lab

Laboratório de painéis e estudos sobre mercado financeiro: sazonalidade, ciclos econômicos e monitores de gráficos. Cada projeto fica numa pasta própria e é publicado pelo GitHub Pages.

**Site:** https://nilsonjacobcosta.github.io/market-lab/

## Projetos

| Projeto | Pasta | Status | Descrição |
|---|---|---|---|
| Rali do Midterm | [`sazonalidade/rali-midterm`](sazonalidade/rali-midterm/) | Publicado, auditado | Sazonalidade do S&P 500 no ano de eleição de meio de mandato nos EUA e nos 12 meses seguintes |
| Termômetro macro do midterm | [`macro/termometro-midterm`](macro/termometro-midterm/) | Publicado | Juros, petróleo, dólar, metais e índices no ciclo presidencial; o que explica outubro de 2026 |
| Monitor BESST | [`carteiras/monitor-besst`](carteiras/monitor-besst/) | Publicado, atualização automática | Preço-teto, DPA médio, DY médio e controle acionário de 144 papéis dos setores BESST |
| Monitor de Dividendos Lisboa | [`portugal/monitor`](portugal/monitor/) | Publicado (estudo), atualização automática | 16 ações da Euronext Lisbon para residentes em Portugal: proventos do cadastro oficial, preço-teto com juro das OT a 10 anos (BCE), alertas; manutenção em [`manutencao/portugal`](manutencao/portugal/) |
| Painel de Ativos | [`monitor/ativos`](monitor/ativos/) | Atualização automática (cerca de 30 min) | Índices, moedas, commodities, juros e cripto organizados como um painel de mercado; cada cotação com hora e fonte, itens sem fonte automática marcados |
| Tendências de mercado (EUA) | [`tendencias`](tendencias/) | Em construção (página pronta; aguardando a primeira coleta automática) | Matriz porte × estilo (9 ETFs Russell) contra o mercado amplo (IWV): retorno relativo em 1, 3, 6 e 12 meses e posição frente à média de 200 dias; modos Iniciante e Completo |
| Monitor multi-gráficos | [`monitor/`](monitor/) | Planejado | Vários gráficos de mercado na mesma tela (widgets do TradingView) |

## Estrutura

```
market-lab/
├── index.html          # página inicial com o índice dos painéis
├── sazonalidade/       # estudos de sazonalidade e ciclos
│   └── rali-midterm/
├── carteiras/          # monitores de carteiras de dividendos
│   └── monitor-besst/
├── macro/              # juros, commodities, dólar e índices
│   └── termometro-midterm/
├── dados/              # dados brutos, processados e documentação (ver dados/README.md)
├── scripts/            # código que recalcula todos os números
├── monitor/            # painéis de acompanhamento de mercado
├── tendencias/         # matriz porte × estilo dos EUA (ETFs Russell)
└── README.md
```

## Como adicionar um novo painel

1. Crie uma pasta dentro da categoria certa (`sazonalidade/`, `monitor/` ou uma nova).
2. Coloque o painel como `index.html` dentro dela, com os dados em `data/` e um `README.md` com objetivo, fontes e limitações.
3. Adicione um card na página inicial (`index.html` da raiz) e uma linha na tabela acima.

## Princípios

- Cada número tem fonte citada e verificável.
- Os números são recalculados por scripts versionados a partir dos dados brutos (ver [`dados/README.md`](dados/README.md)).
- Opiniões de terceiros aparecem separadas dos dados.

## Aviso

Material educativo. Não é recomendação de investimento. Rentabilidade passada não garante resultado futuro.
