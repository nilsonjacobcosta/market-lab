# Monitor BESST: parecer dos juízes sobre o 1º pregão no ar (terça, 03/11/2026)

Time de juízes independente do market-lab. J1 cuida de dados e operação, J2 de regulatório e comunicação, J3 de engenharia e acessibilidade.
Escrito em 03/11/2026 às 18h33 de Brasília (21:33 UTC). Repositório no commit `f25f663`, sem nenhuma alteração.
Base: `primeiro_pregao_dados.md`, `primeiro_pregao_ux.md` e as capturas. Conferimos por conta própria: `gh run list -L 40`, os dois workflows, `dados/besst/painel.json`, `carteiras/monitor-besst/index.html`, `scripts/besst_painel.py` e o comunicado da B3.

Lembrete: o painel é material educativo e não traz recomendação de investimento (Res. CVM 20/2021).

---

## 1. Verificação dos achados

| # | Achado | Veredito | Evidência dos juízes | Gravidade |
|---|---|---|---|---|
| 1 | A coleta agendada rodou 1 vez das 9 previstas | **Confirmado** | No `gh run list` aparece uma única execução `schedule` de "Atualizar Monitor BESST", criada às 20:06:05 UTC. Às 21:33 UTC ainda não havia a das 21:17 UTC (18h17 em Brasília). Nenhuma execução aparece como cancelada: elas **nem chegaram a ser criadas** | **Crítica** |
| 2 | O preço mostrado como "fechamento" é intradiário | **Confirmado** | `gerado_em: 2026-11-03 17:07` (Brasília). `fonte_precos` diz "fechamento diário". Na linha 287 do `index.html`, a definição de Preço diz "Último preço de fechamento". O horário da B3 foi conferido na **fonte primária** ([b3.com.br](https://www.b3.com.br/pt_br/noticias/b3-ajusta-horarios-de-negociacao-de-acoes-e-derivativos-acompanhando-fim-do-horario-de-verao-nos-eua.htm)): a partir de 03/11, pregão regular das 10h às 17h55 e call de fechamento das 17h55 às 18h. O comunicado não trata do after-market. **Agravante**: como a rodada pós-fechamento não saiu, o painel vai mostrar a noite toda o preço de cerca de 16h50 como "Pregão de 03/11", com o ponto verde, até 19h07 de 04/11 | **Alta** |
| 3 | O aviso de dado velho é só a cor do ponto (regra de 26 h) | **Confirmado** | Em `liveLabel()`, linhas 334 a 339, só existe `classList.toggle("stale", age>26)`. O texto não muda e falta `role`. A captura `selo_terca_15h_robo_parado.png` mostra o ponto verde com dado do dia anterior. Subimos a gravidade de "média" para alta, porque esse é o único aviso que existe | **Alta** |
| 4 | O grupo de concorrência compartilhado pode cancelar coletas | **Confirmado como risco; refutado como causa de hoje** | Os dois workflows usam `group: monitor-besst`. O GitHub mantém só uma execução pendente por grupo e cancela a anterior quando chega outra. Hoje nenhuma execução foi cancelada. Achado extra dos juízes: o `monitor-besst.yml` faz `git push` **sem** `git pull --rebase`. Quando os grupos forem separados, o push vai falhar se o workflow de fundamentos publicar no meio da execução | Média |
| 5 | O workflow de fundamentos atrasou 7h18, mas o aceite saiu limpo | **Confirmado** | O `workflow_dispatch` das 10:05 e o `schedule` das 18:01:48 UTC (previsto para 10:43) terminaram com sucesso | Baixa-média |
| 6 | CPFE3 aparece como "Fortes + Abaixo do teto", com teto calculado só sobre 2021–2023 | **Confirmado** | Proventos: 2024 = 0, 2025 = 0, 2026 = 3,73. `dpa_robusto` = 3,2423, que é a mediana de 2021 a 2023. O status simples é `acima_teto` (−27,5%), mas o robusto, que é o exibido, é `abaixo_teto` (+22,7%). O próprio painel desconfia do dado (`lacuna_proventos`), e mesmo assim o papel entra no filtro "Abaixo do teto" | **Alta** (J2) |
| 7 | BBAS3 aparece como "Fracos + Abaixo do teto 43%" | **Confirmado** | `margem_robusta` = 43,2, tendência −30,3% e 2 alertas de atenção. A ficha explica, mas a tabela destaca a margem | Média |
| 8 | CEEB5 e AFLT3 aparecem como "Fortes + Grave" | **Confirmado** | `nivel_alerta: grave` (sem negociação). Esses papéis ficam escondidos pelo filtro padrão de liquidez | Baixa |
| 9 | ENEV3 mostra "teto R$ 0,00" | **Confirmado, com correção de contagem** | São **6** papéis com `sem_proventos` mostrando "R$ 0,00": ENEV3, RNEW3/4, ORVR3 e TELB3/4. O relatório falava em 12. Os outros 6 estão em `nao_se_aplica` e já aparecem como "não se aplica" | Média-baixa |
| 10 | A atualização automática tira o foco | **Confirmado (código)** | O `setInterval` de 5 min chama `render()`, que reescreve as linhas, e não há nada que salve ou devolva `activeElement`. Também não existe anúncio por `aria-live` | Média |
| 11 | No celular, as colunas-chave exigem rolar para o lado | **Confirmado** | Em `COLS`, Alertas, Qualidade e Situação são as **últimas** colunas. Na captura `390_simple_tabela.png` só aparecem Empresa, Preço e DY. Não há nenhuma dica de rolagem | Média-alta |
| 12 | AMBP3 sem negócio apesar de ter liquidez | **Explicado (não é falha)** | O `situacao_especial` informa: "ações só em leilão no fim do pregão por atraso de balanços" | Baixa |
| 13 | Os fechamentos de 03/11 não foram conferidos | **Pendente** | Também não temos acesso ao Yahoo neste ambiente. A conferência fica para 04/11 | Pendente |

## 2. Classificação: o painel continua no ar?

**Sim. Pode continuar no ar, em regime de "aviso reforçado".** A ordem de grandeza dos dados está certa: os sinais batem com o movimento do dia. Os alertas de qualidade existem e o caráter educativo está declarado. O defeito está no **rótulo de tempo**, que diz "fechamento" e mostra o ponto verde sobre um dado intradiário ou velho, e não nos números em si. Tirar o painel do ar seria desproporcional. Mantê-lo sem aviso por mais um pregão inteiro seria inaceitável.

**Aviso imediato.** Uma faixa em texto, logo abaixo do selo, que não depende de cor, com `role="status"`. Deve entrar no ar ainda hoje ou, no máximo, antes das 10h de 04/11:

> **Atenção:** a atualização automática deste painel está instável nesta semana. Os preços podem ter horas ou dias de atraso e, durante o pregão, não são preços de fechamento. Confira a data e a hora no selo acima e confirme na B3 ou na sua corretora. Material educativo, não é recomendação de investimento.

Condição: se até 10h de 04/11 nem a faixa nem os itens P0-1 a P0-3 estiverem publicados, o selo deve passar a mostrar "Dados possivelmente desatualizados" de forma permanente.

## 3. Correções priorizadas

### Sobre o agendamento: avaliação das opções

| Opção | Confiabilidade | Exige ação do dono? | Veredito |
|---|---|---|---|
| **Cron redundante no GitHub** (vários horários, incluindo pós-fechamento) | Média. Cada disparo pode atrasar ou ser descartado, mas é improvável que caiam todos. Custo baixo: o script só faz commit quando o dado muda | **Não** | **P0**: melhor solução sem token |
| **Disparo externo por `workflow_dispatch`** (cron-job.org, Cloudflare Workers Cron ou Cloud Scheduler, com token de permissão fina `actions:write` restrito ao `market-lab`) | Alta. O `dispatch` entra na fila na hora | **SIM.** O dono do repositório precisa criar o token de permissão fina (com validade curta), criar a conta e o agendamento no serviço externo e guardar o token como segredo desse serviço. Nenhum agente pode ou deve fazer isso por ele | **P1**: solução definitiva |
| **Verificação de dado velho no front** (calendário da B3) | Não traz dado novo, mas **garante honestidade**: o usuário passa a saber quando o dado está velho | Não | **P0**: obrigatória em qualquer cenário |
| (alternativa) Tarefa agendada do Claude que roda `gh workflow run` | Média-alta | Sim: o dono precisa aprovar a tarefa e a credencial de escrita | P1, opcional, no lugar do cron externo |

Conclusão: o **P0 que não depende do dono** combina três coisas. (a) Cron redundante. (b) Disparo manual pela sessão principal hoje à noite e amanhã depois das 18h15, usando o acesso que já existe; ela já disparou `workflow_dispatch` em 03/11, às 01:03 e às 01:41. (c) Front honesto. Isso não resolve a confiabilidade, mas impede que o usuário seja enganado.

### P0: antes das 10h de quarta, 04/11

| ID | Correção | Critério de aceite verificável |
|---|---|---|
| P0-1 | **Disparar agora** a coleta de fechamento de 03/11 (`gh workflow run monitor-besst.yml`). Repetir em 04/11 depois das 18h15 se o cron não tiver rodado | Novo commit em `painel.json` com `gerado_em ≥ "2026-11-03 18:15"` e `pregao_referencia = "2026-11-03"` |
| P0-2 | **Cron redundante** no `monitor-besst.yml`: `"7,37 13-20 * * 1-5"` (intradiário), `"22,47 21 * * 1-5"`, `"23 22,23 * * 1-5"` e `"9 1 * * 2-6"` (pós-fechamento) | O YAML é válido (`python -c "import yaml…"`). Em 04/11, `gh run list` mostra **≥ 4** execuções `schedule` entre 13:00 e 21:00 UTC e **≥ 1** commit com `gerado_em` entre 18:15 e 22:00 de Brasília |
| P0-3 | **Grupos de concorrência separados** (`besst-precos` e `besst-fundamentos`) e `git pull --rebase` antes do `git push` no monitor | `grep "group:"` devolve dois nomes diferentes. A etapa de publicação do monitor contém `git pull --rebase` |
| P0-4 | **Campo `fase` e textos honestos.** O script grava `coletado_em` e `fase` = `intradiario` quando roda no próprio dia de `pregao_referencia` antes das 18h15 de Brasília, e `fechamento` nos outros casos. `fonte_precos` passa a ser "Yahoo Finance: último negócio (atraso ~15 min) durante o pregão; fechamento após 18h". A definição de "Preço" segue o texto do relatório de UX, §1. O selo usa os três textos do relatório de UX (em andamento, fechamento, fechamento não chegou) | Rodar o script com o relógio simulado às 14h → `fase:"intradiario"`. Às 19h → `"fechamento"`. A página com `fase:"intradiario"` mostra "em andamento", e a palavra "fechamento" não aparece no selo nem na definição de Preço |
| P0-5 | **Dado velho pelo calendário da B3, em texto.** Último pregão esperado = hoje, se for dia útil e já passar das 10h30; senão, o dia útil anterior, com feriados da B3 numa lista (20/11, 24/12, 25/12, 31/12 etc.). Alertar também se, durante o pregão, `gerado_em` tiver mais de 90 min. Pôr `role="status"` em `#live` e usar texto, não só cor | Teste com relógio simulado em 5 casos: terça 15h com dado de segunda → texto "a atualização automática atrasou". Sábado 21h e segunda 9h com fechamento de sexta → **sem** alerta. Sexta 20/11 com dado de 19/11 → sem alerta. Durante o pregão com dado de 2 h → alerta. Todos passam com o ponto em escala de cinza (sem depender de cor) |
| P0-6 | **Faixa de aviso** (texto da §2) | Visível a 390 px e a 1300 px, nos modos claro e escuro, acima da tabela, sem precisar rolar |
| P0-7 | **CPFE3 e casos com `lacuna_proventos`**: quando o status for `abaixo_teto`, mostrar "Abaixo do teto · conferir dados" e tirar o papel do filtro "Abaixo do teto". O alerta passa a usar o texto do relatório de UX, §3 | Com o filtro "Abaixo do teto" ligado, CPFE3 **não** aparece. Na ficha, CPFE3 mostra "conferir dados" e o texto "O teto usou só 2021–2023" |

### P1: nesta semana

| ID | Correção | Critério de aceite |
|---|---|---|
| P1-1 | **Disparo externo por `workflow_dispatch`. Depende do dono**: token de permissão fina `actions:write`, só no `market-lab`, com validade ≤ 90 dias, e agendamento no cron-job.org ou no Cloudflare. O cron do GitHub continua como reserva | Por 3 pregões seguidos, ≥ 8 execuções por dia com evento `workflow_dispatch` e atraso < 5 min em relação ao horário marcado, e fechamento publicado até 18h30 |
| P1-2 | Atualização automática que **preserva o foco**: adiar o render enquanto houver foco num `input`, anunciar em `aria-live="polite"` ("Dados atualizados às hh:mm…") e avisar quando uma ficha aberta sair do filtro. Fazer a busca automática só em dia útil, das 10h às 18h30 | Num teste com Playwright, o foco continua no campo do simulador depois do refresh, o anúncio aparece no DOM e nenhuma requisição sai no sábado |
| P1-3 | **Celular**: Situação e Alertas logo depois de Empresa a ≤ 480 px, ou dica "Deslize para ver alertas e situação →". `thead` fixo | A 390 px, Situação e Alertas aparecem na primeira tela, sem rolar para o lado |
| P1-4 | Teto "R$ 0,00" → "–" para `sem_proventos` e `historico_curto` | Os 6 papéis listados mostram "–" na tabela e na ficha |
| P1-5 | Linha "Como ler estes sinais juntos" (Abaixo + Fracos, Fortes + Grave, Nenhum alerta + Fracos) | BBAS3, BBSE3 e CEEB5 mostram a frase certa na ficha |
| P1-6 | Selo "preço de dd/mm" na tabela quando `data < pregao_referencia` | CEEB5 e AMBP3 mostram "preço de 30/10" |
| P1-7 | Segundo cron para os fundamentos (`"13 22 * * *"`) | Duas execuções agendadas por dia aparecem no histórico |
| P1-8 | Conferir os fechamentos de 03/11 e 04/11 contra a B3 ou as matérias de fechamento | Diferença ≤ 0,5% nos 11 papéis da tabela do relatório de dados |

### P2: depois

- Fonte alternativa de proventos (CVM ou RI) para corrigir lacunas como a da CPFE3. Aceite: proventos de 2024 e 2025 da CPFE3 diferentes de zero e conferidos no RI.
- Link "Pular para a tabela". Tirar o `aria-label` da `tr` e usar um `<button aria-expanded>` na 1ª célula. Aceite: ≤ 3 paradas de Tab até a 1ª linha.
- Ordenação por DY 12m com graves no fim do modo Iniciante. Nota da BBSE3 explicada na tabela.
- Painel de saúde da operação: última execução bem-sucedida e quantas rodadas houve no dia, lidos do próprio JSON.

## 4. Notas do funcionamento no 1º pregão (0–10)

| Juiz | Nota | Justificativa |
|---|---|---|
| J1: dados/operação | **4,0** | Os fundamentos funcionaram com aceite limpo e os preços coletados estão coerentes. Mas a coleta rodou 1 vez em 9 e o fechamento não foi publicado. O painel virou "foto das 16h50" |
| J2: regulatório/comunicação | **4,5** | Os alertas e o aviso educativo existem e a ficha explica bem. Mas o rótulo "fechamento" é factualmente falso e o aviso de atraso é invisível. A CPFE3 entra limpa no filtro "Abaixo do teto" com dado que o próprio painel acha suspeito |
| J3: engenharia/acessibilidade | **5,5** | Bom desempenho, teclado e contraste AA. O estado do dado depende só de cor, o refresh tira o foco, no celular as colunas-chave ficam escondidas e o push não tem rebase |

**Média: 4,7/10.** O painel continua no ar com aviso reforçado. A reavaliação acontece depois do pregão de 04/11, com base nos critérios de P0-2 e P0-5.
