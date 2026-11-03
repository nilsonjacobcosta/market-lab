# Monitor BESST: UX e comunicação no 1º pregão (03/11/2026)

Time de Experiência do Usuário e Comunicação · market-lab
Base: commit `f25f663` (painel.json `gerado_em: 2026-11-03 17:07`, `pregao_referencia: 2026-11-03`); fundamentos.json de 03/11 (commit `5453fc9`).
Teste local (http.server 8767) com Playwright/Chromium, 1300px e 390px, modos Iniciante e Completo, claro e escuro. Repositório não alterado. O cenário de dado velho foi testado numa cópia em `/tmp/besst_stale`, servida na porta 8768, e com interceptação de rede.
Capturas: `/home/claude/work/times/capturas_pregao1/` (35 arquivos).

> Contexto de horário: a partir de 03/11/2026 a B3 negocia até 17h55, com fechamento às 18h, porque o horário de verão dos EUA acabou (Jornal do Comércio, 10/2026). O robô (`17 13-21 * * 1-5`) roda às hh:17 BRT. Às 18h28 BRT a última publicação ainda era a das 17h07: a rodada das 18h17, que traria o fechamento, não tinha chegado.

---

## 1. Selo "ao vivo"

**O que aparece hoje (18h30):** `● Pregão de 03/11/2026 · atualizado 03/11 às 17:07`, com o ponto verde (captura `selo_hoje_18h30_real.png`).

| Achado | Gravidade |
|---|---|
| 1a. O preço é **intradiário** (17h07, 50 min antes do fechamento). Mesmo assim, o selo, a definição de "Preço" (*"Último preço de fechamento da ação no pregão de referência."*) e `fonte_precos` (*"fechamento diário"*) dizem "fechamento". Um iniciante não tem como saber que o número ainda vai mudar. Às 14h a tela mostra `Pregão de 03/11/2026 · atualizado 03/11 às 14:07` com o mesmo ponto verde, e nada diz que o pregão está em andamento. O DY 12m, a margem e o simulador ("ao preço de hoje") usam esse preço. | **Alta** |
| 1b. O aviso de dado velho **só muda a cor do ponto** (verde para âmbar). O texto não muda, não há `role`/`aria-live` e quem não distingue cores (ou usa leitor de tela) não percebe nada. Com a cópia velha (30/10): `Pregão de 30/10/2026 · atualizado 30/10 às 18:07`, ponto âmbar, e é tudo. | **Alta** |
| 1c. A regra `idade > 26 h` falha nos dois sentidos. Dá **alarme falso** no sábado às 21h e na segunda às 9h, com dados normais de sexta, e em feriado. **Não avisa** na terça às 15h com dados de segunda, quando o robô deveria ter publicado 5 vezes. | Média |
| 1d. O selo diz "Pregão de 03/11", mas papéis com preço de outro dia aparecem sem marca na tabela. CEEB5, por exemplo, tem "Último pregão: 30/10/2026", e isso só está na ficha. Entre os líquidos do modo Iniciante há 1 caso (AMBP3, 30/10). | Baixa |

**Correções propostas**
- O robô passa a gravar `"fase": "intradiario" | "fechamento"` no painel.json (fechamento quando a coleta é feita depois do fim do pregão). Textos do selo:
  - em andamento: **"Pregão de 03/11 em andamento · preços das 17:07, com atraso da fonte. Mudam até o fechamento."**
  - fechado: **"Fechamento do pregão de 03/11/2026 · atualizado às 18:17"**
  - pregão terminou e o fechamento não chegou: **"Preços de 03/11 às 17:07, antes do fechamento. A atualização de fechamento ainda não chegou."**
- Dado velho: calcular o "último pregão esperado" (hoje, se for dia útil e já passar das 10h30; senão, o dia útil anterior) e comparar com `pregao_referencia`. Quando estiver atrasado, trocar o texto, não só a cor: **"⚠ Dados do pregão de 30/10/2026: a atualização automática atrasou. Os preços podem não ser os de hoje."** Pôr `role="status"` no `#live`.
- DEF "Preço": **"Último preço informado pela fonte (Yahoo Finance) no pregão de referência. Durante o pregão é o preço daquele momento, com atraso; depois do fechamento é o preço de fechamento."**
- Rodapé: trocar "fechamento diário" por **"preço do último negócio (durante o pregão) ou de fechamento"**.
- Na tabela, quando `p.data < pregao_referencia`, mostrar abaixo do preço: **"preço de 30/10"**.

## 2. Atualização automática (a cada 5 min)

