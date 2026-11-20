# Mercados e ciclos

**Status:** atualização automática. A primeira coleta real rodou em 17/11/2026 (47 de 48 séries; `risco_hy` não é coletada por licença) e 3 pontos de cada série coletada foram conferidos com a fonte oficial. Os 9 símbolos do widget Advanced Chart abriram no navegador. Ressalvas não bloqueantes dos juízes seguem em `docs/monitor-mercados/pareceres-juizes.md`.

## O que mostra

Onze conjuntos de gráficos para acompanhar como os mercados se comportam, com um seletor de conjunto e dois modos de leitura.

1. **Visão geral** — Um gráfico de cada grande tema: ações, juros, câmbio e Bitcoin. (6 gráficos; 4 no Iniciante)
2. **EUA e Europa** — Índices de ações dos Estados Unidos e da Europa, cada um na sua moeda. (6 gráficos; 4 no Iniciante)
3. **Brasil, Portugal e Ásia** — Índices de ações do Brasil, de Portugal e de três mercados asiáticos, cada um na sua moeda. (6 gráficos; 4 no Iniciante)
4. **Juros (EUA)** — Rendimento dos títulos do Tesouro americano de 2 e de 10 anos e a diferença entre eles. (3 gráficos; 2 no Iniciante)
5. **Juros Brasil** — A taxa Selic, a inflação e o juro real brasileiro. (3 gráficos; 3 no Iniciante)
6. **Inflação** — Variação dos preços ao consumidor em 12 meses no Brasil, nos EUA, na zona do euro e em Portugal. (4 gráficos; 3 no Iniciante)
7. **Liquidez e moeda** — A chamada “impressão de moeda” em três camadas: balanço do banco central, base monetária e M2/M3. (6 gráficos; 4 no Iniciante)
8. **Risco e crédito** — Indicadores acompanhados juntos para descrever o apetite por risco: o VIX, a curva de juros americana, o dólar e o ouro. (5 gráficos; 4 no Iniciante)
9. **Forex** — Câmbio: quanto vale uma moeda em relação a outra. (6 gráficos; 4 no Iniciante)
10. **Commodities** — Matérias-primas negociadas no mundo todo: ouro, prata, petróleo e cobre. (4 gráficos; 4 no Iniciante)
11. **Bitcoin e ciclos** — O preço do Bitcoin em escala logarítmica, com as datas dos halvings marcadas. (5 gráficos; 3 no Iniciante)

- **Modo Iniciante** (padrão): até 4 gráficos por conjunto, cada um com "O que é", "Como ler" e "O que já se observou", e uma caixa "O que este conjunto não diz" antes dos gráficos.
- **Modo Avançado**: até 6 gráficos, seletor de janela (1, 5, 10 anos, tudo), escala linear ou logarítmica e médias móveis de 10 e 40 semanas nos gráficos de preço. As médias são descritas pelo cálculo e não são sinal de compra ou venda.

O modo e o conjunto ficam guardados no endereço da página (`?conjunto=...&modo=...`).

## De onde vêm os gráficos

**Gráficos próprios**, desenhados pela página com dados coletados: índices, juros, inflação, liquidez, risco, commodities e o gráfico do Bitcoin com os halvings. Motivo: os widgets gratuitos do TradingView recusam vários índices. Em teste de 16/11/2026, `SP:SPX` devolveu "Este símbolo está disponível somente no TradingView".

**Widgets gratuitos do TradingView**, só em forex e cripto. Cada cartão tem um botão para trocar pelo gráfico próprio. Os nove símbolos usados estão no bloco `simbolos_tv` de `conjuntos.json` (a página mostra só o par, sem o prefixo da plataforma). Os nove carregaram no widget Mini Symbol Overview em 16/11/2026, no navegador do dono. O widget Advanced Chart, usado no modo Avançado, ainda não foi testado. A atribuição do TradingView fica visível em cada widget e não deve ser removida.

## Séries e fontes

Coleta por `scripts/mercados/coletar_mercados.py`, a partir de `scripts/mercados/catalogo_series.json`. A coluna "Verificação" é a do catálogo.

