# Monitor em tempo real — Fase 0 (proposta e testes)

Data: 19/11/2026. Etapa anterior à construção. Nenhuma página nova foi criada ainda.

Decisões do dono: o monitor em tempo real é uma **página nova dentro do market-lab** (pasta `monitor/tempo-real/`), segue a estrutura dos painéis existentes (conjuntos de cartões, modo Iniciante e Avançado, glossário, "o que este conjunto não diz") e é **completo e para iniciantes**.

## 1. Origem da ideia

Um print de tela de um terminal de mercado (fonte e data não identificadas) mostrou blocos de dólar, commodities, futuros, juros dos EUA, curva DI do Brasil e notícias. Pelo teste desta fase, os valores do print **não são atuais**: em 19/11/2026 o S&P 500 (CFD) estava perto de 7.230 e o DI1F2029 em 15,3%, e no print o S&P 500 futuro estava em 6.740 e o DI1F29 em 13,18%. Além disso, um DI1F26 vence em janeiro de 2026. O print serve só como referência de layout. Nenhum valor dele entra no painel.

## 2. Teste de símbolos em widgets reais

Feito em 19/11/2026, no Chrome do dono, com o widget Market Quotes do TradingView (e, antes, o Ticker Tape). Só mostra se o símbolo abre; não compara valores com a bolsa.

| Grupo | Símbolos que abriram | Símbolos que não abriram |
|---|---|---|
| Moedas e cripto (tempo real) | `FX:EURUSD`, `FX:USDJPY`, `FX:GBPUSD`, `FX_IDC:USDBRL`, `BITSTAMP:BTCUSD`, `BITSTAMP:ETHUSD` | `TVC:DXY` (linha vazia) |
| Índices de ações (CFD de corretora) | `FOREXCOM:SPXUSD`, `FOREXCOM:NSXUSD`, `FOREXCOM:DJI` | `CME_MINI:ES1!`, `CME_MINI:NQ1!`, `CBOT_MINI:YM1!`, `CME_MINI:RTY1!` (erro) |
| Commodities | `TVC:UKOIL`, `TVC:USOIL`, `TVC:GOLD`, `TVC:SILVER`, `CAPITALCOM:COPPER`, `CAPITALCOM:IRON` | `COMEX:HG1!`, `ICEEUR:BRN1!` (erro) |
| Juros dos EUA | `FRED:DGS10` e `FRED:DGS2` (valor diário, sem variação percentual) | `TVC:US02Y`, `TVC:US05Y`, `TVC:US10Y`, `TVC:US30Y`, `ECONOMICS:USINTR` (vazios ou erro) |
| DI Brasil (marcados "D", atrasados) | `BMFBOVESPA:DI1F2027`, `DI1F2028`, `DI1F2029`, `DI1F2031`, `DI1F2033`, `DI1F2035`, `DI1F2036` | `BMFBOVESPA:DI1!` (contínuo, erro) |
| Bolsa brasileira (marcados "D", atrasados) | `BMFBOVESPA:IBOV`, `WIN1!`, `WDO1!`, `PETR4`, `VALE3`, `DOL1!`, `IND1!` | — |

Ressalvas do teste: o widget Market Quotes não foi usado na versão final da página; falta testar Symbol Overview, Mini Chart e Advanced Chart com cada símbolo aprovado; os nomes de contratos DI mudam a cada ano e precisam de rotina de atualização; `TVC:GOLD` e `TVC:UKOIL` são cotações de referência do TradingView e não o contrato de uma bolsa.

## 3. Regras e limites dos dados

