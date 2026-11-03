# Monitor BESST · Fase 2 · Parecer dos juízes sobre a integração BETA (03/11/2026)

Juízes: **J1** dados e contabilidade · **J2** regulatório e comunicação (Res. CVM 20/2021) · **J3** engenharia e acessibilidade.
Insumos: `git pull` em `cb8f6d2` (commits `c76215a`, `253bde2` e `cb8f6d2`); página `carteiras/monitor-besst/index.html`; `dados/besst/fundamentos.json` (gerado em 03/11 07:06); `.github/workflows/fundamentos-besst.yml`; `scripts/fase2/{publicar.py, fundamentos_cvm.py, aceite.py}`; `docs/monitor-besst/fase2-fundamentos.md`. A página foi aberta com Playwright em 1300 px e 390 px, além de 1440 px e do tema escuro. Foram abertas as fichas de BBAS3, BBSE3, SAPR11, AMBP3, ABCB4, CXSE3 e MEGA3 (sem dado na CVM). As capturas estão em `/home/claude/work/times/capturas_beta/`. Nenhum arquivo do repositório foi alterado.

## 0. Veredito: **MANTER NO AR COMO BETA, COM AJUSTES OBRIGATÓRIOS** (prazo: próximo commit)

Os dados publicados estão coerentes com a 3ª rodada: o aceite está limpo, o BB, a SANB e a EGIE batem e o padrão contábil vem por papel. A trava de publicação existe e funciona. O avisos regulatórios estão completos. Não há motivo para retirar o painel do ar.

A integração, porém, trouxe **duas regressões visíveis**:
- a tabela "Outros códigos" ficou com as colunas trocadas;
- no desktop, a tabela do modo Iniciante passou a exigir rolagem lateral, o que esconde a coluna "Situação" e o ⚠ de nota provisória.

Há também lacunas em 4 das 9 ressalvas. Com os ajustes P0 abaixo, o beta fica conforme.

| Juiz | Nota | Comentário |
|---|---|---|
| J1 dados/contábil | 8,0 | Os dados estão corretos e o padrão aparece por papel. Faltam a nota de holding da CXSE e o aviso sobre lucro "regulatório" nas elétricas. "forte/fraco" aplicado ao payout confunde. |
| J2 regulatório/comunicação | 7,5 | O rodapé com a Res. CVM 20/2021 está correto. Os rótulos são descritivos e aceitáveis. Ordenar por "Qualidade" ao lado de "Abaixo do teto" cria uma lista com cara de triagem de compra, e a legenda precisa neutralizar isso. |
| J3 engenharia/a11y | 6,5 | O bloqueio do workflow está correto. Há regressão no `sibBox`, a tabela transborda no desktop, o contraste do selo BETA é insuficiente e textos crus de flag aparecem ao usuário. |
| **Média** | **7,3** | |

## 1. As 9 ressalvas

