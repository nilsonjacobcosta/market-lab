# Monitor em tempo real — Fase 0 (proposta e testes, versão 2)

Data: 19/11/2026. Etapa anterior à construção. Nenhuma página nova foi criada ainda.

**Versão 2:** incorpora os pareceres dos quatro especialistas independentes (Mercados 7,0; Dados e licenças 7,0; Didática 5,5; Engenharia 6,0, todos "adequado com ajustes" ou condicionados). A versão 1 é o commit `85f681b`. Os pareceres estão resumidos em `pareceres-fase0.md`. A seção 8 lista o que muda em relação à versão 1; onde ela contradiz as seções 1 a 7, vale a seção 8.

Decisões do dono: o monitor em tempo real é uma **página nova dentro do market-lab** (pasta `monitor/tempo-real/`), segue a estrutura dos painéis existentes (conjuntos de cartões, modo Iniciante e Avançado, glossário, "o que este conjunto não diz") e é **completo e para iniciantes**.

## 1. Origem da ideia

Um print de tela de um terminal de mercado (fonte e data não identificadas) mostrou blocos de dólar, commodities, futuros, juros dos EUA, curva DI do Brasil e notícias. Pelo teste desta fase, os valores do print **não são atuais**: o argumento que sustenta isso é que um DI1F26 vence em janeiro de 2026, e hoje é 19/11/2026. Valores que algum widget tenha mostrado nesse dia **não foram conferidos** (ticker, unidade e data) e não entram como argumento. O print serve só como referência de layout. Nenhum valor dele entra no painel.

## 2. Teste de símbolos em widgets reais

Feito em 19/11/2026, no Chrome do dono, com o widget Market Quotes do TradingView (e, antes, o Ticker Tape). Só mostra se o símbolo abre; não compara valores com a bolsa.

| Grupo | Símbolos que abriram | Símbolos que não abriram |
|---|---|---|
| Moedas e cripto (abriram; o FAQ descreve forex e cripto como tempo real, latência não verificada) | `FX:EURUSD`, `FX:USDJPY`, `FX:GBPUSD`, `FX_IDC:USDBRL`, `BITSTAMP:BTCUSD`, `BITSTAMP:ETHUSD` | `TVC:DXY` (linha vazia) |
| Índices de ações (CFD de corretora) | `FOREXCOM:SPXUSD`, `FOREXCOM:NSXUSD`, `FOREXCOM:DJI` | `CME_MINI:ES1!`, `CME_MINI:NQ1!`, `CBOT_MINI:YM1!`, `CME_MINI:RTY1!` (erro) |
| Commodities | `TVC:UKOIL`, `TVC:USOIL`, `TVC:GOLD`, `TVC:SILVER`, `CAPITALCOM:COPPER`, `CAPITALCOM:IRON` | `COMEX:HG1!`, `ICEEUR:BRN1!` (erro) |
| Juros dos EUA | `FRED:DGS10` e `FRED:DGS2` (valor diário, sem variação percentual) | `TVC:US02Y`, `TVC:US05Y`, `TVC:US10Y`, `TVC:US30Y`, `ECONOMICS:USINTR` (vazios ou erro) |
| DI Brasil (marcados "D", atrasados) | `BMFBOVESPA:DI1F2027`, `DI1F2028`, `DI1F2029`, `DI1F2031`, `DI1F2033`, `DI1F2035`, `DI1F2036` | `BMFBOVESPA:DI1!` (contínuo, erro) |
| Bolsa brasileira (marcados "D", atrasados) | `BMFBOVESPA:IBOV`, `WIN1!`, `WDO1!`, `PETR4`, `VALE3`, `DOL1!`, `IND1!` | — |

Ressalvas do teste: o teste foi feito no widget Market Quotes, que é o usado na versão 1 da página (com `teste-simbolos.html` para repetir no Chrome do dono); falta testar Symbol Overview, Mini Chart e Advanced Chart com cada símbolo aprovado; os nomes de contratos DI mudam a cada ano e precisam de rotina de atualização; `TVC:GOLD` e `TVC:UKOIL` são cotações de referência do TradingView e não o contrato de uma bolsa.

