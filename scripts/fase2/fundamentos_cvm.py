"""Monitor BESST — esboço de coleta de QUALIDADE FINANCEIRA na CVM (Dados Abertos).

STATUS: ESBOÇO NÃO TESTADO CONTRA OS ARQUIVOS REAIS (o ambiente de escrita não tinha internet).
  Verificado na web (02/11/2026): URLs/nomes dos ZIPs (dfp_cia_aberta_AAAA.zip, itr_cia_aberta_AAAA.zip,
  fca_cia_aberta_AAAA.zip, cad_cia_aberta.csv) e colunas das demonstrações (CNPJ_CIA, DT_REFER, VERSAO,
  DENOM_CIA, CD_CVM, GRUPO_DFP, MOEDA, ESCALA_MOEDA, ORDEM_EXERC, DT_INI_EXERC, DT_FIM_EXERC, CD_CONTA,
  DS_CONTA, VL_CONTA; CSV ';' latin-1).
  NÃO verificado (marcado com # TODO-VERIFICAR): nomes dos CSVs dentro do ZIP do FCA e suas colunas
  (CNPJ_Companhia, Codigo_Negociacao), colunas do cadastro e o texto exato de algumas contas.
  Por isso as contas são localizadas por DESCRIÇÃO (regex) + nível do código, não por código fixo:
  o plano de contas de bancos e seguradoras difere do das empresas não financeiras.

Uso (no GitHub Actions, com internet):
  python3 fundamentos_cvm.py --painel dados/besst/painel.json --saida dados/besst/fundamentos.json
Saída: {ticker: {roe, payout, div_liq_ebitda, div_liq_pl, fcf_yield, semaforos, nota, ...}}
Só biblioteca padrão (mesmo estilo de scripts/besst_painel.py).
"""
import argparse
import csv
import io
import json
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

# Faixas do semáforo: (verde se melhor que a, vermelho se pior que b); "alto" = quanto maior melhor.
FAIXAS = {
    "Bancos":           {"roe": ("alto", 15, 10), "payout": ("faixa", (25, 60), 80)},
    "Seguros":          {"roe": ("alto", 15, 10), "payout": ("faixa", (25, 75), 95)},
    "Energia":          {"roe": ("alto", 12, 8), "div_liq_ebitda": ("baixo", 3.0, 4.0), "payout": ("faixa", (25, 80), 100)},
    "Saneamento":       {"roe": ("alto", 10, 6), "div_liq_ebitda": ("baixo", 2.5, 3.5), "payout": ("faixa", (25, 60), 90)},
    "Telecomunicações": {"fcf_yield": ("alto", 6, 3), "div_liq_ebitda": ("baixo", 2.0, 3.0), "payout": ("faixa", (25, 100), 120)},
}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return s.lower().strip()


def baixar(url, cache):
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / url.rsplit("/", 1)[1]
    if not dest.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "market-lab (Monitor BESST)"})
        with urllib.request.urlopen(req, timeout=180) as r:
            dest.write_bytes(r.read())
    return dest


def ler_csv(zpath, trecho, filtro=None):
    """Lê do ZIP o(s) CSV(s) cujo nome contém `trecho` (ex.: 'DRE_con'); filtra linhas por função."""
    with zipfile.ZipFile(zpath) as z:
        for nome in z.namelist():
            if trecho.lower() in nome.lower():
                with z.open(nome) as f:
                    for row in csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"), delimiter=";"):
                        if filtro is None or filtro(row):
                            yield row


# ---------- 1) ticker -> CD_CVM ----------
def acoes_emitidas(zpath, cds):
    """Total de ações ex-tesouraria por CD_CVM (para FCF yield). TODO-VERIFICAR nome do CSV e colunas."""
    out = {}
    for r in ler_csv(zpath, "composicao_capital", lambda r: r.get("CD_CVM", "").lstrip("0") in cds):
        try:
            tot = float(r["QT_ACAO_TOTAL_CAP_INTEGR"]) - float(r.get("QT_ACAO_TOTAL_TESOURO") or 0)
        except (KeyError, ValueError):
            continue
        out[r["CD_CVM"].lstrip("0")] = tot
    return out


