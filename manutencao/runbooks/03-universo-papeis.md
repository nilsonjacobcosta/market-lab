# RB 03 — Universo de papéis (`dados/besst/universo.json`)

**Última revisão deste runbook:** 2026-11-03 · **Responsável:** Nilson (dono)

## 1. Objetivo
Manter a lista dos papéis acompanhados (hoje 144: Energia 72, Bancos 39, Seguros 13, Saneamento 10,
Telecomunicações 10) fiel ao que **existe e negocia** na B3: incluir listagens novas, tirar deslistados e trocar
tickers que mudaram. Hoje **35 papéis não têm cotação** na fonte (aparecem como `sem_cotacao`), poluem as contagens e
reduzem o indicador `universo_inteiro_com_nota_pct` da qualidade financeira (66,7% em 03/11/2026).

## 2. Quando fazer (gatilhos)
- **Revisão completa:** anual, em abril (junto com a DFP), e na conferência trimestral (RB 08).
- **Mensal:** checar se algum papel virou `sem_cotacao` ou voltou a ter cotação (§5.2).
- **Por evento:** OPA concluída, incorporação, fechamento de capital, mudança de ticker/denominação, IPO no setor,
  exclusão de ofício pela B3 (ex.: Oi em 16/09/2026).

## 3. Arquivos afetados
| Arquivo | Campos | Quem lê |
|---|---|---|
| `dados/besst/universo.json` | raiz: `descricao`, `atualizado`; `papeis[]`: `ticker`, `empresa`, `setor` | `besst_painel.py` (lista de coleta e cálculo); `fundamentos_cvm.py` lê o `setor` via `painel.json` |
| `dados/besst/estatais.json` | `tickers` do registro da empresa (se a raiz mudar) | RB 01 |
| `dados/besst/situacoes_especiais.json` | `tickers` dos casos | RB 02 |
| `dados/besst/mapa_ticker_cvm.csv` | só se a raiz nova não aparecer no FCA | RB 05 |

**Cuidado:** `setor` tem de ser exatamente um de `Bancos`, `Energia`, `Seguros`, `Saneamento`, `Telecomunicações`
(com acento). A qualidade financeira usa esse texto como chave de `FAIXAS` em `scripts/fase2/fundamentos_cvm.py`;
outro valor gera exceção no papel e **reprova o aceite** (`papeis_com_excecao`). `empresa` deve ser igual entre as
classes da mesma empresa (o alerta `divergencia_classes` agrupa por `empresa`).

## 4. Fontes, em ordem de confiança
| Ordem | Fonte | URL | O que procurar |
|---|---|---|---|
| 1a | **CVM — FCA, arquivo `valor_mobiliario`** (semanal) | `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/fca_cia_aberta_AAAA.zip` (usado com sucesso pelas rotinas) | `Codigo_Negociacao`, `Valor_Mobiliario`, `Mercado`, `Data_Fim_Negociacao`, `Data_Fim_Listagem`, `Composicao_BDR_Unit` |
| 1b | **CVM — cadastro** (diário) | `https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv` — **verificada** | `SIT` (ATIVO/CANCELADA), `CATEG_REG` (Categoria A = pode ter ações em bolsa; Categoria B = não), `DT_CANCEL`, `MOTIVO_CANCEL`, `SETOR_ATIV` |
| 1c | **B3** — ofícios de exclusão/alteração de código; página "Empresas listadas" | https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/empresas-listadas.htm — **não verificada** | "códigos de negociação", situação |
| 1d | **B3 — COTAHIST** (arquivo oficial de cotações; prova de que o código negociou) | layout verificado: https://www.b3.com.br:443/data/files/33/67/B9/50/D84057102C784E47AC094EA8/SeriesHistoricas_Layout.pdf | `CODNEG` (pos. 13–24) com negócios na data |
| 2 | **RI da empresa** | fato relevante de alteração de código/incorporação | data efetiva |
| 3 | Imprensa reconhecida | reforço | — |
| 4 | Yahoo Finance | só confirma se **a fonte de preços** tem o código; não prova listagem | — |

## 5. Passo a passo