## 3. Regras e limites dos dados

- Segundo o FAQ de dados do TradingView, forex e cripto são em tempo real, ações são atrasadas e o FAQ não informa o status de futuros e índices. Widgets só exibem dados do TradingView e não permitem exportar dados. Símbolos marcados como "somente no TradingView" não aparecem em widgets.
- Segundo o FAQ geral, widgets não definem cookies; o TradingView registra o endereço da página, o tipo de widget, o símbolo e o IP.
- Segundo os Termos de Uso (seção 3), os dados de mercado são licenciados "para uso de exibição" e o uso comercial não é permitido, salvo acordo à parte. Pela seção 4, a atribuição ao TradingView deve ficar visível. **Correção da versão 1:** a seção 4 dos Termos trata de widgets (a atribuição deve permanecer como foi originalmente desenhada e estar claramente visível). A licença é "pessoal ou de negócio interno" e "uso comercial" não é definido; ver seção 8.
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

## 8. Mudanças da versão 2 (prevalecem sobre as seções 1 a 7)

### 8.1 Conjuntos e cartões (a tabela de símbolos da seção 2 é hipótese até o teste nos widgets reais da página)

**Modo Iniciante: 4 conjuntos, até 4 cartões cada, um widget por cartão.**

1. **Câmbio** — dólar em reais (`FX_IDC:USDBRL`), euro em dólares, dólar em ienes. Texto explica que há três "dólares": o do agregador de câmbio, o futuro da B3 e a PTAX do Banco Central.
2. **Ações** — dois cartões separados, com rótulo de atraso e horário de cada mercado: **EUA** (S&P 500, Nasdaq 100 e Dow, em CFD de corretora) e **Brasil** (Ibovespa, atrasado). Sem minicontratos.
3. **Juros do Brasil** — contratos DI com **3 vencimentos** (`DI1F2028`, `DI1F2031`, `DI1F2035`). Regra: só vencimentos com mais de 90 dias. O `DI1F2027` fica fora porque vence no primeiro dia útil de janeiro de 2027.
4. **Commodities** — ouro, petróleo (**Brent** = `TVC:UKOIL` e **WTI** = `TVC:USOIL`, com os nomes escritos) e cobre (`CAPITALCOM:COPPER`).

**Modo Avançado (acrescenta):** abertura do dia em tabela estática (Market Quotes), cripto, juros dos EUA (`FRED:DGS2`/`DGS10`, rotulados "dado diário do dia útil anterior" e com variação em pontos percentuais), minicontratos da B3 (`WIN1!`, `WDO1!`, `DOL1!`, `IND1!`) com glossário, prata, minério de ferro (só se o texto disser o benchmark), DXY (testar `INDEX:DXY`; se não abrir, link para o gráfico semanal do painel Mercados e ciclos), VIX (testar), calendário econômico (condicionado a teste de idioma e atribuição) e Europa/Ásia (versão futura).

**Fora, com dois motivos para futuros do CME/ICE:** (a) não abriram nos widgets; (b) têm vencimento e rolagem, e os CFDs bastam para o objetivo didático. Manchetes de agências ficam fora. Notícias só como widget do TradingView, no Avançado, depois do teste de idioma e atribuição, e nunca resumidas, traduzidas ou comentadas por nós.

### 8.2 Curva DI própria: fora da versão 1
A seção 3 vale sem exceção: o painel não coleta nem republica cotação de bolsa. A curva DI de fim de dia só entra se a B3 autorizar por escrito a reprodução dos ajustes do pregão (checklist: política de dados de mercado, prazo de defasagem, redistribuição pública, "série derivada", uso educativo). Alternativas a avaliar, cada uma com termos próprios: curva da ANBIMA e taxas do Tesouro Nacional. Sem resposta por escrito, o conjunto "Juros do Brasil" funciona só com os widgets.

