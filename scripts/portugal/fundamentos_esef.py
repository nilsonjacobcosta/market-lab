#!/usr/bin/env python3
"""Monitor Portugal — qualidade financeira (BETA) a partir dos relatórios anuais ESEF (iXBRL).

Fontes:
  - GLEIF (api.gleif.org): ISIN -> LEI do emitente.
  - XBRL International, filings.xbrl.org: relatórios anuais em formato eletrónico europeu (ESEF), como entregues ao
    mecanismo oficial de cada país (em Portugal, o sistema de difusão da CMVM), com versão xBRL-JSON.

Indicadores (mesmas faixas e regra de nota 0–3 do Monitor BESST, fase 2):
  - ROE = lucro atribuível aos acionistas da empresa-mãe / média do capital próprio atribuível (início e fim do ano).
  - Payout declarado = DPA do exercício (cadastro oficial de proventos) / lucro por ação básico do mesmo exercício.
  - Dívida líquida / EBITDA = (empréstimos + locações − caixa) / (resultado operacional + depreciações e amortizações).
    Não se aplica a bancos.

Uso:
  python3 scripts/portugal/fundamentos_esef.py --descobrir           # imprime mapa LEI/relatórios/rubricas (diagnóstico)
  python3 scripts/portugal/fundamentos_esef.py --saida dados/portugal/fundamentos.json
"""
import argparse
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "dados" / "portugal"
UA = {"User-Agent": "Mozilla/5.0 (market-lab; estudo educativo)", "Accept": "application/json"}
FXO = "https://filings.xbrl.org"

SETOR_REGRA = {"Banca": "Bancos", "Energia": "Energia", "Energia renovável": "Energia", "Petróleo, gás e energia": "Energia",
               "Redes de energia (regulada)": "Energia", "Telecomunicações e media": "Telecomunicações"}
FAIXAS = {  # iguais ao Monitor BESST (scripts/fase2/fundamentos_cvm.py) + "Geral" para setores sem equivalente no BESST
    "Bancos": {"roe": ("alto", 15, 10), "payout": ("faixa", (25, 60), 80)},
    "Energia": {"roe": ("alto", 12, 8), "div_liq_ebitda": ("baixo", 3.0, 4.0), "payout": ("faixa", (25, 80), 100)},
    "Telecomunicações": {"roe": ("alto", 12, 8), "div_liq_ebitda": ("baixo", 2.0, 3.0), "payout": ("faixa", (25, 100), 120)},
    "Geral": {"roe": ("alto", 12, 8), "div_liq_ebitda": ("baixo", 2.5, 3.5), "payout": ("faixa", (25, 80), 100)},
}
SANIDADE = {"roe": (-30, 60, -100, 150), "payout": (0, 110, 0, 150), "div_liq_ebitda": (-3, 6, -10, 15)}
MAX_MESES = 18  # relatórios anuais: o de 2025 sai até abril de 2026 e vale até o seguinte

