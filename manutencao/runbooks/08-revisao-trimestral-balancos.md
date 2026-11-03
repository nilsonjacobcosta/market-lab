# RB 08 — Revisão trimestral pós-balanços (ITR/DFP)

**Última revisão deste runbook:** 2026-11-03 · **Responsável:** Nilson (dono)

## 1. Objetivo
Depois de cada temporada de balanços, confirmar que a qualidade financeira (beta) absorveu os números novos, que os
avisos "verificar" foram olhados e que os dados manuais (universo, controle, situações, mapa) continuam coerentes.
É uma **conferência**: as correções de dado são feitas pelos outros runbooks.

## 2. Quando fazer (gatilhos)
Prazos legais da CVM: **ITR** até 45 dias após o fim do trimestre; **DFP** até 3 meses após o fim do exercício.
Os arquivos de Dados Abertos (DFP/ITR/FCA) são atualizados **semanalmente** (inventário da CVM), então a revisão é
feita ~1 semana depois do prazo:

| Temporada | Prazo legal | Fazer em |
|---|---|---|
| 3T26 | 14/11/2026 | 23/11/2026 |
| DFP 2026 | 31/03/2027 | 07/04/2027 (+ itens anuais §5.6) |
| 1T27 | 15/05/2027 | 24/05/2027 |
| 2T27 | 14/08/2027 | 23/08/2027 |
| 3T27 | 14/11/2027 | 22/11/2027 |

## 3. Arquivos afetados
Leitura: `dados/besst/fundamentos.json`, `dados/besst/painel.json`, `dados/besst/fase2_teste/*`.
Possíveis correções (via outros runbooks): `universo.json` (RB 03), `mapa_ticker_cvm.csv` (RB 05),
`situacoes_especiais.json` (RB 02), `estatais.json` (RB 01). Registro: `manutencao/registro.md`.

Campos úteis de `fundamentos.json` → `papeis[ticker]` (gravados por `publicar.py`): `ll`, `roe`,
`roe_medio_exercicios`, `roe_medio_n`, `payout`, `payout_caixa`, `base_payout`, `div_liq_ebitda`, `div_liq_pl`,
`semaforo`, `nota`, `nota_provisoria`, `motivo_sem_nota`, `padrao`, `referencia`, `base`, `componentes_lucro`, `flags`,
`erro`, `motivo`.

## 4. Fontes, em ordem de confiança
| Ordem | Fonte | URL | Uso |
|---|---|---|---|
| 1 | CVM — ITR/DFP (Dados Abertos) | `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/itr_cia_aberta_AAAA.zip`, `.../DFP/DADOS/dfp_cia_aberta_AAAA.zip` | o que o painel usa |
| 1 | CVM — RAD (documento ITR/DFP entregue) | consulta externa em `rad.cvm.gov.br` (**não verificada nesta sessão**) | conferir a demonstração original |
| 2 | RI — release de resultados e planilhas | site de RI de cada empresa | conferir lucro **contábil** (não o "recorrente") |
| 3 | Imprensa reconhecida | — | só para saber a data de divulgação |

## 5. Passo a passo
1. `git pull`. Confirme que a rotina de qualidade publicou na última semana (`gerado_em` em `fundamentos.json`); se não, RB 07.
2. **Data-base e atrasados** (troque `ESPERADA` pelo fim do trimestre da temporada):
```python
import json, collections
f = json.load(open("dados/besst/fundamentos.json", encoding="utf-8"))
p = {x["ticker"]: x for x in json.load(open("dados/besst/painel.json", encoding="utf-8"))["papeis"]}
ESPERADA = "2026-09-30"
print(f["gerado_em"], f["data_base_mais_recente"], collections.Counter(v.get("referencia") for v in f["papeis"].values()).most_common())
for t, v in sorted(f["papeis"].items()):
    if p.get(t, {}).get("status") != "sem_cotacao" and (v.get("referencia") or "") < ESPERADA:
        print(v.get("referencia") or "-", t, v.get("motivo_sem_nota") or v.get("erro") or "")
print("notas provisórias:", [(t, [x for x in v["flags"] if x.startswith("verificar")]) for t, v in f["papeis"].items() if v.get("nota_provisoria")])
```
   Em 03/11/2026 (antes do 3T26): 93 papéis em 2026-06-30, 16 em 2026-09-30, 7 em 2025-12-31, 5 em 2024-12-31,
   9 em 2023-12-31, 14 sem referência. Depois da temporada, a maioria dos negociados deve estar em `ESPERADA`.
   Atrasados: quem não entregou ITR → conferir na CVM (lista de inadimplentes) e no RI; se for crise/RJ, RB 02.
