# RB 09 — Proventos zerados ou com lacuna (CPFE3, ISAE3/4, CPLE3, BMEB3/4)

**Última revisão deste runbook:** 2026-11-03 · **Responsável:** Nilson (dono)

## 1. Objetivo
Descobrir, na fonte primária, se um ano de proventos "zerado" no painel é **falha da fonte de preços** (Yahoo) ou
**corte real**, e registrar a conclusão. Isso decide se o preço-teto daquele papel merece confiança.

## 2. Quando fazer (gatilhos)
- Alerta `lacuna_proventos` ("Proventos quase zerados em AAAA entre anos pagadores: possível falha da fonte; confira no RI").
- Status robusto `abaixo_teto_conferir` (página: "Abaixo do teto · conferir dados"; o papel sai do filtro "Abaixo do teto").
- Depois de mudança de ticker (RB 03 §5.6) ou de reorganização de classes.
- Na revisão trimestral (RB 08 §5 item 5).

Casos em 03/11/2026 (`dados/besst/painel.json`, campo `proventos_ano`, R$/ação por data-ex):
| Papel | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 (parcial) | Status robusto | Hipótese a conferir |
|---|---|---|---|---|---|---|---|---|
| CPFE3 | 3,7014 | 3,2423 | 2,8856 | **0** | **0** | 3,7315 | `abaixo_teto_conferir` | falha da fonte (a imprensa noticiou pagamentos da CPFL em 2024–2025 — reforço, **não conferido no RI**) |
| ISAE3 / ISAE4 | 3,5889 | 1,0624 | 2,2041 | **0** | 3,2864 | 1,1140 | `abaixo_teto_conferir` | troca de código TRPL → ISAE (ex-CTEEP) e perda de eventos de 2024 na fonte — **hipótese, conferir** data da troca e proventos de 2024 |
| CPLE3 | 0,6567 | 0,9026 | 0,3040 | 0,3859 | **0** | 1,0626 | `acima_teto` | possível efeito de reorganização de classes/migração da Copel — **hipótese, conferir** |
| BMEB3 / BMEB4 | 0,53 / 0,65 | 0,47 / 0,57 | 1,34 / 1,63 | 1,81 / 2,20 | **0,02** | 3,20 / 3,51 | `acima_teto` | pode ser real (mudança de calendário de pagamento) ou falha — conferir |
| AFLT3 | 0,6301 | 0,2362 | 0,5943 | 0,9946 | **0,017** | 0,6727 | `nao_se_aplica` (sem negociação) | prioridade baixa: o teto já não se aplica |
| CBEE3 | 0,0701 | 0,0825 | **0** | **0** | 0,4188 | 0 | `nao_se_aplica` (sem negociação) | prioridade baixa: o teto já não se aplica |

## 3. Arquivos afetados
| Arquivo | Campos | Observação |
|---|---|---|
| `dados/besst/painel.json` | `proventos_ano`, `alertas` (`lacuna_proventos`), `alertas_detalhe.anos_lacuna`, `dpa_robusto`, `status_robusto` | gerado; **não editar à mão** |
| `dados/besst/brutos/ultimo.json` | 4º elemento de cada ticker = proventos por ano | regravado a cada coleta; **não editar à mão** |
| `manutencao/registro.md` | conclusão por papel | é onde a conferência fica guardada hoje |
| `dados/besst/proventos_correcoes.json` | — | **planejado** (recomendação P2 dos juízes e de `qualidade-dados.md`), **não existe**; ver §8 |

Como o alerta funciona (`scripts/besst_painel.py`, função `qualidade`): um ano completo vira lacuna quando os proventos
dele são < 10% da mediana dos anos pagadores **e** há anos pagadores antes e depois (contando o ano corrente); só vale
para quem pagou em ≥ 3 anos. O DPA robusto **exclui** os anos-lacuna e, se o status robusto der "abaixo do teto", ele
vira `abaixo_teto_conferir`. Ou seja: o painel já se protege; esta conferência serve para confirmar e documentar.

## 4. Fontes, em ordem de confiança
| Ordem | Fonte | URL | O que procurar |
|---|---|---|---|
| 1a | **CVM — IPE** (avisos aos acionistas, comunicados, fatos relevantes sobre dividendos/JCP) | `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/IPE/DADOS/ipe_cia_aberta_AAAA.zip` — **verificada** | declarações com valor por ação, data-com e data de pagamento |
| 1b | **CVM — DFP do ano** (DVA "remuneração de capitais próprios"; DMPL) | `.../DOC/DFP/DADOS/dfp_cia_aberta_AAAA.zip` | ordem de grandeza do total declarado (por **competência**, não por data-ex) |
| 1c | **B3** — página da empresa (eventos corporativos / proventos em dinheiro) | página da empresa em "Empresas listadas" — **não verificada** | tabela com tipo, valor, data-com |
| 2 | **RI da empresa** — página "Dividendos e JCP"/"Proventos" | ex.: CPFL Energia e ISA Energia Brasil (endereços de RI **não verificados** nesta sessão; achar pela página da empresa na B3 ou pelo FRE) | histórico por ano, data-ex/data-com, valor bruto por ação |
| 3 | Imprensa reconhecida | — | reforço (ex.: notícia de pagamento) |
| 4 | Agregadores de dividendos (Status Invest, Investidor10, Dados de Mercado…) | — | **só contexto**, rotulado; nunca para concluir |