C = {  # rubricas ifrs-full, por ordem de preferência
    "ll": ["ProfitLossAttributableToOwnersOfParent", "ProfitLoss"],
    "pl": ["EquityAttributableToOwnersOfParent", "Equity"],
    "lpa": ["BasicEarningsLossPerShare", "BasicAndDilutedEarningsLossPerShare",
            "BasicEarningsLossPerShareFromContinuingOperations"],
    "op": ["ProfitLossFromOperatingActivities"],
    "lai": ["ProfitLossBeforeTax"],
    "desp_fin": ["FinanceCosts"],
    "rec_fin": ["FinanceIncome"],
    "fin_liq": ["FinanceIncomeCost"],
    "ll_total": ["ProfitLoss"],
    "ir": ["IncomeTaxExpenseContinuingOperations"],
    "da": ["DepreciationAmortisationAndImpairmentLossReversalOfImpairmentLossRecognisedInProfitOrLoss",
           "DepreciationAndAmortisationExpense",
           "AdjustmentsForDepreciationAndAmortisationExpenseAndImpairmentLossReversalOfImpairmentLossRecognisedInProfitOrLoss",
           "AdjustmentsForDepreciationAndAmortisationExpense",
           "DepreciationPropertyPlantAndEquipment"],
    "caixa": ["CashAndCashEquivalents", "Cash"],
    "div_pagos": ["DividendsPaidClassifiedAsFinancingActivities", "DividendsPaidToEquityHoldersOfParentClassifiedAsFinancingActivities",
                  "DividendsPaid", "DividendsRecognisedAsDistributionsToOwnersOfParent"],
}
# Dívida: soma de grupos; em cada grupo usa a 1.ª rubrica presente.
DIVIDA = {
    "emprestimos_total": ["Borrowings"],
    "emprestimos_nc": ["NoncurrentPortionOfNoncurrentBorrowings", "LongtermBorrowings", "NoncurrentFinancialLiabilities"],
    "emprestimos_c": ["CurrentBorrowingsAndCurrentPortionOfNoncurrentBorrowings", "ShorttermBorrowings",
                      "CurrentPortionOfLongtermBorrowings", "CurrentFinancialLiabilities"],
    "locacoes_total": ["LeaseLiabilities"],
    "locacoes_nc": ["NoncurrentLeaseLiabilities"],
    "locacoes_c": ["CurrentLeaseLiabilities"],
}
DIVIDA["outros_emprestimos_nc"] = ["NoncurrentPortionOfOtherNoncurrentBorrowings"]
DIVIDA["outros_emprestimos_c"] = ["OtherCurrentBorrowingsAndCurrentPortionOfOtherNoncurrentBorrowings"]
# Componentes detalhados: só somados quando a empresa NÃO apresenta os totais de empréstimos (evita dupla contagem).
DETALHE = {
    "bancarios_nc": ["NoncurrentPortionOfNoncurrentBankLoansReceived"],
    "bancarios_c": ["CurrentBankLoansReceivedAndCurrentPortionOfNoncurrentBankLoansReceived", "ShorttermBankLoansReceived"],
    "obrigacoes_nc": ["NoncurrentPortionOfNoncurrentBondsIssued"],
    "obrigacoes_c": ["CurrentBondsIssuedAndCurrentPortionOfNoncurrentBondsIssued"],
    "papel_nc": ["NoncurrentPortionOfNoncurrentCommercialPapersIssued"],
    "papel_c": ["CurrentCommercialPapersIssued", "CurrentPortionOfNoncurrentCommercialPapersIssued"],
    "outros_nc": ["NoncurrentPortionOfNoncurrentLoansReceived"],
    "outros_c": ["CurrentLoansReceivedAndCurrentPortionOfNoncurrentLoansReceived"],
}
# Rubricas próprias da empresa (extensões ESEF), conferidas à mão no relatório. Mapa explícito e auditável.
EXTENSOES = {
    "ALTR": {"emprestimos_extra": ["altri:EmprestimosBancariosCorrentes", "altri:EmprestimosBancariosNaoCorrentes"]},
    "EGL": {"emprestimos_extra": ["egl:EmprestimosComRecurso", "egl:EmprestimosComRecursoCorrente",
                                  "egl:EmprestimosSemRecurso", "egl:EmprestimosSemRecursoCorrente"]},
    "EDP": {"ebitda": ["edp:ResultadoLiquidoAntesDeProvisoesAmortizacoesEImparidadesProveitosFinanceirosECustosFinanceirosImpostosSobreOsLucrosEContribuicaoExtraordinariaParaOSectorEnergeticoCESE"]},
    "GALP": {"da": ["galp:AmortizacoesDepreciacoesEImparidadesEmAtivosFixos"]},
    "CTT": {"da": ["ctt:DepreciacoesAmortizacoesEImparidadeDeInvestimentosPerdasReversoes"]},
}
RX_DIVIDA_EXT = re.compile(r"(borrowing|debt|loan|bond|emprestim|financiament|obrigac)", re.I)


def get_json(url, tentativas=3):
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read())
        except Exception as e:
            if i == tentativas - 1:
                raise
            time.sleep(3 * (i + 1))