- Segundo o FAQ de dados do TradingView, forex e cripto são em tempo real, ações são atrasadas e o FAQ não informa o status de futuros e índices. Widgets só exibem dados do TradingView e não permitem exportar dados. Símbolos marcados como "somente no TradingView" não aparecem em widgets.
- Segundo o FAQ geral, widgets não definem cookies; o TradingView registra o endereço da página, o tipo de widget, o símbolo e o IP.
- Segundo os Termos de Uso (seção 3), os dados de mercado são licenciados "para uso de exibição" e o uso comercial não é permitido, salvo acordo à parte. Pela seção 4, a atribuição ao TradingView deve ficar visível. **Pendência:** os Termos não tratam de widgets embutidos de forma específica; o uso do market-lab é educativo e sem fins lucrativos, mas isso precisa de confirmação com o TradingView se a página passar a ter qualquer forma de receita ou patrocínio.
- Cotações em tempo real de bolsas (CME, B3, ICE) e manchetes da Reuters/Bloomberg são dados licenciados: o painel **não coleta, não guarda e não republica**. Só exibe widgets de terceiros, com a atribuição visível. Como a `risco_hy` (ICE), qualquer série licenciada fica fora.
- A coleta atual (GitHub Actions) não serve para tempo real e continua sendo usada só para séries próprias.

## 4. Proposta de conjuntos (modo Iniciante: até 4 cartões por conjunto)

Cada cartão tem "O que é", "Como ler" e "O que já se observou" (agora, com variação do dia, só descrição do que o widget mostra), termos do glossário e a caixa "O que este conjunto não diz". Sem rótulo de compra ou venda; os widgets de "análise técnica" do TradingView, que exibem rótulos de compra e venda, ficam **fora**.

1. **Abertura do dia** — Ticker Tape curto: S&P 500, Nasdaq 100, Dow, dólar/real, euro/dólar, Bitcoin, ouro, petróleo.
2. **Câmbio** — pares de moedas e DXY (DXY não abriu; avaliar substituto ou gráfico próprio).
3. **Commodities** — ouro, prata, petróleo, cobre, minério de ferro.
4. **Ações dos EUA (CFD) e Brasil** — S&P 500, Nasdaq 100, Dow; Ibovespa e minicontratos (atrasados, marcados).
5. **Juros do Brasil: curva DI** — vencimentos 2027 a 2036 (atrasados) e, como série própria de fim de dia, a curva do ajuste da B3 (a avaliar, ver abaixo).
6. **Juros dos EUA** — `FRED:DGS2` e `FRED:DGS10` (diários) no lugar dos `TVC:US*` que não abriram.
7. **Cripto** — Bitcoin e Ether em dólares.
8. **Calendário econômico e notícias** — widgets do TradingView (links para a fonte, sem copiar manchetes). A verificar se o idioma e a atribuição funcionam.

Fora do escopo desta fase: futuros do CME/ICE (não abriram), manchetes da Reuters/Bloomberg, qualquer cotação coletada e republicada.

## 5. Regras de iniciante e de redação (herdadas do painel Mercados e ciclos)

Dez regras de redação do painel anterior continuam valendo: verbos no passado e período datado; lista de palavras proibidas ("vai", "deve", "sinal", "oportunidade", "barato", "alvo"); todo padrão histórico com número de ocorrências e contraexemplo; nunca causa única; indicadores descritos pelo cálculo e não pelo uso. Cada widget traz aviso de atraso ("D" = atrasado) e da atribuição. Material educativo, não é recomendação de investimento.

## 6. Pendências e riscos

- Confirmar com o TradingView o uso dos widgets nos termos de uso, caso a página tenha receita (hoje não tem).
- Testar cada símbolo aprovado nos widgets reais da página (Mini Symbol Overview, Market Overview, Ticker Tape, Advanced Chart).
- Rotina anual para os nomes dos contratos DI.
- Curva DI de fim de dia por fonte própria: só se a B3 permitir a reprodução dos ajustes do pregão (não verificado).
- Carga: vários widgets na mesma tela deixam a página pesada; montar só os do conjunto aberto (regra A11 do painel anterior).
- Os juízes não rodam dentro do GitHub Actions; atuam em sessões de IA a cada mudança de código ou texto.

## 7. Próximo passo

Avaliação independente desta proposta por quatro especialistas (Mercados, Dados e licenças, Didática, Engenharia), cada um em um agente separado, sem ver o parecer dos outros. Só depois disso a página é construída.