Teste: Energia + "Abaixo do teto", fichas CMIG4 e TAEE11 abertas, R$ 2.500 digitados no simulador da CMIG4, página rolada até a ficha. Na resposta seguinte, `gerado_em` passou para 18:07, o preço da CMIG4 mudou e a TAEE11 virou "acima do teto". Avancei o relógio 5 min.

| Preservado | Não preservado |
|---|---|
| setor, filtro de situação, busca, modo, ficha CMIG4 aberta, valor do simulador (2500, via `simAmt`), rolagem (1327 para 1313 px a 1300; idêntica a 390) | **foco**: ia do campo do simulador para `BODY`. Quem está digitando perde o cursor, e quem navega por teclado ou leitor de tela volta ao topo da página |
| | a ficha da TAEE11 **sumiu sem aviso**: a linha saiu do filtro |
| | nenhum anúncio de que os números mudaram. O selo troca de horário em silêncio e um popover "?" aberto é fechado |

Gravidade: **Média-alta**. Durante o pregão a atualização acontece mesmo, de hora em hora, e foi o que se viu hoje.

**Correções:** antes de `render()`, guardar `document.activeElement` (id ou `data-t`) e devolver o foco depois. Se o foco estiver num `input`, adiar a renderização até o `blur`. Anunciar num `aria-live="polite"`: **"Dados atualizados às 18:07. Preços e situações podem ter mudado."** Se uma ficha aberta sair do filtro, avisar no mesmo lugar: **"TAEE11 saiu da lista com os filtros atuais."** Também: só fazer a busca automática em dia útil, das 10h às 18h30. Hoje o `no-store` baixa 144 KB a cada 5 min, 24 h por dia, em qualquer aba aberta.

## 3. Coerência entre Situação × Alertas × Qualidade (dados de hoje)

Não existe "Fortes + Abaixo do teto + Grave", porque o alerta grave força "Teto não se aplica". Existem outras combinações que confundem um iniciante:

1. **CPFE3 (CPFL)**: *Fortes ▮▮▮ + Abaixo do teto (+22,7%) + Atenção · 1* (Iniciante, 390 e 1300). Proventos de 2024 e 2025 = R$ 0,00, tendência −100% e DY 12m de 8,9%. O teto robusto (R$ 54,04) sai só de 2021 a 2023. O resumo diz "pagou em média R$ 1,97 … referência R$ 3,24", dois números muito diferentes sem explicação. A tela explica só no alerta: "Proventos quase zerados em 2024, 2025 … possível falha da fonte; confira no RI." Um "Abaixo do teto" que depende de um dado que o próprio painel acha errado aparece como um filtro limpo. **Alta.**
2. **BBAS3**: *Fracos ▮▯▯ + Abaixo do teto (+43%) + Atenção · 2*. Provento caiu 30% e DY 12m é 4,0% contra 8,1% de média. A ficha explica bem: os alertas e a nota sobre IFRS × Cosif. Mesmo assim, a margem de +43% em destaque na tabela puxa o olhar. Média.
3. **BBSE3 e SANB4**: *Fracos ⚠ + Abaixo do teto + "Nenhum alerta automático"*. "Nenhum alerta" ao lado de "Fracos" parece contradição. Na BBSE3 o "Fracos" vem do payout (vermelho), com ROE de 85,9% marcado como "forte": o pill diz fraco e a ficha mostra ROE forte. A nota da holding explica, mas só dentro da ficha. Média.
4. **EGIE3**: *Fortes ⚠ + Abaixo do teto (+10%) + Nenhum alerta*. Tendência de −23% (logo acima do gatilho de −25%) e DY 12m de 4,2% contra referência de 6,5%. É o tipo de linha que o juiz quis evitar como "filtro de compra". A nota provisória (lucro +107%) só aparece como ⚠ na tabela. Média.
5. **CEEB5, AFLT3, EQPA5/6/7, CEEB3, CLSC3 e BGIP3/4**: *Fortes ▮▮▮ + Grave: teto não se aplica*. O balanço é forte, mas o papel quase não negocia. Esses papéis ficam escondidos pelo filtro padrão de liquidez e aparecem quando o usuário desmarca o filtro (`1300_full_CEEB5_fortes_grave.png`). A ficha explica o grave, mas não diz que os dois sinais medem coisas diferentes. Baixa-média.

Extras do dia:
- **ENEV3** (Iniciante) e mais 11 papéis mostram o **Preço-teto robusto = "R$ 0,00"** ao lado de "Sem proventos". Lê-se como "o teto é zero". Média.
- Ordenar por **DY 12m** no Iniciante põe **BRBI11 (Grave)** em 1º, com 14,2%. Baixa-média.