| Id | Série | Fonte | Código | Periodicidade | Verificação |
|---|---|---|---|---|---|
| `idx_sp500` | S&P 500 | Yahoo Finance | `^GSPC` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'S&P 500', meta.shortName = 'S&P 500'; tipo INDEX; moeda USD; fuso America/New_York; 1404 barras desde 2000-01-01. Valores não comparados com a bolsa de origem. |
| `idx_nasdaq100` | Nasdaq 100 | Yahoo Finance | `^NDX` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'NASDAQ-100', meta.shortName = 'NASDAQ-100'; tipo INDEX; moeda USD; fuso America/New_York; 1404 barras desde 2000-01-01. Valores não comparados com a bolsa de origem. |
| `idx_dow` | Dow Jones Industrial Average | Yahoo Finance | `^DJI` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'Dow Jones Industrial Average', meta.shortName = 'Dow Jones Industrial Average'; tipo INDEX; moeda USD; fuso America/New_York; 1404 barras desde 2000-01-01. Valores não comparados com a bolsa de origem. |
| `idx_dax` | DAX (Alemanha) | Yahoo Finance | `^GDAXI` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'DAX P', meta.shortName = 'DAX'; tipo INDEX; moeda EUR; fuso Europe/Berlin; 1404 barras desde 1999-12-31. Valores não comparados com a bolsa de origem. |
| `idx_eurostoxx50` | Euro Stoxx 50 | Yahoo Finance | `^STOXX50E` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'EURO STOXX 50 I', meta.shortName = 'EURO STOXX 50'; tipo INDEX; moeda não informada; fuso Europe/Zurich; 1027 barras desde 2007-03-25. Valores não comparados com a bolsa de origem. |
| `idx_ftse100` | FTSE 100 (Reino Unido) | Yahoo Finance | `^FTSE` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'FTSE 100', meta.shortName = 'FTSE 100'; tipo INDEX; moeda GBP; fuso Europe/London; 1404 barras desde 2000-01-01. Valores não comparados com a bolsa de origem. |
| `idx_ibovespa` | Ibovespa (Brasil) | Yahoo Finance | `^BVSP` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'IBOVESPA', meta.shortName = 'IBOVESPA'; tipo INDEX; moeda BRL; fuso America/Sao_Paulo; 1404 barras desde 2000-01-01. Valores não comparados com a bolsa de origem. |
| `idx_psi` | PSI (Portugal) | Yahoo Finance | `PSI20.LS` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'PSI', meta.shortName = 'PSI'; tipo INDEX; moeda EUR; fuso Europe/Lisbon; 709 barras desde 2013-04-28. Valores não comparados com a bolsa de origem. |
| `idx_nikkei` | Nikkei 225 (Japão) | Yahoo Finance | `^N225` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'Nikkei 225', meta.shortName = 'Nikkei 225'; tipo INDEX; moeda JPY; fuso Asia/Tokyo; 1404 barras desde 1999-12-31. Valores não comparados com a bolsa de origem. |
| `idx_hangseng` | Hang Seng (Hong Kong) | Yahoo Finance | `^HSI` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'HANG SENG INDEX', meta.shortName = 'HANG SENG INDEX'; tipo INDEX; moeda HKD; fuso Asia/Hong_Kong; 1404 barras desde 1999-12-31. Valores não comparados com a bolsa de origem. |
| `idx_xangai` | Xangai Composto (China) | Yahoo Finance | `000001.SS` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'SSE Composite Index', meta.shortName = 'SSE Composite Index'; tipo INDEX; moeda CNY; fuso Asia/Shanghai; 1404 barras desde 1999-12-31. Valores não comparados com a bolsa de origem. |
| `idx_emergentes` | Mercados emergentes (ETF EEM, não é um índice) | Yahoo Finance | `EEM` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'iShares MSCI Emerging Markets ETF', meta.shortName = 'iShares MSCI Emerging Index Fun'; tipo ETF; moeda USD; fuso America/New_York; 1232 barras desde 2003-04-14. Valores não comparados com a bolsa de origem. |
| `risco_vix` | VIX (volatilidade implícita do S&P 500) | Yahoo Finance | `^VIX` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'CBOE Volatility Index', meta.shortName = 'CBOE Volatility Index'; tipo INDEX; moeda USD; fuso America/Chicago; 1404 barras desde 2000-01-01. Valores não comparados com a bolsa de origem. |
| `fx_dxy` | Índice do dólar (DXY) | Yahoo Finance | `DX-Y.NYB` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'US Dollar Index', meta.shortName = 'ICE US Dollar Index - Index - C'; tipo INDEX; moeda USD; fuso America/New_York; 1404 barras desde 2000-01-01. Valores não comparados com a bolsa de origem. |
| `fx_eurusd` | Euro em dólares (EUR/USD) | Yahoo Finance | `EURUSD=X` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'EUR/USD', meta.shortName = 'EUR/USD'; tipo CURRENCY; moeda USD; fuso Europe/London; 1200 barras desde 2003-12-01. Valores não comparados com a bolsa de origem. |
| `fx_usdbrl` | Dólar em reais (USD/BRL) | Yahoo Finance | `BRL=X` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'USD/BRL', meta.shortName = 'USD/BRL'; tipo CURRENCY; moeda BRL; fuso Europe/London; 1200 barras desde 2003-12-01. Valores não comparados com a bolsa de origem. |
| `fx_eurbrl` | Euro em reais (EUR/BRL) | Yahoo Finance | `EURBRL=X` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'EUR/BRL', meta.shortName = 'EUR/BRL'; tipo CURRENCY; moeda BRL; fuso Europe/London; 1200 barras desde 2003-12-01. Valores não comparados com a bolsa de origem. |
| `fx_usdjpy` | Dólar em ienes (USD/JPY) | Yahoo Finance | `JPY=X` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'USD/JPY', meta.shortName = 'USD/JPY'; tipo CURRENCY; moeda JPY; fuso Europe/London; 1404 barras desde 2000-01-01. Valores não comparados com a bolsa de origem. |
| `fx_gbpusd` | Libra em dólares (GBP/USD) | Yahoo Finance | `GBPUSD=X` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'GBP/USD', meta.shortName = 'GBP/USD'; tipo CURRENCY; moeda USD; fuso Europe/London; 1200 barras desde 2003-12-01. Valores não comparados com a bolsa de origem. |
| `com_ouro` | Ouro (contrato futuro) | Yahoo Finance | `GC=F` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.shortName = 'Gold Dec 26' (não traz longName); tipo FUTURE; moeda USD; fuso America/New_York; 1370 barras desde 2000-08-28. Valores não comparados com a bolsa de origem. |
| `com_prata` | Prata (contrato futuro) | Yahoo Finance | `SI=F` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.shortName = 'Silver Dec 26' (não traz longName); tipo FUTURE; moeda USD; fuso America/New_York; 1370 barras desde 2000-08-28. Valores não comparados com a bolsa de origem. |
| `com_wti` | Petróleo WTI (contrato futuro) | Yahoo Finance | `CL=F` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.shortName = 'Crude Oil Dec 26' (não traz longName); tipo FUTURE; moeda USD; fuso America/New_York; 1371 barras desde 2000-08-21. Valores não comparados com a bolsa de origem. |
| `com_cobre` | Cobre (contrato futuro) | Yahoo Finance | `HG=F` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.shortName = 'Copper Dec 26' (não traz longName); tipo FUTURE; moeda USD; fuso America/New_York; 1370 barras desde 2000-08-28. Valores não comparados com a bolsa de origem. |
| `btc_usd` | Bitcoin em dólares | Yahoo Finance | `BTC-USD` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'Bitcoin USD', meta.shortName = 'Bitcoin USD'; tipo CRYPTOCURRENCY; moeda USD; fuso UTC; 637 barras desde 2014-09-15. Valores não comparados com a bolsa de origem. |
| `eth_btc` | Ether em bitcoins (ETH/BTC) | Yahoo Finance | `ETH-BTC` | semanal | Resposta da API do Yahoo conferida em 16/11/2026 (navegador do dono): HTTP 200, granularidade 1wk com period1/period2; meta.longName = 'Ethereum BTC', meta.shortName = 'Ethereum BTC'; tipo CRYPTOCURRENCY; moeda BTC; fuso UTC; 473 barras desde 2017-11-06. Valores não comparados com a bolsa de origem. |
| `juros_eua_2a` | Juro do Tesouro dos EUA de 2 anos | FRED (Fed de St. Louis) | `DGS2` | semanal | Página da série no FRED conferida em 16/11/2026: 'Market Yield on U.S. Treasury Securities at 2-Year Constant Maturity', diária, sem ajuste sazonal; último 12/11/2026 = 4,86. |
| `juros_eua_10a` | Juro do Tesouro dos EUA de 10 anos | FRED (Fed de St. Louis) | `DGS10` | semanal | Página da série no FRED conferida em 16/11/2026: 'Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity', diária, sem ajuste sazonal; último 12/11/2026 = 5,10. CSV conferido (começa em 1962; ausentes vêm vazios). |
| `juros_eua_10a2a` | Diferença entre os juros de 10 e de 2 anos (EUA) | FRED (Fed de St. Louis) | `T10Y2Y` | semanal | Página da série no FRED conferida em 16/11/2026: '10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity', diária, sem ajuste sazonal; último 13/11/2026 = 0,27. |
| `risco_hy` | Prêmio de risco de crédito de alto rendimento (EUA) | FRED (Fed de St. Louis) | `BAMLH0A0HYM2` | semanal | Página da série no FRED conferida em 16/11/2026: 'ICE BofA US High Yield Index Option-Adjusted Spread', diária; último 12/11/2026 = 3,20. O FRED limita o histórico a 3 anos desde abril de 2026 (CSV conferido: começa em 14/11/2023). |
| `cpi_eua` | Índice de preços ao consumidor dos EUA (CPI, nível do índice) | FRED (Fed de St. Louis) | `CPIAUCSL` | mensal | Chamada real registrada em docs/monitor-mercados/avaliacao-proposta.md (16/11/2026): 10/2026 = 337,476. Página da série não conferida nesta etapa. |
| `liq_eua_m2` | M2 dos EUA | FRED (Fed de St. Louis) | `M2SL` | mensal | Chamada real registrada em docs/monitor-mercados/avaliacao-proposta.md (16/11/2026): 09/2026 = 23.413,9. |
| `liq_fed_balanco` | Balanço do Fed (ativos totais) | FRED (Fed de St. Louis) | `WALCL` | semanal | CSV conferido em 16/11/2026: começa em 18/12/2002; último 11/11/2026 = 6.758.867. |
| `infl_br_12m` | IPCA acumulado em 12 meses (Brasil) | Banco Central do Brasil (SGS) | `13522` | mensal | Chamada real à API em 16/11/2026: série desde 12/1980; último ponto devolvido 09/2026 = 4,58 (a avaliação da proposta registra 10/2026 = 4,63). |
| `juros_br_selic` | Taxa Selic meta (Brasil) | Banco Central do Brasil (SGS) | `432` | semanal | Chamada real à API em 16/11/2026: 13,75; devolve datas futuras. Sem dataInicial/dataFinal, ou com janela acima de 10 anos, a API recusou a chamada; janelas de 5 anos, usadas na coleta, funcionaram (01/01/2020 a 31/12/2024 e 01/01/2025 a 16/11/2026). |
| `liq_br_base` | Base monetária restrita (Brasil) | Banco Central do Brasil (SGS) | `1788` | mensal | Chamada real à API em 16/11/2026: série desde 02/1946; último ponto 09/2026 = 434.922.566. |
| `liq_br_m2` | M2 (Brasil) | Banco Central do Brasil (SGS) | `27810` | mensal | Chamada real à API em 16/11/2026: começa em 08/2001 com valores nulos; último ponto 09/2026 = 7.870.395.191. |
| `infl_ea_12m` | Inflação em 12 meses na zona do euro (HICP) | Eurostat | `prc_hicp_minr?geo=EA&unit=RCH_A&coicop18=TOTAL` | mensal | Chamada real à API em 16/11/2026 com sinceTimePeriod (parâmetro aceito): geo=EA devolveu 322 meses, de 2000-01 a 2026-10 (4,0, estimativa). Endereço do navegador de dados (url_fonte) não conferido. |
| `infl_pt_12m` | Inflação em 12 meses em Portugal (HICP) | Eurostat | `prc_hicp_minr?geo=PT&unit=RCH_A&coicop18=TOTAL` | mensal | Chamada real à API em 16/11/2026 com sinceTimePeriod (parâmetro aceito): geo=PT devolveu 2025-06 a 2026-10 (3,9, estimativa); histórico desde 2000 não conferido para PT. Endereço do navegador de dados (url_fonte) não conferido. |
| `liq_ea_m3` | M3 da zona do euro | BCE (Data Portal) | `BSI.M.U2.Y.V.M30.X.1.U2.2300.Z01.E` | mensal | Verificado por chamada real à API em 16/11/2026 (navegador do dono, HTTP 200, format=csvdata): título 'Monetary aggregate M3, Stocks', EUR, UNIT_MULT 6, dessazonalizado; último 2026-08 = 17.647.597. Endereço da página no portal (url_fonte) não conferido. |
| `liq_bce_balanco` | Balanço do Eurosistema (ativos totais) | BCE (Data Portal) | `ILM.W.U2.C.T000000.Z5.Z01` | semanal | Verificado por chamada real à API em 16/11/2026 (navegador do dono, HTTP 200, format=csvdata): título 'Total assets/liabilities - Eurosystem', EUR, UNIT_MULT 6; período semanal no formato 2026-W45; último 2026-W45 = 5.913.173. Endereço da página no portal (url_fonte) não conferido. |
| `infl_eua_12m` | Inflação em 12 meses nos EUA (CPI) | cálculo do market-lab | `variacao_12m` | mensal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |
| `liq_eua_m2_var12m` | M2 dos EUA, variação em 12 meses | cálculo do market-lab | `variacao_12m` | mensal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |
| `liq_fed_balanco_var12m` | Balanço do Fed, variação em 12 meses | cálculo do market-lab | `variacao_12m` | semanal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |
| `juros_br_real` | Juro real ex-post aproximado (Brasil) | cálculo do market-lab | `juro_real` | mensal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |
| `liq_br_m2_var12m` | M2 do Brasil, variação em 12 meses | cálculo do market-lab | `variacao_12m` | mensal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |
| `liq_br_base_var12m` | Base monetária do Brasil, variação em 12 meses | cálculo do market-lab | `variacao_12m` | mensal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |
| `liq_ea_m3_var12m` | M3 da zona do euro, variação em 12 meses | cálculo do market-lab | `variacao_12m` | mensal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |
| `liq_bce_balanco_var12m` | Balanço do Eurosistema, variação em 12 meses | cálculo do market-lab | `variacao_12m` | semanal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |

