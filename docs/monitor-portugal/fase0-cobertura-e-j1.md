# Monitor Portugal — Fase 0: cobertura da fonte e 1ª conferência do J1 (04/11/2026)

Documento interno de estudo. Nada aqui está publicado no site.

## 1. Universo e cobertura (E1)

Execução do workflow `portugal-teste-cobertura.yml` (Actions, run 41802318727).

- Lista oficial de ações da Euronext Lisbon, mercado regulamentado (MIC XLIS): **32 ações**.
- 31/32 com preços na fonte de cotações (sufixo `.LS`), preço recente e ≥ 6 anos de histórico.
- Falha: **ENXP** (Euronext N.V., emitente não português com linha em Lisboa).
- Linhas estrangeiras/secundárias também presentes: **MRL** (Merlin Properties, espanhola), negócio em Lisboa ~3 mil €/dia.

### Liquidez (mediana do volume financeiro diário, 12 meses)

| Corte | Papéis |
|---:|---:|
| 25 mil € | 17 |
| 100 mil € | 16 |
| 250 mil € | 15 |
| 500 mil € | 14 |
| 1 milhão € | 13 |

**Proposta do E1 (para os juízes):** corte de **100 mil €/dia** e no máximo **5% de dias sem negócio** em 12 meses, excluindo emitentes cuja sede/listagem principal não é Portugal (ENXP, MRL). Resultado: **16 papéis** —
ALTR, BCP, COR, CTT, EDP, EDPR, EGL, GALP, IBS, JMT, NOS, NVG, RENE, SEM, SON, TDSA.
Fronteira a observar: IBS (~202 mil €/dia), PHR (~85 mil €/dia, fica fora). Revisão do corte: trimestral, junto com as revisões do PSI.

Papéis abaixo do corte (preço pode ser "velho"): FLEXD (91% de dias sem negócio), MCP (96%), SCT (41%), ESON (62%), MRL (26%), FCP, SCP, SLBEN, GLINT, IPR, MAR, NBA, RAM, SNC.

## 2. Conferência de proventos (J1) — amostra contra fontes oficiais

Critério do J1: ≥ 95% dos eventos iguais à fonte oficial. Comparação por **ano de pagamento**, valor **bruto** por ação.

| Papel | Ano | Fonte de cotações | Oficial | Resultado | Fonte oficial |
|---|---|---:|---:|---|---|
| BCP | 2022 | 0,0009 | 0,0009 | ok | RI Millennium bcp, página Dividendos |
| BCP | 2023 | 0 | sem pagamento | ok | idem |
| BCP | 2024 | 0,017 | 0,0170 | ok | idem |
| BCP | 2025 | 0,03 | 0,0300 | ok | idem |
| BCP | 2026 (12m) | 0,0344 | 0,0344 | ok | comunicado de 12/05/2026 |
| EDP | 2025 | 0,20 | 0,20 | ok | EDP, "Payment of dividends – year 2024" |
| JMT | 2025 | 0,59 | 0,59 | ok | comunicado de pagamento, abril/2025 (Euronext) |
| RENE | 2025 | 0,157 | 0,093 (mai) + 0,064 (dez) | ok | REN, comunicados de pagamento |
| GALP | 2022 | 0,5236 | 0,25 + 0,26 = 0,51 | **diverge +2,7%** | Galp, página Dividendos |
| GALP | 2023 | 0,5441 | 0,26 + 0,27 = 0,53 | **diverge +2,7%** | idem |
| GALP | 2024 | 0,5646 | 0,27 + 0,28 = 0,55 | **diverge +2,7%** | idem |
| GALP | 2025 | 0,65 | 0,34 + 0,31 = 0,65 | ok | idem |
| EDPR | 2023 | 0 | programa de dividendo em ações (scrip) | **omitido** | EDP/EDPR, anúncio de 27/02/2023 |

Resultado: 10 de 13 valores conferem (77%). **Não atinge os 95%. A fonte de cotações NÃO pode ser a fonte de proventos do painel.**

### Achados
1. **Ajuste não explicado (Galp 2022–2024):** a fonte multiplica os proventos por um fator constante (~1,027). Os valores oficiais são redondos (0,25; 0,26; 0,27…).
2. **Dividendo em ações (scrip) é invisível na fonte:** a EDPR pagou parte dos proventos em ações; a fonte registra zero. O próprio BCP já usou scrip no passado (2001 e 2011). O painel precisa de regra para scrip (valor de referência por ação, informado no comunicado).
3. Os casos sem ajuste (BCP, EDP, JMT, REN) batem ao centavo — a fonte serve como **alerta de evento**, não como valor.
4. Sites de RI (ex.: Millennium bcp) bloqueiam leitura automatizada da nuvem; foi preciso o navegador do dono (lição 7 confirmada).

## 3. Decisão proposta para os juízes

- **Proventos:** cadastro próprio `dados/portugal/proventos_oficiais.csv` (ano, tipo — intercalar/final/scrip, bruto por ação, data ex, data de pagamento, link do comunicado), preenchido a partir de comunicados da empresa / SDI da CMVM / Euronext. A fonte de cotações fica só como detector: se ela mostrar um evento que não está no cadastro, abre alerta.
- **Preços e liquidez:** a fonte de cotações serve (31/32 cobertos).
- **Universo:** 16 papéis pela regra acima, com data de revisão visível.

## Fontes consultadas
- Millennium bcp — Dividendos: https://ind.millenniumbcp.pt/pt/Institucional/investidores/Pages/Dividendos.aspx
- Millennium bcp — comunicado de dividendo, 12/05/2026: https://ind.millenniumbcp.pt/pt/Institucional/investidores/Documents/comunicados/2026/Dividendo_PT_12052026.pdf
- EDP — Payment of dividends, year 2024: https://edp.com/en/investors/investor-information/market-notifications/payment-dividends-year-2024
- Jerónimo Martins — dividend payment 2025 (Euronext): https://live.euronext.com/sites/default/files/company_press_releases/attachments/2025/04/24/Connect_dividendpayment2025.pdf
- REN — pagamento de dividendos do exercício de 2024: https://www.ren.pt/media/u1rjovmy/pagamento-de-dividendos-do-exercício-de-2024.pdf
- REN — dividendos intercalares do exercício de 2024: https://www.ren.pt/media/ennldnhi/pagamento-de-dividendos-intercalares-do-exercicio-de-2024.pdf
- Galp — Dividends: https://www.galp.com/corp/en/investors/information-to-shareholders/dividends
- EDPR — scrip dividend (anúncio de 27/02/2023): https://www.edp.com/sites/default/files/2023-02/20230227_Scrip%20Dividend%20EDPR_EN.pdf
