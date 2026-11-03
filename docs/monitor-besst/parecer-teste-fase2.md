# Monitor BESST · Fase 2: parecer dos juízes sobre o TESTE REAL (02/11/2026)

Juízes: **J1** finanças/contabilidade · **J2** proteção ao investidor (ótica CVM, Res. CVM 20/2021) · **J3** engenharia de dados.
Insumos: `scripts/fase2/fundamentos_cvm.py`, `scripts/fase2/diagnostico_cvm.py`, `dados/besst/fase2_teste/{fundamentos,diagnostico}.json`, logs, `painel.json`, parecer anterior (`work/times/juizes.md`) e `docs/monitor-besst/fase2-fundamentos.md`. Nenhum arquivo do repositório foi alterado.

## 0. Veredito

**NÃO VAI para o painel público.** O teste foi útil: confirmou as colunas reais da CVM, e o núcleo da extração (lucro, PL, LTM) acerta em vários emissores. A Cemig bate em 0%; Itaú, Bradesco e Santander ficam a 4–5% do lucro recorrente, o que é diferença de definição. Mas ainda há quatro problemas:
1. A cobertura é de 55% dos papéis e 60% dos emissores (51/85). Só 45% dos papéis recebem nota.
2. Há erros grosseiros visíveis. ABCB4 aparece com dado de 2023 e lucro 0. LIGT3 e RNEW3 levam nota 0 por um lucro "0,0". OIBR3 tem ROE de +105% com PL negativo. EQTL3 tem payout de 516%.
3. O payout soma os proventos pagos aos **não controladores**. A própria DFP do BB prova isso.
4. Pendências do parecer anterior seguem abertas (PL médio, fallback silencioso do LTM, download, art. 202, rótulos).

Nota dos juízes para o script no estado atual: **J1 5 · J2 3 · J3 5 → 4,5** (antes 3,5).

## 1. Pendências do parecer anterior: o que o teste confirmou ou refutou

