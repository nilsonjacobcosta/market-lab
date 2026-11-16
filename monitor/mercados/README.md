# Mercados e ciclos

**Status:** em construção. Página, coleta, workflow e testes prontos. Faltam a primeira coleta real pelo GitHub Actions e o teste do widget Advanced Chart em navegador. Até a primeira coleta, a página não mostra números.

## O que mostra

Onze conjuntos de gráficos para acompanhar como os mercados se comportam, com um seletor de conjunto e dois modos de leitura.

1. **Visão geral** — Um gráfico de cada grande tema: ações, juros, câmbio e Bitcoin. (6 gráficos; 4 no Iniciante)
2. **EUA e Europa** — Índices de ações dos Estados Unidos e da Europa, cada um na sua moeda. (6 gráficos; 4 no Iniciante)
3. **Brasil, Portugal e Ásia** — Índices de ações do Brasil, de Portugal e de três mercados asiáticos, cada um na sua moeda. (6 gráficos; 4 no Iniciante)
4. **Juros (EUA)** — Rendimento dos títulos do Tesouro americano de 2 e de 10 anos e a diferença entre eles. (3 gráficos; 2 no Iniciante)
5. **Juros Brasil** — A taxa Selic, a inflação e o juro real brasileiro. (3 gráficos; 3 no Iniciante)
6. **Inflação** — Variação dos preços ao consumidor em 12 meses no Brasil, nos EUA, na zona do euro e em Portugal. (4 gráficos; 3 no Iniciante)
7. **Liquidez e moeda** — A chamada “impressão de moeda” em três camadas: balanço do banco central, base monetária e M2/M3. (6 gráficos; 4 no Iniciante)
8. **Risco e crédito** — Quatro termômetros de tensão nos mercados: o VIX, a curva de juros americana, o dólar e o ouro. (5 gráficos; 4 no Iniciante)
9. **Forex** — Câmbio: quanto vale uma moeda em relação a outra. (6 gráficos; 4 no Iniciante)
10. **Commodities** — Matérias-primas negociadas no mundo todo: ouro, prata, petróleo e cobre. (4 gráficos; 4 no Iniciante)
11. **Bitcoin e ciclos** — O preço do Bitcoin em escala logarítmica, com as datas dos halvings marcadas. (5 gráficos; 3 no Iniciante)

- **Modo Iniciante** (padrão): até 4 gráficos por conjunto, cada um com "O que é", "Como ler" e "O que já se observou", e uma caixa "O que este conjunto não diz" antes dos gráficos.
- **Modo Avançado**: até 6 gráficos, seletor de janela (1, 5, 10 anos, tudo), escala linear ou logarítmica e médias móveis de 10 e 40 semanas nos gráficos de preço. As médias são descritas pelo cálculo e não são sinal de compra ou venda.

O modo e o conjunto ficam guardados no endereço da página (`?conjunto=...&modo=...`).

## De onde vêm os gráficos

**Gráficos próprios**, desenhados pela página com dados coletados: índices, juros, inflação, liquidez, risco, commodities e o gráfico do Bitcoin com os halvings. Motivo: os widgets gratuitos do TradingView recusam vários índices. Em teste de 16/11/2026, `SP:SPX` devolveu "Este símbolo está disponível somente no TradingView".

**Widgets gratuitos do TradingView**, só em forex e cripto. Cada cartão tem um botão para trocar pelo gráfico próprio. Símbolos usados: `BINANCE:ETHBTC`, `BITSTAMP:BTCUSD`, `CRYPTOCAP:BTC.D`, `CRYPTOCAP:TOTAL`, `FX:EURUSD`, `FX:GBPUSD`, `FX:USDJPY`, `FX_IDC:EURBRL`, `FX_IDC:USDBRL`. Os nove carregaram no widget Mini Symbol Overview em 16/11/2026, no navegador do dono. O widget Advanced Chart, usado no modo Avançado, ainda não foi testado. A atribuição do TradingView fica visível em cada widget e não deve ser removida.

## Séries e fontes

Coleta por `scripts/mercados/coletar_mercados.py`, a partir de `scripts/mercados/catalogo_series.json`. A coluna "Verificação" é a do catálogo.