### 5.1 Ticker → CNPJ e situação no FCA (um papel)
```python
import csv, io, urllib.request, zipfile
RAIZ = "BRIT"                                    # 4 letras
for ano in (2026, 2025, 2024):
    u = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FCA/DADOS/fca_cia_aberta_{ano}.zip"
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "market-lab"}), timeout=300).read()))
    with z.open(f"fca_cia_aberta_valor_mobiliario_{ano}.csv") as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";"):
            if (r["Codigo_Negociacao"] or "").upper().startswith(RAIZ) or RAIZ in (r["Composicao_BDR_Unit"] or "").upper():
                print(ano, r["CNPJ_Companhia"], r["Nome_Empresarial"], r["Valor_Mobiliario"], r["Codigo_Negociacao"],
                      r["Mercado"], "fim_neg=" + r["Data_Fim_Negociacao"], "fim_list=" + r["Data_Fim_Listagem"])
```
Depois consulte o CNPJ no cadastro (RB 01 §5.1) para ver `SIT`, `CATEG_REG`, `DT_CANCEL`, `MOTIVO_CANCEL`.

### 5.2 Quais papéis estão sem cotação agora
```python
import json
p = json.load(open("dados/besst/painel.json", encoding="utf-8"))
sem = [x["ticker"] for x in p["papeis"] if x["status"] == "sem_cotacao"]
print(p["pregao_referencia"], len(sem), sem)
```
Compare com a lista do §5.4. Papel **novo** na lista = possível deslistagem, suspensão ou mudança de código → §5.1.
Papel com cotação **parada** também é sinal (a fonte pode devolver o último preço de um papel excluído, como OIBR3/4):
```python
import json
from datetime import date
p = json.load(open("dados/besst/painel.json", encoding="utf-8"))
ref = date.fromisoformat(p["pregao_referencia"])
print([(x["ticker"], x["data"]) for x in p["papeis"] if x.get("data") and (ref - date.fromisoformat(x["data"])).days > 20])
```

### 5.3 Teste rápido: a fonte de preços tem o código?
```bash
curl -s -A "Mozilla/5.0" "https://query1.finance.yahoo.com/v8/finance/chart/BRST3.SA?range=5d&interval=1d" | head -c 400; echo
```
`"result":null` / erro 404 = Yahoo não tem o código (não quer dizer que a B3 não tenha: confira no FCA/COTAHIST).

### 5.4 Os 35 papéis sem cotação (03/11/2026) — evidência e decisão sugerida
Evidência da CVM tirada de `dados/besst/fase2_teste/diagnostico_mapa.json` (cadastro e FCA baixados em 02–03/11/2026
pela rotina `diagnostico_mapa.py`). "Conferir" = sem evidência no diagnóstico: rode o §5.1.

