# RB 05 — Mapa ticker → CVM (`dados/besst/mapa_ticker_cvm.csv`)

**Última revisão deste runbook:** 2026-11-03 · **Responsável:** Nilson (dono)

## 1. Objetivo
Garantir que cada empresa do universo seja ligada ao seu código na CVM (`CD_CVM`), para que a qualidade financeira
(beta) ache os balanços dela. O mapeamento é automático na maior parte dos casos; o CSV guarda só as **exceções**
que o automático não resolve (hoje 3: BPAC, EQPA, BRIT).

## 2. Quando fazer (gatilhos)
- A rotina de qualidade acusa **"sem CD_CVM"**: em `aceite.json`, a lista `sem_mapeamento` não está vazia, ou
  `emissores_mapeados_pct (meta >=95)` caiu abaixo de 95 (o aceite reprova e **nada é publicado** — ver RB 07).
- Um papel em `fundamentos.json` tem `"erro": "sem CD_CVM"` (mesmo que não reprove o aceite, se for papel sem cotação).
- Mudança de ticker, incorporação ou reorganização societária (RB 03 §5.6).
- Revisão trimestral (RB 08): conferir se as exceções continuam necessárias.

## 3. Arquivos afetados
| Arquivo | Campos | Quem lê |
|---|---|---|
| `dados/besst/mapa_ticker_cvm.csv` | separador `;`, UTF-8, cabeçalho `raiz;cd_cvm;observacao` | `scripts/fase2/fundamentos_cvm.py`, função `mapa_tickers` (opção `--mapa-manual`, padrão `dados/besst/mapa_ticker_cvm.csv`) |

Como o mapeamento funciona (código real):
1. Lê o CSV manual primeiro (`raiz` em maiúsculas → `cd_cvm` sem zeros à esquerda; motivo "CSV manual"). **O CSV vence o automático.**
2. Para as raízes restantes, lê o FCA dos 3 últimos anos (`fca_cia_aberta_valor_mobiliario_AAAA.csv`: colunas
   `Codigo_Negociacao` e códigos dentro de `Composicao_BDR_Unit`) e pega o `CNPJ_Companhia`.
3. Converte CNPJ → `CD_CVM` usando os índices das DFP/ITR baixadas e o cadastro (`cad_cia_aberta.csv`, preferindo `SIT` ATIVO).
4. O que sobra recebe um motivo, gravado em `LOG["mapa"]` e no papel (`"motivo"`):
   - `"CNPJ <n> no FCA, mas sem CD_CVM no cadastro/DFP"` → a empresa está no FCA, mas o CNPJ não casa com o índice;
   - `"nenhum código de negociação no FCA dos últimos 3 anos (deslistado? incluir no CSV manual)"`.

Exceções atuais e motivo (do próprio CSV):
| raiz | cd_cvm | Por quê |
|---|---|---|
| BPAC | 22616 | BTG Pactual (CNPJ 30.306.294/0001-45): o FCA lista as units sem código de negociação (aparece "000000") |
| EQPA | 18309 | Equatorial Pará (CNPJ 04.895.728/0001-80): o FCA ainda usa os códigos antigos CELP3/5/6/7 |
| BRIT | 27693 | Brisanet: a holding Brisanet Participações (CD 26085) foi **cancelada em 2024-12-04 por incorporação** (cadastro CVM, `diagnostico_mapa.json`); a listada passou a ser a Brisanet Serviços (CD 27693, código BRST3 no FCA 2025). Quando BRIT3 sair do universo (RB 03), esta linha pode ser apagada |

## 4. Fontes, em ordem de confiança
| Ordem | Fonte | URL | O que procurar |
|---|---|---|---|
| 1a | CVM — cadastro | `https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv` — **verificada** | `CNPJ_CIA`, `DENOM_SOCIAL`, `CD_CVM`, `SIT`, `CATEG_REG` |
| 1b | CVM — índice da DFP/ITR | `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_AAAA.zip` → `dfp_cia_aberta_AAAA.csv` (`CNPJ_CIA`, `DT_REFER`, `VERSAO`, `DENOM_CIA`, `CD_CVM`) | se aquele `CD_CVM` **entregou** balanço |
| 1c | CVM — FCA `valor_mobiliario` | `.../DOC/FCA/DADOS/fca_cia_aberta_AAAA.zip` | qual CNPJ declara o ticker |
| 2 | RI / FRE da empresa | — | reorganização societária (quem é a listada) |

## 5. Passo a passo
1. Descubra quais raízes falharam e o motivo:
   - na aba **Actions** → execução de "Atualizar qualidade financeira (BETA)" → passo **Medir aceite** → lista `sem_mapeamento`; ou
   - rode **Fase 2 - teste de fundamentos (CVM)** (RB 07 §5.2) e abra `dados/besst/fase2_teste/aceite.json`
     (`sem_mapeamento`) e `dados/besst/fase2_teste/log_execucao.json` (chave `mapa`: motivo de cada raiz).
