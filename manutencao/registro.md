# Registro de manutenção — Monitor BESST

Uma linha por execução de manutenção (manual ou incidente da rotina automática). Mais recente **embaixo**.
Horários em Brasília (UTC−3); entre parênteses, UTC quando vier dos logs do GitHub.

Formato: `Data hora | Quem | Runbook / tarefa | O que mudou | Fonte / evidência | Commit`

## Reconstituição de 02–03/11/2026
Reconstituído em 03/11/2026 a partir de `git log`, `gh run list` e dos documentos em `docs/monitor-besst/`.
"Sessão" = trabalho do Nilson com assistente de IA (commits com co-autoria); "bot" = `market-lab bot` (GitHub Actions).

| Data hora | Quem | Runbook / tarefa | O que mudou | Fonte / evidência | Commit |
|---|---|---|---|---|---|
| 02/11 17:26–18:24 | Nilson / sessão | — (fora do BESST) | Criação do repositório, página inicial, Rali do Midterm, Termômetro macro | git log | c80590a, 2aaf890, ff3a8b4, dd6fb6d |
| 02/11 22:03 | sessão | RB 03, RB 01 (carga inicial) | `universo.json` com 144 papéis; `estatais.json` com 85 registros (controle acionário revisado manualmente, `atualizado: 2026-11-02`); `monitor-besst.yml`; 1º `painel.json` | fontes registro a registro no próprio `estatais.json` (51 citam a página genérica da B3) | 0e58066 |
| 02/11 22:03 (01:03) | sessão | RB 06 (disparo manual) | 1ª coleta automática via `workflow_dispatch` | gh run list | 7ff7670 |
| 02/11 22:40 | sessão | RB 02 (carga inicial) | `situacoes_especiais.json` criado com 8 casos (AMBP3, OIBR3/4, LIGT3, BSLI3/4, DESK3, EMAE3/4, NEOE3, SRNA3), `atualizado: 2026-11-02`; script v2 com alertas e teto robusto | `docs/monitor-besst/qualidade-dados.md` | f0bd24e |
| 02/11 22:41 (01:41) | sessão | RB 06 (disparo manual) | Coleta para publicar a v2 | gh run list | f6868fd |
| 02/11 22:55–22:57 | sessão / bot | RB 07 (criação do teste) | `fase2-teste.yml` criado e rodado (1ª rodada com dados reais da CVM) | `docs/monitor-besst/parecer-teste-fase2.md` | 6e4273c, e7faea8 |
| 02/11 23:06–23:22 | sessão / bot | RB 07 | 11 correções dos juízes; diagnóstico de mapeamento por nome; 4 execuções do teste (02:16, 02:18, 02:20, 02:22 UTC) | `parecer-teste-fase2.md`, `fase2_teste/diagnostico_mapa.json` | 561364c, 1d40f6b, c438090, 1c2ec4f, 9db7157, a8a4b43, ddc000b |
| 02/11 23:19 | sessão | RB 05 (carga inicial) | `mapa_ticker_cvm.csv` criado com 3 exceções: BPAC→22616, EQPA→18309, BRIT→27693 | observações no próprio CSV; cadastro CVM | 69759ad |
| 02/11 23:21 | sessão | RB 07 | FCF yield retirado (escala de ações inconsistente no `composicao_capital`) | `parecer-teste-fase2-rodada2.md` | af1ad99 |
| 03/11 06:46–06:54 | sessão / bot | RB 07 | 3ª rodada (trava de dado antigo, nota com métrica descartada, LTM coerente, alerta de não recorrente, ROE médio, testes unitários); 2 execuções do teste (09:51 e 09:53 UTC) | `parecer-teste-fase2-rodada3.md` | b59d3d9, ec179c2, 7273c7b, 554429a, b7148a4, 9dcde7f |
| 03/11 07:00–07:06 | sessão / bot | RB 07 | Aprovação "com ressalvas, beta"; integração na página; `fundamentos-besst.yml` criado; 1ª publicação de `fundamentos.json` (dispatch 10:05 UTC), aceite limpo | `parecer-integracao-beta.md` | a5a4cb5, c76215a, 253bde2 |
| 03/11 07:07–07:13 | sessão | — | Ficha de qualidade responsiva e ajustes dos juízes | git log | cb8f6d2, b19999a |
| 03/11 15:01 (18:01) | bot | RB 07 | Rotina agendada de qualidade rodou com **7h18 de atraso**; aceite limpo (mapeados 100%, ≤15 meses 96,9%, com nota 88,1%, payout 93,9%); só `gerado_em` mudou (nenhum ITR 3T26 novo) | `primeiro-pregao-dados.md` §4 | 5453fc9 |
| 03/11 17:06 (20:06) | bot | RB 06 (incidente) | Coleta agendada rodou **1 vez das 9 previstas**; preços intradiários (~16h50) publicados como "fechamento" | `primeiro-pregao-dados.md` §1–2; `parecer-primeiro-pregao.md` | f25f663 |
| 03/11 18:36–18:37 | sessão | RB 06 | P0 dos juízes: faixa de aviso de instabilidade, horários redundantes de coleta, grupos de concorrência separados (`monitor-besst-precos` / `monitor-besst-fundamentos`), `git pull --rebase` | `parecer-primeiro-pregao.md` §3 | 85b86ef, b586584 |
| 03/11 18:36 (21:36) | sessão | RB 06 (disparo manual) | Execução **falhou** no push: `! [rejected] main -> main (fetch first)` (corrida com commit simultâneo) | log da execução 41723313622 | — |
| 03/11 18:45 (21:45) | sessão / bot | RB 06 (disparo manual) | Nova execução ok: fechamento de 03/11 publicado | gh run list | e739b87 |
| 03/11 18:48 | sessão | — | Relatórios de dados/UX e parecer dos juízes do 1º pregão versionados | `docs/monitor-besst/` | 8c214b0 |
| 03/11 19:04 | sessão | RB 04, RB 06, RB 09 | `painel.json` passa a gravar `fase` e `coletado_em_utc`; selo com aviso em texto pelo calendário da B3 (`FERIADOS` 2026 oficial, 2027 provisório); `abaixo_teto_conferir` para teto com anos-lacuna (CPFE3, ISAE3, ISAE4); `painel.json` recalculado (pregão 03/11, `fase: fechamento`) | Ofício Circular B3 054/2025-VNC | 13ab14c |
| 03/11 19:10 | sessão | RB 06 | Coleta **1×/dia após o fechamento** (18h22, 18h47, 19h23, 20h23, 22h09), selo de atraso a partir de 22h30; decisão de não usar agendador externo | commit | 65a84c4 |
| 03/11 ~22h | sessão (time de manutenção) | README da manutenção | Pasta `manutencao/` redigida (commit bbe3395). Achados: (1) o Ofício 054/2025-VNC foi revogado pelo 003/2026-VNC, que por sua vez foi revogado e republicado pela errata 041/2026-VNC (vigente) — datas do Listado inalteradas, lista de 2026 correta, comentário do `index.html` a atualizar; (2) evidência do cadastro/FCA da CVM para 21 dos 35 papéis sem cotação, mais NEOE3 e SRNA3 pela lista de situações especiais (RB 03 §5.4) | PDFs da B3; `fase2_teste/diagnostico_mapa.json` | bbe3395 |

