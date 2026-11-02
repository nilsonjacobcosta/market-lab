"""Fase 2: juros, petróleo, dólar, metais e outros índices no ciclo de midterm, e a decomposição de outubro de 2026.

Saída: data/fase2_macro.json
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from load import load

OUT = Path(__file__).resolve().parent.parent / "dados" / "processados"
m, d = load()
m = m[m.index <= pd.Period("2026-10", "M")]
rng = np.random.default_rng(42)


def val(s, y, mo):
    return s.get(pd.Period(f"{y}-{mo:02d}", "M"), np.nan)


# ---------- 1. Significância do padrão de midterm (teste de permutação) ----------
spx = m["SPX"]
fwd = {y: (val(spx, y + 1, 10) / val(spx, y, 10) - 1) * 100 for y in range(1950, 2026)}
fwd = pd.Series(fwd)
mid_mask = fwd.index % 4 == 2
obs = fwd[mid_mask].mean()
perm = np.array([fwd.sample(19, random_state=int(rng.integers(1e9))).mean() for _ in range(20000)])
p_mean = (perm >= obs).mean()
# probabilidade de 19 positivos em 19 sorteios de anos (sem reposição) dado 80% de positivos no total
pos_all = (fwd > 0).sum()
from math import comb
p_all_pos = comb(int(pos_all), 19) / comb(len(fwd), 19)
signif = dict(media_midterm=obs, media_todos=fwd.mean(), p_valor_media=p_mean,
              anos_positivos_total=int(pos_all), anos_total=int(len(fwd)), p_valor_19_de_19=p_all_pos,
              nota="Teste de permutação: sorteia 19 anos quaisquer (20 mil vezes) e mede com que frequência a média de 12 meses após outubro iguala ou supera a dos midterms.")

# ---------- 2. Ativos no ciclo: de out do midterm até out do ano seguinte ----------
def yld_change(s, y):
    a, b = val(s, y, 10), val(s, y + 1, 10)
    return (b - a) * 100 if not (np.isnan(a) or np.isnan(b)) else np.nan  # pontos-base


def pct(s, y, m0=10, m1=10, dy=1):
    a, b = val(s, y, m0), val(s, y + dy, m1)
    return (b / a - 1) * 100 if not (np.isnan(a) or np.isnan(b)) else np.nan


# Ouro: dataset longo (média mensal) só depois do fim do padrão-ouro (1971); WTI: série FRED, preço livre a partir de 1974.
assets = {
    "S&P 500": ("SPX", pct, 1950, "%"),
    "Nasdaq Composite": ("IXIC", pct, 1985, "%"),
    "Dow Jones": ("DJI", pct, 1992, "%"),
    "Russell 2000 (small caps)": ("RUT", pct, 1988, "%"),
    "S&P 500 pesos iguais (RSP)": ("RSP", pct, 2004, "%"),
    "Ouro": ("GOLD_LONG", pct, 1972, "%"),
    "Prata": ("SILVER", pct, 2001, "%"),
    "Cobre": ("COPPER", pct, 2001, "%"),
    "Petróleo WTI": ("WTISPLC", pct, 1974, "%"),
    "Dólar (DXY)": ("DXY", pct, 1985, "%"),
    "Juro de 10 anos": ("GS10", yld_change, 1954, "p.b."),
    "Juro de 2 anos": ("GS2", yld_change, 1977, "p.b."),
}
# Séries com meses faltantes (futuros do Yahoo): preenche lacunas pontuais com o mês anterior
for c in ["SILVER", "COPPER"]:
    m[c] = m[c].ffill(limit=1)

ciclo_ativos = []
for nome, (col, f, y0, unid) in assets.items():
    s = m[col]
    vals = pd.Series({y: f(s, y) for y in range(y0, 2026)}).dropna()
    mid = vals[vals.index % 4 == 2]
    oth = vals[vals.index % 4 != 2]
    ciclo_ativos.append(dict(ativo=nome, unidade=unid, desde=int(vals.index.min()), n_midterm=int(mid.size),
                             midterm_media=mid.mean(), midterm_mediana=mid.median(),
                             midterm_pos=(mid > 0).mean() * 100, outros_media=oth.mean(),
                             outros_pos=(oth > 0).mean() * 100,
                             midterm_anos={int(k): round(float(v), 1) for k, v in mid.items()}))

# Retorno anual por ano do ciclo (calendário), para cada ativo
def cal(s, y, kind):
    a, b = val(s, y - 1, 12), val(s, y, 12)
    if np.isnan(a) or np.isnan(b):
        return np.nan
    return (b - a) * 100 if kind == "p.b." else (b / a - 1) * 100

CYC = {1: "Pós-eleitoral", 2: "Midterm", 3: "Pré-eleitoral", 0: "Eleitoral"}
ciclo_anual = []
for nome, (col, f, y0, unid) in assets.items():
    s = m[col]
    v = pd.Series({y: cal(s, y, unid) for y in range(y0, 2026)}).dropna()
    row = dict(ativo=nome, unidade=unid, desde=int(v.index.min()))
    for k, c in CYC.items():
        x = v[v.index % 4 == k]
        row[c] = dict(media=x.mean(), mediana=x.median(), n=int(x.size))
    ciclo_anual.append(row)

# ---------- 3. Relações entre ativos (mensal) ----------
mm = m.copy()
rel = {}
# Ouro x juro real (2003+): variação mensal
g = mm["GOLD_LONG"].pct_change() * 100
rr = mm["DFII10_EOM"].diff()
dfg = pd.concat([g, rr], axis=1, keys=["ouro", "jr"]).dropna()
def corr_period(df, a, b, y0, y1):
    x = df[(df.index.year >= y0) & (df.index.year <= y1)]
    return dict(periodo=f"{y0}-{y1}", correl=x[a].corr(x[b]), n=int(len(x)),
                beta=np.polyfit(x[b], x[a], 1)[0])
rel["ouro_x_juro_real"] = [corr_period(dfg, "ouro", "jr", 2003, 2021), corr_period(dfg, "ouro", "jr", 2022, 2026)]
# Nível: ouro x juro real
lv = pd.concat([np.log(mm["GOLD_LONG"]), mm["DFII10_EOM"]], axis=1, keys=["lg", "jr"]).dropna()
rel["nivel_ouro_juro_real"] = [dict(periodo=p, correl=lv[(lv.index.year >= a) & (lv.index.year <= b)].corr().iloc[0, 1])
                               for p, a, b in [("2003-2021", 2003, 2021), ("2022-2026", 2022, 2026)]]
# Cobre/ouro x juro de 10 anos (2001+)
gold_f = mm["GOLD_LONG"]
cg = (mm["COPPER"] / gold_f * 1000)
cdf = pd.concat([cg, mm["GS10"]], axis=1, keys=["cg", "y10"]).dropna()
rel["cobre_ouro_x_juro10"] = dict(correl_nivel=cdf.corr().iloc[0, 1], n=int(len(cdf)),
                                  correl_var12m=cdf.pct_change(12)["cg"].corr(cdf["y10"].diff(12)))
# série para gráfico: cobre/ouro e 10 anos, mensal 2001-2026
serie_cg = [dict(m=str(p), cg=round(float(r.cg), 3), y10=float(r.y10)) for p, r in cdf.iterrows()]
# Juro real e ouro, série
serie_ouro_jr = [dict(m=str(p), ouro=round(float(np.exp(r.lg)), 1), jr=float(r.jr)) for p, r in lv.iterrows()]

# Betas mensais do S&P 500 a fatores macro (2001-09/2026), para atribuir o mês de outubro
f = pd.DataFrame({
    "spx": mm["SPX"].pct_change() * 100,
    "petroleo": mm["WTISPLC"].pct_change() * 100,
    "juro10": mm["GS10"].diff() * 100,
    "dolar": mm["DXY"].pct_change() * 100,
}).dropna()
f = f[(f.index.year >= 2001) & (f.index <= pd.Period("2026-09", "M"))]
X = np.column_stack([np.ones(len(f)), f[["petroleo", "juro10", "dolar"]].values])
beta, *_ = np.linalg.lstsq(X, f["spx"].values, rcond=None)
resid = f["spx"].values - X @ beta
r2 = 1 - resid.var() / f["spx"].values.var()
beta_d = dict(zip(["const", "petroleo", "juro10", "dolar"], beta))

# ---------- 4. Outubro de 2026 ----------
D = d[(d.index >= "2026-09-30") & (d.index <= "2026-10-30")]
def chg(col, kind="%"):
    s = D[col].dropna()
    a, b = s.iloc[0], s.iloc[-1]
    return (b - a) * 100 if kind == "p.b." else (b / a - 1) * 100

out26 = dict(
    indices={"S&P 500": chg("SPX"), "Nasdaq": chg("IXIC"), "Dow Jones": chg("DJI"), "Russell 2000": chg("RUT"),
             "S&P 500 pesos iguais (RSP)": chg("RSP"), "Tecnologia (XLK)": chg("XLK")},
    macro={"Petróleo Brent": chg("BRENT"), "Petróleo WTI": chg("WTI"), "Ouro": chg("GOLD"), "Prata": chg("SILVER"),
           "Cobre": chg("COPPER"), "Dólar (DXY)": chg("DXY")},
    juros_pb={"Juro de 10 anos": chg("DGS10", "p.b."), "Juro de 2 anos": chg("DGS2", "p.b."),
              "Juro real de 10 anos": chg("DFII10", "p.b."), "Inflação implícita 10 anos": chg("T10YIE", "p.b."),
              "Prêmio de crédito (Baa)": chg("BAA10Y", "p.b.")},
    vix=dict(inicio=float(D["VIXCLS"].iloc[0]), fim=float(D["VIXCLS"].iloc[-1])),
)
# Atribuição por fatores (betas mensais 2001-2026 aplicados aos movimentos de outubro)
fat = {"petroleo": chg("WTI"), "juro10": chg("DGS10", "p.b."), "dolar": chg("DXY")}
contrib = {k: beta_d[k] * v for k, v in fat.items()}
explicado = sum(contrib.values()) + beta_d["const"]
out26["atribuicao"] = dict(
    betas=beta_d, r2=r2, n_meses=int(len(f)), movimentos=fat, contribuicao=contrib, constante=beta_d["const"],
    previsto_pelos_fatores=explicado, observado=chg("SPX"), residuo=chg("SPX") - explicado,
    nota="Betas estimados por mínimos quadrados com retornos mensais de 2001 a set/2026: retorno do S&P 500 contra variação do WTI (%), do juro de 10 anos (p.b.) e do DXY (%). Atribuição é estatística, não prova de causa.")
# Composição: quanto a tecnologia explica (diferença entre índice ponderado por valor e por pesos iguais)
out26["composicao"] = dict(spx=chg("SPX"), rsp=chg("RSP"), xlk=chg("XLK"), diferenca_spx_rsp=chg("SPX") - chg("RSP"))
# Correlações diárias em outubro
dr = D[["SPX", "XLK", "RSP", "BRENT", "DGS10", "DXY", "GOLD"]].copy()
dr = pd.DataFrame({"SPX": dr.SPX.pct_change(), "XLK": dr.XLK.pct_change(), "RSP": dr.RSP.pct_change(),
                   "BRENT": dr.BRENT.pct_change(), "DGS10": dr.DGS10.diff(), "DXY": dr.DXY.pct_change(),
                   "GOLD": dr.GOLD.pct_change()}).dropna()
out26["correl_diaria_spx"] = {c: dr["SPX"].corr(dr[c]) for c in ["XLK", "RSP", "BRENT", "DGS10", "DXY", "GOLD"]}
out26["n_dias"] = int(len(dr))
# Séries diárias normalizadas (base 100 em 30/09) para o gráfico
norm = {}
for c in ["SPX", "RSP", "XLK", "RUT", "BRENT", "GOLD"]:
    s = D[c].dropna()
    norm[c] = [dict(d=str(i.date()), v=round(float(v / s.iloc[0] * 100), 2)) for i, v in s.items()]
out26["serie_base100"] = norm

# Outubros de midterm: S&P 500 e o petróleo no mesmo mês
octs = []
for y in range(1954, 2027, 4):
    s_ret = (val(spx, y, 10) / val(spx, y, 9) - 1) * 100
    o = (val(m["WTISPLC"], y, 10) / val(m["WTISPLC"], y, 9) - 1) * 100 if y <= 2025 else chg("WTI")
    octs.append(dict(ano=y, spx_out=s_ret, wti_out=o))

# ---------- 5. Juros e amplitude em 2026 ----------
ytd = {}
for nome, col in [("S&P 500", "SPX"), ("Nasdaq", "IXIC"), ("Dow Jones", "DJI"), ("Russell 2000", "RUT"),
                  ("S&P 500 pesos iguais (RSP)", "RSP"), ("Tecnologia (XLK)", "XLK"), ("Prata", "SILVER"),
                  ("Cobre", "COPPER"), ("Dólar (DXY)", "DXY")]:
    ytd[nome] = (val(m[col], 2026, 10) / val(m[col], 2025, 12) - 1) * 100
ytd["Ouro"] = (D["GOLD"].iloc[-1] / val(m["GOLD_LONG"], 2025, 12) - 1) * 100
ytd["Petróleo WTI"] = (D["WTI"].iloc[-1] / val(m["WTISPLC"], 2025, 12) - 1) * 100


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(v) for v in o]
    if isinstance(o, (float, np.floating)):
        return None if np.isnan(o) else round(float(o), 4 if abs(o) < 0.01 else 2)
    if isinstance(o, (np.integer,)):
        return int(o)
    return o


res = clean(dict(significancia=signif, ciclo_ativos=ciclo_ativos, ciclo_anual=ciclo_anual, relacoes=rel,
                 serie_cobre_ouro=serie_cg, serie_ouro_juro_real=serie_ouro_jr, outubro_2026=out26,
                 outubros_midterm=octs, acumulado_2026_ate_out=ytd))
(OUT / "fase2_macro.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    pd.set_option("display.width", 220)
    print("SIGNIF", {k: v for k, v in res["significancia"].items() if k != "nota"})
    for a in res["ciclo_ativos"]:
        a2 = dict(a); a2.pop("midterm_anos"); print(a2)
    for a in res["ciclo_anual"]:
        print(a["ativo"], {k: (v["media"], v["n"]) for k, v in a.items() if isinstance(v, dict)})
    print("REL", json.dumps(res["relacoes"], ensure_ascii=False))
    o = res["outubro_2026"]
    for k in ["indices", "macro", "juros_pb", "vix", "atribuicao", "composicao", "correl_diaria_spx"]:
        print(k, o[k])
    print("OCTS", res["outubros_midterm"])
    print("YTD", res["acumulado_2026_ate_out"])
