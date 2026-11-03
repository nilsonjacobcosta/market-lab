# Monitor BESST · Fase 2 · Parecer dos juízes, 3ª rodada (03/11/2026)

Juízes: **J1** dados e contabilidade · **J2** regulatório e comunicação (Res. CVM 20/2021) · **J3** engenharia.
Insumos: `git pull` em `9dcde7f`; `scripts/fase2/{fundamentos_cvm.py, aceite.py}`, `tests/test_fase2.py`, `.github/workflows/fase2-teste.yml`, `dados/besst/fase2_teste/*` (incluindo `log_execucao.json` → `conferencia`) e `docs/monitor-besst/fase2-fundamentos.md`. Os 8 testes rodaram localmente sem falha (`OK`). Nenhum arquivo do repositório foi alterado.

## 0. Veredito: **(b) APROVADO COM RESSALVAS. Integração como "beta" permitida**

Os cinco P0 da 2ª rodada foram tratados no código. A meta de lucro (A4) fecha em **12/12 contra a fonte primária** (linha da DFP/ITR da CVM), com **zero divergência sem explicação**. Em 5 dos 12 há também corroboração externa independente. Os contadores de violação do aceite estão todos em 0. O que falta são ajustes de **rótulo** (bancos IFRS × Cosif), de **nota com possível efeito não recorrente**, de **texto do documento** e de **rastreabilidade de erros**. Nada disso exige refazer a coleta, por isso o veredito sai de (c) para (b).

| Juiz | Nota | Comentário |
|---|---|---|
| J1 dados/contábil | **8,0** | A captura bate com a linha da CVM em 12/12, e EGIE, CPLE e SANB ficam explicados. Ressalvas: bancos IFRS × Cosif e verde puxado por não recorrentes. |
| J2 regulatório/comunicação | **7,5** | Os §§ 3º–4º do art. 202 estão corretos. A tabela do documento ainda diz "pagos 12m" e "destrói valor", e o caso BB (IFRS 13,7 bi × Cosif 17,8 bi) exige aviso explícito. |
| J3 engenharia | **7,5** | Trava `startswith` corrigida e testada, try por papel, testes no CI antes da coleta. Ressalvas: `erros[]` nunca é preenchido, a falha forçada não exercita o caminho crítico e os fixtures são sintéticos. |
| **Média** | **7,7** | (2ª rodada: 6,3) |

## 1. Correções no código

| P | Correção | Situação | Evidência e bug remanescente |
|---|---|---|---|
| P0-1 | Trava de dado antigo | **OK** | `nota()` usa `any(f.startswith("dado_antigo"))` (l. 263), há teste (`test_dado_antigo_fica_sem_nota`), e o aceite mede `nota_com_dado_antigo = []` sobre o **universo inteiro** (`todos`). AMBP3, BSLI, UPKP3, LIPR3, BPAN4 e BRGE ficam sem nota. |
| P0-2 | Métrica descartada → sem nota; payout 100% | **OK** | `descartados` → `sem_nota:metrica_fora_da_faixa_plausivel` (CEBR3 agora `None`). `abs(payout−100)<0,5` → `verificar` (SANB, EKTR). `payout_caixa` exposto. **Remanescente:** SANB tem `payout_caixa = None` (a DFC do banco não casa com a regex), e por isso o contraponto falta justamente onde mais seria útil. |
| P0-3 | A4 contra fonte primária | **OK** | Seção 2. |
| P0-4 | LTM coerente | **OK, com 2 ressalvas menores** | `atual` exige `ano == DFP+1` (l. 369), `trims = itr[(cd, tipo)]` usa a mesma visão e a base de lucro é igual nas 3 peças (l. 380). Ressalvas: (a) se o ITR só existe na **outra** visão, `atual = None` e o papel cai no exercício fechado **sem flag** (a defasagem ≤15m esconde o caso); (b) `bant` (PL inicial do exercício) e o `roe_medio_exercicios` podem misturar visões entre anos (`por_ano` escolhe a visão por ano). Hoje nenhum dos 12 é afetado. |
| P0-5 | Testes + `erros[]` + try por papel | **Parcial** | Os 8 testes rodam no CI **antes** da coleta (passo sem `continue-on-error`, então uma falha bloqueia). O try por papel grava `erro: excecao`. **Mas:** (i) `erros = []` (l. 365) nunca é preenchido, e uma falha de download não aparece no `fundamentos.json`. Só vai para o `--log`, que a execução forçada **nem passa**; (ii) a falha forçada derruba a DFP **2024**, que não está no caminho crítico (0 notas mudam entre as duas execuções), e por isso não prova a robustez de quando falta a DFP 2025 ou o ITR 2026; (iii) os fixtures são sintéticos "no formato real". Faltam o leiaute de seguradora (3.13.01, BBSE), o de banco (3.09.01, ITUB/SANB/BPAC) e testes de `processar()` (regra ano+1, visão diferente). |
| P1 | Variação do lucro > ±60% | **OK, mas sem efeito na nota** | São 34 papéis com `verificar` (SAPR, EGIE, LIGT, VBBR, AXIA, ENGI, COCE, PINE, BMEB…). O alerta compara acumulado com acumulado (e não LTM com exercício). É aceitável. **Problema:** a flag não muda a nota. Oito papéis ficam com **nota 3** apoiados em ROE inflado por não recorrente: EGIE (29%, UBP), VBBR (+333%), BMEB (32%), PINE (40,7%), COCE (+306%). |
| P1 | ROE médio dos exercícios | **OK** | `roe_medio_exercicios` + `roe_medio_n`. Ex.: EGIE 32,0, SAPR 16,5 (LTM 3,8), BBAS 11,3 (LTM 6,7). |
| P1 | Sem cotação → sem nota | **OK** | Nota calculada e depois anulada com `sem_nota:sem_cotacao`; o aceite mede `nota_sem_cotacao = []`. Os deslistados (AESO, ELPL, OMGE, BPAN) continuam no universo, mas sem nota. Aceito para o beta. |
| P1 | Arredondamento | **OK** | `int(3*pts/len+0,5)`. |
| P1 | Doc sem FCF yield | **Parcial** | O FCF saiu, mas a tabela da seção 2 **ainda** define payout como "Dividendos+JCP pagos 12m" (o código usa o declarado na DVA do exercício) e a nota de calibragem ainda diz "ROE < 10% destrói valor". A seção "Atualização" corrige no texto, mas a tabela contradiz. |

