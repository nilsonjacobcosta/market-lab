# RB 02 — Situações especiais (`dados/besst/situacoes_especiais.json`)

**Última revisão deste runbook:** 2026-11-03 · **Responsável:** Nilson (dono)

## 1. Objetivo
Manter a lista de empresas em recuperação judicial (RJ), falência, OPA/fechamento de capital, deslistagem ou crise com
negociação restrita. Todo ticker listado aqui recebe o alerta `situacao_especial`, que é **grave**: o papel fica com
status `nao_se_aplica` ("preço-teto não se aplica") e a ficha mostra o `texto_iniciante`. Um caso esquecido deixa um
papel problemático parecendo "barato"; um caso que não foi encerrado esconde um papel que voltou ao normal.

## 2. Quando fazer (gatilhos)
- **Revisão completa:** todo 1º dia útil do mês (última: 02/11/2026).
- **Varredura semanal** (segunda): fatos relevantes novos no IPE da CVM (snippet §5.1).
- **Por evento:** pedido/encerramento de RJ, decretação de falência, edital/leilão/resultado de OPA, saída do Novo
  Mercado, cancelamento de registro, ofício da B3 de suspensão/exclusão, intervenção/liquidação pelo BCB (bancos),
  balanços atrasados com negociação só em leilão.
- **Sinal de atraso:** `"atualizado"` com mais de 35 dias.

## 3. Arquivos afetados
| Arquivo | Campos | Quem lê |
|---|---|---|
| `dados/besst/situacoes_especiais.json` | raiz: `descricao`, `atualizado`, `tipos`; em `casos[]`: `tickers`, `empresa`, `tipo`, `data`, `descricao`, `texto_iniciante`, `fonte`, `confianca` | `scripts/besst_painel.py` (função `qualidade`): copia `tipo`, `descricao`, `data`, `fonte` para `situacao_especial` no `painel.json` e usa `texto_iniciante` no alerta; `metodo.situacoes_especiais_versao` = `atualizado` |
| `dados/besst/painel.json` | regenerado | página |

Tipos em uso (`tipos`): `recuperacao_judicial`, `rj_encerrada`, `falencia`, `opa_pendente`, `opa_concluida`,
`crise_negociacao_restrita`. Tipo novo: acrescente-o também na lista `tipos` (o script não valida, mas a lista documenta).

Casos ativos em 02/11/2026: AMBP3 (RJ), OIBR3/4 (falência, deslistada), LIGT3 (RJ encerrada 09/09/2026),
BSLI3/4 (BRB, crise), DESK3 (OPA pendente), EMAE3/4 (OPA pendente), NEOE3 (OPA concluída), SRNA3 (OPA concluída).

## 4. Fontes, em ordem de confiança
| Ordem | Fonte | URL | O que procurar |
|---|---|---|---|
| 1a | **CVM — IPE** (fatos relevantes, comunicados; atualização semanal) | https://dados.cvm.gov.br/dataset/cia_aberta-doc-ipe → `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/IPE/DADOS/ipe_cia_aberta_AAAA.zip` — **verificada 03/11/2026** | `Categoria` = Fato Relevante / Comunicado ao Mercado; `Assunto`; `Link_Download` (documento) |
| 1b | **CVM — RAD / Empresas.NET** | consulta externa em `rad.cvm.gov.br` — **não verificada nesta sessão** | o mesmo documento, para citar na `fonte` |
| 1c | **CVM — cadastro** | `.../CAD/DADOS/cad_cia_aberta.csv` (RB 01 §5.1) | `SIT`, `SIT_EMISSOR` (ex.: "EM RECUPERAÇÃO JUDICIAL", "FALIDA"), `DT_CANCEL`, `MOTIVO_CANCEL`; o nome social ganha "EM RECUPERAÇÃO JUDICIAL" |
| 1d | **B3** — ofícios e comunicados (suspensão, exclusão, leilão de OPA) | página da empresa em "Empresas listadas" e área de comunicados/ofícios da B3 — **não verificada** | número do ofício (ex.: "Ofício 337/2026-DRL") |
| 1e | **BCB** (bancos) | comunicados de intervenção/liquidação/RAET no site do Banco Central | regime especial |
| 2 | **RI da empresa** | fato relevante, edital de OPA, plano de RJ | datas, preço da OPA, etapas |
| 3 | Imprensa reconhecida (reforço) | Valor, Estadão, Reuters, InfoMoney… | contexto e cronologia |
| 4 | Alternativa (contexto, rotulada) | portais de investimento | nunca como `fonte` principal |

## 5. Passo a passo

