# Qualidade financeira no Monitor BESST — vale a pena?

Analista: fundamentalista (bancos, utilities, seguros, saneamento, telecom) · Data-base: 02/11/2026
Insumos lidos: `dados/besst/painel.json` (144 papéis, ~75 emissores), `scripts/besst_painel.py`, `carteiras/monitor-besst/index.html`, workflow `monitor-besst.yml`.

## 1. Veredito: SIM, com escopo PARCIAL (3 métricas por setor, não um "score" completo)

O painel hoje mede só *preço vs. proventos passados*. O preço-teto Bazin (DPA médio 5a ÷ 6%) é retrovisor: quando o mercado
antecipa um corte de dividendo, o preço cai antes do DPA, e a "margem" aumenta justamente no papel que piora. Exemplo do
próprio painel: BBAS3 aparece com margem +41,8% e tendência −30,3% — o sinal de "barato" e o de deterioração convivem e o
iniciante não tem como separá-los. É o padrão clássico de *dividend trap* (yield alto por preço em queda, não por geração de caixa).

Base na literatura e na prática:
- **Piotroski (2000)** mostrou que, dentro de ações "baratas", sinais simples de balanço (lucro positivo, FCO > lucro, menos
  alavancagem, sem diluição) separam vencedoras de perdedoras — ideia direta do "teto barato × deterioração".
  [J. Accounting Research 38 — doi:10.2307/2672906](https://doi.org/10.2307/2672906)
- **Asness, Frazzini & Pedersen — "Quality minus junk"**: qualidade (lucratividade, segurança, payout) é precificada e
  complementa valor. [Rev. Accounting Studies 24 (2019) — doi:10.1007/s11142-018-9470-2](https://doi.org/10.1007/s11142-018-9470-2)
- **Skinner & Soltes (2011)**: lucros de pagadoras de dividendos são mais persistentes; *perder* o dividendo sinaliza piora.
  [Rev. Accounting Studies 16 — doi:10.1007/s11142-009-9113-8](https://doi.org/10.1007/s11142-009-9113-8)
- **Lintner (1956)**: empresas suavizam dividendos em torno de um payout-alvo; payout muito acima do lucro não se sustenta.
  [American Economic Review 46(2)](https://www.jstor.org/stable/1910664)
- Brasil (Lei 6.404, art. 202): o dividendo obrigatório é o que o estatuto fixar; se o estatuto for omisso, é **metade
  (50%) do lucro líquido ajustado**; se a assembleia alterar um estatuto omisso para fixá-lo, o percentual não pode ser
  inferior a 25% do lucro ajustado. Exceções: o § 3º permite dividendo inferior ou retenção total em companhia aberta só
  quando ela capta recursos exclusivamente por debêntures não conversíveis (e em fechadas não controladas por abertas), e o
  § 4º dispensa o obrigatório no exercício em que a administração informar que ele é incompatível com a situação financeira. Payout acima de 100% indica distribuição de reservas ou de recursos de terceiros.
  *(Texto corrigido em 02/11/2026 por exigência do parecer dos juízes.)* [Planalto](https://www.planalto.gov.br/ccivil_03/leis/l6404consol.htm)

Por que "parcial": (i) para iniciante, mais de 3 números por papel vira ruído; (ii) parte das métricas setoriais corretas
(Basileia, inadimplência, índice combinado) não está na DFP e exige outra fonte; (iii) contabilidade IFRS de concessões
(ICPC 01/CPC 47 — ativo de contrato em transmissoras) distorce ROE e EBITDA de elétricas. Começar com ROE + alavancagem +
payout (fase 1, só CVM) e acrescentar as regulatórias depois (fase 2).

## 2. Métricas por setor (semáforo para iniciantes; faixas são heurísticas de mercado, não normas)

| Setor | Métrica | Fórmula | Verde | Amarelo | Vermelho |
|---|---|---|---|---|---|
| Bancos | ROE | Lucro 12m atrib. controladores ÷ PL médio controladores | ≥ 15% | 10–15% | < 10% ou prejuízo |
| Bancos | Payout | Dividendos+JCP declarados no exercício (DVA) ÷ lucro do exercício | 25–60% | 60–80% ou < 25% | > 80% |
| Bancos (fase 2) | Índice de Basileia | Patrimônio de referência ÷ ativos ponderados por risco (BCB IF.data) | ≥ 14% | 11,5–14% | < 11,5% |
| Bancos (fase 2) | Custo de crédito | Despesa de PDD 12m ÷ carteira média | < 3% | 3–5% | > 5% |
| Seguros | ROE | idem bancos | ≥ 15% | 10–15% | < 10% |
| Seguros | Payout | idem | 25–75% | 75–95% | > 95% |
| Seguros (fase 2) | Índice combinado | (sinistros + despesas de comercialização + adm.) ÷ prêmios ganhos (SUSEP SES) | < 95% | 95–100% | > 100% |
| Energia | Dív. líq./EBITDA | (Empréstimos+debêntures CP+LP − caixa − aplic.) ÷ (EBIT + D&A) 12m | ≤ 3,0x | 3–4x | > 4x |
| Energia | ROE | idem | ≥ 12% | 8–12% | < 8% |
| Energia | Payout | idem | 25–80% | 80–100% | > 100% |
| Saneamento | Dív. líq./EBITDA | idem | ≤ 2,5x | 2,5–3,5x | > 3,5x |
| Saneamento | ROE | idem | ≥ 10% | 6–10% | < 6% |
| Saneamento | Payout | idem | 25–60% | 60–90% | > 90% |
| Telecom | Dív. líq./EBITDA | idem | ≤ 2,0x | 2–3x | > 3x |
| Telecom | ROE (FCF yield retirado em 03/11/2026) | lucro 12m ÷ PL médio | ≥ 12% | 8–12% | < 8% |
| Telecom | Payout | idem | 25–100% | 100–120% | > 120% |

Notas de calibragem: Basileia mínimo regulatório total = 8% + 2,5% de conservação (+ adicional sistêmico para D-SIBs),
conforme Res. CMN 4.958/2021 — 11,5% amarelo dá folga sobre o piso. Transmissoras (TAEE, ISAE, ALUP) toleram até ~4x por
receita contratada (RAP); distribuidoras e geradoras com energia descontratada não. ROE é comparado ao custo de capital: com Selic em dois
dígitos, ROE < 10% fica abaixo do custo de capital típico do setor. Payout < 25% fica amarelo (baixo para quem busca dividendos, mas não é risco).
Exibição: 3 bolinhas coloridas por linha + tooltip com o número e a frase "por que importa"; cinza = sem dado.

## 3. Fonte pública e gratuita automatizável (GitHub Actions)

**Funciona bem — CVM Dados Abertos** (verificado em 02/11/2026):
- DFP anual: `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_AAAA.zip` (2010–2026);
  ITR: `.../DOC/ITR/DADOS/itr_cia_aberta_AAAA.zip` (2026 atualizado em 01/11/2026, 19 MB; ~30 MB/ano).
  [DFP](https://dados.cvm.gov.br/dataset/cia_aberta-doc-dfp) · [ITR (índice)](https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/)
- Dentro do ZIP: um CSV por demonstração e visão (`..._BPA_con_AAAA.csv`, `BPP`, `DRE`, `DFC_MD`, `DFC_MI`, `DMPL`, `DVA`;
  `_con` consolidado / `_ind` individual), separador `;`, codificação latin-1. Colunas: `CNPJ_CIA, DT_REFER, VERSAO,
  DENOM_CIA, CD_CVM, GRUPO_DFP, MOEDA, ESCALA_MOEDA, ORDEM_EXERC, DT_INI_EXERC, DT_FIM_EXERC, CD_CONTA, DS_CONTA,
  VL_CONTA` (+ `ST_CONTA_FIXA`). Cuidados: filtrar `ORDEM_EXERC = ÚLTIMO`, maior `VERSAO` (reapresentações), multiplicar
  por `ESCALA_MOEDA` (MIL/UNIDADE); no ITR a DRE vem com coluna do trimestre e acumulada — usar `DT_INI_EXERC = 01/01`.
  [Gist com leitura real](https://gist.github.com/Vido/de4823b632e1fe875e8a48dd8f7e4a44) · [GetDFPData2](https://rdrr.io/cran/GetDFPData2/src/R/fct_clean_dfp_itr_data.R)
- Contas (não financeiras): 3.05 EBIT, 3.11 lucro consolidado (3.11.01 controladores), 2.03 PL, 2.01.04 + 2.02.01
  empréstimos e financiamentos, 1.01.01 + 1.01.02 caixa e aplicações, 6.01 FCO, 6.02 investimento, 6.03 financiamento
  (dividendos/JCP pagos). **Bancos e seguradoras usam outro leiaute de DFP** (intermediação financeira, provisões técnicas;
  numeração do lucro e do PL muda). Por isso o script localiza contas por *descrição + nível*, não por código fixo.
- **Ticker → CD_CVM**: o cadastro (`.../CAD/DADOS/cad_cia_aberta.csv`, atualizado diariamente) traz CNPJ e CD_CVM mas
  **não traz ticker**. O ticker está no FCA (`fca_cia_aberta_AAAA.zip`, arquivo `valor_mobiliario`, campo de código de
  negociação — nome exato da coluna não confirmado). Recomendo: mapear pela raiz de 4 letras (todas as classes = 1 emissor)
  e manter um CSV manual de ~75 linhas como fallback/override — é pequeno, auditável e evita quebra silenciosa.
  [FCA](https://dados.cvm.gov.br/dataset/cia_aberta-doc-fca) · [Cadastro](https://dados.cvm.gov.br/dataset/cia_aberta-cad)

**Difícil / fora da CVM:**
- EBITDA não vem pronto: aproximar por EBIT (3.05) + D&A da DFC (6.01.01.xx, por texto). Não é o EBITDA regulatório
  (ANEEL) nem o "ajustado" do release; em transmissoras IFRS ele é pouco informativo.
- Basileia e inadimplência: **BCB IF.data** (API OData `olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/`,
  funções `IfDataValores(AnoMes, TipoInstituicao, Relatorio)`, relatório "Informações de Capital"); exige mapear CNPJ do
  conglomerado prudencial (TipoInstituicao=1). O robots.txt bloqueia leitura por crawler, mas a API é pública.
  [Dataset IF.data](https://dadosabertos.bcb.gov.br/dataset/ifdata---dados-selecionados-de-instituies-financeiras) · [python-bcb](https://wilsonfreitas.github.io/python-bcb/ifdata.html)
- Índice combinado: **SUSEP SES** (base por seguradora, código SUSEP ≠ CNPJ da holding listada; BBSE3, CXSE3 e PSSA3
  consolidam participações por equivalência — índice combinado da holding não sai da DFP).
  [SUSEP SES](https://www2.susep.gov.br/menuestatistica/ses/principal.aspx)
- Volume: 3 DFPs + 1 ITR + FCA ≈ 150–200 MB por execução; rodar **semanal** (não de hora em hora como os preços) com cache.

## 4. Nota de qualidade 0–3 e combinação com a margem

Regra (igual para todos os setores, métricas da tabela): verde = 1 ponto, amarelo = 0,5, vermelho = 0; nota = 3 × pontos ÷
métricas disponíveis, arredondada. Travas: prejuízo nos 12m → 0; qualquer vermelho → no máximo 1; menos de 2 métricas → "sem nota".
Frase para iniciante: **"A nota mostra se a empresa ganha dinheiro suficiente, sem dever demais, para continuar pagando o
que pagou no passado (3 = indicadores fortes, 0 = indicadores fracos; não é recomendação)."**

Matriz preço × qualidade — **rótulos descritivos, sem juízo de compra ou venda** (Res. CVM 20/2021; reescrita em
02/11/2026 por exigência dos juízes):

| | Nota 3 | Nota 2 | Nota 0–1 |
|---|---|---|---|
| Preço ≥ 20% abaixo do teto | Abaixo do teto · indicadores fortes | Abaixo do teto · indicadores mistos | Abaixo do teto · indicadores fracos — investigar o motivo |
| Preço 0–20% abaixo do teto | Perto do teto · indicadores fortes | Perto do teto · indicadores mistos | Perto do teto · indicadores fracos |
| Preço acima do teto | Acima do teto · indicadores fortes | Acima do teto · indicadores mistos | Acima do teto · indicadores fracos |

Na tela, os indicadores são rotulados como **"lucro contábil (IFRS/Cosif), últimos 12 meses"** — diferente do lucro
"recorrente" ou "ajustado" que bancos e empresas destacam nos releases.

Combinar também com a coluna "tendência" já existente: margem alta + tendência < −20% + nota ≤ 1 = alerta vermelho explícito.

## 5. Riscos e limitações

- **Defasagem**: ITR sai até 45 dias após o trimestre (3T26 ≈ meados de nov/26); DFP até março. O preço é diário, a
  qualidade é trimestral — mostrar "dados até 30/06/2026" ao lado da nota.
- **Não recorrentes**: créditos fiscais, reversões de PDD, ganhos na RAP/revisão tarifária, venda de ativos e
  impairments inflam ou derrubam o ROE de um ano; usar LTM e, se possível, média de 3 anos para ROE.
- **Holdings e controladas listadas**: CMIG/CEMIG GT, ENGI (holding) e controladas (ENMT, EQPA), CEEB/COCE (Neoenergia),
  BRGE (Alfa), RPAD (Alfa), Eletrobras (AXIA) — consolidado da holding ≠ caixa que sobe para o acionista; alavancagem pode
  estar na holding ou na controlada.
- **Várias classes** (ON/PN/UNIT; ex. SANB3/4/11, TAEE3/4/11, EQPA3/5/6/7): fundamentos são do emissor — mesma nota para
  todas as classes; (o FCF yield, que usava preço × total de ações, foi retirado).
- **Estatais**: payout e ROE dependem de decisão política (BBAS3, CMIG, SAPR, CSMG, CASN); a coluna de controle já ajuda.
- **Contábil setorial**: IFRS de concessão (transmissão), ativos financeiros indenizáveis e IFRS 17 (seguros, desde 2023)
  quebram comparabilidade histórica; bancos seguem Cosif + Res. CMN 4.966 (perda esperada, desde 2025).
- **Papéis ilíquidos e em recuperação** (OIBR, CEBR, GEPA, CEED): dado pode faltar ou ser atípico → "sem nota" e não 0.
- Faixas do semáforo são convenções de mercado para triagem, não recomendação; revisar anualmente com Selic/custo de capital.

## Próximos passos sugeridos
1. Rodar `fundamentos_cvm.py` uma vez num runner com internet; conferir 10 emissores à mão contra os releases (BBAS3, ITUB4,
   BBSE3, TAEE11, CMIG4, EGIE3, SBSP3, SAPR11, VIVT3, TIMS3) e ajustar regex de contas.
2. Gerar `dados/besst/fundamentos.json` em workflow semanal; página lê os dois JSONs e mostra 3 bolinhas + nota + matriz.
3. Fase 2: IF.data (Basileia) para bancos e SUSEP SES (índice combinado) para seguradoras operacionais.

## Atualização após a 2ª rodada de testes (03/11/2026)

- **FCF yield retirado** da tabela de métricas: a contagem de ações do arquivo `composicao_capital` da CVM tem escala
  inconsistente entre emissores. Em Telecomunicações, o ROE ocupa o lugar dele.
- **Payout = proventos declarados sobre o lucro do exercício** (JCP + dividendos da linha "remuneração de capitais
  próprios" da DVA), divididos pelo lucro atribuído aos controladores do mesmo exercício. O valor pago em caixa no ano
  (DFC) aparece só como conferência.
- **Lucro = lucro contábil (IFRS/Cosif)** dos últimos 12 meses; pode diferir do lucro "recorrente" dos releases.
- Variação do lucro acumulado acima de ±60% contra o mesmo período do ano anterior recebe o aviso "verificar"
  (possível efeito não recorrente). O ROE médio dos exercícios fechados aparece ao lado do ROE de 12 meses.