2. Se o motivo for "nenhum código no FCA": a empresa provavelmente saiu da bolsa ou trocou de código → **primeiro** RB 03.
   Só mapeie no CSV se o papel continuar no universo.
3. Ache o CNPJ e os `CD_CVM` candidatos (troque o nome):
```python
import csv, io, re, urllib.request
URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"
txt = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "market-lab manutencao"}), timeout=300).read().decode("latin-1")
NOME = "BRISANET"                       # parte do nome, em maiúsculas e sem acento funciona melhor
for r in csv.DictReader(io.StringIO(txt), delimiter=";"):
    if NOME in (r["DENOM_SOCIAL"] + " " + r["DENOM_COMERC"]).upper():
        print(r["CNPJ_CIA"], r["CD_CVM"], r["DENOM_SOCIAL"][:50], r["SIT"], r["CATEG_REG"], r["DT_CANCEL"], r["MOTIVO_CANCEL"][:40])
```
4. Confirme qual `CD_CVM` entrega DFP/ITR (o que tiver balanço recente é o certo):
```python
import csv, io, urllib.request, zipfile
CD = {"27693", "26085"}                 # candidatos (sem zeros à esquerda)
for tipo, ano in (("DFP", 2025), ("ITR", 2026)):
    u = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/{tipo}/DADOS/{tipo.lower()}_cia_aberta_{ano}.zip"
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "market-lab"}), timeout=300).read()))
    with z.open(f"{tipo.lower()}_cia_aberta_{ano}.csv") as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";"):
            if r["CD_CVM"].lstrip("0") in CD:
                print(tipo, ano, r["CD_CVM"], r["DENOM_CIA"], r["DT_REFER"], "versão", r["VERSAO"])
```
   (Cada ZIP tem dezenas de MB. Alternativa local: `python3 scripts/fase2/diagnostico_mapa.py` depois de acrescentar o
   nome à lista `NOMES` no topo do script; ele grava `dados/besst/fase2_teste/diagnostico_mapa.json` com cadastro,
   índices DFP/ITR e FCA dos nomes procurados. **Cuidado:** ele e o `diagnostico_cvm.py` guardam os downloads da CVM
   em `.cache_cvm/` na pasta atual, que **não** está no `.gitignore` — nunca use `git add .`/`git add -A`; adicione só
   os arquivos citados no §7.)
5. Acrescente a linha no CSV, sem `;` dentro da observação:
```
XXXX;12345;Nome S.A. (CNPJ 00.000.000/0001-00): motivo em uma frase e documento conferido
```
6. Se uma exceção antiga deixou de ser necessária (o FCA passou a ter o código certo), apague a linha: assim o
   mapeamento volta a acompanhar a CVM sozinho.

## 6. Como validar
- Rode **Fase 2 - teste de fundamentos (CVM)** (RB 07 §5.2). Em `dados/besst/fase2_teste/aceite.json`:
  `sem_mapeamento` = `[]` e `emissores_mapeados_pct (meta >=95)` ≥ 95 (era 100,0 em 03/11/2026).
- Em `dados/besst/fase2_teste/fundamentos.json`, o papel tem `cd_cvm`, `empresa_cvm` e
  `"mapeamento": "CSV manual"`, sem `"erro"`.

## 7. Como publicar (commit)
```bash
git add dados/besst/mapa_ticker_cvm.csv manutencao/registro.md
git commit -m "Manutenção: mapa ticker→CVM — <RAIZ> → CD <n> (<motivo>; conferido no cadastro e na DFP <ano>)"
git pull --rebase && git push
```
A publicação do `fundamentos.json` acontece na próxima execução de "Atualizar qualidade financeira (BETA)"
(07h43 ou 19h13) ou disparando-a pelo botão **Run workflow** (RB 07 §5.3).

## 8. Se a fonte mudar ou falhar
- O FCA mudou nomes de colunas (`Codigo_Negociacao`, `Composicao_BDR_Unit`, `CNPJ_Companhia`): o mapeamento
  automático inteiro cai e `emissores_mapeados_pct` despenca. Rode `python3 scripts/fase2/diagnostico_cvm.py` (grava as
  colunas reais em `dados/besst/fase2_teste/diagnostico.json`) e ajuste `mapa_tickers` em `fundamentos_cvm.py`
  (mudança de código: peça revisão). **Não** tente compensar com dezenas de linhas no CSV.
- Cadastro fora do ar: o script ainda usa os índices DFP/ITR; o aceite dirá se basta.

## 9. Registro de execuções
Em `manutencao/registro.md`.

## 10. Riscos e cuidados
- O CSV **sobrepõe** o automático: uma exceção esquecida após reorganização aponta para um CD que parou de entregar
  balanço → o papel fica com `dado_antigo` e sem nota. Revise o CSV todo trimestre (RB 08).
- Não mapeie papel deslistado só para "fechar a conta" do aceite: o aceite já ignora papéis sem cotação.
