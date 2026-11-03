"""Monitor BESST — fase 2 (TESTE): indicadores de qualidade financeira a partir dos Dados Abertos da CVM.

Versão 2 (02/11/2026), com as 11 correções exigidas pelo parecer dos juízes sobre o 1º teste
(docs/monitor-besst/parecer-teste-fase2.md):
  1. usa a demonstração INDIVIDUAL quando a empresa não entrega a consolidada;
  2. mapa ticker -> CD_CVM por CNPJ (cadastro + índice da própria DFP/ITR), FCA de 3 anos, CSV manual e log do motivo;
  3. lucro zero/ausente = "indisponível" (nunca nota 0);
  4. payout só com proventos aos acionistas da própria empresa, de preferência os DECLARADOS sobre o lucro do
     exercício (DVA, "remuneração de capitais próprios"); o fluxo de caixa (excluindo não controladores) é só reserva;
  5. ROE com patrimônio médio na MESMA janela do lucro de 12 meses; ROE vazio se patrimônio <= 0;
  6. LTM nunca cai para o dado anual em silêncio (marca "ltm_incompleto");
  7. dado com mais de 15 meses não recebe nota;
  8. limites de sanidade: "verificar" (mostra) e "descartado" (não entra na nota);
  9. FCF yield com o arquivo composicao_capital ligado por CNPJ;
 10. download com tratamento de erro (uma falha não derruba a execução) e modo de falha forçada para teste;
 11. textos: o número é LUCRO CONTÁBIL (IFRS/Cosif) e nada aqui é recomendação.

Uso: python3 fundamentos_cvm.py --painel dados/besst/painel.json --saida fundamentos.json
Variável FASE2_FORCAR_FALHA="dfp_cia_aberta_2024.zip" simula falha de download desse arquivo.
Só biblioteca padrão. Material educativo, não é recomendação de investimento.
"""
import argparse
import csv
import io
import json
import os
import re
import unicodedata
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

CVM = "https://dados.cvm.gov.br/dados/CIA_ABERTA"
URL_DFP = CVM + "/DOC/DFP/DADOS/dfp_cia_aberta_{ano}.zip"
URL_ITR = CVM + "/DOC/ITR/DADOS/itr_cia_aberta_{ano}.zip"
URL_FCA = CVM + "/DOC/FCA/DADOS/fca_cia_aberta_{ano}.zip"
URL_CAD = CVM + "/CAD/DADOS/cad_cia_aberta.csv"
FINANCEIROS = {"Bancos", "Seguros"}
ESCALA = {"MIL": 1000.0, "UNIDADE": 1.0}
DEMOS = ("BPA", "BPP", "DRE", "DFC_MI", "DFC_MD", "DVA")
MAX_MESES = 15

FAIXAS = {
    "Bancos":           {"roe": ("alto", 15, 10), "payout": ("faixa", (25, 60), 80)},
    "Seguros":          {"roe": ("alto", 15, 10), "payout": ("faixa", (25, 75), 95)},
    "Energia":          {"roe": ("alto", 12, 8), "div_liq_ebitda": ("baixo", 3.0, 4.0), "payout": ("faixa", (25, 80), 100)},
    "Saneamento":       {"roe": ("alto", 10, 6), "div_liq_ebitda": ("baixo", 2.5, 3.5), "payout": ("faixa", (25, 60), 90)},
    "Telecomunicações": {"fcf_yield": ("alto", 6, 3), "div_liq_ebitda": ("baixo", 2.0, 3.0), "payout": ("faixa", (25, 100), 120)},
}
# (verificar se fora de [a, b]; descartar se fora de [c, d])
SANIDADE = {"roe": (-30, 60, -100, 150), "payout": (0, 110, 0, 150),
            "div_liq_ebitda": (-3, 6, -10, 15), "fcf_yield": (-20, 25, -60, 60)}
LOG = {"downloads_falhos": [], "mapa": {}}


