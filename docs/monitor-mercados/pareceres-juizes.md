# Mercados e ciclos — pareceres dos juízes (rodada 1)

Data: 16 e 17/11/2026. Commit avaliado: e825ddc (J1 e J2) e 6146903 (J3). Cada juiz avaliou de forma independente, sem participar da construção.

| Juiz | Nota | Veredito | Bloqueantes | Situação |
|---|---|---|---|---|
| J1 dados e fontes | 7,0 | Aprovado com ressalvas | 2 | Corrigidos; reconferidos por revisor independente (resolvidos) |
| J2 regulatório e comunicação | 7,5 | Aprovado com ressalvas | 3 | Corrigidos; reconferência achou resíduos, também corrigidos |
| J3 engenharia e operabilidade | 7,0 | Aprovado com ressalvas | 1 | Corrigido; conferido pelo coordenador com a mesma reprodução do juiz |

Observação de método: J1 e J2 rodaram no modelo Fable 5.2; a primeira tentativa de J3 foi interrompida por limite de uso e refeita em outro modelo (Sonnet 5.5). A reconferência dos bloqueantes de J1 e J2 também foi feita em outro modelo. A conferência do bloqueante de J3 foi feita pelo coordenador, não por juiz independente.

## Bloqueantes e correções

**J1-1.** `fontes.py` datava as barras semanais do Yahoo com o deslocamento de inverno (`gmtoffset`), o que colocava barras de segunda-feira no domingo anterior durante o horário de verão. Corrigido com o fuso da bolsa (`exchangeTimezoneName`) e dois testes novos (Nova York e Lisboa no verão).

**J1-2.** A tabela do README divergia do catálogo e havia nomes de instrumento do Yahoo que não eram literais. Os 25 tickers foram conferidos na API real em 16/11/2026 (nome literal, tipo, moeda, fuso, barras e primeira data) e a tabela passou a ser gerada do catálogo. Descoberta nova: ouro, prata, petróleo e cobre são contratos futuros em andamento (ex.: "Gold Dec 26"), com possíveis saltos na troca de contrato; isso foi registrado.

**J2-1.** Prefixos de plataforma (BITSTAMP, BINANCE, FX_IDC, CRYPTOCAP) apareciam em texto visível. A página mostra só o par (ex.: BTCUSD); o link mantém o símbolo completo.

**J2-2.** A contagem de inversões da curva de juros estava imprecisa. O texto foi reescrito com os dados diários do FRED (T10Y2Y: três períodos longos desde 2000 e três dias levemente negativos em agosto de 2019) e a datação do NBER (recessões iniciadas em março de 2001, dezembro de 2007 e fevereiro de 2020).

**J2-3.** Textos da prata, do cobre, do balanço do Fed e do ciclo do Bitcoin reescritos sem causa única e sem afirmação de uso do preço.

**J3-1.** O aceite exigia 24 pontos por série e o HICP de Portugal tem só 17 no conjunto vigente do Eurostat; a primeira coleta seria reprovada e a branch de dados nunca nasceria. `min_pontos` de `infl_pt_12m` passou a 12.

## Ressalvas não bloqueantes que seguem abertas

- Série "ok" com dado velho reprova o arquivo inteiro (`aceite.py`); considerar rebaixar essa série a "anterior" no coletor.
- Série "anterior" por 3 dias ou mais: resolvido em 17/11/2026 (campo `anterior_desde`; aviso no log do aceite e nota na página).
- Resolvido em 18/11/2026: o passo de coleta não usa mais `continue-on-error`; falha geral deixa o job vermelho e não publica.
- Se o Yahoo bloquear o Actions no primeiro dia, restam 23 de 48 séries e o aceite reprova (limite de 60%).
- A comparação de 3 pontos por série com a fonte oficial foi feita em 17/11/2026 depois da 1.ª coleta real: coincidem, salvo o último ponto de VIX e WTI (barra semanal em curso, moveu entre coleta e conferência). Séries derivadas não conferidas contra fonte externa.
- Widget Advanced Chart: os 9 símbolos abriram em 17/11/2026 (com RSI e média móvel); "RSI@tv-basicstudies" e locale/timezone seguem sem confirmação na documentação do TradingView.
- Textos com afirmações factuais sem fonte (composição do DXY, Nikkei 1989, WTI negativo em 2020, par mais negociado, entre outras listadas por J1 e J2) a revisar com fonte ou a retirar.
- `innerHTML` com `dataBR(s.ultimo_dado)` sem escape e `url_fonte` sem validação de esquema (risco baixo, dados da própria conta).
- Série ausente do JSON aparece com o id cru na nota do gráfico.
- A branch `dados-mercados` cresce (cerca de 1 MB por atualização); fazer squash periódico.
- Glossário: variantes de Portugal e termos faltantes (obrigações do Tesouro, unidade de participação, recessão, contrato futuro).

## Rodada 2 — razão XLP/XLK e média de 200 semanas do Bitcoin (18/11/2026)

Escopo: PR #12 (faixa da razão e episódios dos cartões `rc-xlp-xlk` e `btc-ciclos`). Juízes independentes e só de leitura.

| Juiz | Nota | Veredito | Bloqueantes |
|---|---|---|---|
| J1 dados e fontes | 8,5 | Aprovado com ressalvas | 0 |
| J2 regulatório e comunicação | 7,0 | Aprovado com ressalvas | 1 (corrigido; reconferido por revisor independente: resolvido, nota 9) |
| J3 engenharia e operabilidade | 9,0 | Aprovado com ressalvas | 0 |

**J2-B1.** Episódios do cartão XLP/XLK sem critério de escolha e sem datas/valores em 2022 e 2023; texto do desdobramento do XLK confuso. Reescrito com datas e valores, "trechos escolhidos como exemplo" e explicação do desdobramento.

Ressalvas tratadas: "cerca de 27 anos"; semana parcial na contagem do Bitcoin; data de março de 2020; "cerca de 32% abaixo"; `observacao` de `rel_xlp_xlk` sem "indica" nem "defensivo".

Ressalvas abertas: último valor da razão repetido em 14/11 e 17/11/2026 (barra parcial com o mesmo fechamento; sem efeito no aceite); exemplo numérico no `como_ler` da razão; texto do `como_ler` do cartão do Bitcoin com repetição (herdado); o workflow roda só `unittest tests/test_mercados.py`; valores de `btc_usd` sem comparação com a bolsa de origem.