def mapa_tickers(raizes, cache, ano, manual=None):
    """Raiz do ticker (4 letras) -> CD_CVM. Todas as classes (3/4/5/6/11) da mesma raiz = mesmo emissor."""
    mapa = {}
    if manual and Path(manual).exists():  # CSV raiz;cd_cvm mantido à mão tem prioridade
        for r in csv.DictReader(open(manual, encoding="utf-8"), delimiter=";"):
            mapa[r["raiz"].upper()] = r["cd_cvm"]
    cnpj_cd = {}
    for r in csv.DictReader(io.StringIO(baixar(URL_CAD, cache).read_bytes().decode("latin-1")), delimiter=";"):
        if r.get("SIT", "").upper().startswith("ATIVO"):  # TODO-VERIFICAR colunas SIT/CNPJ_CIA/CD_CVM
            cnpj_cd[r["CNPJ_CIA"]] = r["CD_CVM"].lstrip("0")
    for a in (ano, ano - 1):  # FCA do ano corrente pode ainda estar incompleto
        try:
            z = baixar(URL_FCA.format(ano=a), cache)
        except Exception as e:
            print("FCA", a, "indisponível:", e)
            continue
        # TODO-VERIFICAR: arquivo fca_cia_aberta_valor_mobiliario_AAAA.csv e colunas abaixo
        for r in ler_csv(z, "valor_mobiliario"):
            tk = (r.get("Codigo_Negociacao") or "").strip().upper()
            cd = cnpj_cd.get(r.get("CNPJ_Companhia", ""))
            if len(tk) >= 5 and cd and tk[:4] in raizes:
                mapa.setdefault(tk[:4], cd)
    faltam = sorted(set(raizes) - set(mapa))
    if faltam:
        print("Sem CD_CVM (incluir no CSV manual):", " ".join(faltam))
    return mapa


# ---------- 2) leitura das demonstrações ----------
def carregar(zpath, cds, ordem="ULTIMO"):
    """{(cd_cvm, dt_fim, dt_ini, demo): {cd_conta: (ds_conta, valor_em_R$)}} — só consolidado, última versão."""
    dados, versao = {}, {}
    for demo in ("BPA_con", "BPP_con", "DRE_con", "DFC_MI_con", "DFC_MD_con"):
        for r in ler_csv(zpath, demo, lambda r: r["CD_CVM"].lstrip("0") in cds
                         and norm(r["ORDEM_EXERC"]).upper() == ordem):
            chave = (r["CD_CVM"].lstrip("0"), r["DT_FIM_EXERC"], r.get("DT_INI_EXERC", ""), demo[:3])
            v = int(r.get("VERSAO") or 1)
            if versao.get((chave, r["CD_CONTA"]), 0) > v:
                continue
            versao[(chave, r["CD_CONTA"])] = v
            val = float(r["VL_CONTA"] or 0) * ESCALA.get(r["ESCALA_MOEDA"].upper(), 1.0)
            dados.setdefault(chave, {})[r["CD_CONTA"]] = (norm(r["DS_CONTA"]), val)
    return dados


def nivel(cod):
    return cod.count(".") + 1


def achar(contas, padrao, niv=None, prefixo="", ultimo=False):
    hits = [(c, v) for c, (d, v) in sorted(contas.items())
            if re.search(padrao, d) and c.startswith(prefixo) and (niv is None or nivel(c) == niv)]
    return (hits[-1] if ultimo else hits[0])[1] if hits else None


def somar(contas, padrao, niv=None, prefixo="", excluir=None):
    tot = [v for c, (d, v) in contas.items() if re.search(padrao, d) and c.startswith(prefixo)
           and (niv is None or nivel(c) == niv) and not (excluir and re.search(excluir, d))]
    return sum(tot) if tot else None