# ---------------------------------------------------------------- descoberta
NOMES = {  # padrões do nome registado no filings.xbrl.org (normalizado, maiúsculas, sem acentos)
    "ALTR": r"\bALTRI\b", "BCP": r"BANCO COMERCIAL PORTUGUES", "COR": r"CORTICEIRA AMORIM", "CTT": r"\bCTT\b",
    "EDP": r"^EDP[ ,-]+(S\.?A|ENERGIAS)", "EDPR": r"EDP RENEWABLES|EDP RENOVAVEIS", "EGL": r"MOTA\s*-?\s*ENGIL",
    "GALP": r"\bGALP\b", "IBS": r"IBERSOL", "JMT": r"JERONIMO MARTINS", "NOS": r"^NOS[ ,]+S\.?G\.?P\.?S",
    "NVG": r"NAVIGATOR", "RENE": r"REDES ENERGETICAS|^REN\b", "SEM": r"SEMAPA", "SON": r"^SONAE[ ,-]+S\.?G\.?P\.?S",
    "TDSA": r"TEIXEIRA DUARTE"}


def _norm(s):
    import unicodedata
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper().strip()


def todos_relatorios_pt():
    """Todos os relatórios ESEF com país PT, agrupados por LEI: {lei: {"nome":..., "relatorios":[...]}}."""
    f = urllib.parse.quote(json.dumps([{"name": "country", "op": "eq", "val": "PT"}]))
    pag, out = 1, {}
    while True:
        j = get_json(f"{FXO}/api/filings?filter={f}&include=entity&page%5Bsize%5D=100&page%5Bnumber%5D={pag}")
        ents = {e["id"]: e["attributes"] for e in j.get("included") or [] if e.get("type") == "entity"}
        for d in j.get("data") or []:
            a = d["attributes"]
            eid = ((d.get("relationships") or {}).get("entity") or {}).get("data", {}).get("id")
            ent = ents.get(eid) or {}
            lei = ent.get("identifier") or (a.get("fxo_id") or "").split("-")[0]
            g = out.setdefault(lei, {"nome": ent.get("name") or "", "relatorios": []})
            g["nome"] = g["nome"] or ent.get("name") or ""
            g["relatorios"].append({"periodo": a.get("period_end"), "fxo_id": a.get("fxo_id"), "json_url": a.get("json_url"),
                                    "report_url": a.get("report_url"), "viewer_url": a.get("viewer_url"),
                                    "publicado": a.get("date_added"), "erros": a.get("error_count")})
        if not (j.get("links") or {}).get("next") or not j.get("data"):
            break
        pag += 1
        time.sleep(0.5)
    for g in out.values():
        g["relatorios"].sort(key=lambda r: (r["periodo"] or "", r["publicado"] or ""), reverse=True)
    return out


def casar(papel, base, mapa):
    lei = (mapa.get(papel) or {}).get("lei")
    if lei and lei in base:
        return lei
    rx = re.compile(NOMES[papel])
    achados = [k for k, g in base.items() if rx.search(_norm(g["nome"]))]
    return achados[0] if len(achados) == 1 else (lei or None)


# ---------------------------------------------------------------- leitura de factos
def _per(p):
    """'2024-01-01T00:00:00/2025-01-01T00:00:00' -> ('d', '2024-01-01', '2024-12-31'); instante -> ('i', '2024-12-31')."""
    def dia(s):
        d = datetime.fromisoformat(s.replace("Z", ""))
        if s.endswith("T00:00:00"):
            d = d.fromordinal(d.toordinal() - 1)  # convenção xBRL-JSON: fim do dia = 00:00 do dia seguinte
        return d.strftime("%Y-%m-%d")
    if "/" in p:
        a, b = p.split("/")
        return ("d", a[:10], dia(b))
    return ("i", dia(p))


def indexar(doc):
    """Factos sem dimensões extra: {(conceito, periodo): valor}; guarda também o prefixo do conceito."""
    idx = {}
    for f in (doc.get("facts") or {}).values():
        dims = f.get("dimensions") or {}
        extra = [k for k in dims if k not in ("concept", "entity", "period", "unit", "language")]
        if extra or "period" not in dims:
            continue
        try:
            v = float(f.get("value"))
        except (TypeError, ValueError):
            continue
        conc = dims["concept"]
        idx.setdefault((conc, _per(dims["period"])), v)
    return idx


