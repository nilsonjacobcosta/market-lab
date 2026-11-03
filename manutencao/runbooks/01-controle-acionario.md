# RB 01 — Controle acionário (`dados/besst/estatais.json`)

**Última revisão deste runbook:** 2026-11-03 · **Responsável:** Nilson (dono)

## 1. Objetivo
Manter correta, com fonte, a classificação de quem controla cada empresa do universo (estatal federal, estadual,
estrangeira, participação estatal relevante ou privada). Ela alimenta a coluna "Controle", o filtro "Só estatais" e o
texto da ficha. Classificação errada engana o iniciante sobre risco político de dividendos.

## 2. Quando fazer (gatilhos)
- **Revisão completa:** no máximo a cada **60 dias** (última: 02/11/2026 → limite **01/01/2027**; fazer até 15/12/2026).
- **Conferência rápida:** todo mês (script do §5.2).
- **Por evento:** privatização, venda de controle, OPA por alienação de controle, oferta secundária do governo,
  acordo de acionistas novo, incorporação, entrada de papel novo no universo (RB 03).
- **Sinal de atraso:** `"atualizado"` de `estatais.json` com mais de 60 dias.
  **Planejado (ainda não existe):** aviso automático na página quando a revisão passar de 60 dias.

## 3. Arquivos afetados
| Arquivo | Campos | Quem lê |
|---|---|---|
| `dados/besst/estatais.json` | raiz: `atualizado` (AAAA-MM-DD); em `empresas[]`: `tickers`, `nome`, `setor`, `categoria`, `controlador`, `nota`, `fonte`, `confianca` | `scripts/besst_painel.py` (função `calcular`) grava em `painel.json` os campos `controle`, `controlador`, `controle_nota`, `controle_fonte` |
| `dados/besst/painel.json` | regenerado | página |

Como o script casa ticker e empresa: primeiro pelo ticker exato em `tickers`; se não achar, pela **raiz de 4 letras**
(ex.: `AXIA7` herda o registro de `AXIA3/AXIA6`). Logo, uma classe nova da mesma empresa herda a classificação sozinha;
uma empresa com raiz nova precisa de registro novo.

Valores aceitos: `categoria` ∈ {`estatal_federal`, `estatal_estadual`, `estatal_estrangeira`,
`participacao_estatal_relevante`, `privada`}; `confianca` ∈ {`alta`, `media`, `baixa`}.

### Critérios de classificação (convenção do painel)
| Categoria | Regra | Exemplos atuais |
|---|---|---|
| `estatal_federal` | União controla, direta ou indiretamente (BB, Caixa, BNDESPar) | BBAS3, BBSE3, CXSE3, BNBR3, BAZA3, TELB3/4 |
| `estatal_estadual` | Estado ou DF controla | BRSR, BSLI (DF), CEBR (DF), CMIG, SAPR, CASN, CLSC, BGIP, BPAR, BEES, GPAR |
| `estatal_estrangeira` | Controlador final é Estado estrangeiro ou empresa controlada por ele | CPFE3 (State Grid), GEPA (CTG), ISAE (ISA/Ecopetrol), COCE/CBEE/ELPL (Enel/MEF), TIMS3 (TIM/Poste Italiane), ABCB4 |
| `participacao_estatal_relevante` | Sem controle estatal, mas ente público com ≥ ~10% do capital ou ação de classe especial (golden share) | AXIA3/6, CPLE3, SBSP3, CSMG3, LIPR3 |
| `privada` | Demais | ITUB, BBDC, SANB, EGIE … |

`confianca`: **alta** = documento primário (Formulário de Referência, fato relevante, ofício B3) com menos de 12 meses;
**media** = imprensa reconhecida, ou documento primário mais antigo; **baixa** = indício ou "verificar".
(Os registros de 02/11/2026 **não** seguem esta régua: 38 dos 51 que citam a página genérica da B3 estão como `alta`,
e nenhum dos 85 cita documento primário — ver §10.)

