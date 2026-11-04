# Monitor Portugal — estudo: núcleo de alta liquidez + empresas em observação (04/11/2026)

Pedido do dono: avaliar se vale incluir todas as cotadas portuguesas elegíveis da Euronext Lisbon, classificando a liquidez
em **Alta** (> 100 mil €/dia), **Média** (25–100 mil €/dia) e **Baixa** (< 25 mil €/dia), mantendo as 16 atuais como núcleo,
para não descartar uma empresa de qualidade só por negociar um pouco abaixo do corte. Material de estudo; não publicado no painel.

## 1. Dados (E1 + E2)

Universo elegível: 30 emitentes portugueses do mercado regulamentado (32 ações XLIS menos Euronext N.V. e Merlin Properties).
Liquidez = mediana do volume financeiro diário em 12 meses (fonte de cotações, execução de 04/11/2026). Contas: relatórios
anuais ESEF 2021–2025 com comparativos de 2020 (workflow `portugal-estudo.yml`). Proventos 2021–2025 por ano de pagamento:
**fonte de cotações, não oficial** (servem só para triagem).

| Papel | Empresa | Liquidez/dia | Faixa | Dias sem negócio | Anos com lucro (2020–25) | ROE 2025 | ROIC aprox. (faixa) | Dív. líq./EBITDA 2025 | Proventos 2021–25 (não oficiais) |
|---|---|---:|---|---:|---|---:|---|---:|---|
| PHR | Pharol | 84,6 mil € | Média | 0% | 2/6 | 2,3% | −3% a 30% | caixa líquida | nenhum |
| IPR | Impresa | 17,6 mil € | Baixa | — | 4/5 | 1,3% | 6–14% | caixa líquida | nenhum |
| NBA | Novabase | 12,3 mil € | Baixa | — | **6/6** | 8,8% | **13–30%** | **caixa líquida** | 0 · 0,45 · 0,11 · 1,79 · 1,35 (irregular, devolução de capital) |
| GLINT | Glintt | 11,0 mil € | Baixa | 2% | **6/6, a crescer** | 9,1% | 4–9% | **1,4x (a descer)** | desde 2023: 0,017 · 0,035 · 0,043 (a crescer) |
| RAM | Ramada | 10,1 mil € | Baixa | 0% | **6/6** | 8,1% | 6–13% | ≤ 1,7x | **0,60 · 0,60 · 0,82 · 1,36 · 1,05** |
| SLBEN | Benfica SAD | 9,6 mil € | Baixa | 0% | — (exercício termina em junho) | — | — | — | nenhum |
| MAR | Martifer | 8,7 mil € | Baixa | 0,4% | **6/6** | 12,2% | **10–34%** | 2,8x (0,1x em 2024) | só 2025: 0,12 |
| SNC | Sonaecom | 5,6 mil € | Baixa | — | **6/6** | 3,9% | 0–12% | caixa líquida | irregular; free float ≈ 11% |
| FCP | FC Porto SAD | 378 € | Baixa | 16,5% | — | — | — | — | nenhum |
| SCP | Sporting SAD | 230 € | Baixa | 14,1% | — | — | — | — | nenhum |
| SCT | Toyota Caetano | 69 € | Baixa | **41%** | **6/6, a crescer** | 13,0% | **8–16%** | **0,4x** | **0,22 · 0,20 · 0,25 · 0,30 · 0,35** |
| ESON | Estoril Sol | ~0 € | Baixa | 62% | 3/6 | prejuízo | volátil | caixa líquida | só 2024 |
| FLEXD | Flexdeal | ~0 € | Baixa | 91% | 1/3 | 4,7% | — | caixa líquida | sim (sociedade de investimento) |
| MCP | Media Capital | ~0 € | Baixa | 96,5% | 4/6 | 3,7% | −7% a 9% | 2,0x | irregular |

Nota: no núcleo, a menos líquida é a Ibersol (≈ 202 mil €/dia). ROIC aproximado = resultado operacional × (1 − taxa efetiva)
÷ (capital próprio total + dívida líquida). Ramada e Toyota Caetano têm anos sem ROIC por rubricas de dívida próprias ainda não mapeadas.

### Achado principal
- **A faixa Média está praticamente vazia:** só a Pharol (holding sem atividade operacional relevante e sem dividendos).
  Hoje não existe em Lisboa o caso "empresa excelente a 80 mil €/dia". O salto é do núcleo (≥ 200 mil €) para valores abaixo de 25 mil €.