## Pendências abertas (03/11/2026)
| Pendência | Runbook | Prazo sugerido |
|---|---|---|
| Conferir os fechamentos de 03/11 e 04/11 contra B3/corretora (P1-8 dos juízes) | RB 06 §6 | 04–05/11/2026 |
| Decidir e aplicar a limpeza dos 35 papéis sem cotação (+ OIBR3/4, cotação parada desde 22/09/2026) | RB 03 §5.4 | até 23/11/2026 (revisão do 3T26) |
| Trocar fontes de imprensa/portal das 8 situações especiais por documento primário | RB 02 §5.4 | 01/12/2026 |
| Revisão completa do controle acionário (60 dias) e troca das 51 fontes genéricas da B3 | RB 01 §5.4 | até 15/12/2026 (limite 01/01/2027) |
| Feriados 2027 oficiais (ofício da B3 de dezembro) e atualização do comentário de 2026 | RB 04 | até 20/12/2026 |
| Conferir no RI/CVM as lacunas de CPFE3 (2024–25), ISAE3/4 (2024), CPLE3 (2025), BMEB3/4 (2025) | RB 09 | até 23/11/2026 |
| Revisão pós-ITR 3T26 | RB 08 | 23/11/2026 |
| **Planejado:** rotina mensal CVM (`CONTROLE_ACIONARIO`, `SIT`, `SIT_EMISSOR` + posição acionária do FRE) que abre issue com divergências, sem alterar a classificação | RB 01 | a desenvolver |
| **Planejado:** aviso na página quando a revisão manual do controle passar de 60 dias | RB 01 | a desenvolver |
| **Planejado (P2):** `proventos_correcoes.json` para corrigir lacunas confirmadas | RB 09 §8 | a desenvolver |

## Execuções a partir de agora
| Data hora | Quem | Runbook / tarefa | O que mudou | Fonte / evidência | Commit |
|---|---|---|---|---|---|
| | | | | | |
| 03/11/2026 ~23h | time de revisão de fontes (sessão de IA) | RB 02 (1ª execução, revisão de fontes) | Cópia de trabalho de `situacoes_especiais.json` (não aplicada): `atualizado` 2026-11-03; fontes de portal trocadas (RAD: AMBP3; RI: OIBR, NEOE3; CVM: EMAE; B3: SRNA3; imprensa reconhecida: LIGT3, BSLI, DESK3); confiança rebaixada para media em LIGT3, BSLI, DESK3, SRNA3; EMAE3/4 → `incorporacao_concluida` (último pregão 23/10/2026; tirar do universo, RB 03); caso novo proposto FIQE3 (`opa_pendente`, media); 11 lições para o RB 02 | `revisao_fontes/relatorio_situacoes.md`; IPE não baixado (403) | — |
| 03/11 (rev. fontes) | sessão (time de revisão) | RB 01 — revisão de fontes, 1ª etapa | 34 registros (32 não privados + LIGT3, UPKP3): 17 fontes trocadas por RI/CVM, 2 por imprensa, 13 pendentes (confiança baixa); nenhuma categoria alterada; suno/auvp removidas; achado: LIPR3 cancelada na CVM (02/06/2025) → RB 03; `atualizado` 2026-11-03 (rever, ver Lição 6) | relatorio_controle.md (RI: BB, Banrisul, ABC, BRB, Basa, Banese, Banpará, Banestes, Cemig, ISA, Copel, Celesc, Sanepar, Sabesp, Copasa; CVM cad.) | — |
| 03/11/2026 ~23h30 | sessão (orquestrador) | Publicação da revisão de fontes | Juízes aprovaram com ajustes (notas 8,0 / 8,5 / 8,0): `estatais.json` com data mantida em 2026-11-02 (só 34 de 85 revistos), notas sem jargão; `situacoes_especiais.json` em 2026-11-03 com EMAE (incorporação concluída) e FIQE3 (OPA pendente; fonte primária até 10/11). Lições incorporadas aos RB 01 e 02. Pendentes: BRB (% do DF), Taesa (% ISA), Enel (fonte recente), 13 registros sem documento primário, portais em registros privados (próxima etapa) | parecer dos juízes | este commit |