| Id | Série | Fonte | Código | Periodicidade | Verificação |
|---|---|---|---|---|---|
| `idx_sp500` | S&P 500 | Yahoo Finance | `^GSPC` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `idx_nasdaq100` | Nasdaq 100 | Yahoo Finance | `^NDX` | semanal | Verificado na resposta da API do Yahoo em 16/11/2026 (navegador do dono): meta.longName = 'NASDAQ-100', tipo INDEX. |
| `idx_dow` | Dow Jones Industrial Average | Yahoo Finance | `^DJI` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `idx_dax` | DAX (Alemanha) | Yahoo Finance | `^GDAXI` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `idx_eurostoxx50` | Euro Stoxx 50 | Yahoo Finance | `^STOXX50E` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). Resposta da API em 16/11/2026 (navegador do dono): 1027 pontos semanais desde 2007-03-25. |
| `idx_ftse100` | FTSE 100 (Reino Unido) | Yahoo Finance | `^FTSE` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `idx_ibovespa` | Ibovespa (Brasil) | Yahoo Finance | `^BVSP` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `idx_psi` | PSI (Portugal) | Yahoo Finance | `PSI20.LS` | semanal | Verificado na resposta da API do Yahoo em 16/11/2026 (navegador do dono): meta.longName = 'PSI', tipo INDEX, moeda EUR; histórico semanal desde 2013-04-28. |
| `idx_nikkei` | Nikkei 225 (Japão) | Yahoo Finance | `^N225` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `idx_hangseng` | Hang Seng (Hong Kong) | Yahoo Finance | `^HSI` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `idx_xangai` | Xangai Composto (China) | Yahoo Finance | `000001.SS` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `idx_emergentes` | Mercados emergentes (ETF EEM, não é um índice) | Yahoo Finance | `EEM` | semanal | Verificado na resposta da API do Yahoo em 16/11/2026 (navegador do dono): meta.longName = 'iShares MSCI Emerging Markets ETF', tipo ETF. |
| `risco_vix` | VIX (volatilidade implícita do S&P 500) | Yahoo Finance | `^VIX` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `fx_dxy` | Índice do dólar (DXY) | Yahoo Finance | `DX-Y.NYB` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `fx_eurusd` | Euro em dólares (EUR/USD) | Yahoo Finance | `EURUSD=X` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `fx_usdbrl` | Dólar em reais (USD/BRL) | Yahoo Finance | `BRL=X` | semanal | Respondeu na API do Yahoo em 16/11/2026 (navegador do dono): 1199 pontos semanais desde 2003-12-01, com fechamentos nulos descartados. Nome do instrumento na resposta não registrado; o painel de ativos usa USDBRL=X. |
| `fx_eurbrl` | Euro em reais (EUR/BRL) | Yahoo Finance | `EURBRL=X` | semanal | Verificado na resposta da API do Yahoo em 16/11/2026 (navegador do dono): meta.longName = 'EUR/BRL', tipo CURRENCY. |
| `fx_usdjpy` | Dólar em ienes (USD/JPY) | Yahoo Finance | `JPY=X` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `fx_gbpusd` | Libra em dólares (GBP/USD) | Yahoo Finance | `GBPUSD=X` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `com_ouro` | Ouro (contrato futuro) | Yahoo Finance | `GC=F` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `com_prata` | Prata (contrato futuro) | Yahoo Finance | `SI=F` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `com_wti` | Petróleo WTI (contrato futuro) | Yahoo Finance | `CL=F` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `com_cobre` | Cobre (contrato futuro) | Yahoo Finance | `HG=F` | semanal | Ticker em uso no painel de ativos (scripts/ativos/catalogo.py). |
| `btc_usd` | Bitcoin em dólares | Yahoo Finance | `BTC-USD` | semanal | Verificado na resposta da API do Yahoo em 16/11/2026 (navegador do dono): meta.longName = 'Bitcoin USD'; 636 pontos semanais desde 2014-09-15. |
| `eth_btc` | Ether em bitcoins (ETH/BTC) | Yahoo Finance | `ETH-BTC` | semanal | Verificado na resposta da API do Yahoo em 16/11/2026 (navegador do dono): meta.longName = 'Ethereum BTC', tipo CRYPTOCURRENCY; histórico desde 2017-11-06. |
| `juros_eua_2a` | Juro do Tesouro dos EUA de 2 anos | FRED (Fed de St. Louis) | `DGS2` | semanal | Página da série no FRED conferida em 16/11/2026: 'Market Yield on U.S. Treasury Securities at 2-Year Constant Maturity', diária, sem ajuste sazonal; último 12/11/2026 = 4,86. |
| `juros_eua_10a` | Juro do Tesouro dos EUA de 10 anos | FRED (Fed de St. Louis) | `DGS10` | semanal | Página da série no FRED conferida em 16/11/2026: 'Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity', diária, sem ajuste sazonal; último 12/11/2026 = 5,10. CSV conferido (começa em 1962; ausentes vêm vazios). |
| `juros_eua_10a2a` | Diferença entre os juros de 10 e de 2 anos (EUA) | FRED (Fed de St. Louis) | `T10Y2Y` | semanal | Página da série no FRED conferida em 16/11/2026: '10-Year Treasury Constant Maturity Minus 2-Year Treasury Constant Maturity', diária, sem ajuste sazonal; último 13/11/2026 = 0,27. |
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
| `infl_eua_12m` | Inflação em 12 meses nos EUA (CPI) | cálculo do market-lab | `variacao_12m(cpi_eua)` | mensal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |
| `liq_eua_m2_var12m` | M2 dos EUA, variação em 12 meses | cálculo do market-lab | `variacao_12m(liq_eua_m2)` | mensal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |
| `liq_fed_balanco_var12m` | Balanço do Fed, variação em 12 meses | cálculo do market-lab | `variacao_12m(liq_fed_balanco)` | semanal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |
| `juros_br_real` | Juro real ex-post aproximado (Brasil) | cálculo do market-lab | `juro_real(juros_br_selic,infl_br_12m)` | mensal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |
| `liq_br_m2_var12m` | M2 do Brasil, variação em 12 meses | cálculo do market-lab | `variacao_12m(liq_br_m2)` | mensal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |
| `liq_br_base_var12m` | Base monetária do Brasil, variação em 12 meses | cálculo do market-lab | `variacao_12m(liq_br_base)` | mensal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |
| `liq_ea_m3_var12m` | M3 da zona do euro, variação em 12 meses | cálculo do market-lab | `variacao_12m(liq_ea_m3)` | mensal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |
| `liq_bce_balanco_var12m` | Balanço do Eurosistema, variação em 12 meses | cálculo do market-lab | `variacao_12m(liq_bce_balanco)` | semanal | Cálculo do market-lab coberto por tests/test_mercados.py; a verificação das séries-base está nas entradas delas. |