| # | Ressalva | Situação | Evidência e o que falta |
|---|---|---|---|
| 1 | Selo "BETA · dados em teste" com a data-base | **Cumprida** | O selo BETA aparece no cabeçalho da coluna ("Qualidade (beta)"), na ficha, na legenda, no passo 5, no cartão de método e no rodapé. A ficha diz "Dados até 30/06/2026" (BBAS3) e "31/12/2024" (AMBP3). Ressalva de a11y: o selo tem contraste de **3,5:1** (#B86E0C sobre #FBEFDC, 10,6 px), abaixo dos 4,5:1. |
| 2 | Lucro rotulado por padrão (IFRS/Cosif), "pode diferir do recorrente/ajustado/regulatório" e nota específica do BB | **Parcial** | A ficha mostra "Lucro (12 meses até 30/06/2026) · R$ 12,27 bi · IFRS consolidado" e o ABCB4 aparece como "Cosif individual". A nota do BB existe. Faltam três coisas: (a) o rótulo não diz "Lucro **contábil** … (CVM)" na própria linha; (b) **"regulatório" não aparece** em lugar nenhum, embora seja o caso das elétricas (TAEE, ISAE) e esteja na ressalva; (c) "IFRS", "Cosif" e "CPC" não são explicados para o iniciante. |
| 3 | Payout "do exercício 2025: proventos declarados ÷ lucro do mesmo padrão", pago em caixa, sem recompras e sem dividendos de reservas | **Parcial** | Aparece "declarado (DVA) 2025 · pago em caixa no ano: 48,8%", e o cartão de método explica a conta. Faltam: (a) a frase **"recompras e dividendos de reservas não entram"**, que não aparece em nenhum lugar; (b) "DVA" sem explicação; (c) o semáforo traduzido como **"forte/fraco" no payout** induz a erro: BBSE com 96,7% sai "fraco" e SAPR com 28,1% sai "forte". |
| 4 | ⚠ verificar com frase simples, ROE médio ao lado e nota provisória | **Parcial** | Na ficha aparecem "O lucro acumulado mudou -110% … pode haver efeito não recorrente. A nota é provisória." e "média de 2 exercício(s): 16,5%". A tabela mostra ⚠, e 32 papéis estão com nota provisória. Problemas: (a) **no desktop (1300 e 1440 px) o ⚠ e a coluna Situação ficam fora da área visível** (tabela de 1389 px num contêiner de 1206 px; antes da integração era 1206 = 1206); (b) as outras flags aparecem cruas: "Valor fora do usual, conferir: roe=85.9." (BBSE3) e "div liq_ebitda=-3.28" (TELB); (c) o cartão de método diz que só "lucro que variou mais de 60%" deixa a nota provisória, mas o código marca como provisória com **qualquer** `verificar:*` (payout = 100%, ROE alto, dívida negativa). |
| 5 | Holdings (BBSE, CXSE): ROE não comparável | **Parcial** | Há texto para a BBSE. **A CXSE não tem nota** e aparece com "Indicadores fortes ▮▮▮" e ROE de 32,5%. `NOTA_EMP` só tem BBSE e BBAS. |
| 6 | "Sem nota" sempre com motivo, nunca nota 0 por falta de dado | **Cumprida (com ajuste)** | AMBP3 mostra "Sem nota: o último balanço entregue à CVM tem mais de 15 meses." Todo `nota=null` com dados tem `motivo_sem_nota`. Ajustes: (a) papéis sem cadastro na CVM (MEGA3, CSRN, COMR etc., visíveis ao desmarcar os filtros) mostram texto técnico: "nenhum código de negociação no FCA dos últimos 3 anos (deslistado? incluir no CSV manual)"; (b) na tabela, o motivo fica só no `title` (inacessível no toque e no leitor de tela); (c) o AMBP3 sem nota ainda mostra "Dívida líquida/EBITDA 2,46x **forte**" com dado de 23 meses. |
| 7 | Rodapé fixo com Res. CVM 20/2021 e faixas como convenção | **Cumprida** | "Este painel é material educativo e não constitui recomendação de investimento nem relatório de análise nos termos da Resolução CVM 20/2021. As faixas e notas são convenções do painel." |
| 8 | Documento: payout "declarado no exercício (DVA)" e sem "destrói valor" | **Cumprida** | A tabela da §2 foi corrigida e a nota de calibragem diz "fica abaixo do custo de capital típico do setor". Não sobrou "pagos 12m" nem "destrói". |
| 9 | Produção não publica com teste falho, contador "(meta 0)" diferente de 0 ou meta mínima não atingida | **Cumprida** | O passo de testes não tem `continue-on-error`. `publicar.py` sai com código 1 se algum `(meta 0)` não estiver vazio, se uma das 4 metas mínimas não for atingida ou se houver `papeis_com_excecao`, e nesse caso o commit não roda. A chave ausente vale 0 e bloqueia (falha segura). Observações para o próximo ciclo: `erros` não está em `CAMPOS`, então não é publicado; `erros += LOG["downloads_falhos"]` anexa a lista **global e acumulada** a cada papel; uma publicação bloqueada não gera aviso na página além da data "gerado em". |

**Placar: 4 cumpridas (1, 7, 8, 9), 1 cumprida com ajuste (6), 4 parciais (2, 3, 4, 5), nenhuma descumprida.**

## 2. Linguagem (recomendação de compra ou venda?)

- **"Indicadores fortes/mistos/fracos/muito fracos"** descrevem o balanço, não a ação, e são aceitáveis. Nenhum texto fala em comprar, vender, "oportunidade" ou "barata".
- **As barras ▮▮▯** lembram estrelas de *rating* de analista. São aceitáveis só porque o rótulo vem escrito e as barras têm `aria-hidden`. Não usar barras sem texto.
- **Risco real: a combinação.** Ordenar por "Qualidade (beta)" põe no topo "Indicadores fortes ▮▮▮ · Abaixo do teto" (CMIG4, TAEE11, ISAE4, CPFE3), o que funciona como um filtro de compra pronto. A legenda e o passo 5 precisam dizer que a soma das duas colunas também não é sinal de compra.
- O passo 5 diz "Um preço baixo com indicadores fracos pede investigação". O leitor pode inferir o inverso (preço baixo + fortes = bom). Completar a frase.
- O payout "forte/fraco" é linguagem de juízo onde deveria haver uma faixa (ver ressalva 3).
- O `DEF._q` diz "0–1 = fracos", mas o rótulo da nota 0 é "muito fracos". É inconsistente.

## 3. Acessibilidade e celular

- 390 px: sem rolagem horizontal da página, a ficha de qualidade empilha bem (grade de 2 colunas) e o tema escuro está OK.
- Enter na linha abre a ficha, e o "?" da coluna abre a explicação.
- **Desktop: a tabela do Iniciante transborda** (ver ressalva 4a). O `white-space:nowrap` da pílula `.q` com o rótulo longo é a causa.
- ⚠ provisória: está como `<span aria-label="provisória">⚠</span>` sem `role`, e o leitor pode ler só "aviso". Usar texto visualmente oculto.
- Selo BETA com contraste de 3,5:1 (precisa de ≥ 4,5:1).
- O motivo do "Sem nota" fica só em `title`.

## 4. Bugs

| ID | Gravidade | Bug |
|---|---|---|
| B1 | **Alta (regressão)** | `sibBox` foi corrompido no commit `cb8f6d2`, numa troca `</td>`→`</span>` aplicada no lugar errado. O preço vai para a coluna "Classe", o "Preço" mostra o DY (1,8%), o "DY 12m" mostra a liquidez ("R$ 70,9 mi") e a coluna Liquidez fica vazia. Afeta toda empresa com mais de um código (captura `*_irmaos_SAPR11.png`). |
| B2 | **Alta** | Tabela Iniciante com 1389 px num contêiner de 1206 px no desktop. Ficam ocultos a coluna Situação e o ⚠ (captura `desk_tabela_iniciante_transborda.png`). |
| B3 | Média | O guia diz "Como ler este painel em **4 passos**", mas agora são 5. |
| B4 | Média | Flags cruas na ficha: `roe=85.9` e `div liq_ebitda=-3.28` (o `replace("_"," ")` só troca o 1º "_" e mantém o ponto decimal). |
| B5 | Média | Falta a nota de holding da CXSE. |
| B6 | Baixa | O rodapé diz "Dados financeiros até 30/09/2026" (máximo do arquivo), mas 93 papéis estão em 30/06/2026 e alguns em 2023/2024. |
| B7 | Baixa | O cartão de método fala em "lucro >60%" como único gatilho da nota provisória. |
| B8 | Baixa | `DEF._q` incoerente com `QL[0]`. |
| B9 | Baixa | Ficha sem nota por dado antigo ainda mostra "forte/fraco" nos indicadores. |
| B10 | Baixa (próximo ciclo) | `erros` não é publicado e é acumulado globalmente por papel. |

## 5. Ajustes obrigatórios, em ordem de prioridade (o trecho exato quando é texto)

**P0 (antes do próximo publish)**
1. **B1 `sibBox`**: trocar `${classe(x.ticker)}</span><span class="c">${brl(x.preco)}</td>` por `${classe(x.ticker)}</td><td>${brl(x.preco)}</td>`, e `${liq(x.liquidez_mil)}</span></div>` por `${liq(x.liquidez_mil)}</td></tr>`.
2. **B2 transbordo**: na tabela, usar rótulo curto (`QL_CURTO=["Muito fracos","Fracos","Mistos","Fortes"]`) e manter o longo na ficha, ou tirar o `white-space:nowrap` de `.q`. Critério: a tabela cabe em 1206 px no modo Iniciante.
3. **Ressalva 5 (CXSE)**: acrescentar a `NOTA_EMP` `CXSE:"A Caixa Seguridade é uma holding: o patrimônio é pequeno perto do lucro que recebe das participadas, por isso o ROE fica alto e não é comparável ao de uma seguradora."` e, na BBSE, trocar "Compare com cuidado." por "Não é comparável ao ROE de uma seguradora."
4. **Ressalva 3 (payout)**: na ficha, trocar `" · "+esc(f.base_payout)` por `" · proventos declarados sobre o lucro de 2025 (demonstração do valor adicionado); recompras e dividendos pagos de reservas não entram"`. Para o payout, trocar o `SEM` "forte/intermediário/fraco" por `{verde:"dentro da faixa",amarelo:"atenção",vermelho:"fora da faixa",cinza:"sem dado"}`.
5. **Ressalva 2 (rótulo)**: trocar `<b>Lucro (` por `<b>Lucro contábil (`; trocar `esc(f.padrao||"")` por `esc(f.padrao||"")+", CVM"`; no rodapé da ficha, trocar "pode diferir do lucro recorrente ou ajustado do release" por "pode diferir do lucro recorrente, ajustado ou regulatório divulgado pela empresa". Acrescentar ao cartão de método: "IFRS é o padrão contábil internacional; Cosif é o padrão do Banco Central para bancos."
6. **B4 flags cruas**: trocar ``avisos.push(`Valor fora do usual, conferir: ${…}`)`` por frases fixas: `roe` → "ROE muito acima do usual: confira se a empresa é holding ou teve ganho pontual."; `div_liq_ebitda` negativo → "Empresa com mais caixa do que dívida (dívida líquida negativa)."; `payout` → "Payout acima de 100%: distribuiu mais do que lucrou."
7. **B3**: "Como ler este painel em 4 passos" → "Como ler este painel em 5 passos".
8. **Legenda (linguagem)**: trocar "qualidade financeira pelo balanço entregue à CVM (não é recomendação)" por "qualidade financeira pelo balanço entregue à CVM. Indicadores fortes, mesmo com preço abaixo do teto, não são sinal de compra". No passo 5, trocar "Um preço baixo com indicadores fracos pede investigação." por "Um preço baixo com indicadores fracos pede investigação; indicadores fortes não garantem bom investimento."

**P1 (até a próxima rodada)**
9. Cartão de método: trocar "Lucro que variou mais de 60% em um ano deixa a nota **provisória**." por "Lucro que variou mais de 60% em um ano, ou outro valor fora do usual, deixa a nota **provisória**."
10. `DEF._q`: "0–1 = fracos" → "1 = fracos, 0 = muito fracos".
11. Rodapé: trocar ``Dados financeiros até ${…}`` por "Data-base varia por empresa (veja a ficha); a mais recente é ${…}".
12. Papéis com `erro`: em vez do motivo técnico, mostrar "Não encontramos este código nos cadastros da CVM (pode ter deixado a bolsa)." (o motivo técnico fica só no JSON).
13. A11y: ⚠ com `<span class="sr-only">nota provisória</span>`; selo BETA com contraste ≥ 4,5:1 (texto mais escuro, ex. #8A4F00); "Sem nota" com o motivo em texto visível na ficha (já existe) e também em `aria-label` na tabela.
14. Sem nota por dado antigo: omitir as palavras "forte/fraco" (mostrar só o número).
15. Frase de variação: "-110%" → "caiu 110% (passou de lucro a prejuízo)" quando o sinal muda.

**P2 (próximo ciclo, herdado da 3ª rodada)**: publicar `erros` por papel (só os downloads que afetaram o papel), aviso na página quando a rotina for bloqueada (ex.: `gerado_em` com mais de 3 dias → "atualização em pausa"), o resto da seção 5 do parecer anterior.

## 6. Divergências
- J2 queria trocar "Indicadores fortes/fracos" por "3 de 3 na faixa verde". J1 e J3 acham o rótulo atual mais claro para o iniciante. *Prevalece manter o rótulo, com a frase de legenda do item 8.*
- J3 propôs retirar do ar até corrigir B1/B2. J1 e J2: B1 e B2 são de apresentação e não afetam o dado de qualidade. *Prevalece manter o beta no ar, corrigindo P0 no próximo commit.*