### 5.1 Varredura de fatos relevantes do universo (semanal/mensal)
Salve fora do repositório (ex.: `/tmp/varrer_ipe.py`) e rode na raiz do repo com `python3 -I /tmp/varrer_ipe.py`.
Lista os fatos relevantes e comunicados dos últimos 45 dias das empresas do universo; marca com `<<<` os que têm
palavras-chave. Não altera nada.
```python
import csv, io, json, re, urllib.request, zipfile
from datetime import date, timedelta
CVM = "https://dados.cvm.gov.br/dados/CIA_ABERTA"
def baixar(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "market-lab manutencao"}), timeout=300) as r:
        return r.read()
dig = lambda s: re.sub(r"\D", "", s or "")
raizes = {p["ticker"][:4] for p in json.load(open("dados/besst/universo.json", encoding="utf-8"))["papeis"]}
hoje = date.today()
cnpj_raiz = {}
for ano in (hoje.year, hoje.year - 1):                    # FCA: liga código de negociação ao CNPJ
    z = zipfile.ZipFile(io.BytesIO(baixar(f"{CVM}/DOC/FCA/DADOS/fca_cia_aberta_{ano}.zip")))
    with z.open(f"fca_cia_aberta_valor_mobiliario_{ano}.csv") as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";"):
            cod = (r["Codigo_Negociacao"] or "").strip().upper()
            if cod[:4] in raizes:
                cnpj_raiz[dig(r["CNPJ_Companhia"])] = cod[:4]
PAL = re.compile(r"recupera..o judicial|fal.ncia|\bOPA\b|oferta p.blica|cancelamento|fechamento de capital|novo mercado|"
                 r"incorpora..o|aliena..o de controle|liquida..o|interven..o|suspens|leil.o", re.I)
desde = (hoje - timedelta(days=45)).isoformat()
z = zipfile.ZipFile(io.BytesIO(baixar(f"{CVM}/DOC/IPE/DADOS/ipe_cia_aberta_{hoje.year}.zip")))
with z.open(next(n for n in z.namelist() if n.lower().endswith(".csv"))) as f:
    for r in csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";"):
        rz = cnpj_raiz.get(dig(r["CNPJ_Companhia"]))
        if rz and r["Data_Entrega"] >= desde and r["Categoria"] in ("Fato Relevante", "Comunicado ao Mercado"):
            txt = " ".join(r.get(k, "") for k in ("Assunto", "Tipo", "Especie"))
            print("<<<" if PAL.search(txt) else "   ", r["Data_Entrega"], rz, r["Categoria"][:14], txt[:90], r["Link_Download"])
```
Obs.: confira no dicionário `.../DOC/IPE/META/meta_ipe_cia_aberta.txt` o formato de `Data_Entrega` (o filtro assume
AAAA-MM-DD; se vier dd/mm/aaaa, troque a comparação). Um fato relevante sem `Assunto` aparece sem `<<<`: leia os de
empresas que você não conhece o motivo.

### 5.2 Abrir um caso novo
1. Abra o documento primário (link do IPE/RAD, ofício B3, comunicado BCB).
2. Acrescente em `casos`:
```json
{"tickers": ["XXXX3", "XXXX4"], "empresa": "Nome", "tipo": "recuperacao_judicial", "data": "AAAA-MM-DD",
 "descricao": "Fato, data e número do documento (ex.: pedido de RJ em dd/mm/aaaa, processo nº …).",
 "texto_iniciante": "frase curta, sem jargão, que diga por que o preço-teto não se aplica.",
 "fonte": "URL do documento primário", "confianca": "alta"}
```
   - `tickers`: **todas** as classes listadas (ON, PN, units) — o script casa por ticker exato, não por raiz.
   - `data`: data do evento (AAAA-MM-DD; AAAA-MM se só houver o mês).
   - `texto_iniciante`: começa em minúscula (a página antepõe "Situação especial: ").
   - `confianca`: `alta` com documento primário; `media` só com imprensa reconhecida.
3. Atualize `"atualizado"`.

### 5.3 Atualizar ou encerrar um caso
| Situação | Ação |
|---|---|
| OPA pendente → leilão realizado | `tipo: "opa_concluida"`, nova `data`, `descricao` com resultado do leilão; RB 03 para tirar o papel do universo se ele deixou de negociar |
| RJ aprovada/encerrada | `tipo: "rj_encerrada"` e data do encerramento. **Convenção sugerida** (decisão do dono): manter o caso até sair a DFP do 1º exercício completo pós-RJ e reavaliar |
| Falência com cancelamento da listagem | manter enquanto o papel estiver no universo; quando sair do universo (RB 03), remover o caso |
| Crise resolvida (balanços em dia, negociação normal) | remover o caso e registrar o motivo em `registro.md` |
| OPA cancelada/desistência | remover o caso, com o documento de desistência no registro |

