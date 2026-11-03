"""Fase 2: investiga emissores sem mapeamento ou com dado antigo (por nome) nos índices da CVM."""
import csv, io, json, re, sys, unicodedata, urllib.request, zipfile
from pathlib import Path
CVM = "https://dados.cvm.gov.br/dados/CIA_ABERTA"
CACHE = Path(".cache_cvm"); CACHE.mkdir(exist_ok=True)
NOMES = ["BTG PACTUAL", "COSERN", "CELPE", "EQUATORIAL PARA", "CEEE", "ELETROPAULO", "OMEGA", "COMERC", "IGUA",
         "ALIANCA DA BAHIA", "ABC BRASIL", "ALFA", "BRISANET", "BANCO PAN", "BRB", "ELETROPAR", "AMBIPAR", "CELGPAR",
         "NEOENERGIA PERNAMBUCO", "NEOENERGIA COSERN", "EQUATORIAL"]
n = lambda s: unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()
def baixar(u):
    d = CACHE / u.rsplit("/", 1)[1]
    if not d.exists():
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "market-lab"}), timeout=300) as r:
            d.write_bytes(r.read())
    return d
def casa(txt):
    return [k for k in NOMES if k in n(txt)]
out = {"cad": [], "indices": [], "fca": []}
for r in csv.DictReader(io.StringIO(baixar(CVM + "/CAD/DADOS/cad_cia_aberta.csv").read_bytes().decode("latin-1")), delimiter=";"):
    if casa(r["DENOM_SOCIAL"] + " " + r["DENOM_COMERC"]):
        out["cad"].append({k: r[k] for k in ("CNPJ_CIA", "DENOM_SOCIAL", "SIT", "CD_CVM", "CATEG_REG", "DT_CANCEL", "MOTIVO_CANCEL")})
for tipo, anos in (("DFP", (2023, 2024, 2025)), ("ITR", (2025, 2026))):
    for a in anos:
        z = zipfile.ZipFile(baixar(f"{CVM}/DOC/{tipo}/DADOS/{tipo.lower()}_cia_aberta_{a}.zip"))
        with z.open(f"{tipo.lower()}_cia_aberta_{a}.csv") as f:
            for r in csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";"):
                if casa(r["DENOM_CIA"]):
                    out["indices"].append([tipo, a, r["CNPJ_CIA"], r["DENOM_CIA"], r["CD_CVM"], r["DT_REFER"], r["VERSAO"]])
        # contagem de linhas DRE por CD para os casos
for a in (2024, 2025, 2026):
    z = zipfile.ZipFile(baixar(f"{CVM}/DOC/FCA/DADOS/fca_cia_aberta_{a}.zip"))
    with z.open(f"fca_cia_aberta_valor_mobiliario_{a}.csv") as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";"):
            if casa(r["Nome_Empresarial"]):
                out["fca"].append([a, r["CNPJ_Companhia"], r["Nome_Empresarial"], r["Valor_Mobiliario"], r["Codigo_Negociacao"], r["Composicao_BDR_Unit"], r["Mercado"], r["Data_Fim_Negociacao"]])
Path("dados/besst/fase2_teste/diagnostico_mapa.json").write_text(json.dumps(out, ensure_ascii=False, indent=0))
print({k: len(v) for k, v in out.items()})
