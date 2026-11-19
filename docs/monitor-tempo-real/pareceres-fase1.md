# Monitor em tempo real — pareceres dos juízes da Fase 1 (PR #15)

Data: 19/11/2026. Três juízes independentes, em agentes separados, sem ver o parecer dos outros. Avaliaram a página `monitor/tempo-real/` antes do merge.

| Juiz | Nota | Bloqueantes | Principais pontos | Situação |
|---|---|---|---|---|
| J1 (dados e fontes) | 7,0 | 3 | Variação em pontos percentuais do DI e do FRED não testada; `CAPITALCOM:*` rotulado como "referência do TradingView"; origem de ouro, petróleo e prata afirmada além do registro; rótulo do FRED; "agregador" de câmbio | Corrigido no commit `473c55b` |
| J2 (comunicação e privacidade) | 7,0 | 2 | Frase "não gravam cookies" sem fonte; faixa de cotações sem legenda de cores e sem aviso de falha; glossário (B3, PTAX, Selic, Treasury); acessibilidade; faixa "Para estudo" só por JavaScript | Corrigido no commit `9759835` |
| J3 (engenharia) | 6,5 | 0 | Âncora "pular" redesenhava a página; ARIA da aba e do botão; erro do JSON mascarado; testes que passavam sem verificar (7 mutações); regex de número e lista de proibidas frágeis; runbook com mês errado (DI1F2028 cruza 90 dias em 03/10/2027) | Corrigido nesta rodada |

Não verificado por nenhum juiz (depende do Chrome do dono): o que a coluna de variação do Market Quotes mostra para DI e FRED; se os símbolos da faixa abrem no Ticker Tape; natureza dos feeds TVC e CAPITALCOM; leitor de tela e layout reais.

Limite dos testes: são textuais (JSON e HTML) e não executam a página. O teste de DI só avisa em pull request e falha no agendamento mensal.