### 8.3 Licenças, atribuição e privacidade
- Atribuição do TradingView mantida como no modelo oficial, claramente visível; conferir o rodapé atual do painel Mercados ("Cotação de X by TradingView") contra o modelo antes de reaproveitá-lo.
- **Consulta formal ao TradingView desde já** (uso público, educativo e sem receita), com resposta guardada no repositório; não condicionada a receita. Definição de "uso comercial" adotada: qualquer receita, anúncio, patrocínio, doação associada ou afiliado; qualquer um desses reabre a decisão.
- Nenhum script lê valores de dentro dos widgets, e nenhum dado deles é gravado.
- Aviso de privacidade antes do primeiro widget (quem recebe, quais dados, finalidade, link da política do TradingView). Decisão do dono: carregar os widgets só após clique.
- Reconferir os termos do TradingView a cada trimestre e a cada nova versão da página, com a data da última conferência no README.
- Registrar que `FRED:*` e `BMFBOVESPA:*` têm licenças de origem próprias e que o painel apenas exibe.

### 8.4 Regras de redação para tempo real (somam-se às herdadas)
- **R-TR1** cores neutras no nosso texto; verde e vermelho só do widget, com legenda "acima ou abaixo do fechamento anterior; não significa bom nem ruim".
- **R-TR2** variação do dia sempre com a âncora ("em relação ao fechamento de [data]"); nunca é a manchete do cartão; proibido adjetivar ("forte", "despenca", "dispara", "pânico").
- **R-TR3** nenhum texto nosso liga manchete a preço do dia; "nunca causa única" inclui a causa do movimento de hoje.
- **R-TR4** o texto é estático e não cita valor atual; números ao vivo só dentro do widget. O campo "O que já se observou" descreve o que o widget mostra, no passado, ou diz "ainda sem observação registrada".
- **R-TR5** aviso de atraso por extenso em cada cartão ("atrasado em cerca de 15 minutos", ou "atraso não informado pela fonte") e proibido misturar relógios diferentes no mesmo cartão sem legenda. Faixa em toda a página: "Para estudo. Não use para operar. Preços atrasados ou de referência podem diferir dos de uma corretora."
- Termos novos do glossário: tempo real e atraso, cotação, fechamento, variação do dia, pregão e horário, contrato futuro, vencimento, DI, ponto percentual, ticker, CFD (com "pode diferir da bolsa"), minicontrato e alavancagem (Avançado), widget de terceiros, ruído e tendência, calendário econômico, dado diário.

### 8.5 Ordem e ritmo
Primeiro bloco ensina a ler, não pisca. **Ticker Tape ligado por padrão (decisão do dono, 8.7), com botão liga/desliga**; não monta com `prefers-reduced-motion` e tem botão "Pausar". Cada conjunto tem link para o histórico no painel Mercados e ciclos. Cartão "Como usar este painel" de poucas linhas no topo e a frase "você não precisa acompanhar isto durante o dia".

### 8.6 Engenharia
- **Copiar e enxugar** `monitor/mercados/index.html` (sem canvas, sem coleta), registrando o commit de origem; extrair módulo comum só na terceira página parecida. Prefixo de armazenamento `tempo-real-*`.
- `monitor/tempo-real/conjuntos.json` com `widget` (lista fechada) e `simbolos: [{s, rotulo, atraso}]`; um cartão por widget (Market Quotes ou Overview reúnem vários símbolos num iframe); até 4 iframes no Iniciante e 6 no Avançado; até 8 símbolos por widget; no máximo 1 Advanced Chart por conjunto. Montagem por `IntersectionObserver`, token de geração na troca, tempos de espera por tipo de widget.
- Reserva (widget não carregou): causa provável, lista estática dos símbolos com link por símbolo e aviso de que linha vazia ou erro dentro do iframe a página não detecta.
- Acessibilidade: título no `iframe` (não na `div`), alternativa em texto fora do iframe, "pular este gráfico" antes e depois de cada widget, `aria-live="off"`, avisos que não dependem só de cor.
- **Matriz símbolo × widget como critério de aceite:** nenhum símbolo entra no JSON sem registro de teste para o widget em que será usado, com data. Página auxiliar `teste-simbolos.html` para o teste no Chrome do dono.
- Teste automatizado `tests/test_tempo_real.py` (esquema, limites, widgets permitidos e nenhum de análise técnica, símbolos reprovados, matriz testada, termos no glossário, palavras proibidas, todo `BMFBOVESPA:*` como "atrasado", nenhum número de cotação no JSON) e teste de calendário dos contratos DI em workflow mensal. Workflow `testes-tempo-real.yml`. Runbook novo `11-simbolos-e-contratos-tempo-real.md`; rotina anual em dezembro junto do RB 04. Registros: README de manutenção, calendário, registro, `monitor/README.md`, `monitor/tempo-real/README.md` e cartão na página inicial com "Em construção".