## 4. Fontes, em ordem de confiança
| Ordem | Fonte | URL | O que procurar |
|---|---|---|---|
| 1a | **CVM — Cadastro de companhias abertas** (diário) | https://dados.cvm.gov.br/dataset/cia_aberta-cad → `https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv` (dicionário: `.../CAD/META/meta_cad_cia_aberta.txt`) — **verificada 03/11/2026** | `CONTROLE_ACIONARIO` (tipo de controle declarado), `SIT`, `SIT_EMISSOR`, `DT_CANCEL`, `MOTIVO_CANCEL` |
| 1b | **CVM — Formulário de Referência (FRE), posição acionária** (semanal) | https://dados.cvm.gov.br/dataset/cia_aberta-doc-fre → `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/fre_cia_aberta_AAAA.zip`, CSV `fre_cia_aberta_posicao_acionaria_AAAA.csv` — **verificada 03/11/2026** (colunas não conferidas; ver `.../DOC/FRE/META/meta_fre_cia_aberta.zip`) | acionistas com ≥ 5%, quem é controlador, % ON e % total |
| 1c | **CVM — RAD / Empresas.NET** (documento original) | consulta externa em `rad.cvm.gov.br` (o próprio FCA da CVM aponta links `http://www.rad.cvm.gov.br/ENETCONSULTA/frmDownloadDocumento.aspx?...`) — **não verificada nesta sessão** | FRE, item "Posição acionária" (6.1 no FRE da Res. CVM 80; 15.1 no antigo); fatos relevantes de venda de controle |
| 1d | **CVM — IPE** (fatos relevantes, comunicados; semanal) | https://dados.cvm.gov.br/dataset/cia_aberta-doc-ipe — **verificada** | eventos de alienação de controle, privatização |
| 1e | **B3** — página da empresa em "Empresas listadas" | https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/empresas-listadas.htm (**não verificada**; é a página genérica hoje citada em 51 registros) | aba de informações: composição acionária. **Citar o endereço da empresa, não a página genérica** |
| 2 | **RI da empresa** | site de RI (endereço no FRE/FCA ou na página da B3) | "Composição acionária", "Estrutura societária" |
| 3 | Imprensa reconhecida (reforço) | Valor, Estadão, Folha, Reuters, InfoMoney… | notícia de privatização/venda — só junto com 1 ou 2 |
| 4 | Alternativa (contexto, rotulada) | Wikipedia, portais de investimento | só no campo `nota`, escrito "contexto:" |

## 5. Passo a passo

### 5.1 Consulta de uma empresa no cadastro da CVM (pelo CNPJ)
Rode na raiz do repositório (`python3 -I`), trocando o CNPJ:
```python
import csv, io, re, urllib.request
URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"
txt = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "market-lab manutencao"}), timeout=300).read().decode("latin-1")
ALVO = "00000000000191"  # CNPJ só com dígitos (exemplo: Banco do Brasil)
for r in csv.DictReader(io.StringIO(txt), delimiter=";"):
    if re.sub(r"\D", "", r["CNPJ_CIA"]) == ALVO:
        print({k: r[k] for k in ("DENOM_SOCIAL", "CD_CVM", "SIT", "SIT_EMISSOR", "CONTROLE_ACIONARIO",
                                 "CATEG_REG", "DT_CANCEL", "MOTIVO_CANCEL")})
```
Não sabe o CNPJ? Descubra pelo ticker no FCA (snippet do RB 03 §5.1) ou na página da empresa na B3.