def norm(s):
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower().strip()


def so_digitos(s):
    return re.sub(r"\D", "", s or "")


def baixar(url, cache):
    """Baixa com cache. Devolve None (e registra) se falhar — nunca derruba a execução."""
    nome = url.rsplit("/", 1)[1]
    try:
        if nome in os.environ.get("FASE2_FORCAR_FALHA", "").split(","):
            raise OSError("falha forçada para teste")
        cache.mkdir(parents=True, exist_ok=True)
        dest = cache / nome
        if not dest.exists():
            req = urllib.request.Request(url, headers={"User-Agent": "market-lab (Monitor BESST)"})
            with urllib.request.urlopen(req, timeout=300) as r:
                dest.write_bytes(r.read())
        if nome.endswith(".zip"):
            zipfile.ZipFile(dest).close()
        return dest
    except Exception as e:
        print("download falhou:", nome, e)
        LOG["downloads_falhos"].append(f"{nome}: {e}")
        return None


def ler_csv(zpath, padrao, filtro=None):
    """Lê do ZIP os CSVs cujo nome casa com a regex `padrao`."""
    with zipfile.ZipFile(zpath) as z:
        for nome in z.namelist():
            if re.search(padrao, nome, re.I):
                with z.open(nome) as f:
                    for row in csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";"):
                        if filtro is None or filtro(row):
                            yield nome, row


# ---------- 1) ticker -> CD_CVM ----------
def indice_cnpj(zips, cache):
    """CNPJ (só dígitos) -> CD_CVM, a partir do índice das DFP/ITR (quem entregou) e do cadastro (todos os registros)."""
    cnpj_cd, nomes = {}, {}
    for z in zips:
        for _, r in ler_csv(z, r"_cia_aberta_\d{4}\.csv$"):
            cnpj_cd[so_digitos(r["CNPJ_CIA"])] = r["CD_CVM"].lstrip("0")
    cad = baixar(URL_CAD, cache)
    if cad:
        for r in csv.DictReader(io.StringIO(cad.read_bytes().decode("latin-1")), delimiter=";"):
            cn, cd = so_digitos(r.get("CNPJ_CIA")), (r.get("CD_CVM") or "").lstrip("0")
            ativo = (r.get("SIT") or "").upper().startswith("ATIVO")
            if cd and (cn not in cnpj_cd or ativo):
                cnpj_cd.setdefault(cn, cd)
            nomes[cd] = r.get("DENOM_SOCIAL", "")
    return cnpj_cd, nomes


def mapa_tickers(raizes, cache, ano, cnpj_cd, manual):
    mapa, motivo = {}, {}
    if manual and Path(manual).exists():
        for r in csv.DictReader(open(manual, encoding="utf-8"), delimiter=";"):
            if r.get("raiz") and r.get("cd_cvm"):
                mapa[r["raiz"].strip().upper()] = r["cd_cvm"].strip().lstrip("0")
                motivo[r["raiz"].strip().upper()] = "CSV manual"
    vistos = {}
    for a in (ano, ano - 1, ano - 2):
        z = baixar(URL_FCA.format(ano=a), cache)
        if not z:
            continue
        for _, r in ler_csv(z, r"valor_mobiliario"):
            cods = [(r.get("Codigo_Negociacao") or "").strip().upper()]
            cods += re.findall(r"[A-Z]{4}\d{1,2}", (r.get("Composicao_BDR_Unit") or "").upper())
            for tk in cods:
                if len(tk) >= 5 and tk[:4] in raizes:
                    cn = so_digitos(r.get("CNPJ_Companhia"))
                    vistos.setdefault(tk[:4], set()).add(cn)
                    cd = cnpj_cd.get(cn)
                    if cd and tk[:4] not in mapa:
                        mapa[tk[:4]] = cd
                        motivo[tk[:4]] = f"FCA {a} ({tk})"
    for rz in sorted(set(raizes) - set(mapa)):
        motivo[rz] = (f"CNPJ {', '.join(sorted(vistos[rz]))} no FCA, mas sem CD_CVM no cadastro/DFP" if rz in vistos
                      else "nenhum código de negociação no FCA dos últimos 3 anos (deslistado? incluir no CSV manual)")
    LOG["mapa"] = motivo
    return mapa


