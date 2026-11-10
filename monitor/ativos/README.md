# Painel de Ativos

Painel de mercado organizado em blocos: índices americanos, europeus e asiáticos, cesta DX, commodities, outros ativos (futuros, juros, cripto), moedas do mundo e emergentes.

## Fonte e atualização

- Cotações: Yahoo Finance (endpoint `chart`), coletadas por `scripts/ativos/coletar_ativos.py`.
- Os dados ficam na branch `dados-ativos` (arquivo `cotacoes.json`), separada da `main`, para não poluir o histórico do código. A página lê o JSON direto dessa branch.
- A página fica na `main` (GitHub Pages).
- Workflow `.github/workflows/atualizar-ativos.yml`: cerca de a cada 30 minutos. O GitHub pode atrasar ou pular execuções.
- Cada linha mostra a hora da cotação. Itens com **captura** são o valor transcrito da captura de tela de 10/11/2026 (sem fonte automática); **anterior** é a última cotação obtida antes de uma falha; **sem fonte** não tem cotação automática.
- Se a atualização passar de 90 minutos, a página mostra um aviso.

## Limitações

- O endpoint do Yahoo não é oficial e pode mudar ou bloquear sem aviso.
- Sem cobertura automática: BCOM, CME FedWatch, minério de ferro, CDS Brasil, juros de 2 anos e de GB, DE, JP e CN.
- Cotações podem ter atraso; não são tempo real.

## Para mudar ativos

Edite `scripts/ativos/catalogo.py`. Para testar localmente: `COTACOES_SAIDA=/tmp/cotacoes.json python3 scripts/ativos/coletar_ativos.py`.

Material educativo. Não é recomendação de investimento.