### 5.2 Conferência do universo inteiro contra o cadastro (mensal)
Salve como `/tmp/conferir_controle.py` (fora do repositório) e rode `python3 -I /tmp/conferir_controle.py` na raiz do repo.
Baixa ~3 FCA (≈ poucos MB cada) e o cadastro. Só **lista** divergências; não altera nada.
```python
import csv, io, json, re, urllib.request, zipfile, collections
CVM = "https://dados.cvm.gov.br/dados/CIA_ABERTA"
def baixar(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "market-lab manutencao"}), timeout=300) as r:
        return r.read()
dig = lambda s: re.sub(r"\D", "", s or "")
est = json.load(open("dados/besst/estatais.json", encoding="utf-8"))["empresas"]
raizes = {t[:4] for e in est for t in e["tickers"]}
cnpj = {}                                    # raiz -> CNPJ, pelo FCA (valor_mobiliario) dos 3 últimos anos
for ano in (2026, 2025, 2024):
    z = zipfile.ZipFile(io.BytesIO(baixar(f"{CVM}/DOC/FCA/DADOS/fca_cia_aberta_{ano}.zip")))
    with z.open(f"fca_cia_aberta_valor_mobiliario_{ano}.csv") as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";"):
            cod = (r["Codigo_Negociacao"] or "").strip().upper()
            if cod[:4] in raizes:
                cnpj.setdefault(cod[:4], dig(r["CNPJ_Companhia"]))
por_cnpj, por_cd = {}, {}
for r in csv.DictReader(io.StringIO(baixar(f"{CVM}/CAD/DADOS/cad_cia_aberta.csv").decode("latin-1")), delimiter=";"):
    c = dig(r["CNPJ_CIA"])
    if c not in por_cnpj or r["SIT"].upper().startswith("ATIVO"):
        por_cnpj[c] = r
    por_cd[r["CD_CVM"].lstrip("0")] = r
for r in csv.DictReader(open("dados/besst/mapa_ticker_cvm.csv", encoding="utf-8"), delimiter=";"):
    if r["raiz"] not in cnpj and r["cd_cvm"].lstrip("0") in por_cd:        # exceções manuais (BPAC, EQPA, BRIT)
        cnpj[r["raiz"]] = dig(por_cd[r["cd_cvm"].lstrip("0")]["CNPJ_CIA"])
print("valores de CONTROLE_ACIONARIO no cadastro:",
      collections.Counter(r["CONTROLE_ACIONARIO"] for r in por_cnpj.values()).most_common())
ESTATAIS = ("estatal_federal", "estatal_estadual")
for e in est:
    rz = e["tickers"][0][:4]
    r = por_cnpj.get(cnpj.get(rz, ""), {})
    cvm = (r.get("CONTROLE_ACIONARIO") or "?").upper()
    diverg = (e["categoria"] in ESTATAIS) != ("ESTATAL" in cvm)
    if not r or diverg or not r.get("SIT", "").upper().startswith("ATIVO"):
        print(f'{rz}\t{e["categoria"]}\tCVM={cvm}\tSIT={r.get("SIT", "?")}\tSIT_EMISSOR={r.get("SIT_EMISSOR", "?")}\t{e["nome"]}')
```
Leitura do resultado:
- `CVM=?` → raiz sem CNPJ no FCA (papel deslistado ou exceção): conferir à mão (RB 03/RB 05).
- `SIT=CANCELADA` → registro cancelado: o papel provavelmente saiu da bolsa (RB 03 e RB 02).
- divergência estatal × não estatal → abrir a posição acionária (§5.3) e decidir. O campo da CVM é **autodeclarado**
  e não distingue "estatal estrangeira" (costuma vir como estrangeiro) nem "participação relevante" (costuma vir como privado):
  ele é **indício**, não decisão.

### 5.3 Posição acionária no FRE (prova do controle)
```python
import csv, io, re, urllib.request, zipfile
ALVO, ANO = "00000000000191", 2026         # CNPJ só dígitos; ano de entrega do FRE
u = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/fre_cia_aberta_{ANO}.zip"
z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "market-lab"}), timeout=300).read()))
nome = next(n for n in z.namelist() if re.search(r"posicao_acionaria_\d{4}\.csv$", n))
with z.open(nome) as f:
    rd = csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";")
    print(rd.fieldnames)                     # 1º confira os nomes reais das colunas
    col = next(c for c in rd.fieldnames if c.lower().startswith("cnpj_comp"))
    linhas = [r for r in rd if re.sub(r"\D", "", r[col]) == ALVO]
chave = lambda r: (r.get("Data_Referencia", ""), int(r.get("Versao") or 0))
ult = max(map(chave, linhas))                # FRE mais recente e última versão
for r in linhas:
    if chave(r) == ult:
        print({k: v for k, v in r.items() if v and re.search(r"acionista|controlador|percentual", k, re.I)})
```
Se `linhas` vier vazio, tente `ANO - 1` (o FRE é entregue uma vez por ano, até 31/05, e reapresentado em eventos).
Abra também o documento no RAD (link na coluna de link, se houver) para guardar a URL do **documento** como `fonte`.

### 5.4 Revisão completa (a cada 60 dias)
1. `git pull`.
2. Rode o §5.2 e anote as divergências.
3. Para cada divergência, e para todo registro com `confianca` ≠ `alta` ou `fonte` = página genérica da B3,
   priorizando os papéis **com cotação** e as estatais: abra o FRE (§5.3) ou o RI e decida a categoria pela tabela do §3.
4. Edite o registro: `categoria`, `controlador` (quem e país/ente), `nota` (percentuais e data do documento, ex.:
   "União 50,0% do capital (FRE 2026, data-base 31/12/2025)"), `fonte` (URL do documento primário), `confianca`.
5. Atualize `"atualizado": "AAAA-MM-DD"` (só na revisão completa; numa correção pontual, registre em `registro.md`
   e **não** mude a data — ela marca a última revisão do conjunto inteiro).