# ---------- 2) leitura das demonstrações ----------
def carregar(zpath, cds, ordens=("ULTIMO",)):
    """{(cd, ordem, dt_fim, dt_ini, demo, tipo): {cd_conta: (ds, valor R$)}}, consolidado e individual, última versão."""
    dados, versao = {}, {}
    padrao = r"_(" + "|".join(DEMOS) + r")_(con|ind)_\d{4}\.csv$"
    for nome, r in ler_csv(zpath, padrao, lambda r: r["CD_CVM"].lstrip("0") in cds
                           and norm(r["ORDEM_EXERC"]).upper() in ordens):
        demo, tipo = re.search(padrao, nome).groups()
        demo = demo[:3]  # DFC_MI/DFC_MD -> DFC
        chave = (r["CD_CVM"].lstrip("0"), norm(r["ORDEM_EXERC"]).upper(), r["DT_FIM_EXERC"],
                 r.get("DT_INI_EXERC", ""), demo, tipo)
        v = int(r.get("VERSAO") or 1)
        if versao.get((chave, r["CD_CONTA"]), 0) > v:
            continue
        versao[(chave, r["CD_CONTA"])] = v
        val = float(r["VL_CONTA"] or 0) * ESCALA.get((r.get("ESCALA_MOEDA") or "").upper(), 1.0)
        dados.setdefault(chave, {})[r["CD_CONTA"]] = (norm(r["DS_CONTA"]), val)
    return dados


def tem_dre(por_ano):
    """True se há DRE com valores não nulos (para preferir a consolidada; correção 1)."""
    return any(any(v for _, v in d.get("DRE", {}).values()) for d in por_ano.values())


def nivel(cod):
    return cod.count(".") + 1


def achar(contas, padrao, niv=None, prefixo="", ultimo=False, excluir=None):
    hits = [(c, v) for c, (d, v) in sorted(contas.items())
            if re.search(padrao, d) and c.startswith(prefixo) and (niv is None or nivel(c) == niv)
            and not (excluir and re.search(excluir, d))]
    return (hits[-1] if ultimo else hits[0])[1] if hits else None


def somar(contas, padrao, niv=None, prefixo="", excluir=None):
    tot = [v for c, (d, v) in contas.items() if re.search(padrao, d) and c.startswith(prefixo)
           and (niv is None or nivel(c) == niv) and not (excluir and re.search(excluir, d))]
    return sum(tot) if tot else None


def nz(x):
    """Zero exato em conta de lucro = campo não preenchido (correção 3)."""
    return None if x is None or x == 0 else x


def proventos_declarados(dva):
    """JCP + dividendos da 'remuneração de capitais próprios' da DVA (competência), sem não controladores."""
    pais = [c for c, (d, _) in dva.items() if re.search(r"remuneracao de capita(is|l) propri", d)]
    if not pais:
        return None
    pai = sorted(pais)[0]
    filhos = [v for c, (d, v) in dva.items() if c.startswith(pai + ".") and nivel(c) == nivel(pai) + 1
              and re.search(r"dividend|juros sobre( o)? capital", d) and not re.search(r"nao controlador", d)]
    return sum(filhos) if filhos else None