### 8.7 Decisões do dono (19/11/2026)
1. **Widgets carregam sempre ao abrir a página** (sem clique). O aviso de privacidade (8.3) continua obrigatório e fica visível antes do primeiro widget, e o texto não pode dizer que "nada é carregado antes de você aceitar".
2. **Consulta formal ao TradingView autorizada**, com envio feito por Claude no canal oficial de contato, com texto sem dados pessoais além do necessário e resposta guardada no repositório. O envio por e-mail ou formulário em nome do dono segue o que ele autorizou aqui; endereço e canal serão os publicados pelo próprio TradingView.
3. **CI: testes de JSON e HTML apenas (biblioteca padrão), sem Playwright.** Motivo: os widgets são iframes de terceiros, que um teste simulado não valida de verdade; a dependência nova só testaria nosso próprio código de montagem, que o teste manual no Chrome do dono (`teste-simbolos.html`) já cobre. Reavaliar se a montagem ficar complexa.
4. **Curva DI própria fora da versão 1** (confirmado).
5. **Ticker Tape ligado por padrão, com botão liga/desliga** que lembra a escolha (`tempo-real-ticker`). Fica sempre desligado com `prefers-reduced-motion`, tem botão "Pausar" e não ocupa o primeiro bloco: vai em faixa fina no topo, abaixo do aviso "Para estudo. Não use para operar.". Isso substitui a regra da seção 8.5 de que o Ticker Tape é desligado por padrão. Símbolos da faixa: só os já testados.

### 8.8 Autorizações
Merge do PR #14 e início da Fase 1 (construção de `monitor/tempo-real/`) autorizados, com rodada de juízes antes do merge da Fase 1.

### 8.9 Correções após o juiz J1 (PR #15)
Variação do DI e do FRED sem afirmar o que o widget mostra (não verificado); `TVC:*` como "feed TVC, composição não verificada"; `CAPITALCOM:*` como corretora (provável CFD); "agregador" removido; rótulo do FRED passa a citar o Federal Reserve (H.15). Pendente no Chrome do dono: ver o que a coluna de variação do Market Quotes exibe para DI e FRED e se os símbolos da faixa abrem no Ticker Tape.

### 8.10 Teste do dono em 19/11/2026 (PR #15 já na `main`)
Feito em `teste-simbolos.html`, Chrome do dono, PDFs enviados na conversa. Resultados: (1) a faixa rola com valores; (2) todos os 27 símbolos dos cartões e os 6 da faixa abriram; (3) DI: o widget mostra duas colunas de variação, em pontos (diferença entre taxas) e em porcentagem relativa; FRED: valor arredondado a uma casa, variação em pontos, variação percentual em branco, abertura/máxima/mínima iguais ao valor; (4) natureza dos feeds TVC e CAPITALCOM não consultada. Achado: no cartão em meia largura o widget mostra só nome e valor; por isso os cartões passam a ocupar a largura inteira e os textos dizem que a variação aparece quando há espaço. Também se observou, nos PDFs, o widget em fundo claro: pode ser efeito da impressão em PDF; conferir na tela.

Atualização (19/11/2026, 17:11): o dono clicou em cobre no TradingView: XCUUSD, Capital.com, "Commodity • Cfd", CAPITALCOM. Cobre confirmado como CFD de corretora. Minério (`CAPITALCOM:IRON`) e os `TVC:*` seguem não conferidos.