def fluxo(dre, dfc):
    """Itens de resultado/fluxo de UM período (ano ou acumulado no ano)."""
    ll = achar(dre, r"atribuid[oa].*(controlador|socios da)", niv=3)
    if ll is None:  # sem quebra controlador/minoritário: último total de lucro de nível 2
        ll = achar(dre, r"(lucro|prejuizo|resultado) liquido|lucro.*(periodo|exercicio)", niv=2, ultimo=True)
    ebit = achar(dre, r"antes do resultado financeiro", niv=2)  # só existe no layout não financeiro
    da = somar(dfc, r"deprecia|amortiza|exaust", prefixo="6.01", excluir=r"custo de capta|agio|desagio")
    prov = somar(dfc, r"dividend|juros sobre( o)? capital", prefixo="6.03")
    fco = achar(dfc, r"operaciona", niv=2)
    capex = somar(dfc, r"(aquisi|adic|compra|investimento).*(imobilizado|intangivel)", prefixo="6.02")
    return dict(ll=ll, ebit=ebit, da=abs(da) if da else None, prov=abs(prov) if prov else None,
                fco=fco, capex=abs(capex) if capex else None)


def balanco(bpa, bpp):
    pl = achar(bpp, r"patrimonio liquido", niv=2)
    minor = achar(bpp, r"nao controlador", niv=3)
    divida = somar(bpp, r"^emprestimos e financiamentos", niv=3)  # 2.01.04 + 2.02.01 (inclui debêntures)
    caixa = (achar(bpa, r"^caixa e equivalentes", niv=3) or 0) + (achar(bpa, r"^aplicacoes financeiras", niv=3) or 0)
    return dict(pl=(pl - (minor or 0)) if pl is not None else None, divida=divida, caixa=caixa)


def ltm(anual, ytd, ytd_ant):
    """Últimos 12 meses = ano fechado + acumulado do ano − acumulado do ano anterior."""
    out = {}
    for k in anual:
        a, b, c = anual.get(k), ytd.get(k), ytd_ant.get(k)
        out[k] = a + b - c if None not in (a, b, c) else a
    return out


# ---------- 3) métricas, semáforos e nota ----------
def cor(metrica, valor, regra):
    if valor is None:
        return "cinza"
    tipo, a, b = regra
    if tipo == "alto":
        return "verde" if valor >= a else "vermelho" if valor < b else "amarelo"
    if tipo == "baixo":
        return "verde" if valor <= a else "vermelho" if valor > b else "amarelo"
    lo, hi = a  # payout: faixa saudável; acima de b ou negativo = vermelho
    return "verde" if lo <= valor <= hi else "vermelho" if valor > b or valor < 0 else "amarelo"


def nota(setor, m):
    """Nota 0–3: verde=1, amarelo=0,5, vermelho=0, reescalada pelo nº de métricas disponíveis."""
    sem = {k: cor(k, m.get(k), r) for k, r in FAIXAS[setor].items()}
    ok = [c for c in sem.values() if c != "cinza"]
    if len(ok) < 2:
        return sem, None  # dado insuficiente: mostrar "sem nota", nunca "nota baixa"
    pts = sum(1 if c == "verde" else 0.5 if c == "amarelo" else 0 for c in ok)
    n = round(3 * pts / len(ok))
    if (m.get("ll") or 0) <= 0 or "vermelho" in ok and n > 1:  # prejuízo zera; um vermelho limita a 1
        n = 0 if (m.get("ll") or 0) <= 0 else 1
    return sem, n