| Papéis | Empresa | Evidência | Decisão sugerida |
|---|---|---|---|
| BRIV3, BRIV4 | Banco Alfa de Investimento | Cadastro: CANCELADA em 2024-03-28, cancelamento voluntário | **Remover** |
| BRGE3, BRGE5, BRGE6, BRGE8, BRGE11, BRGE12 | Consórcio Alfa de Administração | Cadastro: CANCELADA em 2024-03-28, cancelamento voluntário | **Remover** |
| BPAN4 | Banco Pan | Cadastro: CANCELADA em 2026-03-30, cancelamento voluntário | **Remover** |
| CSAB3, CSAB4 | Cia. Seguros Aliança da Bahia | Cadastro: CANCELADA em 2024-03-08; FCA 2024: fim de negociação 2024-01-19 | **Remover**. Avaliar incluir a holding **PEAB3/PEAB4** (Cia. de Participações Aliança da Bahia, ATIVO, Categoria A, códigos no FCA 2024) — conferir se a atividade cabe em "Seguros" |
| LIPR3 | Eletropar | Cadastro: CANCELADA em 2025-06-02, "elisão por incorporação" | **Remover** |
| BRIT3 | Brisanet Participações | Cadastro: CANCELADA em 2024-12-04, "elisão por incorporação"; FCA 2025: **BRST3** na Brisanet Serviços (CD 27693) | **Remover** (BRST3 já está no universo e no `estatais.json`). No mesmo commit: apagar o registro `["BRIT3"]` do `estatais.json` e a linha `BRIT` do `mapa_ticker_cvm.csv` (RB 05 §3) |
| CSRN3, CSRN5, CSRN6 | Cosern | Cadastro: ATIVO, mas **Categoria B**; FCA 2024 só lista debêntures | **Remover** |
| CEPE3, CEPE5 | Celpe | Cadastro: ATIVO, **Categoria B**; FCA 2024 só lista debêntures | **Remover** |
| ELPL4 | Eletropaulo (Enel SP) | Cadastro: ATIVO, **Categoria B** | **Remover** |
| COMR3 | Comerc Energia | Cadastro: ATIVO, Categoria A; FCA 2024: ações ordinárias **sem código de negociação** | **Remover** (nunca negociou) |
| IGSN3 | Iguá Saneamento | Cadastro: ATIVO, Categoria A; FCA 2024: código "023175" (não é ticker) | **Remover** (sem ações em bolsa) |
| NEOE3 | Neoenergia | Situação especial `opa_concluida` (leilão 09/04/2026) | **Remover** do universo e do RB 02 depois de confirmar cancelamento/saída no FCA/cadastro |
| SRNA3 | Serena Energia | Situação especial `opa_concluida` (resgate das remanescentes) | **Remover** (idem) |
| MEGA3, OMGE3 | Omega Energia / Omega Geração | `estatais.json` aponta o mesmo controlador da Serena (Actis e GIC). Hipótese: códigos antigos do grupo que virou Serena | Conferir (§5.1) e **remover** se confirmado |
| AESO3 | AES Brasil | `estatais.json`: controlador "Auren Energia" (hipótese: incorporada pela Auren, AURE3 já no universo) | Conferir e **remover** se confirmado |
| COCE6, CEEB6 | Coelce, Coelba (classe PNB) | As outras classes (COCE3/5, CEEB3/5) têm cotação | Conferir no FCA se a classe ainda existe; **remover só a classe** se não existir |
| PINE11, RNEW11 | Pine, Renova (units) | PINE3/4 e RNEW3/4 têm cotação | Conferir `Composicao_BDR_Unit` no FCA; remover a unit se ela não existir mais |
| EEEL3, EEEL4 | CEEE-GT | Registros "CEEE" do cadastro no diagnóstico: geração em Categoria B | Conferir (§5.1) e decidir |
| UPKP3, RIOS3, APER3 | UPK, Rios, Alper | Sem evidência no diagnóstico (UPKP3 tem `confianca: baixa` e controlador "verificar" no `estatais.json`) | Conferir (§5.1); remover se não houver código ativo no FCA |

Fora dos 35, mas pela mesma regra: **OIBR3, OIBR4** (Oi) ainda aparecem **com** cotação, porém parada em 22/09/2026,
e a B3 cancelou a listagem de ofício (Ofício 337/2026-DRL, citado em `situacoes_especiais.json`). Decisão sugerida:
**remover** do universo e encerrar o caso no RB 02, depois de abrir o ofício na B3.

Regra de decisão (para estes e para casos futuros):
1. **Remover** se: `SIT = CANCELADA`, **ou** `CATEG_REG = Categoria B`, **ou** o código não aparece (ou tem
   `Data_Fim_Negociacao`/`Data_Fim_Listagem` preenchido) nos 3 últimos FCA, **ou** há ofício da B3 de exclusão/troca de código.
2. **Manter** (aceitando `sem_cotacao`) se: suspensão temporária pela B3, ou o código está ativo no FCA e negocia
   (COTAHIST), mas a fonte de preços não o tem → é falha de fonte (RB 06 §8), não de universo.
3. Sempre que remover um papel em situação especial, remova-o também do `situacoes_especiais.json` (ou o caso inteiro).

Sugestão opcional (não exige mudar código, porque o script só lê `papeis`): guardar o histórico das saídas numa chave
nova na raiz, `"removidos": [{"ticker": "...", "empresa": "...", "setor": "...", "removido_em": "AAAA-MM-DD", "motivo": "...", "fonte": "..."}]`.

### 5.5 Incluir um papel
1. Confirme no FCA que o código existe e está ativo (§5.1) e que a empresa é dos 5 setores.
2. Acrescente em `papeis`: `{"ticker": "XXXX3", "empresa": "Mesmo nome das outras classes", "setor": "Energia"}`.
3. Raiz nova? Crie o registro de controle (RB 01). Em situação especial? RB 02.
4. Teste o código na fonte de preços (§5.3). Depois do commit, dispare a coleta (RB 06 §5.3): o papel só ganha
   preço quando `--coletar` roda.