- **O filtro atual exclui 4 a 5 empresas próximas do perfil que o dono descreveu, todas na faixa Baixa:**
  **Toyota Caetano** (6/6 anos de lucro, proventos a crescer, dívida baixa, ROIC ≈ 15%), **Ramada** (6/6, proventos altos e
  consistentes, dívida baixa), **Novabase** (6/6, ROIC alto, caixa líquida, proventos irregulares), **Martifer** (6/6, ROIC alto,
  primeiro dividendo em 2025) e **Glintt** (lucro e dividendo a crescer, dívida a descer, ROIC ainda moderado).
- **Conclusão do E1/E2:** a observação do dono é **válida e proveitosa** — o corte de 100 mil €/dia está, de facto, a esconder empresas
  com histórico de qualidade. Mas o motivo real não é "80 em vez de 100 mil"; é que estas empresas negoceiam 10 mil €/dia ou menos.

## 2. Pareceres dos especialistas

- **E1 Dados de mercado:** manter as 3 faixas do dono. Acrescentar dois avisos que a faixa não mostra: **negociação intermitente**
  (> 20% de dias sem negócio: Toyota Caetano, Estoril Sol, Flexdeal, Media Capital) e **free float pequeno** (< 15%: Sonaecom).
  Para evitar entra-e-sai no núcleo a cada revisão trimestral: entra com ≥ 100 mil €/dia; só sai abaixo de 80 mil €/dia em duas
  revisões seguidas.
- **E2 Fundamentos:** o ESEF cobre 2020–2025 (6 anos). "Dez anos de lucros" exige relatórios em PDF de 2015–2019: viável à mão
  só para as finalistas. Proposta: mostrar "anos com lucro: n de 6 (desde 2020)" e completar 10 anos nas finalistas. Acrescentar
  **ROIC** ao painel (para todas). Mapear as rubricas de dívida próprias da Ramada e da Toyota Caetano. As SAD de futebol têm
  exercício a terminar em junho: tratar à parte ou deixar sem indicadores.
- **E3 Metodologia:** o preço-teto aplica-se igual; a liquidez não entra na fórmula. Em vez de um "filtro de qualidade" escondido,
  mostrar na ficha um **quadro de perfil** com os critérios do dono, cada um verificável: anos com lucro, crescimento de proventos
  (CAGR e anos sem queda), dívida líquida/EBITDA, ROIC e liquidez. A **vantagem competitiva** não é medível de forma automática:
  ou fica como nota qualitativa com fonte, marcada como interpretação, ou substitui-se pelo indicador "ROIC ≥ 10% em pelo menos
  4 de 5 anos" (persistência de rentabilidade).
- **E4 Regulatório/comunicação:** "em observação" deve querer dizer "fora do núcleo de liquidez", **não** "na lista de compras".
  Nenhum destaque do tipo "oportunidade". O quadro de perfil mostra factos contra critérios públicos; manter a apresentação objetiva.
  Sobre as instituições sugeridas: ver secção 3.
- **E6 Engenharia:** passar de 16 para 30 empresas exige cadastrar os proventos oficiais de cerca de 9 pagadoras (as restantes
  não pagam) e alargar o leitor ESEF. Corrigir a falha de leitura da Impresa em 2024. Esforço estimado: uma sessão de trabalho.
- **E7 Linguagem:** usar "Núcleo (alta liquidez)" e "Em observação"; na tabela, pílula de liquidez Alta/Média/Baixa.

## 3. Pesquisadores — referências de mercado em Portugal (R1/R3)

- **JB Capital, CaixaBI e BPI Research são, de facto, as três casas de research de referência para Lisboa:** foram as nomeadas
  para "Research House" nos Euronext Lisbon Awards 2026, prémio ganho pela JB Capital. O CaixaBI (grupo CGD) cobre o PSI e
  "selected Mid & Small Caps"; os relatórios estão numa área reservada a clientes. O research de ações do BPI funciona em conjunto
  com o CaixaBank desde 2017.
- **DECO PROteste Investe** é o mais parecido, em propósito, com a referência brasileira: serviço por subscrição para o
  investidor individual, com análises, carteiras-modelo, alertas e educação financeira.