### 5.4 Pendências conhecidas (03/11/2026)
- Todas as 8 `fonte` atuais são de imprensa/portais (analitica.auvp, renovainvest, suno, investidor10, seudinheiro,
  visnoinvest). Trocar por documento primário na próxima revisão: OIBR → Ofício B3 337/2026-DRL; NEOE3/SRNA3 →
  edital e resultado do leilão (RAD); DESK3/EMAE → fato relevante/edital de OPA; AMBP3/LIGT3 → fatos relevantes da RJ;
  BSLI → fatos relevantes do BRB e comunicados do BCB.
- Acompanhar (recomendação de `docs/monitor-besst/qualidade-dados.md` §5): edital da OPA da Desktop, 2ª etapa da OPA
  da EMAE, balanços/aumento de capital do BRB, AGC da Ambipar, Light pós-RJ.

## 6. Como validar
```python
import json
s = json.load(open("dados/besst/situacoes_especiais.json", encoding="utf-8"))
u = {p["ticker"] for p in json.load(open("dados/besst/universo.json", encoding="utf-8"))["papeis"]}
CAMPOS = {"tickers", "empresa", "tipo", "data", "descricao", "texto_iniciante", "fonte", "confianca"}
for c in s["casos"]:
    falta = CAMPOS - set(c)
    fora = [t for t in c["tickers"] if t not in u]
    if falta or fora or c["tipo"] not in s["tipos"]:
        print(c["empresa"], "faltam campos:", falta, "| fora do universo:", fora, "| tipo:", c["tipo"])
print("atualizado:", s["atualizado"], "|", len(s["casos"]), "casos")
```
Depois rode `python3 scripts/besst_painel.py` (sem `--coletar`; veja o aviso sobre o selo no RB 01 §7) e confira:
```python
import json
p = {x["ticker"]: x for x in json.load(open("dados/besst/painel.json", encoding="utf-8"))["papeis"]}
for t in ["XXXX3"]:   # tickers alterados
    print(t, p[t].get("nivel_alerta"), p[t]["status"], p[t].get("situacao_especial"))
```
Esperado: caso aberto → `grave`, status `nao_se_aplica` (ou `sem_cotacao`), `situacao_especial` preenchido.
Caso removido → o alerta some (o nível passa a depender dos outros alertas).

## 7. Como publicar (commit)
```bash
git add dados/besst/situacoes_especiais.json dados/besst/painel.json manutencao/registro.md
git commit -m "Manutenção: situações especiais — <empresa>: <tipo> (fonte: <documento>)"
git pull --rebase && git push
```
(Se preferir não commitar o `painel.json`, a rotina diária recalcula no fim do dia.)

## 8. Se a fonte mudar ou falhar
- **IPE fora do ar ou com atraso** (atualização é semanal): use o RAD (consulta por empresa, categoria "Fato Relevante")
  e o RI. Para algo urgente (OPA hoje), o RI e o comunicado da B3 saem no mesmo dia.
- **Colunas do IPE mudaram:** confira `meta_ipe_cia_aberta.txt` e ajuste os nomes no snippet.
- **Nenhuma fonte primária encontrada:** não abra o caso só com portal; se a imprensa reconhecida noticiar algo grave
  (ex.: suspensão de negociação), abra com `confianca: "media"` e troque a fonte em até 7 dias.

## 9. Registro de execuções
Em `manutencao/registro.md`.

## 10. Riscos e cuidados
- O alerta é por **ticker exato**: esquecer uma classe (ex.: só BSLI4) deixa a outra (BSLI3) sem alerta.
- `situacao_especial` torna o papel `grave` mesmo sem cotação: um papel deslistado continua aparecendo no painel até
  sair do universo (RB 03).
- RJ/falência mudam de estado por decisão judicial (liminares): registre sempre a data e o número do documento.
- Não escreva juízo de compra/venda no `texto_iniciante` (Res. CVM 20/2021): descreva o fato e o efeito no teto.

## Lições da 1ª execução (03/11/2026)

Todas aceitas pelos juízes; a nº 4 só em parte (sem campos novos por ora) e a nº 11 com ajuste: o recálculo de teste usa `BESST_BASE` apontando para uma cópia de `dados/besst`. Até a próxima revisão do texto, estas lições prevalecem sobre as seções que citam.