def pega(idx, nomes, periodo, ext=False):
    for n in nomes:
        for pref in ("ifrs-full:",):
            v = idx.get((pref + n, periodo))
            if v is not None:
                return v, pref + n
    return None, None


def periodos(ano):
    return ("d", f"{ano}-01-01", f"{ano}-12-31"), ("i", f"{ano}-12-31"), ("i", f"{ano - 1}-12-31")


def extrair(idx, ano, papel=None):
    dur, fim, ini = periodos(ano)
    r, origem = {}, {}
    for k in ("ll", "ll_total", "ir", "lpa", "op", "lai", "desp_fin", "rec_fin", "fin_liq", "da", "div_pagos"):
        r[k], origem[k] = pega(idx, C[k], dur)
    for k, per in (("pl", fim), ("pl_ini", ini), ("caixa", fim)):
        r[k], origem[k] = pega(idx, C["pl" if k.startswith("pl") else k], per)
    g = {k: pega(idx, v, fim) for k, v in DIVIDA.items()}
    emp = g["emprestimos_total"][0]
    partes = [g[k][0] for k in ("emprestimos_nc", "emprestimos_c", "outros_emprestimos_nc", "outros_emprestimos_c")]
    if emp is None and any(v is not None for v in partes):
        emp = sum(v or 0 for v in partes)
    if g["emprestimos_total"][0] is None and g["emprestimos_nc"][0] is None and g["emprestimos_c"][0] is None:
        det = {k: pega(idx, v, fim) for k, v in DETALHE.items()}
        if any(v[0] is not None for v in det.values()):
            emp = (emp or 0) + sum(v[0] or 0 for v in det.values())
            origem["divida_detalhe"] = {k: v[1] for k, v in det.items() if v[1]}
    ext = EXTENSOES.get(papel, {})
    extra = [idx.get((c, fim)) for c in ext.get("emprestimos_extra", [])]
    if any(v is not None for v in extra):
        emp = (emp or 0) + sum(v or 0 for v in extra)
        origem["divida_extensoes"] = [c for c, v in zip(ext["emprestimos_extra"], extra) if v is not None]
    for k in ("da", "ebitda"):
        for c in ext.get(k, []):
            v = idx.get((c, dur))
            if v is not None and (k == "ebitda" or r.get("da") is None):
                r[k], origem[k] = v, c
                break
    loc = g["locacoes_total"][0]
    if loc is None and (g["locacoes_nc"][0] is not None or g["locacoes_c"][0] is not None):
        loc = (g["locacoes_nc"][0] or 0) + (g["locacoes_c"][0] or 0)
    r["emprestimos"], r["locacoes"] = emp, loc
    r.setdefault("ebitda", None)
    origem["divida"] = {k: v[1] for k, v in g.items() if v[1]}
    # extensões da empresa que parecem dívida (só para diagnóstico/alerta, não entram na conta)
    ext = sorted({(c, round(v)) for (c, p), v in idx.items()
                  if p == fim and not c.startswith("ifrs-full:") and RX_DIVIDA_EXT.search(c.split(":")[-1])})
    r["_ext_divida"] = ext[:15]
    rx = re.compile(r"(Depreciation|Amorti|OperatingActivit|OperatingProfit|FinanceIncome|FinanceCost|Borrowing|EBITDA|Ebitda|Bond|Loan|Paper|Obrigac|Papel|Emprest|BeforeTax|IncomeTax)")
    r["_candidatos"] = sorted({(c, p[0], round(v)) for (c, p), v in idx.items()
                               if rx.search(c) and ((p[0] == "d" and p[2] == f"{ano}-12-31") or (p[0] == "i" and p[1] == f"{ano}-12-31"))})[:60]
    r["_origem"] = origem
    return r


# ---------------------------------------------------------------- métricas e nota
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