def fluxo(dre, dfc, dva=None):
    ll = nz(achar(dre, r"atribuid[oa].*(controlador|socios da)", niv=3, excluir=r"nao controlador"))
    base_ll = "controladores"
    if ll is None:
        ll = nz(achar(dre, r"(lucro|prejuizo|resultado) liquido|lucro.*(periodo|exercicio)", niv=2, ultimo=True))
        base_ll = "total (sem quebra controlador)" if ll is not None else None
    ebit = achar(dre, r"antes do resultado financeiro", niv=2)
    da = somar(dfc, r"deprecia|amortiza|exaust", prefixo="6.01", excluir=r"custo de capta|agio|desagio")
    prov_caixa = somar(dfc, r"dividend|juros sobre( o)? capital", prefixo="6.03",
                       excluir=r"nao controlador|minoritari|recebid")
    fco = achar(dfc, r"operaciona", niv=2)
    capex = somar(dfc, r"(aquisi|adic|compra|investimento).*(imobilizado|intangivel)", prefixo="6.02")
    return dict(ll=ll, base_ll=base_ll, ebit=ebit, da=abs(da) if da else None,
                prov_caixa=abs(prov_caixa) if prov_caixa else None,
                prov_decl=proventos_declarados(dva or {}), fco=fco, capex=abs(capex) if capex else None)


def balanco(bpa, bpp):
    pl = achar(bpp, r"patrimonio liquido", niv=2)
    minor = achar(bpp, r"nao controlador", niv=3)
    divida = somar(bpp, r"^emprestimos e financiamentos", niv=3)
    caixa = (achar(bpa, r"^caixa e equivalentes", niv=3) or 0) + (achar(bpa, r"^aplicacoes financeiras", niv=3) or 0)
    return dict(pl=(pl - (minor or 0)) if pl is not None else None, divida=divida, caixa=caixa)


def ltm(anual, ytd, ytd_ant, chaves=("ll", "ebit", "da", "fco", "capex")):
    """12 meses = ano fechado + acumulado do ano − acumulado do ano anterior. Sem fallback silencioso (correção 6)."""
    out, faltou = {}, []
    for k in chaves:
        a, b, c = anual.get(k), ytd.get(k), ytd_ant.get(k)
        if None in (a, b, c):
            out[k] = None
            if a is not None:
                faltou.append(k)
        else:
            out[k] = a + b - c
    out["base_ll"] = ytd.get("base_ll") or anual.get("base_ll")
    return out, faltou


# ---------- 3) métricas, semáforos e nota ----------
def cor(valor, regra):
    if valor is None:
        return "cinza"
    tipo, a, b = regra
    if tipo == "alto":
        return "verde" if valor >= a else "vermelho" if valor < b else "amarelo"
    if tipo == "baixo":
        return "verde" if valor <= a else "vermelho" if valor > b else "amarelo"
    lo, hi = a
    return "verde" if lo <= valor <= hi else "vermelho" if valor > b or valor < 0 else "amarelo"


def nota(setor, m, flags):
    sem = {k: cor(m.get(k) if k not in m.get("descartados", []) else None, r) for k, r in FAIXAS[setor].items()}
    if m.get("ll") is None:
        flags.append("lucro_indisponivel")
        return sem, None
    if "dado_antigo" in flags:
        return sem, None
    ok = [c for c in sem.values() if c != "cinza"]
    if len(ok) < 2:
        return sem, None
    pts = sum(1 if c == "verde" else 0.5 if c == "amarelo" else 0 for c in ok)
    n = round(3 * pts / len(ok))
    if m["ll"] < 0:
        n = 0
    elif "vermelho" in ok and n > 1:
        n = 1
    return sem, n