| # | Problema encontrado | Texto proposto |
|---|---|---|
| 1 | **Acesso:** no ambiente de IA, `curl`/Python recebem 403 de CVM, B3 e RI. O WebFetch abre a listagem de `dados.cvm.gov.br`, links diretos de documentos do RAD e PDFs de RI em `api.mziq.com`, mas não abre zip/CSV ("binary data"), `ri.*.com.br` nem tjrj.jus.br. O snippet do §5.1 não roda aqui. | §8, novo item: "**Ambiente sem acesso à CVM (IA):** o §5.1 não roda. Busque na web por `rad.cvm.gov.br ENETCONSULTA <empresa> <assunto>` e pelos PDFs de RI (`api.mziq.com/mzfilemanager`): os links diretos de documento abrem por leitura de página. Registre em `registro.md` que a varredura do IPE ficou pendente." |
| 2 | **URL do RAD mudou:** `frmConsultaExternaCVM.aspx` em `/ENET/` foi aposentado e redireciona para `https://www.rad.cvm.gov.br/ENETWeb/frmConsultaExternaCVM.aspx`. Os links de documento usam `/ENETCONSULTA/frmDownloadDocumento.aspx?...`. | §4, linha 1b: trocar a URL e acrescentar "link citável do documento: `https://www.rad.cvm.gov.br/ENETCONSULTA/frmDownloadDocumento.aspx?Tela=99&numSequencia=…&numVersao=1&numProtocolo=…&descTipo=IPE&CodigoInstituicao=1`". |
| 3 | **Confiança mal definida:** o §5.2 só define confiança ao **abrir** caso. A carga inicial marcou `alta` em 7 de 8 casos com fonte de portal, o que contradiz a regra. Não está dito o que fazer quando o documento primário prova só **parte** do fato (ex.: edital da OPA, mas não o resultado do leilão). | §5.3, nova linha: "`confianca` vale para **o fato descrito no estado atual**: `alta` só se a `fonte` primária comprova o estado atual (ex.: resultado do leilão, sentença, ofício). Se a fonte primária comprova só a origem e a imprensa comprova o desfecho → `media`. Revise a confiança em toda revisão mensal." |
| 4 | **Um único campo `fonte`:** não cabe "primária + reforço". Por isso descrições com dois documentos acabam com a imprensa na `fonte`. | Opcional (o script ignora campos extras): campo `fontes_reforco: [url, …]` e `consultado_em: "AAAA-MM-DD"` por caso. Se o dono não quiser campo novo: citar o nº do documento primário na `descricao`. |
| 5 | **Desfecho que não está na tabela §5.3:** OPA sem adesão seguida de **incorporação de ações** (EMAE). Também falta o caso "papel deixou de existir sem OPA". | §5.3, nova linha: "OPA sem adesão / incorporação de ações / resgate → `tipo: \"incorporacao_concluida\"` (ou `opa_concluida`), data da consumação, último pregão na `descricao`; RB 03 para tirar o papel do universo; remover o caso quando o papel sair do universo." Acrescentar `incorporacao_concluida` à lista de tipos do §3. |
| 6 | **Restrição por emissor, não por ticker:** o leilão permanente da B3 (atraso de informações) vale para todas as classes do emissor. A carga inicial dizia "BSLI4 só negocia em leilão". | §10, novo risco: "Medidas da B3 por atraso de informações periódicas (leilão permanente) alcançam **todas** as classes do emissor; confira o comunicado da B3 e não só a notícia sobre uma classe." |
| 7 | **"Cancelamento de registro" ≠ "fim da negociação":** Neoenergia, Oi e Desktop continuam (ou continuarão) registradas na CVM após sair da bolsa. As OPAs de conversão A→B tiram o papel da bolsa sem `SIT = CANCELADA`. | §4, linha 1c: "Atenção: após OPA de conversão A→B ou cancelamento de listagem, `SIT` continua ATIVO; use `CATEG_REG = Categoria B`, `Data_Fim_Negociacao` no FCA ou o ofício da B3." |
| 8 | **Comunicados da B3 sem número na imprensa:** nem o leilão permanente do BRB nem o da Ambipar trazem número de ofício nas notícias, e a área de comunicados da B3 não abre aqui. | §4, linha 1d: dizer onde fica o comunicado (página da empresa em "Empresas listadas" → aba "Avisos/Comunicados") e aceitar o comunicado da companhia no RAD que cita a medida da B3 como alternativa. |
| 9 | **Gatilho de caso novo ambíguo:** "edital/leilão/resultado de OPA" não diz se a **decisão** da controladora (antes do pedido de registro) já abre caso. A carga inicial abriu DESK3 nessa fase. | §5.2: "Abra `opa_pendente` quando houver fato relevante/comunicado da companhia sobre OPA para fechamento, conversão de registro ou saída do Novo Mercado (não espere o registro da CVM); `confianca` conforme a regra do item 3." |
| 10 | **Pendências do §5.4 desatualizadas:** EMAE ("2ª etapa da OPA") e OIBR ("abrir o ofício") já mudaram. | Reescrever o §5.4 com a tabela da seção 1 deste relatório e marcar com data. |
| 11 | **Validação §6 exige o repositório**, e o recálculo do painel muda `painel.json`. Não há modo de "conferir uma cópia". | §6: aceitar o caminho do arquivo como argumento (`ARQ = sys.argv[1] if len(sys.argv) > 1 else "dados/besst/situacoes_especiais.json"`). |
