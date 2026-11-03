# Monitor BESST: primeiro pregão no ar (terça, 03/11/2026). Parecer do time de dados e operação

Escrito em 03/11/2026, por volta das 18h30 de Brasília (21h30 UTC). Repositório no commit `f25f663`. Nenhum arquivo do repositório foi alterado.

## 1. Agendamento (GitHub Actions)

**Fatos confirmados** (`gh run list`, `gh api .../actions/workflows`):
- O repositório foi criado em 02/11, às 20:25 UTC. O `monitor-besst.yml` existe desde 01:03 UTC de 03/11 e o `fundamentos-besst.yml` desde 10:05 UTC. Os dois estão `active` e no branch padrão.
- "Atualizar Monitor BESST" deveria rodar 9 vezes (13:17 a 21:17 UTC) e rodou **uma**, com evento `schedule`, criada às **20:06:05 UTC**. Um agendamento nunca dispara antes do horário, então essa execução é a das 19:17 (ou de um horário anterior) com pelo menos 49 minutos de atraso. As execuções das 13:17 às 18:17 não aconteceram. A das 20:17 também não, ou foi absorvida pela anterior. Às 21:30 UTC, a das 21:17 ainda não tinha aparecido. Essa é a **única rodada depois do fechamento**.
- "Atualizar qualidade financeira", marcada para 10:43 UTC, rodou às **18:01:48 UTC**, cerca de 7h18 de atraso. Foi o primeiro disparo desse agendamento, porque o arquivo só chegou ao repositório às 10:05.
- Os dois workflows usam o **mesmo** `concurrency.group: monitor-besst` com `cancel-in-progress: false`. No GitHub, um grupo guarda no máximo uma execução rodando e uma pendente. Se chega uma terceira, a pendente mais antiga é cancelada. Assim, uma execução de fundamentos atrasada pode cancelar uma coleta de preços que estava na fila.