Endereços das APIs: BCB `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json`; FRED `https://fred.stlouisfed.org/graph/fredgraph.csv?id={codigo}`; Eurostat `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_minr`; BCE `https://data-api.ecb.europa.eu/service/data/{chave}?format=csvdata`; Yahoo Finance, endpoint `chart`, como nos outros painéis.

Halvings do Bitcoin: datas em `scripts/mercados/eventos.json`, com fonte. A data de 2012 diverge em um dia entre as fontes consultadas (27 ou 28 de novembro) e nenhuma foi conferida em explorador de blocos.

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

Edite `monitor/mercados/conjuntos.json` e acrescente um item em `conjuntos`: até 6 gráficos, até 4 com `iniciante: true`, até 4 séries da mesma unidade por gráfico. Série nova entra antes em `scripts/mercados/catalogo_series.json`, com o código conferido na fonte. Os textos seguem as regras de redação de `docs/monitor-mercados/avaliacao-proposta.md`.

## Como testar localmente

```
python3 -m unittest tests/test_mercados.py
python3 scripts/mercados/gerar_amostra.py     # grava monitor/mercados/_amostra/mercados.json (sintético)
python3 -m http.server                        # abrir http://localhost:8000/monitor/mercados/
```

Em `localhost` a página lê a amostra sintética e mostra a faixa "DADOS SINTÉTICOS DE TESTE". A pasta `_amostra/` não vai para o repositório.

Material educativo. Não é recomendação de investimento. Rentabilidade passada não garante resultado futuro.