Endereços das APIs: BCB `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json`; FRED `https://fred.stlouisfed.org/graph/fredgraph.csv?id={codigo}`; Eurostat `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_minr`; BCE `https://data-api.ecb.europa.eu/service/data/{chave}?format=csvdata`; Yahoo Finance, endpoint `chart`, como nos outros painéis.

Halvings do Bitcoin: datas em `scripts/mercados/eventos.json`, copiadas para `conjuntos.json`. Foram conferidas em 16/11/2026 pelo horário (UTC) dos blocos 210000, 420000, 630000 e 840000 no explorador [mempool.space](https://mempool.space/block/840000). Fontes secundárias divergem em um dia na data de 2012 (27 ou 28 de novembro); vale a do explorador, 28/11/2012 em UTC.

## Atualização e travas

- Workflow `.github/workflows/atualizar-mercados.yml`: dias úteis às 23h10 UTC, com repescagem às 11h10 UTC. O GitHub pode atrasar ou pular execuções.
- Ordem: testes (`tests/test_mercados.py`) → coleta → aceite (`scripts/mercados/aceite.py`) → publicação de `mercados.json` na branch `dados-mercados`. Se os testes ou o aceite reprovarem, nada é publicado e o arquivo anterior fica no ar.
- Se uma série falhar, o painel mantém o último bloco e marca **anterior**. Série nunca coletada aparece como **sem dados**.
- A página avisa em texto quando a coleta tem mais de 4 dias.
- Mudanças de código, de conjuntos ou de textos passam pelos juízes J1, J2 e J3 antes de ir para a `main` (pareceres em `docs/monitor-mercados/`).

## Limitações

- A coleta real ainda não rodou de ponta a ponta. O ambiente de desenvolvimento não acessa as fontes; os testes usam amostras fixas no formato real de cada API.
- Yahoo Finance e o endereço `fredgraph.csv` do FRED não são APIs oficiais documentadas e podem mudar ou bloquear sem aviso.
- Cotações semanais; o último ponto das séries do Yahoo é a semana em andamento. Não é tempo real.
- Histórico: PSI desde 2013, Euro Stoxx 50 desde 2007 e Bitcoin desde 2014 nessa fonte. O halving de 2012 fica fora da janela do gráfico.
- Inflação comparada pela taxa em 12 meses. O CPI dos EUA é dessazonalizado; IPCA e HICP não. Portugal e zona do euro usam o HICP do Eurostat (`prc_hicp_minr`).
- Portugal não tem agregado monetário próprio: está no euro. A contribuição nacional para o M3 e o IPC do INE ficaram fora desta versão [referência não verificada].
- Juro real do Brasil é uma aproximação: Selic meta menos IPCA em 12 meses do mesmo mês.
- Spread de crédito high yield (FRED `BAMLH0A0HYM2`) ficou fora: a [página da série](https://fred.stlouisfed.org/series/BAMLH0A0HYM2) informa restrição de reprodução pela ICE, e o histórico público tem 3 anos.
- CDI ficou fora: o código da série não foi confirmado na fonte.
- Índices em moeda local, alguns de retorno total (Ibovespa, DAX) e outros só de preço (S&P 500, PSI). As alturas das linhas não são comparáveis entre gráficos.

## Privacidade

Os widgets do TradingView carregam scripts de terceiros. Segundo a [documentação deles](https://www.tradingview.com/widget-docs/faq/general/), o serviço registra o endereço da página, o símbolo e o IP do visitante. Os gráficos próprios só leem o JSON deste repositório.

## Como acrescentar um conjunto

Edite `monitor/mercados/conjuntos.json` e acrescente um item em `conjuntos`: até 6 gráficos, até 4 com `iniciante: true`, até 4 séries da mesma unidade por gráfico. Séries de unidades diferentes nunca dividem o eixo: a página exibe só as da unidade da primeira e avisa em texto. A exceção é declarada com `unidade_eixo: "%"`, para sobrepor séries todas em porcentagem com rótulos diferentes (`% a.a.` e `% em 12 meses`). Campos opcionais: `preco: true` (liga escala linear/log e médias móveis de 10 e 40 semanas no Avançado), `marcadores: "halvings"`, `notas` no conjunto (frase com link) e, nos gráficos `tipo: "tv"`, `simbolo_tv`, `serie_alternativa` e `padrao`. Série nova entra antes em `scripts/mercados/catalogo_series.json`, com o código conferido na fonte. Os textos seguem as regras de redação de `docs/monitor-mercados/avaliacao-proposta.md`.

## Como testar localmente

```
python3 -m unittest tests/test_mercados.py
python3 scripts/mercados/gerar_amostra.py     # grava monitor/mercados/_amostra/mercados.json (sintético)
python3 -m http.server                        # abrir http://localhost:8000/monitor/mercados/
```

Em `localhost` a página lê a amostra sintética e mostra a faixa "DADOS SINTÉTICOS DE TESTE". A pasta `_amostra/` não vai para o repositório.

Material educativo. Não é recomendação de investimento. Rentabilidade passada não garante resultado futuro.

## Tema claro e escuro

A página segue a aparência do sistema (`prefers-color-scheme`): claro por padrão, escuro quando o sistema está escuro. Os gráficos próprios (canvas) leem as cores das variáveis CSS (`--s1` a `--s4`, `--grid`, `--eixo`) a cada desenho, e os widgets do TradingView usam o mesmo tema. Se o tema mudar com a página aberta, o painel é redesenhado. Os testes (`TemaTests`) impedem cores fixas no CSS e no JavaScript.