**Causa.** A documentação oficial diz: "The `schedule` event can be delayed during periods of high loads… High load times include the start of every hour… If the load is sufficiently high enough, some queued jobs may be dropped" ([docs.github.com, evento schedule](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#schedule)). Há relatos recentes de atrasos de horas e de execuções que somem por completo ([#201472](https://github.com/orgs/community/discussions/201472), [#211258](https://github.com/orgs/community/discussions/211258), [#210625](https://github.com/orgs/community/discussions/210625)). O minuto 17 já foge da virada da hora, então o problema é a fila do próprio GitHub, provavelmente agravada porque o agendamento acabou de ser criado. O cron em si está certo. Conclusão: **o `schedule` do GitHub não serve como relógio de pregão.**

**Correções propostas**
1. **Disparo externo como mecanismo principal.** Um serviço de cron externo (cron-job.org, Cloudflare Workers Cron, Google Cloud Scheduler) chama `POST /repos/nilsonjacobcosta/market-lab/actions/workflows/monitor-besst.yml/dispatches` com um token de permissão fina, `actions:write`, restrito a esse repositório. O `workflow_dispatch` entra na fila na hora.
2. **Agendamento redundante como reserva.** Como o script só faz commit quando o dado muda, repetir rodadas custa pouco. Sugestão: `cron: "7,37 13-20 * * 1-5"` (intradiário a cada 30 minutos) e, no pós-fechamento, `"23,47 21 * * 1-5"`, `"19 22,23 * * 1-5"` e `"9 1 * * 2-6"`. Para os fundamentos: `"43 10 * * *"` e `"13 22 * * *"`.
3. **Separar os grupos de concorrência**, por exemplo `besst-precos` e `besst-fundamentos`. Para evitar conflito no push, a coleta de preços passa a fazer `git pull --rebase` antes de `git push`, como o workflow de fundamentos já faz.
4. **Confirmação do fechamento.** Depois das 18h05 de Brasília, a coleta grava `"fase": "fechamento"`. Se às 19h30 ainda não houver fechamento do dia, uma rodada de verificação dispara de novo. Ela pode ser feita pelo próprio cron externo.

## 2. Qualidade dos dados de hoje

**Horário da B3.** A partir de 03/11/2026, com o fim do horário de verão nos EUA, o pregão regular vai das **10h às 17h55**, o call de fechamento termina às **18h** e não há after-market ([Jornal do Comércio](https://www.jornaldocomercio.com/economia/2026/10/1268516-b3-amplia-horario-de-negociacao-ate-17h55-a-partir-de-3-11-com-fim-do-horario-de-verao-nos-eua.html); [BP Money](https://bpmoney.com.br/mercado/b3-muda-horarios-pregao-3-novembro-fim-horario-de-verao/); [comunicado da B3](https://www.b3.com.br/pt_br/noticias/b3-ajusta-horarios-de-negociacao-de-acoes-e-derivativos-acompanhando-fim-do-horario-de-verao-nos-eua.htm)). A coleta das 17:06–17:07 foi feita cerca de 50 minutos antes do fechamento. A cotação do Yahoo para a B3 vem com uns 15 minutos de atraso, e o candle diário, durante o pregão, traz o último preço negociado. **Todos os 82 preços de hoje são intradiários**, de algo perto das 16h50. Mesmo assim, a página diz "Pregão de 03/11" e o glossário (linha 287 do `index.html`) define preço como "Último preço de fechamento". Além disso, `fonte_precos` no `painel.json` diz "fechamento diário". Os dois textos estão errados para o dado de hoje.

**Variação entre a coleta de 01:42 UTC (fechamento de 30/10) e a de hoje (17:07), comparada com o que a imprensa publicou durante o dia**

| Papel | 30/10 | Hoje 17:07 | Variação | Imprensa (horário) |
|---|---|---|---|---|
| BBAS3 | 16,47 | 16,28 | −1,15% | −0,36% (13h08, [IstoÉ Dinheiro](https://istoedinheiro.com.br/ibovespa-hoje-queda-petrobras-juros-fiscal)) |
| ITUB4 | 38,69 | 38,54 | −0,39% | −0,30% (13h08) |
| BBDC4 | 13,86 | 13,56 | −2,16% | −1,23% (13h08) |
| SANB11 | 23,94 | 24,46 | +2,17% | +3,22% (13h08) |
| TIMS3 | 19,17 | 19,52 | +1,83% | +3,23% (15h20, [TradeMap](https://trademap.com.br/noticias/news-8552005)) |
| CMIG4 | 10,07 | 9,89 | −1,79% | n/d |
| SAPR11 | 30,85 | 29,70 | −3,73% | n/d |
| VIVT3 | 30,70 | 30,54 | −0,52% | n/d |
| BBSE3 | 41,32 | 40,54 | −1,89% | n/d |
| EGIE3 | 26,26 | 26,30 | +0,15% | n/d |
| TAEE11 | 39,59 | 39,12 | −1,19% | n/d |

Ibovespa no dia: −1,89% às 13h08 e −1,39% às 15h20 ([Forbes](https://forbes.com.br/forbes-money/2026/11/ibovespa-cai-antes-do-copom-com-incertezas-sobre-juros-e-politica-fiscal/)).

Os sinais e as ordens de grandeza batem com o movimento do dia. **Os fechamentos de 03/11 não puderam ser conferidos.** O proxy deste ambiente bloqueia o Yahoo (erro 403), e até 18h30 as matérias de fechamento ainda não estavam indexadas (a ao vivo da [InfoMoney](https://www.infomoney.com.br/mercados/ibovespa-hoje-bolsa-de-valores-ao-vivo-03112026/) parou às 9h37). A conferência precisa ser refeita amanhã contra a B3 ou as matérias de fechamento.

**Efeito no status.** O TIMS3 passou de `abaixo_teto` para `acima_teto` com base no preço intradiário. O status pode virar durante o dia e voltar no fechamento.

**Os 27 papéis com cotação mas sem data de hoje** são falta de negócio, não falha de coleta.
- 23 papéis estão com data de 30/10, o último pregão antes do feriado. Outros 2 estão em 26/10 (EMAE3/4) e 2 em 22/09 (OIBR3/4).
- 26 deles têm liquidez média de 0 a 128 mil reais por dia. Todos já trazem `baixa_liquidez` e `nivel_alerta` grave, a maioria com `sem_negociacao`.
- **A exceção é o AMBP3**: liquidez de 609 mil reais por dia e nenhum negócio hoje. É compatível com papel suspenso ou em situação especial (já tem o alerta `situacao_especial`), mas vale conferir na B3.
- Na ficha, a data do último negócio aparece (linha 501 do `index.html`). Na tabela, não.
- Outros 35 papéis devolvem erro 404 no Yahoo e aparecem como `sem_cotacao`. Isso já era conhecido.

**Proventos.** Só ITUB4 e ITUB3 mudaram: 2026 foi de 0,8926 para 0,9108, ou +0,0182, compatível com o JCP mensal com data "ex" no início do mês. O Yahoo registra proventos **pela data ex, não pelo anúncio**. Nada anunciado hoje entra antes dessa data, por exemplo o que o Itaú e a BB Seguridade divulgarem com os resultados do 3T26 depois do fechamento.

## 3. Aviso de dado velho na página

Em `carteiras/monitor-besst/index.html`, linhas 334–339, `liveLabel()` marca o dado como velho (`stale`) quando `gerado_em` passa de **26 horas**. O efeito é só **mudar a cor do ponto**, sem texto. A página consulta o JSON a cada 5 minutos.

Esse critério não serve para atualização intradiária:
- Hoje, das 10h às 17h07, a página mostrou os preços de 30/10 (gerados em 02/11, às 22:42) com o ponto **sem alerta**, porque a idade ficou entre 11 e 18 horas.
- Nas manhãs de segunda, o alerta acende antes de qualquer falha.
- O texto "Pregão de dd/mm" não diferencia preço intradiário de preço de fechamento.

**Proposta**
- **Regra pelo calendário da B3.** Durante o pregão (dias úteis, 10h–18h), alerta se o dado tiver mais de 90 minutos ou se `pregao_referencia` não for o dia de hoje. Fora do pregão, alerta se `pregao_referencia` for anterior ao último pregão encerrado. Os feriados vêm de uma lista no JSON.
- **Texto explícito**, além da cor: "Preço intradiário (atraso ~15 min), coletado às 17h07; o fechamento sai depois das 18h" ou "Dados atrasados: último pregão é 30/10".
- **No `painel.json`**: gravar `coletado_em_utc` e `fase` (`intradiario` ou `fechamento`) e corrigir `fonte_precos`. Na tabela, marcar com um selo os papéis cuja `data` difere de `pregao_referencia`.

## 4. Fundamentos (qualidade financeira, versão beta)

- As duas publicações de hoje passaram pelo aceite: o `workflow_dispatch` das 10:05 (commit `253bde2`) e o agendamento das 18:01 (commit `5453fc9`). Na rodada das 18:01, os 8 testes unitários passaram, os 109 papéis negociados foram considerados e os indicadores de aceite ficaram assim:

| Indicador | Resultado | Meta |
|---|---|---|
| Emissores mapeados | 100% | ≥95% |
| Emissores com dado de até 15 meses | 96,9% | ≥90% |
| Papéis com nota | 88,1% | ≥75% |
| Payout calculado nos papéis lucrativos | 93,9% | ≥90% |

  Todas as listas de "meta 0" vieram vazias e a saída foi "Publicado: … 144 papéis". As marcações `verificar:` (variações de lucro de −328% a +87% e um ROE de 85,9) são só informativas.
- Comparando `dados/besst/fundamentos.json` entre os dois commits, **a única mudança foi `gerado_em`**: nenhuma nota, data de referência ou métrica mudou. **Nenhum ITR do 3T26 entrou hoje.** Os 16 papéis com referência em 30/09/2026 já estavam na publicação das 07:06: BBDC3/4, SANB3/4/11, NEOE3, COCE3/5/6, CEEB3/5/6, EKTR3/4, CBEE3 e AFLT3.
- O Itaú e a BB Seguridade divulgam o 3T26 depois do fechamento de hoje ([IstoÉ Dinheiro](https://istoedinheiro.com.br/ibovespa-hoje-queda-petrobras-juros-fiscal)). Só entram quando aparecerem no Portal de Dados Abertos da CVM, na próxima rodada que funcionar.
- Ainda há referências antigas: 9 papéis com dado de 2023 e 5 com dado de 2024. A trava de dado antigo deveria tirar a nota deles. O aceite confirma `nota_com_dado_antigo = []`.

## Achados, por gravidade

1. **Alta.** A coleta de preços rodou 1 vez em 9. A única rodada pós-fechamento (21:17 UTC) não tinha aparecido às 21:30 UTC. Correção: disparo externo via `workflow_dispatch` e agendamento redundante.
2. **Alta.** Os preços de hoje são intradiários (cerca de 16h50, com atraso), mas a página e o JSON dizem "fechamento". Correção: campo `fase`, texto na página e rodada pós-fechamento garantida.
3. **Média.** O alerta de 26 horas não acendeu enquanto a página mostrou preços de 30/10 o dia inteiro, e o aviso é só uma cor. Correção: regra pelo calendário da B3 e texto explícito.
4. **Média.** Os dois workflows dividem o grupo de concorrência, o que pode cancelar uma coleta pendente. Correção: grupos separados e `pull --rebase` na coleta.
5. **Média.** O workflow de fundamentos atrasou 7h18. Nenhum ITR do 3T26 entrou hoje (o Itaú e a BB Seguridade saem depois do fechamento). Correção: um segundo cron, às 22:13 UTC.
6. **Baixa.** Os 27 papéis sem data de hoje são ilíquidos, sem falha de coleta. A exceção é o AMBP3: conferir se está suspenso e mostrar a "data do último negócio" na tabela.
7. **Baixa.** O status em relação ao teto pode mudar durante o pregão (TIMS3 hoje). Proventos entram pela data ex: hoje só ITUB3/4, com +0,0182.
8. **Pendente.** Os fechamentos de 03/11 não foram conferidos (Yahoo bloqueado e matérias de fechamento ainda não indexadas). Refazer amanhã.