**Redação proposta** (uma linha "Como ler estes sinais juntos" no topo da ficha, montada a partir da combinação):
- Abaixo + Fracos: **"O preço está abaixo do teto, mas o balanço está fraco. O teto supõe que a empresa continue pagando como pagou, e um balanço fraco torna isso menos provável."**
- Abaixo + Nenhum alerta + Fracos: **"Nenhuma regra de proventos disparou, mas a qualidade financeira é fraca. São verificações diferentes: uma olha os proventos e o preço, a outra olha o balanço."**
- Fortes + Grave: **"O balanço é forte, mas o preço-teto não serve para este código: [motivo]. Saúde da empresa e confiabilidade do preço são coisas diferentes."**
- CPFE3 (`lacuna_proventos` com status abaixo): situação **"Abaixo do teto · conferir dados"**, com o alerta reescrito: **"Proventos zerados em 2024 e 2025, embora a empresa tenha pago antes e depois: provável falha da fonte. O teto usou só 2021–2023. Confira no RI antes de usar este número."**
- Teto zero: mostrar **"–"** quando `status` for `sem_proventos` ou `historico_curto`.

## 4. Acessibilidade

O que funciona: Tab chega às linhas e Enter/Espaço abre a ficha (`aria-expanded` e o rótulo passa a "Fechar ficha"). O foco fica na linha depois de abrir e o próximo Tab vai ao simulador. O "?" abre com Enter, usa `aria-expanded`/`aria-describedby`, e Esc fecha e devolve o foco ao "?". A ordenação funciona pelo teclado e tem `aria-sort`. O contorno de foco é visível (2px âmbar). No modo escuro **todos os textos medidos passaram de AA**: o menor foi o link (5,79:1), seguido dos rótulos "Federal" (5,78:1) e "Sem nota" (6,0:1). No claro, o menor foi "Participação estatal" (4,57:1, limite).

Problemas:
- **Selo sem texto de estado nem `role`** (ver 1b). Alta.
- **33 paradas de Tab** antes da 1ª linha (guia, 5 setores, 9 filtros e 18 botões do cabeçalho), sem link "Ir para a tabela". Baixa-média.
- **390px**: o Iniciante mostra Empresa, Preço e DY 12m. **Alertas, Qualidade e Situação exigem rolar para o lado** (tabela de 878px numa área de 356px) e nada indica isso. O aviso grave pode passar despercebido. Média-alta.
- O cabeçalho da tabela não fica fixo na rolagem vertical (só a 1ª coluna fica fixa na horizontal). No meio de 40 linhas, os pills perdem o rótulo. Média.
- A linha focada é anunciada só como "CMIG4, Cemig. Abrir ficha" (o `aria-label` na `tr` esconde preço e situação). `aria-label` em `<span>` sem `role` (pill de qualidade) funciona no Chromium, mas o ARIA 1.2 desaconselha. Baixa.

Correções: link "Pular para a tabela"; `position:sticky; top:0` no `thead` (no desktop, abaixo da barra de filtros); no mobile, colocar Situação e Alertas logo depois de Empresa, ou um degradê lateral com o texto **"Deslize para ver alertas e situação →"**; tirar o `aria-label` da `tr` e pôr o botão de abrir na 1ª célula (`<button aria-expanded>`).

## 5. Desempenho

| | Local | 4G lento (1,6 Mbps, 150 ms) + CPU 4× |
|---|---|---|
| Tabela visível | 0,3 s | 2,5 s |
| painel.json | 144 KB (gzip ~20 KB) | chega aos 1,8 s |
| fundamentos.json | 69 KB (gzip ~6 KB) | 1,5 s |
| index.html | 56 KB (gzip ~19 KB) | |
| Troca de modo | 30–50 ms | 200–400 ms |

Sem erros de JS (só as fontes, que bloqueei de propósito). Está bom. Sugestões: mostrar "Carregando dados…" também no lugar da tabela e restringir a busca automática ao horário do pregão (seção 2).

---

## Prioridade sugerida
1. Selo e definição de "Preço": intradiário × fechamento (1a) e aviso de atraso em texto (1b, 1c).
2. "Abaixo do teto · conferir dados" quando há lacuna de proventos (CPFE3).
3. Atualização automática sem perder o foco, com anúncio.
4. Mostrar Situação e Alertas no mobile sem rolar para o lado; cabeçalho fixo.
5. Linha "Como ler estes sinais juntos"; "–" no lugar de R$ 0,00.

Fonte do horário da B3: https://www.jornaldocomercio.com/economia/2026/10/1268516-b3-amplia-horario-de-negociacao-ate-17h55-a-partir-de-3-11-com-fim-do-horario-de-verao-nos-eua.html
