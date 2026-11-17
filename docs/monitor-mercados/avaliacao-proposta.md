# Mercados e ciclos — avaliação da proposta (seção 0)

Data: 16/11/2026. Etapa anterior à construção. Nenhum código do painel foi escrito ainda.

Método: quatro especialistas (Mercados, Macro e dados, Didática, Engenharia) avaliaram a proposta de forma independente, cada um em um agente separado, sem ver o parecer dos outros. A consolidação abaixo é do coordenador.

Limite desta etapa: o ambiente de nuvem não abre tradingview.com nem o portal de dados do BCE. Por isso nenhum símbolo foi testado em um embed real, e as duas séries do BCE têm a chave conferida na página do portal, mas a chamada de API não foi testada.

## 1. Achados que mudam a proposta

1. **Símbolos de índices podem não abrir nos widgets gratuitos.** A documentação do TradingView informa que alguns símbolos só aparecem no site deles, e ter plano pago não muda isso ([FAQ de dados](https://id.tradingview.com/widget-docs/faq/data/)). Os exemplos oficiais usam CFDs e o prefixo `INDEX:`, e não `SP:`, `DJ:` ou `TVC:` ([demo de índices](https://de.tradingview.com/widget-docs/widgets/watchlists/market-overview/demos/indices)). Nenhum dos índices propostos foi confirmado em embed. Ibovespa, PSI e Xangai não têm substituto conferido.
2. **O símbolo do PSI estava errado.** O correto é `EURONEXT:PSI20` ([página do símbolo](https://in.tradingview.com/symbols/EURONEXT-PSI20)); o embed não foi verificado.
3. **Marcar halvings dentro do widget gratuito não deve ser possível.** A documentação diz que os widgets só mostram dados do TradingView e não aceitam scripts ([FAQ geral](https://id.tradingview.com/widget-docs/faq/general/)). Não há parâmetro de desenho documentado. Isso é ausência na documentação, não proibição expressa.
4. **O conjunto de dados do Eurostat sugerido está congelado.** `prc_hicp_manr` parou em 12/2025. O vigente é `prc_hicp_minr`, com dimensão `coicop18=TOTAL` (conferido por chamada real: zona do euro 09/2026 = 3,8%; Portugal = 3,6%).
5. **"IPC de Portugal" ao lado de "HICP da zona do euro" não é comparável.** A comparação correta usa o HICP para os dois.
6. **Portugal não tem agregado monetário próprio.** Está no euro; existe só a contribuição nacional para o M3, e essa série não foi localizada no BPstat.
7. **A Selic (SGS 432) traz datas futuras** e o M2 (SGS 27810) vem fora de ordem. A coleta precisa filtrar e ordenar, senão a "data do último dado" sai errada.
8. **Juízes não rodam a cada atualização diária.** São sessões de IA e não executam dentro do GitHub Actions sem chave paga, e o projeto proíbe criar tokens.
9. **O conjunto 2 lista 11 símbolos**, acima do limite de 6. Os conjuntos 1 e 3 não dizem quais 4 aparecem no modo Iniciante.

## 2. Melhorias aceitas

| # | Melhoria | Origem |
|---|---|---|
| A1 | Testar cada símbolo em um embed real, no navegador do dono, antes de fechar a lista. O que não abrir vira gráfico próprio ou substituto, conforme a decisão D1. | Mercados, Engenharia |
| A2 | Bitcoin em gráfico próprio, com escala logarítmica e linhas nos halvings, e o texto "4 ocorrências não são regra". As datas dos halvings serão conferidas em fonte antes de publicar. | Mercados, Engenharia |
| A3 | Inflação comparada pela taxa em 12 meses. HICP (`prc_hicp_minr`) para zona do euro e Portugal, IPCA 12 meses (SGS 13522) para o Brasil, CPI (FRED `CPIAUCSL`) para os EUA. Nota de que o CPI é dessazonalizado e os outros não. | Macro |
| A4 | Liquidez em três camadas explicadas: balanço do banco central, base monetária e M2/M3. Cada série em moeda local e em variação anual, nunca somadas nem no mesmo eixo nominal. Portugal aparece dentro do euro. | Macro |
| A5 | Juros passam para dados oficiais (2 anos, 10 anos e a diferença 10a–2a), em vez de depender de símbolos `TVC:` não confirmados. Códigos a verificar na construção. | Mercados |
| A6 | Dividir o conjunto 2 em "EUA e Europa" e "Brasil, Portugal e Ásia", e fixar os 4 gráficos do Iniciante em cada conjunto. | Mercados |
| A7 | Cartão com "o que é", "como ler", "o que já se observou" (no lugar de "o que costuma indicar") e "o que este gráfico não diz", obrigatório em todos. | Didática |
| A8 | Dez regras de redação: verbos no passado com período datado; lista de palavras proibidas ("vai", "deve", "sinal", "oportunidade", "barato", "alvo"); todo padrão histórico com número de ocorrências e contraexemplo; nunca causa única; indicadores descritos pelo cálculo, não pelo uso. | Didática |
| A9 | Conjuntos em botões ou abas no lugar do select (select só no celular), estado guardado na URL, e ordem com juros, inflação e liquidez antes do Bitcoin. | Didática |
| A10 | Glossário com botão "?" acessível por toque e teclado, como no Monitor BESST, e não só tooltip. Título em cada iframe e resumo em texto ao lado. | Didática |
| A11 | Widgets montados só para o conjunto selecionado e removidos na troca. Iniciante com widget leve; gráfico avançado só no modo Avançado. Cartão com link quando o widget não carregar. | Engenharia |
| A12 | Arquitetura da coleta: `scripts/mercados/` com catálogo de séries, coleta e aceite; branch `dados-macro` criada na primeira execução (padrão do `atualizar-tendencias.yml`); falha por série mantém o bloco anterior com "anterior". | Engenharia |
| A13 | Trava diária por testes automatizados mais aceite por script. Juízes J1, J2 e J3 atuam em mudanças de código, catálogo ou texto. | Engenharia |
| A14 | Coleta uma vez por dia útil mais uma repescagem. As séries são semanais ou mensais; 30 minutos seria desperdício. | Engenharia |
| A15 | README avisa que os widgets carregam scripts de terceiros, que registram endereço da página, símbolo e IP do visitante. | Engenharia |
| A16 | Fora da primeira versão: IPC nacional do INE, contribuição de Portugal ao M3 e "% do PIB". Ficam marcados como [referência não verificada] ou pendência. | Macro |

## 3. Melhorias rejeitadas ou adiadas

| Sugestão | Decisão | Motivo |
|---|---|---|
| Trocar "Avançado" por "Completo" | Adiada | O dono pediu "avançados". Os outros painéis usam "Completo"; a troca é de uma palavra e fica a critério dele. |
| Alternância de texto Brasil/Portugal | Rejeitada na v1 | Dobra os textos a manter. Termos de Portugal entram no glossário. |
| Índia, Russell 2000, Brent, minério, USDCNY | Adiada | Aumenta os conjuntos antes de saber quais símbolos abrem. EURBRL entra no conjunto de forex por ser o par de quem vive entre Brasil e Portugal. |
| Converter índices para uma moeda comum | Rejeitada | Mistura câmbio com bolsa. Cada índice fica em moeda local, com nota. |

## 4. Séries oficiais verificadas

Status "verificado" significa chamada real à API em 16/11/2026, com o último valor devolvido.

| Indicador | Fonte e código | Periodicidade | Status |
|---|---|---|---|
| IPCA mensal | BCB SGS 433 | mensal, % | Verificado: 10/2026 = 0,14 |
| IPCA 12 meses | BCB SGS 13522 | mensal, % | Verificado: 10/2026 = 4,63 |
| Selic meta | BCB SGS 432 | diária, % a.a. | Verificado: 13,75; contém datas futuras |
| Base monetária restrita | BCB SGS 1788 | mensal, R$ mil | Verificado; último ponto 07/2026 |
| M2 | BCB SGS 27810 | mensal, R$ mil | Verificado; último ponto 09/2026 |
| CPI EUA | FRED CPIAUCSL | mensal, índice | Verificado: 10/2026 = 337,476 |
| M2 EUA | FRED M2SL | mensal, US$ bi | Verificado: 09/2026 = 23.413,9 |
| Balanço do Fed | FRED WALCL | semanal, US$ mi | Verificado: 11/11/2026 = 6.758.867 |
| HICP zona do euro e Portugal | Eurostat `prc_hicp_minr`, `unit=RCH_A`, `coicop18=TOTAL` | mensal, % | Verificado: 09/2026 = 3,8 e 3,6 |
| M3 zona do euro | BCE `BSI.M.U2.Y.V.M30.X.1.U2.2300.Z01.E` | mensal, € mi | Chave vista no portal; API não testada |
| Ativos do Eurosistema | BCE `ILM.W.U2.C.T000000.Z5.Z01` | semanal, € mi | Chave vista no portal; API não testada |
| Contribuição de Portugal ao M3 | BPstat | mensal | [referência não verificada] |
| IPC Portugal | INE | mensal | [referência não verificada] |

Endereços: BCB `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json`; FRED `https://fred.stlouisfed.org/graph/fredgraph.csv?id={codigo}` (endereço de gráfico, não a API documentada; pode mudar sem aviso); Eurostat `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_minr`.

## 5. Símbolos do TradingView

Nenhum foi testado em embed. "Em demo oficial" significa que o símbolo consta no código de exemplo do TradingView.

| Proposto | Situação | Substituto candidato |
|---|---|---|
| BITSTAMP:BTCUSD, CRYPTOCAP:TOTAL, BINANCE:ETHBTC | Em demo oficial | Manter |
| CRYPTOCAP:BTC.D | Não verificado | Testar |
| FX:EURUSD, FX:GBPUSD, FX:USDJPY | Não verificado | Testar |
| FX:USDBRL | Não verificado; o feed pode não ter real | Testar |
| SP:SPX | Não verificado | FOREXCOM:SPXUSD ou FRED:SP500 (demos oficiais) |
| NASDAQ:NDX | Não verificado | FOREXCOM:NSXUSD ou FRED:NDQ100 |
| DJ:DJI | Não verificado | FOREXCOM:DJI |
| TVC:SX5E, XETR:DAX, TVC:NI225, TVC:HSI, TVC:DXY | Não verificado | INDEX:SX5E, INDEX:DEU40, INDEX:NKY, INDEX:HSI, INDEX:DXY |
| TVC:UKX | Não verificado | FOREXCOM:UKXGBP |
| BMFBOVESPA:IBOV | Não verificado | Sem substituto conferido |
| EURONEXT:PSI | Símbolo errado; correto EURONEXT:PSI20 | Sem substituto conferido |
| SSE:000001 | Não verificado | Sem substituto conferido |
| TVC:GOLD, SILVER, USOIL, COPPER | Não verificado | A testar |
| TVC:US02Y, US10Y, DE10Y | Não verificado | Séries oficiais (A5) |

## 6. Decisões que dependem do dono

- **D1.** Índices que não abrirem no embed: gráfico próprio com dados coletados, ou substituto do TradingView que exibe o nome de uma corretora (FOREXCOM, OANDA)?
- **D2.** Nome do conjunto 8: "Liquidez e moeda" (com "impressão de moeda" explicada no subtítulo) ou manter "Impressão de moeda"?
- **D3.** Acrescentar o conjunto "Risco e crédito" (VIX, spread de crédito) e "Juros Brasil" (Selic, juro longo), ou manter os conjuntos atuais?
- **D4.** Acesso de escrita ao repositório nesta sessão, necessário para gravar este arquivo e o painel no GitHub.