def meses_entre(ref, hoje):
    y, mth = int(ref[:4]), int(ref[5:7])
    return (hoje.year - y) * 12 + hoje.month - mth


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--painel", default="dados/besst/painel.json")
    ap.add_argument("--saida", default="fundamentos.json")
    ap.add_argument("--log", default=None)
    ap.add_argument("--cache", default=".cache_cvm")
    ap.add_argument("--mapa-manual", default="dados/besst/mapa_ticker_cvm.csv")
    ap.add_argument("--anos", type=int, default=3)
    a = ap.parse_args()
    cache, hoje = Path(a.cache), date.today()
    papeis = json.loads(Path(a.painel).read_text())["papeis"]
    raizes = {p["ticker"][:4] for p in papeis}

    zdfp = {ano: baixar(URL_DFP.format(ano=ano), cache) for ano in range(hoje.year - a.anos, hoje.year)}
    zitr = {ano: baixar(URL_ITR.format(ano=ano), cache) for ano in (hoje.year - 1, hoje.year)}
    zips = [z for z in list(zdfp.values()) + list(zitr.values()) if z]
    cnpj_cd, nomes = indice_cnpj(zips, cache)
    mapa = mapa_tickers(raizes, cache, hoje.year, cnpj_cd, a.mapa_manual)
    cds = set(mapa.values())

    anuais, acoes = {}, {}
    for ano, z in sorted(zdfp.items()):
        if not z:
            continue
        for (cd, _, fim, ini, demo, tipo), contas in carregar(z, cds).items():
            anuais.setdefault((cd, tipo), {}).setdefault(fim[:4], {}).setdefault(demo, {}).update(contas)
        for _, r in ler_csv(z, r"composicao_capital"):
            cd = cnpj_cd.get(so_digitos(r.get("CNPJ_CIA")))
            if cd in cds:
                try:
                    acoes[cd] = float(r["QT_ACAO_TOTAL_CAP_INTEGR"]) - float(r.get("QT_ACAO_TOTAL_TESOURO") or 0)
                except (KeyError, ValueError):
                    pass
    # ITR: ytd (DT_INI = 1º/jan) do ano corrente e do anterior; BP de cada trimestre (para PL na mesma janela)
    itr = {}
    for ano, z in sorted(zitr.items()):
        if not z:
            continue
        for (cd, ordem, fim, ini, demo, tipo), contas in carregar(z, cds, ("ULTIMO",)).items():
            if demo in ("DRE", "DFC", "DVA") and not ini.endswith("-01-01"):
                continue
            itr.setdefault((cd, tipo), {}).setdefault(fim, {}).setdefault(demo, {}).update(contas)

    saida = {}
    for p in papeis:
        tk, setor = p["ticker"], p["setor"]
        cd = mapa.get(tk[:4])
        if not cd:
            saida[tk] = {"erro": "sem CD_CVM", "motivo": LOG["mapa"].get(tk[:4])}
            continue
        tipos = {}
        for (c, t) in anuais:
            if c == cd:
                tipos[t] = anuais[(c, t)]
        if not tipos:
            saida[tk] = {"erro": "sem DFP", "cd_cvm": cd, "empresa_cvm": nomes.get(cd)}
            continue
        tipo = "con" if "con" in tipos and tem_dre(tipos["con"]) else "ind" if "ind" in tipos else "con"
        anos = sorted(tipos[tipo])
        d, dant = tipos[tipo][anos[-1]], tipos[tipo].get(anos[-2], {}) if len(anos) > 1 else {}
        fa = fluxo(d.get("DRE", {}), d.get("DFC", {}), d.get("DVA", {}))
        ba, bant = balanco(d.get("BPA", {}), d.get("BPP", {})), balanco(dant.get("BPA", {}), dant.get("BPP", {}))
        flags, m = [], {}

        # janela de 12 meses
        trims = itr.get((cd, tipo), {})
        atual = max((f for f in trims if f[:4] > anos[-1]), default=None)
        f12, b_fim, b_ini, ref, base = fa, ba, bant, anos[-1] + "-12-31", "exercício " + anos[-1]
        if atual:
            ant = f"{int(atual[:4]) - 1}{atual[4:]}"
            x, y = trims[atual], trims.get(ant)
            if y:
                fl, faltou = ltm(fa, fluxo(x.get("DRE", {}), x.get("DFC", {})), fluxo(y.get("DRE", {}), y.get("DFC", {})))
                if fl["ll"] is not None:
                    f12, ref, base = fl, atual, "12 meses até " + atual
                    b_fim, b_ini = balanco(x.get("BPA", {}), x.get("BPP", {})), balanco(y.get("BPA", {}), y.get("BPP", {}))
                    flags += [f"ltm_incompleto:{k}" for k in faltou]
                else:
                    flags.append("ltm_incompleto:ll (usado o exercício fechado)")
            else:
                flags.append(f"sem ITR de {ant} (usado o exercício fechado)")

        m["ll"] = f12["ll"]
        m["base_lucro"] = f"lucro contábil, {f12.get('base_ll') or 'indisponível'}"
        # ROE: patrimônio médio do início e do fim da MESMA janela (correção 5)
        pi, pf = b_ini.get("pl"), b_fim.get("pl")
        if m["ll"] is not None and pf:
            if pf <= 0 or (pi is not None and pi <= 0):
                flags.append("patrimonio_negativo")
                m["roe"] = None
            else:
                pl_med = (pi + pf) / 2 if pi else pf
                if not pi:
                    flags.append("roe_sem_pl_inicial")
                m["roe"] = round(100 * m["ll"] / pl_med, 1)
        # payout do último exercício fechado (correção 4)
        if fa["ll"] and fa["ll"] > 0 and (fa["prov_decl"] or fa["prov_caixa"]):
            if fa["prov_decl"]:
                m["payout"], m["base_payout"] = round(100 * fa["prov_decl"] / fa["ll"], 1), f"declarado (DVA) {anos[-1]}"
            else:
                m["payout"], m["base_payout"] = round(100 * fa["prov_caixa"] / fa["ll"], 1), f"pago em caixa (DFC) {anos[-1]}"
        if setor not in FINANCEIROS:
            dl = (b_fim["divida"] or 0) - (b_fim["caixa"] or 0)
            ebitda = (f12["ebit"] or 0) + (f12["da"] or 0) if f12.get("ebit") is not None else None
            m["div_liq_ebitda"] = round(dl / ebitda, 2) if ebitda and ebitda > 0 else None
            m["div_liq_pl"] = round(dl / b_fim["pl"], 2) if b_fim["pl"] and b_fim["pl"] > 0 else None
            if acoes.get(cd) and p.get("preco") and f12.get("fco") is not None and f12.get("capex") is not None:
                m["fcf_yield"] = round(100 * (f12["fco"] - f12["capex"]) / (acoes[cd] * p["preco"]), 1)
        # sanidade (correção 8)
        m["descartados"] = []
        for k, (va, vb, da_, db) in SANIDADE.items():
            v = m.get(k)
            if v is None:
                continue
            if not (da_ <= v <= db):
                m["descartados"].append(k)
                flags.append(f"descartado:{k}={v}")
            elif not (va <= v <= vb):
                flags.append(f"verificar:{k}={v}")
        idade = meses_entre(ref, hoje)
        if idade > MAX_MESES:
            flags.append(f"dado_antigo:{idade}_meses")
        if tipo == "ind":
            flags.append("demonstracao_individual")
        m["semaforo"], m["nota"] = nota(setor, m, flags)
        m.update(cd_cvm=cd, empresa_cvm=nomes.get(cd), demonstracao="consolidada" if tipo == "con" else "individual",
                 referencia=ref, base=base, mapeamento=LOG["mapa"].get(tk[:4]), flags=flags)
        if not m["descartados"]:
            m.pop("descartados")
        saida[tk] = m
    Path(a.saida).write_text(json.dumps(saida, ensure_ascii=False, indent=1))
    if a.log:
        Path(a.log).write_text(json.dumps(LOG, ensure_ascii=False, indent=1))
    com = sum(1 for v in saida.values() if "erro" not in v)
    print(len(saida), "papéis;", com, "com dados;", sum(1 for v in saida.values() if v.get("nota") is not None),
          "com nota; downloads falhos:", len(LOG["downloads_falhos"]))


if __name__ == "__main__":
    main()