| Pendência | Situação | Evidência |
|---|---|---|
| Colunas do FCA não testadas | **RESOLVIDA** | `fca_cia_aberta_valor_mobiliario_AAAA.csv` tem `CNPJ_Companhia` e `Codigo_Negociacao` (ex.: BBAS3, VIVT3, TAEE3, BBSE3, SAPR3). Cadastro: `CNPJ_CIA`, `SIT`, `CD_CVM` confirmados. `ORDEM_EXERC` vem acentuado ("ÚLTIMO"/"PENÚLTIMO") e `norm()` trata corretamente. |
| Colunas de `composicao_capital` | **BUG NOVO CONFIRMADO** | O CSV **não tem `CD_CVM`** (só `CNPJ_CIA`). `acoes_emitidas()` filtra por `CD_CVM` e devolve sempre `{}`. Resultado: **FCF yield nunca é calculado**, e Telecom fica só com DL/EBITDA + payout. |
| Nota 0 com lucro desconhecido | **CONFIRMADA (pior que o previsto)** | O código ainda faz `(m.get("ll") or 0) <= 0 → 0`. Além disso, aparecem **5 emissores com lucro exatamente 0,0** (ABCB, GEPA, LIGT, RNEW, RIOS), o que é sintoma de conta errada. LIGT3/RNEW3/RNEW4/RNEW11 recebem **nota 0** por isso. |
| PL médio misturando datas | **CONFIRMADA** | Com o LTM em 30/06/2026, `pl_med` faz a média do PL de 30/06/2026 com o de 31/12/**2024** (`b_ant` vem de `anos_cd[-2]`), 18 meses antes. O correto é o PL do início da janela (30/06/2025) ou a média dos 5 trimestres. |
| Payout: caixa ÷ competência | **CONFIRMADA + agravada** | Além do descasamento de exercícios, `somar(r"dividend|juros sobre capital", prefixo="6.03")` soma todas as linhas. Na DFP 2025 do BB: 6.03.04 "pagos aos acionistas **controladores**" R$ 6,68 bi + 6.03.05 "pagos aos **não controladores**" R$ 2,69 bi. O payout 2025 sairia 68% em vez de 49%. Isso explica os outliers EQTL3 516%, CEBR 225%, AESO3 123%, WIZC3 121%, REDE3 118% e ENGI 106% (holdings com controladas que têm minoritários; CEBR também paga reservas de venda de ativos). Somar todos os níveis também pode contar em dobro quando há subtotal mais detalhamento. |
| Falha de download derruba a execução | **CONFIRMADA (no código)** | O download da DFP (linha 240) e o do cadastro não têm `try`. O teste não falhou, mas o risco segue igual. |
| `ltm()` volta ao anual em silêncio | **CONFIRMADA** | Basta faltar uma conta no ITR para o campo virar o valor de 2025, enquanto `base="LTM"` continua marcado. Payout e EBITDA podem misturar períodos sem aviso. |
| Art. 202 da Lei 6.404 impreciso | **ABERTA** | O doc ainda diz "mínimo obrigatório de 25%". Correto: se o estatuto é omisso, 50% do lucro líquido ajustado. Se o estatuto for alterado para fixar o dividendo, o piso é de 25%. Há exceções (§§ 3º–4º). |
| Rótulos com cara de recomendação | **ABERTA** | A matriz do doc mantém "Oportunidade a estudar", "Evitar / acompanhar" e "Possível armadilha". |
| Limites de sanidade | **AUSENTES** | ROE +105% em OIBR (lucro negativo ÷ PL negativo), ROE 42% em PINE, payout 516%. Nada é barrado. |

## 2. Cobertura: por que 65 papéis ficaram "sem dados CVM"

São 65 papéis = **34 emissores** de 85. Há duas causas distintas.

### 2a. Os 16 emissores com CD_CVM achado e nenhuma demonstração (31 papéis)
BAZA, BGIP, BMIN, BNBR, BPAR, RPAD (bancos); AFLT, CBEE, CEEB, CEED, COCE, EKTR, ENMT (energia); **SAPR**, CASN (saneamento); TELB (telecom).

**Causa (alta confiança):** `carregar()` lê só `BPA_con`, `BPP_con`, `DRE_con` e `DFC_*_con`. Empresa **sem controladas não entrega DF consolidada**, só a individual (`_ind`), e então `anuais` fica vazio para o CD_CVM. A prova está no próprio diagnóstico: o cadastro devolve o CD_CVM 18627 da Sanepar, mas `contas_dfp2025_referencia` (que varre só `*_con_*`) traz BBAS, VIVT e BBSE e **nenhuma linha da Sanepar**. Distribuidoras isoladas (Coelba, Coelce, Elektro, EMT, Ampla, CEEE-D), bancos estaduais/regionais (Banpará, Banese, BNB, Basa, Mercantil, Alfa) e Casan/Telebras seguem o mesmo padrão.
*Correção:* por CD_CVM e por documento, usar `_con` quando existir e, se não existir, `_ind`, registrando `visao: "individual"`. Nunca misturar as duas visões no mesmo emissor.
Observação: no diagnóstico, a TAEE não aparece em `cd_cvm_referencia` porque a busca foi pelo nome "Taesa" e a razão social é "Transmissora Aliança…". Isso é limitação do diagnóstico, não da produção: o mapa via FCA achou o CD 20257.

### 2b. Os 18 emissores sem CD_CVM (34 papéis)
APER, BPAC, BPAN, BRGE, BRIT, BRIV, CEPE, COMR, CSAB, CSRN, EEEL, ELPL, EQPA, IGSN, LIPR, MEGA, OMGE, UPKP.

Causas possíveis no código (sem internet não dá para separar caso a caso):
1. `mapa_tickers` lê o FCA só de 2026 e 2025. Quem não entregou FCA nesses anos (inadimplente ou entrega atrasada) some.
2. O cruzamento passa pelo cadastro **filtrado por `SIT` = ATIVO**. CNPJ com registro suspenso ou cancelado é descartado. ELPL (Eletropaulo) e OMGE (Omega Energia) foram reorganizadas ou deslistadas, e o problema nelas é o **universo da fase 1**, não a CVM.
3. Unidades e classes cujo `Codigo_Negociacao` vem vazio ou fora do padrão (BPAC11, BRGE11/12), ou emissor da unit diferente do emissor das ações.
4. `dados/besst/mapa_ticker_cvm.csv` (o override manual previsto) **não existe** no repositório.

*Correção:* (i) mapear `Codigo_Negociacao → CNPJ_Companhia` no FCA e depois **CNPJ → CD_CVM pelo próprio índice da DFP/ITR** (`dfp_cia_aberta_AAAA.csv` traz `CNPJ_CIA` e `CD_CVM`), sem depender do `SIT` do cadastro; (ii) ler o FCA dos últimos 3 anos; (iii) registrar o motivo de cada raiz não mapeada (`sem_linha_fca`, `codigo_vazio`, `cnpj_sem_dfp`); (iv) criar o CSV manual para o que restar e retirar do universo os papéis deslistados.

### 2c. Dados velhos exibidos como atuais
ABCB4 (referência 2023), BSLI3/4 (2024; o BRB atrasou a DFP 2025), GPAR3 (2024), AMBP3 (2024, em recuperação judicial) e GEPA (2025 com lucro 0,0). Hoje entram com semáforo como qualquer outro. É preciso uma regra de defasagem: referência há mais de 15 meses → "sem nota · dado desatualizado".

## 3. Sanidade numérica (teste × fontes oficiais ou imprensa)

O teste usa **lucro contábil atribuído aos controladores (IFRS consolidado da DFP/ITR)**. Bancos e elétricas divulgam lucro **recorrente/ajustado** (bancos: BR GAAP gerencial). Diferença de até ~5% contra o recorrente é **definição**, não erro, mas tem de estar escrita na tela.

| Papel | Teste | Oficial / imprensa | Diagnóstico |
|---|---|---|---|
| BBAS3 | LL LTM 2T26 **12,27 bi**; ROE **6,7%** | Ajustado (BR GAAP): 3T25 3,8 + 4T25 5,7 + 1T26 3,4 + 2T26 3,9 ≈ **16,8 bi**; RSPL 2T26 **8,3%** ([Forbes/Reuters](https://forbes.com.br/forbes-money/2026/08/lucro-banco-do-brasil-2o-trimestre-2026/), [InfoMoney 4T25](https://www.infomoney.com.br/?p=3209544), [Canal Rural 1T26](https://www.canalrural.com.br/diversos/banco-do-brasil-fecha-primeiro-trimestre-de-2026-com-lucro-ajustado-de-r-34-bilhoes/)) | **Definição.** Na DFP 2025 (CVM) o lucro IFRS dos controladores é R$ 13,70 bi, contra R$ 20,7 bi ajustado BR GAAP. A extração está correta, mas é −27% contra o número que o investidor vê. As duas versões ficam vermelhas (<10%). Exibir como "ROE contábil IFRS". |
| ITUB4 | LL **46,83 bi**; ROE **21,8%** | Recorrente LTM 2T26 = 2025 46,8 − 1S25 22,64 + 1S26 24,69 ≈ **48,9 bi**; ROE recorrente **24,3%** ([release Itaú 2T26](https://www.itau.com.br/media/dam/m/4a2ea1e7879ff197/original/itau-unibanco-registra-lucro-de-12-4-bilhoes-e-roe1-24-3-no-segundo-trimestre-de-2026-04-08-26.pdf), [InfoMoney 4T25](https://www.infomoney.com.br/mercados/itau-itub4-resultados-quarto-trimestre-2025/)) | −4% no lucro, −2,5 p.p. no ROE. Definição (contábil × recorrente, PL IFRS) mais o viés do PL médio. |
| BBDC4 | LL LTM 3T26 **26,15 bi**; ROE **14,4%** | Recorrente 4T25 6,5 + 1T26 6,81 + 2T26 7,05 + 3T26 7,1 ≈ **27,5 bi**; ROAE 3T26 **16,1%** ([Investidor10](https://investidor10.com.br/noticias/bradesco-bbdc4-lucra-r-7-1-bilhoes-no-3t26-alta-de-14-6-123437/), [InfoMoney 4T25](https://www.infomoney.com.br/mercados/bradesco-bbdc4-resultados-quarto-trimestre-2025/)) | −5% / −1,7 p.p. Definição. |
| SANB11 | LL **13,16 bi**; ROE **10,6%**; payout **ausente** | Gerencial 4T25 4,1 + 1T26 3,8 + 2T26 ~3,0 + 3T26 2,885 ≈ **13,8 bi**; ROAE 3T26 **11,9%** ([Seu Dinheiro](https://www.seudinheiro.com/2026/empresas/santander-sanb11-lucro-roe-rentabilidade-3t26-veja-os-destaques-do-balanco-miql/), [InfoMoney 4T25](https://www.infomoney.com.br/?p=3198995)) | −5% / −1,3 p.p. Definição. **Payout ausente num pagador regular é falha de extração.** |
| CMIG4 | LL LTM 2T26 **4,60 bi**; DL/EBITDA **2,28** | 3T25 0,797 + 4T25 1,876 + 1T26 0,979 + 2T26 0,945 = **4,60 bi** ✔; alavancagem oficial **2,58x** (EBITDA ajustado) ([release Cemig 2T26](https://ri.cemig.com.br/docs/Cemig-2026-06-30-THtJzCB9.pdf), [Cenário Energia 4T25](https://cenarioenergia.com.br/2026/03/20/cemig-registra-lucro-liquido-de-r-188-bilhao-no-4t25-com-impulso-de-acordo-judicial/), [FinanceNews 3T25](https://financenews.com.br/2025/11/cemig-cmig4-reporta-lucro-de-r-797-milhoes-no-3t25-queda-anual/)) | Lucro exato. Alavancagem 0,3x menor: o EBITDA IFRS inclui o ganho não recorrente do acordo judicial do 4T25. Definição; mostrar a fonte. |
| EGIE3 | LL **3,96 bi**; ROE **30,1%** | Contábil 3T25 0,738 + 4T25 0,727 + 1T26 0,789 + 2T26 ~1,9 ≈ **4,1–4,2 bi**. O 2T26 tem **R$ 1,26 bi não recorrente** (repactuação UBP); ajustado 2T26 = 0,694 ([Cenário Energia](https://cenarioenergia.com.br/2026/08/06/engie-lucra-r-19-bi-no-2t26-com-efeito-da-repactuacao-do-ubp-e-avanco-na-transmissao/), [FinanceNews 4T25](https://financenews.com.br/2026/02/engie-brasil-egie3-lucro-liquido-de-r-727-milhoes-no-4t25-queda-anual/), [FinanceNews 3T25](https://financenews.com.br/2025/11/engie-egie3-reporta-lucro-de-r-738-milhoes-no-3t25-companhia-anuncia-aumento-de-capital-com-bonificacao-de-acoes/)) | Lucro próximo (−5%, a esclarecer). **O ROE de 30% é inflado pelo não recorrente**; sem ele, fica em torno de 21%. Precisa de aviso ou de média de 3 anos. |
| VIVT3 | LL **6,60 bi**; payout **43%** | DFP 2025 6,17 (CVM) + 1S26 ≈ 2,8 − 1S25 ≈ 2,5 → **≈ 6,5 bi** ✔ ([Visno 1S26](https://visnoinvest.com.br/news/14421/telefonica-brasil-vivt3-registra-lucro-de-r-28-bi-no-1s26), [InfoMoney 2T26](https://www.infomoney.com.br/?p=3428013)) | Lucro ok. **O payout de 43% engana:** na DFC 2025 a Vivo pagou R$ 2,19 bi em dividendos/JCP mais R$ 1,95 bi em redução de capital e R$ 1,75 bi em recompra (linhas 6.03.07 e 6.03.05, fora da regex). A remuneração total passa de 100% do lucro. |
| BBSE3 | LL **9,19 bi**; ROE **89,3%**; payout **96%** | Lucro 2025 **9,1 bi**; 2T26 2,151 e 1T26 2,22 ([Nord 4T25](https://www.nordinvestimentos.com.br/blog/bb-seguridade-bbse3-4t25/), [Mercado&Consumo 2T26](https://mercadoeconsumo.com.br/04/08/2026/mc-capital/bb-seguridade-tem-lucro-liquido-gerencial-de-r-2151-bi-no-2o-trimestre-queda-de-39/)) | Lucro ✔ (DFP 2025: 9,02 bi). ROE na ordem de grandeza certa (holding com PL pequeno, ~R$ 10 bi); ROAE oficial não conferido. Payout plausível. |
| CPLE3 | DL/EBITDA **2,81** | Alavancagem jun/26 **2,9x** ([O Povo/Estadão Conteúdo](https://www.opovo.com.br/noticias/economia/2026/08/05/copel-lucro-recorrente-salta-426-no-segundo-trimestre-para-rs-64507-milhoes.html)) | ✔ (−0,1x). |
| TAEE11 | ROE **21,8%**; DL/EBITDA **3,48**; payout **76%** | Lucro **regulatório** 2T26 R$ 206,8 mi; proventos do trimestre = **100% do lucro regulatório** ([Análise de Ações](https://www.analisedeacoes.com/noticias/lucro-da-taesa-taee11-cai-28-5-no-2-trimestre-e-empresa-anuncia-207-milhoes-em-proventos/)) | IFRS não conferido (sem fonte acessível). Ilustra a limitação já documentada: em transmissora, ROE e payout IFRS ≠ regulatórios. O payout de 76% contradiz a prática de 100%; precisa de nota de rodapé. |
| ABCB4 | Referência **2023**, LL **0,0**, ROE **0,0%** (vermelho) | Banco ativo e lucrativo: LL 2T26 **R$ 257,3 mi** ([release ABC via PR Newswire](https://www.prnewswire.com/br/comunicados-para-a-imprensa/abc-brasil-entrega-desempenho-solido-no-2t26-com-lucro-liquido-de-r257-3-milhoes-302844991.html)) | **ERRO ÓBVIO.** (a) Não há DF consolidada 2024/2025 nem ITR 2026 sob o CD 20958 nos `_con`, provavelmente a mesma causa da seção 2a (passou a entregar só `_ind`); (b) o 0,0 vem de `achar()` pegar a linha "Atribuído a sócios da controladora" preenchida com 0 quando a empresa só informa o total (3.11). |

**Resumo da conferência:** em 9 casos com lucro comparável, 3 batem com contábil ou recorrente (CMIG 0%, VIVT ≈0%, BBSE ≈+1%) e 4 ficam a −4/−5% do recorrente (ITUB, BBDC, SANB, EGIE), diferença de definição. BBAS fica a −27% por IFRS × BR GAAP ajustado (definição, mas relevante). ABCB tem erro de dado. Na alavancagem, CPLE bate (2,81 × 2,9) e CMIG difere por definição (2,28 × 2,58). Os ROE dos bancos saem 1,3 a 2,5 p.p. abaixo do divulgado: parte é definição, parte é o PL médio de 18 meses.

**Payouts "inteiros", 106% e 225%:** `round(x, 0)` gera float (45.0). Isso não é bug, mas a interface deve formatar sem decimal. Os valores acima de 100% vêm de três fontes: (1) inclusão de proventos a não controladores (EQTL 516%, ENGI 106%, AESO 123%, REDE 118%); (2) caixa ≠ competência, como no caso da CEB (CEBR 225%), que paga reservas da venda de ativos sobre um lucro de 12 meses de R$ 160 mi, um dado real mas que precisa de contexto; (3) WIZC 121%, corretora com política de payout alto. Faltam payouts em pagadores conhecidos (TIMS3, SANB, AXIA, NEOE). É falha de regex ou de layout da DFC, e é preciso despejar as linhas 6.03 desses emissores para ajustar.

## 4. Plano de contas de bancos e seguradoras

- **Correto:** `FINANCEIROS` pula dívida e DL/EBITDA (todos os bancos e seguradoras saem com `div_liq_ebitda = None`). O PL do BB é "2.07 Patrimônio Líquido Consolidado" (nível 2), e o minoritário "2.07.02 … Não Controladores" é descontado. O lucro do BB é 3.11.01 e o da BBSE é 3.13.01 (o leiaute de seguradora tem a numeração deslocada, e a busca por descrição resolveu). Isso confirma que a busca por descrição + nível é a escolha certa.
- **Frágil:** a regex `atribuid[oa].*(controlador|socios da)` também casa "Atribuído aos Sócios **não Controladores**". Hoje funciona só porque `achar` pega o primeiro código (.01). Exigir "controladora" e excluir "nao".
- **Atenção:** bancos grandes entregam IFRS na CVM, e o release usa BR GAAP gerencial. O ROE do painel nunca vai bater com o do release. Rotular "ROE contábil (IFRS, CVM)" e, na ficha, dar o link do release.
- **WIZC3** (corretora) e **BBSE/CXSE/PSSA** (holdings de equivalência) estão como "Seguros". O semáforo de ROE de holding com PL pequeno (BBSE 89%) não é comparável ao de seguradora operacional. Basta nota explicativa.
- **PINE (ROE 42%)** e **BMEB (33%)**: fora do padrão de banco médio. Exigem conferência (efeito fiscal ou não recorrente) antes de qualquer "verde".

## 5. Correções obrigatórias (ordem de prioridade)

1. **Fallback `_ind`** quando não houver `_con` (por emissor e documento) e campo `visao`. *Por quê:* é a maior causa da baixa cobertura (16 emissores, incluindo SAPR, CASN e as distribuidoras).
2. **Mapa ticker→CD_CVM sem depender de `SIT`:** FCA de 3 anos, CNPJ→CD_CVM pelo índice da DFP/ITR, CSV manual versionado e log com o motivo de cada raiz faltante. Tirar do universo os deslistados (ELPL, OMGE, AESO3 e outros). *Por quê:* 18 emissores sem mapa.
3. **Lucro:** se "atribuído à controladora" for 0 ou ausente e o total (3.11/3.13) for ≠ 0 sem minoritários, usar o total. Lucro exatamente 0,0 → "indisponível". `ll is None` → "sem nota" (nunca 0). *Por quê:* nota 0 indevida em LIGT/RNEW e o erro do ABCB.
4. **Payout:** numerador só com linhas de proventos **aos controladores**. Excluir "não controlador", somar um único nível (o mais detalhado ou o subtotal, nunca os dois) e preferir os proventos **declarados** (DMPL) ou explicar "pagos em caixa". Tratar recompra e redução de capital como item separado ("remuneração total"). *Por quê:* outliers de 106–516% e Vivo subestimada.
5. **PL médio** = média do PL no início e no fim da mesma janela LTM, ou dos 5 trimestres. **ROE = None se o PL médio for ≤ 0.** *Por quê:* OIBR +105% e o viés de 18 meses.
6. **`ltm()` sem fallback silencioso:** se faltar componente, o campo vai para None com `motivo`. Nunca misturar o anual com `base="LTM"`.
7. **Defasagem:** referência há mais de 15 meses → sem nota, rótulo "dado desatualizado (aaaa-mm)". Exibir sempre a data de referência por linha (hoje há 30/06 e 30/09 misturados).
8. **Limites de sanidade com flag `verificar`** (sem cor): ROE > 40% ou < −50%; payout < 0 ou > 150%; DL/EBITDA < −2 ou > 8; variação de lucro maior que ±60% contra o ano anterior (pega não recorrente: EGIE). Média de 3 anos do ROE como métrica de apoio.
9. **FCF yield:** casar `composicao_capital` por `CNPJ_CIA`, ou remover a métrica de Telecom até funcionar.
10. **Robustez:** `try` por download (DFP/ITR/FCA/CAD) com registro em `erros[]` e saída parcial válida. Fixtures de CSV reais (BBAS, BBSE, VIVT, SAPR, TAEE, ABCB, EQTL, TIMS) e testes unitários de `fluxo`, `balanco`, `ltm` e `nota`. Arredondamento da nota explícito (`floor(x+0,5)`, não o `round` bancário do Python).
11. **Texto e rótulos (J2, bloqueante para publicação):** corrigir o art. 202 (50% com estatuto omisso; 25% como piso quando o estatuto é alterado para fixar o dividendo; exceções). Trocar a matriz por rótulos descritivos ("preço abaixo do teto · indicadores sem alerta" / "… indicadores fracos"). Na tela: "lucro contábil IFRS (CVM), pode diferir do lucro recorrente do release". Faixas apresentadas como "convenção do painel". Aviso de material educativo (Res. CVM 20/2021).

## 6. Critérios de aceite do próximo teste (todos mensuráveis)

| # | Critério | Meta |
|---|---|---|
| A1 | Emissores do universo (excluídos os deslistados) com CD_CVM mapeado | **≥ 95%**, com motivo registrado para cada faltante |
| A2 | Emissores com dado de referência ≤ 15 meses | **≥ 90%** (hoje 60%); SAPR, CASN, BNBR, BPAR, COCE, CEEB e ABCB obrigatoriamente com dado |
| A3 | Papéis com nota (≥ 2 métricas válidas) | **≥ 75%** (hoje 45%) |
| A4 | Lucro LTM × soma dos 4 trimestres do lucro **contábil atribuído aos controladores** (ITR/release) | diferença **≤ 2%** em **≥ 10 de 12** emissores: BBAS, ITUB, BBDC, SANB, ABCB, BBSE, TAEE, CMIG, EGIE, CPLE, VIVT, SAPR |
| A5 | ROE recalculado à mão a partir do ITR (mesma fórmula do script) | diferença **≤ 0,5 p.p.** nos 12 emissores; diferença contra o ROE do release documentada caso a caso |
| A6 | DL/EBITDA × release, quando a definição coincide | **≤ 0,3x** em ≥ 4 de 5 (CMIG, CPLE, TAEE, EGIE, VIVT), ou divergência explicada |
| A7 | Payout calculado nos papéis com proventos nos últimos 12 meses no `painel.json` | **≥ 90%**; **0** payouts > 150% sem flag; BBAS 2025 com numerador só de controladores (≈ 49%, não 68%) |
| A8 | Valores impossíveis | **0** lucro = 0,0 exato aceito sem verificação; **0** ROE com PL ≤ 0; **0** nota atribuída com `ll = None` |
| A9 | Robustez | execução com 1 download forçado a falhar termina com código 0, `erros[]` preenchido e demais papéis íntegros; testes unitários passando no CI |
| A10 | Revisão J2 | textos e rótulos aprovados antes de qualquer cor ou nota aparecer na página pública |

## 7. Divergências entre juízes
- **J1** aceitaria publicar já **só o lucro e o ROE dos 5 bancos grandes e da BBSE**, com o rótulo "contábil IFRS", porque a extração confere. **J2** veta: o BB aparece com ROE 6,7% contra 8,3% divulgado, e sem a correção 11 isso gera confusão. **J3** veta qualquer publicação antes dos testes (A9). *Prevalece o veto.*
- **J1** prefere manter o payout em caixa (DFC) com rótulo claro. **J2** prefere os proventos declarados (DMPL), mais próximos do que o investidor ouve. *Resolução:* declarado como métrica principal e caixa na ficha. Se a DMPL se mostrar inviável no próximo teste, fica o caixa, só de controladores, com rótulo.