Para achar candidatos (revisão anual), liste companhias ativas por setor no cadastro e cruze com o FCA:
```python
import csv, io, urllib.request, collections, re
URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"
rows = list(csv.DictReader(io.StringIO(urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "market-lab"}), timeout=300).read().decode("latin-1")), delimiter=";"))
ativos = [r for r in rows if r["SIT"].upper().startswith("ATIVO") and r["CATEG_REG"] == "Categoria A"]
print(collections.Counter(r["SETOR_ATIV"] for r in ativos).most_common(60))   # veja os nomes reais dos setores
SET = re.compile(r"banc|energia|segur|saneamento|telecom", re.I)               # ajuste depois de ver a lista acima
for r in ativos:
    if SET.search(r["SETOR_ATIV"]):
        print(r["CNPJ_CIA"], r["CD_CVM"], r["DENOM_SOCIAL"][:50], "|", r["SETOR_ATIV"])
```
Para cada candidato, rode o §5.1 pelo nome/CNPJ para obter os códigos e confirme que negocia.

### 5.6 Mudança de ticker (mesma empresa)
1. Fonte primária: fato relevante/comunicado (IPE/RAD) ou ofício da B3 com a data efetiva.
2. Em `universo.json`: troque o `ticker` (mantenha `empresa`/`setor`).
3. Raiz mudou (ex.: BRIT → BRST)? Atualize `tickers` no `estatais.json` e nos casos do `situacoes_especiais.json`;
   se o FCA ainda não tiver o código novo, acrescente a exceção no `mapa_ticker_cvm.csv` (RB 05).
4. Depois da coleta, confira `proventos_ano` do papel: algumas fontes perdem o histórico do código antigo,
   o que aparece como ano zerado (`lacuna_proventos`) ou `historico_curto` → RB 09.

## 6. Como validar
```python
import json, collections
u = json.load(open("dados/besst/universo.json", encoding="utf-8"))
SET = {"Bancos", "Energia", "Seguros", "Saneamento", "Telecomunicações"}
t = [p["ticker"] for p in u["papeis"]]
print(len(t), "papéis", collections.Counter(p["setor"] for p in u["papeis"]))
print("duplicados:", [x for x, n in collections.Counter(t).items() if n > 1])
print("setor inválido:", [p["ticker"] for p in u["papeis"] if p["setor"] not in SET])
print("empresa diferente na mesma raiz:", {r: s for r, s in
      ((r, {p["empresa"] for p in u["papeis"] if p["ticker"][:4] == r}) for r in {x[:4] for x in t}) if len(s) > 1})
```
Esperado: nenhum duplicado, nenhum setor inválido. Rode também a validação do RB 01 §6 (papéis sem controle) e do RB 02 §6
(casos fora do universo). Depois da coleta seguinte: `com_cotacao` em `painel.json` coerente com o esperado e o aceite
da qualidade financeira continua passando.

## 7. Como publicar (commit)
```bash
git add dados/besst/universo.json dados/besst/estatais.json dados/besst/situacoes_especiais.json dados/besst/mapa_ticker_cvm.csv manutencao/registro.md
git commit -m "Manutenção: universo — remove <tickers> (<motivo>, fonte: cadastro CVM <data>)"
git pull --rebase && git push
```
Depois dispare **Atualizar Monitor BESST** (RB 06 §5.3) para recalcular com a nova lista (inclusões precisam da coleta).
Atualize também o texto "144 papéis" / "35 papéis sem cotação" em `carteiras/monitor-besst/README.md` se mudar.

## 8. Se a fonte mudar ou falhar
- FCA sem o código mas a empresa diz que negocia: confira o COTAHIST da B3 (página "Cotações históricas" do
  site da B3, não verificada nesta sessão; o arquivo anual traz `COTAHIST.AAAA.TXT`, layout verificado acima) e o RI.
- Cadastro/FCA fora do ar: use o RAD (FCA da empresa) e o ofício da B3; registre a fonte usada.
- Yahoo sem o código, mas B3 com negócios: **não remova**; é problema de fonte de preços (RB 06 §8).

## 9. Registro de execuções
Em `manutencao/registro.md`.

## 10. Riscos e cuidados
- Remover um papel apaga o histórico dele no `painel.json` (o bruto antigo continua no git). Registre o motivo.
- Uma classe nova com a mesma raiz herda controle (RB 01), mas **não** herda situação especial (RB 02 é por ticker).
- Mudança de ticker com troca de raiz quebra o mapa ticker→CVM se o FCA ainda não refletir o código novo (RB 05).
