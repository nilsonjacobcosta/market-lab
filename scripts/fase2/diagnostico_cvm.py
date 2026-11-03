"""Fase 2 (teste): inspeciona a estrutura real dos arquivos de Dados Abertos da CVM.

Grava dados/besst/fase2_teste/diagnostico.json com: arquivos dentro de cada ZIP, colunas de cada CSV,
amostra de linhas do FCA (valores mobiliários) e as contas de DRE/BP/DFC de algumas empresas de referência.
Só biblioteca padrão. Não altera o painel.
"""
import csv, io, json, sys, urllib.request, zipfile
from pathlib import Path

CVM = "https://dados.cvm.gov.br/dados/CIA_ABERTA"
SAIDA = Path(__file__).resolve().parents[2] / "dados" / "besst" / "fase2_teste"
CACHE = Path(".cache_cvm")
UA = {"User-Agent": "market-lab (Monitor BESST, teste fase 2)"}
REF = {"TAEE": "Taesa", "BBAS": "Banco do Brasil", "BBSE": "BB Seguridade", "SAPR": "Sanepar", "VIVT": "Telefônica"}


def baixar(url):
    CACHE.mkdir(exist_ok=True)
    d = CACHE / url.rsplit("/", 1)[1]
    if not d.exists():
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
            d.write_bytes(r.read())
    return d


def cab(z, nome, n=3):
    with z.open(nome) as f:
        rd = csv.reader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";")
        h = next(rd)
        return h, [next(rd, None) for _ in range(n)]


def main():
    out = {"erros": []}
    try:
        cad = baixar(CVM + "/CAD/DADOS/cad_cia_aberta.csv").read_bytes().decode("latin-1").splitlines()
        out["cad_colunas"] = cad[0].split(";")
        out["cad_linhas"] = len(cad)
    except Exception as e:
        out["erros"].append(f"cad: {e}")
    for tipo, ano in (("FCA", 2026), ("FCA", 2025), ("DFP", 2025), ("ITR", 2026)):
        url = f"{CVM}/DOC/{tipo}/DADOS/{tipo.lower()}_cia_aberta_{ano}.zip"
        try:
            z = zipfile.ZipFile(baixar(url))
        except Exception as e:
            out["erros"].append(f"{tipo} {ano}: {e}")
            continue
        info = {}
        for nome in z.namelist():
            try:
                h, amostra = cab(z, nome, 2)
                info[nome] = {"colunas": h, "amostra": amostra}
            except Exception as e:
                info[nome] = {"erro": str(e)}
        out[f"{tipo}_{ano}"] = info
        if tipo == "FCA":
            vm = [n for n in z.namelist() if "valor_mobiliario" in n.lower()]
            achados = {}
            for n in vm:
                with z.open(n) as f:
                    for r in csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";"):
                        txt = ";".join(r.values()).upper()
                        for raiz in REF:
                            if raiz in txt and raiz not in achados:
                                achados[raiz] = r
            out[f"{tipo}_{ano}_valor_mobiliario_exemplos"] = achados
    # contas de referência: CD_CVM a partir do cadastro (por nome)
    try:
        rows = list(csv.DictReader(io.StringIO("\n".join(cad)), delimiter=";"))
        cds = {}
        for raiz, nome in REF.items():
            for r in rows:
                if nome.upper() in (r.get("DENOM_SOCIAL", "") + r.get("DENOM_COMERC", "")).upper() and r.get("SIT", "").upper().startswith("ATIVO"):
                    cds[raiz] = r.get("CD_CVM")
                    break
        out["cd_cvm_referencia"] = cds
        z = zipfile.ZipFile(baixar(f"{CVM}/DOC/DFP/DADOS/dfp_cia_aberta_2025.zip"))
        contas = {}
        for nome in z.namelist():
            if not nome.endswith(".csv") or "_con_" not in nome:
                continue
            demo = nome.split("_cia_aberta_")[1].rsplit("_", 1)[0]
            with z.open(nome) as f:
                for r in csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";"):
                    for raiz, cd in cds.items():
                        if r.get("CD_CVM", "").lstrip("0") == str(cd).lstrip("0") and r.get("ORDEM_EXERC", "").upper().startswith("ÚLTIMO"[:2]) and r["CD_CONTA"].count(".") <= 2:
                            contas.setdefault(raiz, {}).setdefault(demo, []).append([r["CD_CONTA"], r["DS_CONTA"], r["VL_CONTA"], r.get("ESCALA_MOEDA")])
        out["contas_dfp2025_referencia"] = contas
    except Exception as e:
        out["erros"].append(f"contas: {e}")
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "diagnostico.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print("erros:", out["erros"])


if __name__ == "__main__":
    main()
