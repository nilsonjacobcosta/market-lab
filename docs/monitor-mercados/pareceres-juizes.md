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
- Séries "anterior" por muitos dias não geram aviso próprio; o banner só dispara quando todas as fontes falham por 5 dias ou mais.
- O passo de coleta usa `continue-on-error`: falha geral não deixa o job vermelho. O runbook RB 10 descreve a conferência.
- Se o Yahoo bloquear o Actions no primeiro dia, restam 23 de 48 séries e o aceite reprova (limite de 60%).
- A comparação de 3 pontos por série com a fonte oficial ainda não foi feita (a coleta real não rodou). Obrigatória antes de trocar o status "Em construção".
- O widget Advanced Chart (modo Avançado) não foi testado com os símbolos; "RSI@tv-basicstudies" e locale/timezone não foram confirmados na documentação.
- Textos com afirmações factuais sem fonte (composição do DXY, Nikkei 1989, WTI negativo em 2020, par mais negociado, entre outras listadas por J1 e J2) a revisar com fonte ou a retirar.
- `innerHTML` com `dataBR(s.ultimo_dado)` sem escape e `url_fonte` sem validação de esquema (risco baixo, dados da própria conta).
- Série ausente do JSON aparece com o id cru na nota do gráfico.
- A branch `dados-mercados` cresce (cerca de 1 MB por atualização); fazer squash periódico.
- Glossário: variantes de Portugal e termos faltantes (obrigações do Tesouro, unidade de participação, recessão, contrato futuro).