- **Como os times podem usar (sem copiar):** os relatórios e recomendações destas casas são conteúdo protegido e, ao serem
  divulgados, são recomendações de investimento ao abrigo do MAR. O painel **não** deve republicar preços-alvo nem ratings.
  Usos permitidos e úteis: (1) **benchmark de produto** (R1): que informação o investidor individual português espera;
  (2) **indicador factual de cobertura**: algumas empresas publicam no próprio site a lista de casas que as acompanham
  (ex.: a página de investidores da Navigator lista JB Capital, CaixaBank BPI, Caixa BI e outras) — o painel pode mostrar
  "n.º de casas de research que acompanham a empresa", com link para essa página do emitente. As empresas em observação quase não
  têm cobertura, o que reforça a utilidade de as mostrar com dados oficiais.
- **Literatura revisada por pares (R3):** ações menos líquidas tendem a oferecer, em média, rendibilidades esperadas maiores
  como compensação pelo custo de negociar (Amihud e Mendelson, 1986; Amihud, 2002). Isto apoia não as excluir, mas também
  confirma que o custo e o risco de negociação são reais e devem ficar visíveis.

## 4. Juízes — avaliação da linha de raciocínio do dono

**J1 (dados) 8,5 · J2 (comunicação) 8,0 · J3 (engenharia) 8,5 — aprovam a decisão "núcleo de 16 + todas as outras em
observação", com quatro correções:**

1. **O exemplo dos 80 mil € não se aplica hoje** (faixa Média só tem a Pharol). As faixas continuam úteis porque as empresas mudam
   de faixa, mas a decisão importante é mostrar a faixa Baixa.
2. **Observação não pode ter dados piores.** Mesmas regras do núcleo: proventos só do cadastro oficial e contas do ESEF.
   Enquanto o cadastro de uma empresa não estiver completo, ela aparece sem preço-teto ("em cadastro"), nunca com valores da fonte
   de cotações.
3. **A liquidez baixa é risco real e tem de estar ao lado do preço:** diferença entre compra e venda maior, dificuldade em vender
   numa crise e, com free float pequeno, risco de oferta de saída de bolsa ao preço do controlador. Isto liga-se à fase seguinte
   (situações especiais).
4. **Dos cinco critérios do dono, três são automáticos já (lucros, dívida, ROIC), um é parcial (crescimento de proventos, depois do
   cadastro oficial) e um não é automatizável (vantagem competitiva).** Os "dez anos" ficam em seis até haver recolha manual.

Coerência com o Brasil: o Monitor BESST já segue este desenho (141 papéis, com o filtro "Só com liquidez ≥ R$ 500 mil/dia"
ligado por omissão e alerta de liquidez). O painel português ficaria com 30 empresas, o universo completo de emitentes portugueses.

## 5. Plano proposto (se o dono aprovar)
1. Universo com 30 empresas: campo `grupo` (núcleo/observação) e `faixa_liquidez` (alta/média/baixa) com regra de entrada/saída.
2. Página: coluna/pílula de liquidez, filtro "Núcleo / Todas" (núcleo por omissão), avisos de negociação intermitente e free float.
3. Cadastro oficial de proventos das 9 pagadoras em observação; leitor ESEF alargado; ROIC para todas.
4. Quadro de perfil na ficha (critérios do dono) e contagem de casas de research com link para o emitente.
5. Controlo acionista das 14 novas; juízes e publicação.

## Fontes
- Euronext — Euronext Lisbon Awards 2026: https://www.euronext.com/en/about/media/euronext-press-releases/euronext-lisbon-awards-2026
- CaixaBI — Research: https://caixabi.pt/en/what-we-do/research/
- ECO (26/05/2017) — research do BPI e do CaixaBank em conjunto: https://eco.sapo.pt/2017/05/26/equipas-de-research-do-bpi-e-caixabank-fazem-joint-venture
- DECO PROteste Investe — vantagens para subscritores: https://www.deco.proteste.pt/investe/vantagens-membros
- The Navigator Company — página da ação (lista de analistas): https://thenavigatorcompany.com/investidores/accao-navigator/
- Amihud, Y. e Mendelson, H. (1986). Asset pricing and the bid-ask spread. *Journal of Financial Economics*, 17(2), 223–249: https://econpapers.repec.org/RePEc:eee:jfinec:v:17:y:1986:i:2:p:223-249
- Amihud, Y. (2002). Illiquidity and stock returns: cross-section and time-series effects. *Journal of Financial Markets*, 5(1), 31–56: https://forrt.org/flora-replication-atlas/doi/10.1016/s1386-4181(01)00024-6/
- Relatórios anuais ESEF via filings.xbrl.org (execução do workflow `portugal-estudo.yml` em 04/11/2026).