def nota(regra, m, flags):
    sem = {k: cor(m.get(k) if k not in m.get("descartados", []) else None, r) for k, r in FAIXAS[regra].items()}
    if m.get("ll") is None:
        flags.append("sem_nota:lucro_indisponivel")
        return sem, None
    if any(f.startswith("dado_antigo") for f in flags):
        flags.append("sem_nota:dado_antigo")
        return sem, None
    if m.get("descartados"):
        flags.append("sem_nota:metrica_fora_da_faixa_plausivel")
        return sem, None
    ok = [c for c in sem.values() if c != "cinza"]
    if len(ok) < 2:
        flags.append("sem_nota:indicadores_insuficientes")
        return sem, None
    pts = sum(1 if c == "verde" else 0.5 if c == "amarelo" else 0 for c in ok)
    n = int(3 * pts / len(ok) + 0.5)
    if m["ll"] < 0:
        n = 0
    elif "vermelho" in ok and n > 1:
        n = 1
    return sem, n


MOTIVO = {"lucro_indisponivel": "o lucro do exercício não foi encontrado no relatório eletrónico",
          "dado_antigo": "o último relatório anual tem mais de 18 meses",
          "metrica_fora_da_faixa_plausivel": "um indicador ficou fora da faixa plausível e precisa de conferência",
          "indicadores_insuficientes": "há menos de dois indicadores disponíveis",
          "sem_relatorio": "não foi encontrado relatório anual ESEF desta empresa"}