## 2. Conferência do lucro (A4: ≤ 2% do lucro contábil dos controladores em ≥ 10 de 12)

Método: o valor usado no teste (`componentes_lucro`) foi comparado com a linha "atribuído a sócios da empresa controladora" da DFP 2025 e do ITR acumulado de 2026, publicada pela CVM (o `conferencia` traz a linha bruta, com código e descrição). Onde foi possível, também com o release ou com as DFs publicadas. **Limite:** o `conferencia` é gerado pelo mesmo leitor de CSV. Ele prova que a **linha certa** foi escolhida, mas não é uma fonte 100% independente. Por isso a coluna "externa" importa.

| Emissor | Teste (R$ mi) | Linha CVM (código) | Fonte externa (tipo) | Situação |
|---|---|---|---|---|
| EGIE | 2025: 2.582,8; 1S26: 2.661,5 | 3.11.01 = 2.582,8; 3.11 total = 2.857,9; ITR 3.11.01 = 2.661,5 | Total 2025 de **2.858** e proventos propostos de 1.377 ([Times Brasil](https://timesbrasil.com.br/empresas-e-negocios/engie-lucra-r-727-milhoes-no-quarto-trimestre-e-anuncia-dividendos-bilionarios-veja-valor/), imprensa) | **✔ 0%.** O −9,4% da rodada 2 era total × controladores (275,1 de minoritários). O DVA de 1.377 é igual aos proventos propostos, o que valida o payout de 53,3%. |
| CPLE | 2025: 2.688,6; 1S26: 1.683,2 | 3.11.01 = 2.688,6 / 1.683,2; 3.11 1S26 = 1.741,5 | O release 2T26 traz 1.741,5 (total) (RI, rodada 2) | **✔ 0%.** O −3,4% eram os minoritários (58,3). Resolvido. |
| CMIG | LTM 4.595 | 3.11.01 = 4.897,4 / 1.923,6 | LTM 4.597 ([release 2T26](https://ri.cemig.com.br/docs/Cemig-2026-06-30-THtJzCB9.pdf), RI) | **✔ 0%** |
| BBSE | 2025: 9.017,3 | 3.13.01 = 9.017,3 | Recorrente 9.084 ([release 4T25](https://api.mziq.com/mzfilemanager/v2/d/d4ee6df5-1dd8-4fb5-b518-e05397c304e4/cc0a8ff6-10e9-026c-7412-d43ce1c3d9a3?origin=2), RI) | **✔** CVM; −0,7% contra o recorrente (o release não traz o contábil IFRS 17) |
| BPAC | 2025: 16.006,0; 1S26: 9.663,3 | 3.09.01 = 16.006,0 / 9.663,3 | 1S25 bate (−0,1%); 1S26 +2,0% contra o "contábil" dos [destaques 2T26](https://static.poder360.com.br/uploads/2026/08/destaques-BTG-2trimestre-11ago2026.pdf) (cópia do release) | **✔** CVM; a diferença no 1S26 é de padrão (IFRS × Cosif) |
| BBDC | 2025: 23.672,7; 9M26: 19.647,9 | 3.11.01 = 23.672,7 / 19.647,9 | Contábil Cosif 2025 **24.550**; recorrente 24.652 ([Relatório 4T25](https://static.poder360.com.br/2026/02/Bradesco_Relatorio-de-Analise-Economica-e-Financeira_4T25.pdf), release do emissor, cópia no Poder360) | **✔** CVM; −3,6% contra o Cosif: **padrão contábil**, não erro |
| BBAS | 2025: 13.698,1; 1S26: 4.794,8 | 3.11.01 = 13.698,1 / 4.794,8 | Cosif 2025: controladores **17.808,0**, total 21.134,1 ([DFs publicadas, Correio Braziliense 26/03/26](https://edicao.correiobraziliense.com.br/correiobraziliense/2026/03/26/1353e9/pdf/A08-ECO-2603-DIG.pdf)); ajustado 20.685 ([release 4T25](https://static.poder360.com.br/2026/02/Banco-do-Brasil-4T25.pdf)) | **✔** CVM; −23% contra o Cosif. A DFP consolidada da CVM é **IFRS** e o "contábil" do release é Cosif. **É o maior risco de confusão.** |
| ITUB | 2025: 44.857; 1S26: 23.615 | 3.09.01 = 44.857 / 23.615 | Só o recorrente gerencial, 46.830 ([comunicado 4T25](https://filemanager-cdn.mziq.com/published/42787847-4cf6-4461-94a5-40ed237dca33/a4220edc-816e-4a88-a314-cae9614d2b1d_itau_unibanco_holding_s.a..pdf), RI) | **✔** CVM; −4,2% contra o recorrente (definição) |
| SANB | 2025: 12.766,0; 9M26: 8.896,1 | 3.11.01 = 12.766,0; ITR 3.09.01 = 8.896,1 | Só o gerencial nos releases | **✔** CVM. A DVA confirma: JCP 7.620 + dividendos 5.146 = 12.766 |
| TAEE | 2025: 1.579,9; 1S26: 920,8 | 3.11.01 = 1.579,9 / 920,8 | A imprensa só traz o regulatório | **✔** CVM (IFRS ≠ regulatório: definição) |
| ISAE | 2025: 2.447,9; 1S26: 1.297,7 | 3.11.01 = 2.447,9 / 1.297,7 | 1T26 IFRS 609,1 conferido na rodada 2 ([release 1T26](https://www.isaenergiabrasil.com.br/documents/90/Release_de_Resultados_1T2026_-_ISA_ENERGIA_BRASIL.pdf), RI); a imprensa traz "1,625 bi" em 2025 sem dizer o padrão | **✔** CVM |
| EKTR | 2025: 958; 9M26: 507 (total, individual) | 3.11 = 958 / 507 (sem quebra) | Não buscada | **✔** CVM; a DVA dá 111 + 847 = 958 = lucro, retidos 0 |

**Placar A4: 12/12 ✔ contra a fonte primária (CVM), 0 divergência sem explicação.** Há corroboração externa no mesmo conceito ou no total em 5 (EGIE, CPLE, CMIG, BBSE, BPAC 1S25). As diferenças contra os releases dos bancos são **de padrão** (IFRS consolidado na CVM × Cosif ou recorrente no release), e a do BB está documentada com as DFs Cosif publicadas. A aritmética do LTM confere em todos (ex.: EGIE 2.582,8 + 2.661,5 − 1.285,0 = 3.959,3). Fora do A4, continuam válidos ABCB, SAPR, VIVT, EQTL e PINE (rodada 2). **Meta atingida.**

**Achados do orquestrador:** EGIE **confirmado** (definição, não erro). SANB e EKTR **confirmados quanto à captura**: a DVA declara de fato JCP + dividendos iguais ao lucro dos controladores. No SANB os "lucros retidos" (199,1) são iguais à parcela dos não controladores, o que indica que o banco classificou a sobra dos minoritários nessa linha. É coerente com 100% de distribuição sobre o IFRS. Como os JCP anunciados em 2025 somam valores dessa ordem, o dado é plausível. Manter "verificar" e mostrar a frase de payout alto.

## 3. Achados novos desta rodada

1. **Bancos misturam padrões.** BBAS, ITUB, BBDC, SANB, BPAC, BRSR, BMEB, PINE e outros usam a consolidada da CVM (**IFRS**). ABCB, BAZA, BGIP e BNBR usam a individual (**Cosif**). Dentro do mesmo setor, o ROE de cada um vem de um padrão diferente. O BB sai com ROE de 6,7% (IFRS) enquanto o mercado fala em ROE ajustado de dois dígitos.
2. **Verde apoiado em não recorrente.** Oito papéis têm nota 3 com `verificar:variacao_lucro` (EGIE, VBBR, BMEB, PINE, COCE).
3. **`erros[]` vazio por construção** e **falha forçada fora do caminho crítico** (seção 1, P0-5).
4. **Payout dos bancos:** o BB tem 38,1% sobre o IFRS, contra cerca de 29% sobre o Cosif e 25% sobre o ajustado do release. Rotular a base.

## 4. O que a tela precisa mostrar (ressalvas obrigatórias para o beta)

1. Selo **"BETA · dados em teste"** no bloco de fundamentos, com a data-base ("dados até 30/06/2026" ou "30/09/2026").
2. Rótulo do lucro **por padrão**: "Lucro contábil **IFRS** (consolidado, CVM)" ou "Lucro contábil **Cosif** (individual, CVM)", 12 meses até dd/mm/aaaa. Em bancos e elétricas, acrescentar: "pode diferir do lucro recorrente/ajustado/regulatório do release". No BB, nota específica: "no padrão do Banco Central (Cosif) o lucro de 2025 foi maior".
3. **Payout:** "do exercício 2025: proventos declarados ÷ lucro contábil do mesmo padrão". Mostrar o pago em caixa quando existir. Recompras e dividendos de reservas não entram.
4. **⚠ verificar (cinza)** com frase simples: "possível efeito não recorrente: lucro variou X% no ano", mostrando o **ROE médio dos exercícios** ao lado. Nos papéis com essa flag, a nota aparece como **"provisória"**. Recomendado para o próximo ciclo: calcular a cor do ROE pelo menor entre o ROE LTM e o ROE médio.
5. Holdings (BBSE, CXSE): "ROE de holding com patrimônio pequeno, não comparável ao de seguradora".
6. **"Sem nota"** sempre com o motivo (dado desatualizado, sem cotação, métrica fora da faixa plausível, lucro indisponível), nunca nota 0 por falta de dado.
7. Rodapé fixo: "Material educativo. Não é recomendação de investimento (Res. CVM 20/2021). Faixas de cor são convenções do painel, não normas."
8. **Documento:** antes de ligar a tela, corrigir a tabela da seção 2 (payout = "declarado no exercício, DVA") e trocar "destrói valor" por "fica abaixo do custo de capital típico".

**Integração como beta:** permitida, se os itens 1 a 8 estiverem na tela e o workflow de produção **não publicar** quando os testes unitários falharem ou quando algum contador do aceite for diferente de 0 (o aceite atual roda com `continue-on-error`; na produção, deve bloquear).

## 5. Correções para o próximo ciclo (não bloqueiam o beta)

- **P1:** preencher `erros[]` (download falho que afetou o papel, LTM recusado) e gravar `downloads_falhos` dentro do JSON de saída; fazer a falha forçada atingir a **DFP do último ano** e o **ITR corrente**, e exigir no aceite que os afetados saiam com flag.
- **P1:** fixtures reais (BBSE 3.13.01, bancos 3.09.01, SAPR/ABCB individual, SANB DVA) e testes de `processar()` (regra ano+1, ITR só na outra visão → flag).
- **P1:** flag quando o ITR existe só na outra visão; visão única para o PL inicial e o ROE médio.
- **P2:** capturar o pago em caixa dos bancos (DFC do SANB); tirar do universo os deslistados (AESO, ELPL, OMGE, BPAN).

## 6. Divergências entre juízes
- **J1** queria a nota limitada a 2 quando houver `verificar:variacao_lucro`. **J2** aceita "nota provisória + ⚠" para o beta. **J3** condiciona o beta ao bloqueio do workflow por aceite ≠ 0. *Prevalece (b), com as ressalvas da seção 4.*

Fontes externas desta rodada: releases e DFs dos emissores (RI ou cópias integrais), mais uma reportagem (Times Brasil) para o total da EGIE. Não foram usados vídeos nem a AGF.