6. Papel novo de raiz nova → acrescente um objeto novo em `empresas`.

### 5.5 Correção por evento (ex.: privatização)
Mesmo fluxo, só para a empresa afetada: documento do evento (fato relevante no IPE/RAD) + posição acionária
atualizada. Se o evento for OPA/fechamento, faça também o RB 02.

## 6. Como validar
```python
import json
u = json.load(open("dados/besst/universo.json", encoding="utf-8"))["papeis"]
e = json.load(open("dados/besst/estatais.json", encoding="utf-8"))
CATS = {"estatal_federal", "estatal_estadual", "estatal_estrangeira", "participacao_estatal_relevante", "privada"}
ruins = [x["tickers"] for x in e["empresas"] if x["categoria"] not in CATS or x["confianca"] not in {"alta", "media", "baixa"}
         or not x["fonte"].startswith("http")]
tk = {t for x in e["empresas"] for t in x["tickers"]}
sem = [p["ticker"] for p in u if p["ticker"] not in tk and p["ticker"][:4] not in {t[:4] for t in tk}]
print("atualizado:", e["atualizado"], "| registros inválidos:", ruins, "| papéis sem controle:", sem)
```
Esperado: listas vazias. Depois da publicação, na página: filtro "Só estatais (qualquer esfera)" e a ficha do papel
alterado mostram o controlador novo.

## 7. Como publicar (commit)
Caminho simples (recomendado): commit só do `estatais.json`; a rotina diária recalcula o `painel.json` no fim do dia.
```bash
git add dados/besst/estatais.json manutencao/registro.md
git commit -m "Manutenção: controle acionário — <empresa>: <de> → <para> (fonte: FRE/fato relevante <data>)"
git pull --rebase && git push
```
Caminho urgente (página atualizada já): depois de editar, rode `python3 scripts/besst_painel.py` (sem `--coletar`:
não usa internet, recalcula a partir de `dados/besst/brutos/ultimo.json`) e inclua `dados/besst/painel.json` no commit.
**Atenção:** o recálculo local regrava `gerado_em`, `coletado_em_utc` e `fase` com a hora atual, e o selo passa a
dizer "atualizado dd/mm às hh:mm" com os preços da última coleta. Use-o só depois das 18h20 e de uma coleta de fechamento
(confira `fase: "fechamento"` em `painel.json` antes); se não for publicar o painel, desfaça com
`git restore dados/besst/painel.json`.

## 8. Se a fonte mudar ou falhar
- **Cadastro da CVM fora do ar/URL mudou:** procure o conjunto em https://dados.cvm.gov.br (busca "cia_aberta-cad").
  Se mudar o nome de coluna, confira o dicionário `meta_cad_cia_aberta.txt` e ajuste o snippet.
- **FRE sem a empresa:** use o ano anterior; depois o documento no RAD; depois o RI.
- **Empresa sem FRE recente** (inadimplente, em crise): use fato relevante + RI e marque `confianca: "media"`.
- **CVM bloqueada no seu ambiente** (ex.: proxy de IA retorna 403): rode o snippet num runner do GitHub (copie-o para
  um passo do `fase2-teste.yml` numa branch) ou no computador do dono. Não troque por fonte não oficial.
- Nunca use a página genérica de "Empresas listadas" como única prova numa revisão nova.

## 9. Registro de execuções
Em `manutencao/registro.md`.

## 10. Riscos e cuidados
- **Fontes fracas herdadas (02/11/2026):** 51 dos 85 registros citam a página genérica da B3; outros citam portais
  (acionista.com.br, investidor10, suno, moneytimes, italianismo, tipranks, wikipedia, lexlegal, euqueroinvestir,
  bnamericas…). Prioridade de troca: ABCB4 (Wikipedia, `media`), UPKP3 (`baixa`, controlador "verificar"),
  TAEE (controle compartilhado), COCE/CBEE/ELPL (Enel com MEF ~23,6% "controle de fato" — critério discutível; deixar
  explícito na `nota`), TIMS3 (Poste Italiane, notícia de 09/2026), CPLE3/AXIA/SBSP (percentuais públicos mudam com ofertas).
- `CONTROLE_ACIONARIO` é autodeclarado e pode estar desatualizado: nunca decida só por ele.
- Holding × controlada: classifique pelo **controlador final** e diga na `nota` quem é o controlador direto.
- A rotina mensal automática é **planejada**: quando existir, ela **só abre issue** com divergências; a classificação
  continua sendo decisão manual (nunca alterar `estatais.json` automaticamente).