## 5. Passo a passo
1. `git pull`. Liste os casos atuais:
```python
import json
p = json.load(open("dados/besst/painel.json", encoding="utf-8"))
for x in p["papeis"]:
    if "lacuna_proventos" in (x.get("alertas") or []):
        print(x["ticker"], x.get("alertas_detalhe", {}).get("anos_lacuna"), x.get("status_robusto"), x.get("proventos_ano"))
```
2. Para cada empresa, pegue o CNPJ (RB 03 §5.1) e procure no IPE as declarações de proventos dos anos-lacuna
   (rode na raiz do repo; troque CNPJ e anos). Lista documentos para você abrir, não soma nada:
```python
import csv, io, re, urllib.request, zipfile
ALVO, ANOS = "00000000000000", (2024, 2025)          # CNPJ só dígitos; anos de entrega a varrer
PAL = re.compile(r"dividend|juros sobre|jcp|provento|remunera..o aos acionistas", re.I)
for ano in ANOS:
    u = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/IPE/DADOS/ipe_cia_aberta_{ano}.zip"
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "market-lab"}), timeout=300).read()))
    with z.open(next(n for n in z.namelist() if n.lower().endswith(".csv"))) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";"):
            txt = " ".join(r.get(k, "") for k in ("Categoria", "Tipo", "Especie", "Assunto"))
            if re.sub(r"\D", "", r["CNPJ_Companhia"]) == ALVO and PAL.search(txt):
                print(r["Data_Entrega"], r["Categoria"][:22], txt[:100], r["Link_Download"])
```
3. Abra os documentos (ou a página de proventos do RI) e monte, para cada ano-lacuna, a lista de proventos com
   **data-ex** (primeiro pregão "ex", normalmente o dia útil seguinte à data-com), valor bruto por ação e tipo
   (dividendo/JCP). Use o valor **bruto** (o painel usa JCP antes do IR).
4. Compare a soma por data-ex de cada ano com `proventos_ano`. Atenção a:
   - desdobramento/grupamento/bonificação no período (o Yahoo ajusta valores antigos; compare na mesma base);
   - classes diferentes (ON × PN × unit) e troca de código;
   - proventos declarados num ano e com data-ex no seguinte.
5. Conclua e registre em `manutencao/registro.md`, uma linha por papel:
   `AAAA-MM-DD | quem | RB 09 | CPFE3: 2024 = R$ x,xx (data-ex …), 2025 = R$ y,yy → falha da fonte confirmada | fonte: <URL do documento> | commit`.
   - **Falha da fonte confirmada:** nada a mudar no painel hoje (ele já exclui o ano e mostra "conferir dados").
     Se o caso for importante, é argumento para implementar o arquivo de correções (§8).
   - **Zero real confirmado** (empresa não pagou: prejuízo, RJ, retenção): registre; o texto do alerta ("possível falha
     da fonte") fica impreciso para esse papel até existir o arquivo de correções. Se houver evento grave, RB 02.

## 6. Como validar
- Cada papel com `lacuna_proventos` tem uma linha de conclusão no `registro.md`, com documento primário.
- Valores conferidos batem com os do RI/CVM na mesma base (bruto, por data-ex, ajustado por desdobramento).

## 7. Como publicar (commit)
```bash
git add manutencao/registro.md
git commit -m "Manutenção: proventos — conferência de lacunas <tickers> (fonte: RI/CVM)"
git pull --rebase && git push
```

## 8. Se a fonte mudar ou falhar
- **Arquivo de correções (planejado, não existe):** a proposta é `dados/besst/proventos_correcoes.json`, por exemplo
  `{"atualizado": "AAAA-MM-DD", "correcoes": [{"ticker": "CPFE3", "ano": "2024", "valor": 0.0, "tipo": "falha_fonte|zero_real", "fonte": "URL", "conferido_em": "AAAA-MM-DD"}]}`,
  aplicado em `besst_painel.py` antes das regras de qualidade. Exige mudança de código, testes e revisão; até lá,
  **não** edite `brutos/ultimo.json` (seria sobrescrito na coleta seguinte).
- **RI sem histórico** (página removida): use IPE/RAD (documentos ficam na CVM) e a DFP.
- **IPE sem o documento:** procure no RAD pela empresa e categoria "Aviso aos Acionistas"/"Comunicado ao Mercado".

## 9. Registro de execuções
Em `manutencao/registro.md`.

## 10. Riscos e cuidados
- Data-ex × data de pagamento × competência: misturar as três gera "lacunas" falsas ou somas duplicadas.
- Não use agregadores como prova; eles também copiam de fontes com falhas.
- Conclusão de que o provento "vai se repetir" não cabe aqui: o painel descreve o passado (Res. CVM 20/2021).