def dpa_exercicio(papel, ano):
    tot, achou = 0.0, False
    with open(DADOS / "proventos_oficiais.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["papel"] == papel and r["exercicio"] == str(ano) and r["tipo"] in ("dinheiro", "scrip"):
                tot += float(r["valor_bruto"]); achou = True
    return round(tot, 6) if achou else None


def metricas(papel, setor, dados_ano, dados_ant, ano, hoje):
    regra = SETOR_REGRA.get(setor, "Geral")
    flags, m = [], {"regra": regra, "exercicio": ano}
    d = dados_ano
    m["ll"] = d["ll"]
    if d["ll"] is not None and d["pl"] and d["pl_ini"]:
        m["roe"] = round(100 * d["ll"] / ((d["pl"] + d["pl_ini"]) / 2), 1)
    elif d["ll"] is not None and d["pl"]:
        m["roe"] = round(100 * d["ll"] / d["pl"], 1); flags.append("verificar:roe_sem_capital_inicial")
    if dados_ant and dados_ant.get("ll") is not None and dados_ant.get("pl") and dados_ant.get("pl_ini"):
        r2 = 100 * dados_ant["ll"] / ((dados_ant["pl"] + dados_ant["pl_ini"]) / 2)
        if m.get("roe") is not None:
            m["roe_medio_2a"] = round((m["roe"] + r2) / 2, 1)
    dpa = dpa_exercicio(papel, ano)
    if dpa is None and hoje.date() > datetime(ano + 1, 7, 31).date():
        dpa = 0.0; flags.append("info:sem_dividendo_cadastrado_para_o_exercicio")
    m["dpa_exercicio"], m["lpa"] = dpa, d["lpa"]
    if dpa is not None and d["lpa"] and d["lpa"] > 0:
        m["payout"] = round(100 * dpa / d["lpa"], 1)
    elif dpa is None:
        flags.append("payout:dpa_do_exercicio_nao_cadastrado")
    if d.get("div_pagos") and d["ll"] and d["ll"] > 0:
        m["payout_caixa"] = round(100 * abs(d["div_pagos"]) / d["ll"], 1)
    if regra != "Bancos":
        op = d["op"]
        if d.get("ebitda") is not None:
            op = None  # a empresa etiqueta o EBITDA: não reconstruir o resultado operacional
        elif op is None and d["lai"] is not None and d["fin_liq"] is not None:
            op = d["lai"] - d["fin_liq"]; flags.append("info:ebit_reconstruido_resultado_financeiro")
        elif op is None and d["lai"] is not None and d["desp_fin"] is not None:
            op = d["lai"] + abs(d["desp_fin"]) - abs(d["rec_fin"] or 0); flags.append("info:ebit_reconstruido_resultado_financeiro")
        elif op is None and d["ll_total"] is not None and d["ir"] is not None and d["desp_fin"] is not None:
            op = d["ll_total"] + d["ir"] + abs(d["desp_fin"]) - abs(d["rec_fin"] or 0)
            flags.append("verificar:ebit_reconstruido_lucro_impostos_financeiro")
        ebitda = op + abs(d["da"]) if op is not None and d["da"] is not None else None
        if d.get("ebitda") is not None:
            ebitda = d["ebitda"]; flags.append("info:ebitda_reportado_pela_empresa")
        m["ebitda"] = ebitda
        if d["emprestimos"] is None:
            flags.append("verificar:emprestimos_nao_identificados" + (":extensoes" if d["_ext_divida"] else ""))
        if d["emprestimos"] is not None and d["caixa"] is not None:
            dl = d["emprestimos"] + (d["locacoes"] or 0) - d["caixa"]
            m["divida_liquida"] = dl
            if ebitda and ebitda > 0:
                m["div_liq_ebitda"] = round(dl / ebitda, 2)
            if d["locacoes"] is None:
                flags.append("info:locacoes_nao_identificadas")
    m["descartados"] = []
    for k, (va, vb, da_, db) in SANIDADE.items():
        v = m.get(k)
        if v is None:
            continue
        if not (da_ <= v <= db):
            m["descartados"].append(k); flags.append(f"descartado:{k}={v}")
        elif not (va <= v <= vb):
            flags.append(f"verificar:{k}={v}")
    idade = (hoje.year - ano) * 12 + hoje.month - 12
    if idade > MAX_MESES:
        flags.append(f"dado_antigo:{idade}_meses")
    m["semaforo"], m["nota"] = nota(regra, m, flags)
    m["nota_provisoria"] = m["nota"] is not None and any(f.startswith("verificar") for f in flags)
    if m["nota"] is None:
        sn = [f.split(":", 1)[1] for f in flags if f.startswith("sem_nota:")]
        m["motivo_sem_nota"] = MOTIVO.get(sn[0], sn[0]) if sn else MOTIVO["indicadores_insuficientes"]
    if not m["descartados"]:
        m.pop("descartados")
    m["flags"] = flags
    return m


# ---------------------------------------------------------------- principal
def escolher(lista, ano):
    """Do mesmo período, prefere a versão consolidada (tem lucro atribuível à empresa-mãe) e a mais recente."""
    return sorted([r for r in lista if (r["periodo"] or "").startswith(str(ano))],
                  key=lambda r: r["publicado"] or "", reverse=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--descobrir", action="store_true")
    ap.add_argument("--saida", default=str(DADOS / "fundamentos.json"))
    a = ap.parse_args()
    universo = json.loads((DADOS / "universo.json").read_text(encoding="utf-8"))
    hoje = datetime.now(timezone.utc)
    mapa_arq = DADOS / "mapa_lei.csv"
    mapa = {}
    if mapa_arq.exists():
        with open(mapa_arq, encoding="utf-8") as f:
            mapa = {r["papel"]: r for r in csv.DictReader(f)}
    saida = {"beta": True, "gerado_em": hoje.strftime("%Y-%m-%d %H:%M"),
             "fonte": "Relatórios anuais ESEF (iXBRL) via filings.xbrl.org; LEI via GLEIF",
             "aviso": "Material educativo, não é recomendação de investimento. Faixas são convenções do painel.",
             "papeis": {}}
    novos_mapa = []
    base = todos_relatorios_pt()
    print("Entidades PT no filings.xbrl.org:", len(base))
    if a.descobrir:
        for k, g in sorted(base.items(), key=lambda x: x[1]["nome"]):
            print(f"  {k}  {g['nome']}  ({len(g['relatorios'])} relatórios; último {g['relatorios'][0]['periodo'] if g['relatorios'] else '-'})")
    for p in universo["papeis"]:
        t = p["papel"]
        try:
            lei = casar(t, base, mapa)
            nome_lei = (base.get(lei) or {}).get("nome", "")
            novos_mapa.append({"papel": t, "isin": p["isin"], "lei": lei or "", "nome_lei": nome_lei or ""})
            if not lei:
                saida["papeis"][t] = {"erro": "LEI não encontrado", "nota": None, "motivo_sem_nota": MOTIVO["sem_relatorio"]}
                print(t, "sem LEI"); continue
            rel = (base.get(lei) or {}).get("relatorios") or []
            anos = sorted({int(r["periodo"][:4]) for r in rel if r.get("periodo")}, reverse=True)
            if a.descobrir:
                print(f"\n=== {t} {p['nome']} LEI {lei} ({nome_lei}) — relatórios: {[r['fxo_id'] for r in rel[:6]]}")
            if not anos:
                saida["papeis"][t] = {"erro": "sem relatório ESEF", "lei": lei, "nota": None,
                                      "motivo_sem_nota": MOTIVO["sem_relatorio"]}
                continue
            dados, usado = {}, {}
            for ano in anos[:2]:
                for cand in escolher(rel, ano):
                    doc = get_json(FXO + cand["json_url"])
                    idx = indexar(doc)
                    d = extrair(idx, ano, t)
                    if d["ll"] is not None or ano not in dados:
                        dados[ano], usado[ano] = d, cand
                    if d["_origem"].get("ll") == "ifrs-full:ProfitLossAttributableToOwnersOfParent":
                        break  # consolidado encontrado
                    time.sleep(0.5)
            ano = anos[0]
            m = metricas(t, p["setor"], dados[ano], dados.get(ano - 1), ano, hoje)
            m.update({"lei": lei, "relatorio": usado[ano]["fxo_id"],
                      "relatorio_url": FXO + (usado[ano].get("viewer_url") or usado[ano].get("report_url") or ""),
                      "publicado": usado[ano]["publicado"],
                      "origem_rubricas": dados[ano]["_origem"],
                      "componentes": {k: dados[ano][k] for k in ("ll", "ll_total", "ir", "pl", "pl_ini", "lpa", "op", "lai", "fin_liq", "desp_fin", "rec_fin", "da", "ebitda", "caixa", "emprestimos", "locacoes", "div_pagos")}})
            saida["papeis"][t] = m
            if a.descobrir:
                print(json.dumps({k: v for k, v in m.items() if k not in ("semaforo",)}, ensure_ascii=False))
                print("extensões tipo dívida:", dados[ano]["_ext_divida"])
                print("candidatas:", dados[ano]["_candidatos"])
        except Exception as e:
            saida["papeis"][t] = {"erro": f"falha: {str(e)[:120]}", "nota": None, "motivo_sem_nota": "falha ao ler a fonte"}
            print(t, "ERRO", e)
        time.sleep(0.5)
    # aceite resumido (o teste formal fica em tests/test_portugal.py)
    vals = list(saida["papeis"].values())
    n = len(vals)
    saida["aceite"] = {
        "com_relatorio_pct (meta >=90)": round(100 * sum(1 for v in vals if "erro" not in v) / n, 1),
        "com_nota_pct (meta >=75)": round(100 * sum(1 for v in vals if v.get("nota") is not None) / n, 1),
        "lucro_encontrado_pct (meta >=90)": round(100 * sum(1 for v in vals if v.get("ll") is not None) / n, 1),
    }
    Path(a.saida).write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    if not mapa_arq.exists() or a.descobrir:
        with open(mapa_arq if not mapa_arq.exists() else Path(a.saida).with_name("mapa_lei_descoberto.csv"), "w",
                  newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["papel", "isin", "lei", "nome_lei"]); w.writeheader(); w.writerows(novos_mapa)
    print("\nACEITE:", json.dumps(saida["aceite"], ensure_ascii=False))
    for t, v in saida["papeis"].items():
        print(f"{t:5} nota={v.get('nota')} prov={v.get('nota_provisoria')} roe={v.get('roe')} payout={v.get('payout')} "
              f"dl/ebitda={v.get('div_liq_ebitda')} rel={v.get('relatorio') or v.get('erro')} flags={v.get('flags')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