def calcular(cd, setor, anual, ult, preco, acoes=None):
    f = ltm(anual["f"], ult["ytd"], ult["ytd_ant"]) if ult else anual["f"]
    b = ult["b"] if ult else anual["b"]
    pl_med = (b["pl"] + anual["b_ant"]["pl"]) / 2 if b["pl"] and anual.get("b_ant", {}).get("pl") else b["pl"]
    m = dict(ll=f["ll"])
    m["roe"] = round(100 * f["ll"] / pl_med, 1) if f["ll"] is not None and pl_med else None
    m["payout"] = round(100 * f["prov"] / f["ll"], 0) if f["prov"] and f["ll"] and f["ll"] > 0 else None
    if setor not in FINANCEIROS:  # dívida não faz sentido no balanço de banco/seguradora
        dl = (b["divida"] or 0) - (b["caixa"] or 0)
        ebitda = (f["ebit"] or 0) + (f["da"] or 0) if f["ebit"] is not None else None
        m["div_liq_ebitda"] = round(dl / ebitda, 2) if ebitda and ebitda > 0 else None
        m["div_liq_pl"] = round(dl / b["pl"], 2) if b["pl"] else None
        # aproximação: preço desta classe × total de ações (distorce se as classes valem muito diferente)
        if acoes and preco and f["fco"] is not None and f["capex"] is not None:
            m["fcf_yield"] = round(100 * (f["fco"] - f["capex"]) / (acoes * preco), 1)
    m["semaforo"], m["nota"] = nota(setor, m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--painel", default="dados/besst/painel.json")
    ap.add_argument("--saida", default="fundamentos.json")
    ap.add_argument("--cache", default=".cache_cvm")
    ap.add_argument("--mapa-manual", default="dados/besst/mapa_ticker_cvm.csv")
    ap.add_argument("--anos", type=int, default=3)
    a = ap.parse_args()
    cache, hoje = Path(a.cache), date.today()
    papeis = json.loads(Path(a.painel).read_text())["papeis"]
    raizes = {p["ticker"][:4] for p in papeis}
    mapa = mapa_tickers(raizes, cache, hoje.year, a.mapa_manual)
    cds = set(mapa.values())

    # DFP dos últimos N anos fechados (o do ano corrente só existe a partir de ~março)
    anuais, acoes = {}, {}
    for ano in range(hoje.year - a.anos, hoje.year):
        zdfp = baixar(URL_DFP.format(ano=ano), cache)
        acoes.update(acoes_emitidas(zdfp, cds))  # fica o ano mais recente
        for (cd, fim, ini, demo), contas in carregar(zdfp, cds).items():
            anuais.setdefault((cd, fim[:4]), {}).setdefault(demo, {}).update(contas)
    # ITR mais recente (ano corrente): acumulado do ano (DT_INI = 1º/jan) + mesmo período do ano anterior
    itr = {}
    try:
        z = baixar(URL_ITR.format(ano=hoje.year), cache)
        for ordem, rot in (("ULTIMO", "atual"), ("PENULTIMO", "ant")):
            for (cd, fim, ini, demo), contas in carregar(z, cds, ordem).items():
                if demo in ("DRE", "DFC") and not ini.endswith("-01-01"):
                    continue  # descarta a coluna "só o trimestre"
                if rot == "ant" and demo in ("BPA", "BPP"):
                    continue  # no BP o PENÚLTIMO é o 31/12 anterior, já coberto pela DFP
                itr.setdefault(cd, {}).setdefault((rot, fim), {}).setdefault(demo, {}).update(contas)
    except Exception as e:
        print("ITR indisponível:", e)

    saida = {}
    for p in papeis:
        cd = mapa.get(p["ticker"][:4])
        anos_cd = sorted(k[1] for k in anuais if k[0] == cd)
        if not cd or not anos_cd:
            saida[p["ticker"]] = {"erro": "sem dados CVM"}
            continue
        d = anuais[(cd, anos_cd[-1])]
        dant = anuais.get((cd, anos_cd[-2]), {}) if len(anos_cd) > 1 else {}
        an = dict(f=fluxo(d.get("DRE", {}), d.get("DFC", {})), b=balanco(d.get("BPA", {}), d.get("BPP", {})),
                  b_ant=balanco(dant.get("BPA", {}), dant.get("BPP", {})))
        ult = None
        if cd in itr:
            atual = max(k for k in itr[cd] if k[0] == "atual")
            ant = [k for k in itr[cd] if k[0] == "ant" and k[1][5:] == atual[1][5:]]
            x, y = itr[cd][atual], itr[cd][ant[0]] if ant else {}
            if y:
                ult = dict(ytd=fluxo(x.get("DRE", {}), x.get("DFC", {})), ytd_ant=fluxo(y.get("DRE", {}), y.get("DFC", {})),
                           b=balanco(x.get("BPA", {}), x.get("BPP", {})), ref=atual[1])
        m = calcular(cd, p["setor"], an, ult, p.get("preco"), acoes.get(cd))
        m.update(cd_cvm=cd, referencia=ult["ref"] if ult else anos_cd[-1] + "-12-31", base="LTM" if ult else "DFP")
        saida[p["ticker"]] = m
    Path(a.saida).write_text(json.dumps(saida, ensure_ascii=False, indent=1))
    print(len(saida), "papéis;", sum(1 for v in saida.values() if v.get("nota") is not None), "com nota")


if __name__ == "__main__":
    main()