3. **Avisos "verificar"** (a nota fica provisória, com ⚠ na página). Para cada um, abrir o release e anotar no
   `registro.md` se o número é real:
   - `verificar:variacao_lucro=X%` → efeito não recorrente provável (crédito fiscal, venda de ativo, impairment, RAP).
     Em 03/11/2026: AURE3, AXIA3/7, BEES3/4, BMEB3/4, BRST3, CBEE3, CEED3/4, COCE3/5, EGIE3, ENGI3/4/11, LIGT3,
     PINE3/4, SAPR3/4/11, VBBR3.
   - `verificar:payout_igual_ao_lucro (conferir DVA x DMPL)` → conferir na DMPL os dividendos/JCP declarados
     (EKTR3/4, SANB3/4/11 em 03/11/2026).
   - `verificar:roe=…`, `verificar:payout=…`, `verificar:div_liq_ebitda=…` → valor fora da faixa típica (ex.: BBSE3
     ROE 85,9% — holding com equivalência patrimonial, esperado; GEPA payout 122%; TELB dívida líquida negativa).
4. **Conferência manual de 10 emissores** (lista recomendada em `docs/monitor-besst/fase2-fundamentos.md`): BBAS3,
   ITUB4, BBSE3, TAEE11, CMIG4, EGIE3, SBSP3, SAPR11, VIVT3, TIMS3. Compare com o ITR/release:
   lucro atribuído aos controladores (`componentes_lucro`: exercício + acumulado do ano − acumulado do ano anterior),
   ROE e payout. Diferença acima de ~2% no lucro contábil → investigar (versão reapresentada? consolidado × individual?
   — ver `padrao` e `flags`). Para ver as contas que o script leu, rode `fase2-teste.yml` (RB 07 §5.2) e abra
   `log_execucao.json` → `conferencia` (DRE e DVA de EGIE, CPLE, ITUB, BBDC, SANB, BBAS, BBSE, EKTR, CMIG, TAEE, ISAE, BPAC).
5. **Dados manuais afetados pela temporada:**
   - `sem_mapeamento`/`sem DFP` no aceite → RB 05; papéis que viraram/deixaram de ser `sem_cotacao` → RB 03 §5.2;
   - fatos relevantes divulgados com os balanços (OPA, RJ, reorganização, mudança de controle) → RB 02 / RB 01 (varredura RB 02 §5.1);
   - revisar se as 3 exceções do `mapa_ticker_cvm.csv` ainda são necessárias (RB 05 §5 item 6);
   - proventos anunciados com o balanço: conferir se entraram pela data-ex nas semanas seguintes; lacunas → RB 09.
6. **Somente na DFP (abril) — itens anuais:**
   - revisar as **faixas do semáforo** (`FAIXAS` em `scripts/fase2/fundamentos_cvm.py`) contra Selic/custo de capital
     — decisão do dono, registrada; mudança de código com testes;
   - revisão completa do universo (RB 03 §5.5);
   - lembrar que o Formulário de Referência anual costuma ser entregue até o fim de maio: bom momento para a revisão
     completa do controle acionário (RB 01) em junho.

## 6. Como validar
- O snippet do passo 2 não lista atrasados sem explicação (cada um tem motivo anotado).
- Todos os avisos "verificar" da temporada foram lidos e anotados no registro.
- Os 10 emissores conferem (ou a divergência está explicada no registro).

## 7. Como publicar (commit)
Esta revisão normalmente só gera registro:
```bash
git add manutencao/registro.md
git commit -m "Manutenção: revisão trimestral <3T26> — <n> atrasados, <n> verificar conferidos"
git pull --rebase && git push
```
Correções de dado: commits próprios, pelos runbooks correspondentes. Problemas de cálculo: abrir issue (não corrigir dado
para "acertar" o número).

## 8. Se a fonte mudar ou falhar
- ITR entregue mas ausente nos Dados Abertos depois de 2 semanas: conferir no RAD; aguardar a atualização semanal; registrar.
- Empresa reapresentou o ITR (nova `VERSAO`): o script usa a maior versão — confira se o número novo apareceu.
- Leiaute da CVM mudou: RB 07 §8.

## 9. Registro de execuções
Em `manutencao/registro.md`.

## 10. Riscos e cuidados
- O lucro do painel é **contábil** (IFRS/Cosif); releases destacam o "recorrente/ajustado" — diferença esperada.
- Bancos e seguradoras têm leiaute próprio (Cosif/IFRS 17); elétricas de transmissão têm IFRS de concessão: ROE e
  EBITDA podem destoar sem erro.
- Nada aqui é recomendação; a nota é convenção do painel.
