"""Fase 1: recalcula o estudo de midterm do S&P 500 (1950 a out/2026) a partir de dados de mercado.

Base: fechamento mensal do índice S&P 500 (^GSPC, retorno de preço, sem dividendos), Yahoo Finance.
Saída: data/fase1_midterm.json e uma comparação com os números do estudo preliminar.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from load import load

OUT = Path(__file__).resolve().parent.parent / "dados" / "processados"
m, _ = load()
spx = m["SPX"].dropna()
spx = spx[spx.index <= pd.Period("2026-10", "M")]
low = m["SPX_LOW"].reindex(spx.index)
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def px(y, mo):
    p = pd.Period(f"{y}-{mo:02d}", "M")
    return spx.get(p, np.nan)


def ret(a, b):
    return (b / a - 1) * 100


def cycle(y):
    return {0: "Eleitoral", 1: "Pós-eleitoral", 2: "Midterm", 3: "Pré-eleitoral"}[y % 4]


years = range(1950, 2027)
rows = []
for y in years:
    base = px(y - 1, 12)
    r = dict(ano=y, ciclo=cycle(y))
    r["retorno_ano"] = ret(base, px(y, 12)) if y <= 2025 else None
    r["ate_outubro"] = ret(base, px(y, 10))
    r["out_dez"] = ret(px(y, 10), px(y, 12)) if y <= 2025 else None
    r["out_12m"] = ret(px(y, 10), px(y + 1, 10)) if y <= 2025 else None
    r["out_jun"] = ret(px(y, 10), px(y + 1, 6)) if y <= 2025 else None
    yr = [pd.Period(f"{y}-{k:02d}", "M") for k in range(1, 13) if pd.Period(f"{y}-{k:02d}", "M") in spx.index]
    # queda máxima: base do ano anterior até a menor mínima mensal (intradiária) do ano
    lows = low.reindex(yr)
    closes = spx.reindex(yr)
    mmin = lows.idxmin()
    r["queda_max"] = min(0.0, ret(base, lows.min()))
    r["queda_max_fech"] = min(0.0, ret(base, closes.min()))
    r["mes_minima"] = MESES[mmin.month - 1]
    nxt = mmin + 12
    r["minima_12m"] = ret(lows.min(), spx[nxt]) if nxt in spx.index else None
    rows.append(r)
Y = pd.DataFrame(rows).set_index("ano")

# 1) Ciclo presidencial: retorno anual 1950-2025
cyc = []
for c in ["Pós-eleitoral", "Midterm", "Pré-eleitoral", "Eleitoral"]:
    s = Y.loc[(Y.ciclo == c) & (Y.index <= 2025), "retorno_ano"]
    cyc.append(dict(ciclo=c, anos=int(s.size), media=s.mean(), mediana=s.median(), pct_pos=(s > 0).mean() * 100,
                    pior=s.min(), pior_ano=int(s.idxmin()), melhor=s.max(), melhor_ano=int(s.idxmax())))

# 2) A partir do fim de outubro
def grupo(nome, mask):
    s = Y[mask & Y.out_12m.notna()]
    return dict(grupo=nome, anos=int(len(s)), out_dez=s.out_dez.mean(), dez_pos=(s.out_dez > 0).mean() * 100,
                out_jun=s.out_jun.mean(), out_12m=s.out_12m.mean(), pos_12m=(s.out_12m > 0).mean() * 100,
                pior_12m=s.out_12m.min(), pior_12m_ano=int(s.out_12m.idxmin()), mediana_12m=s.out_12m.median(),
                anos_lista=[int(a) for a in s.index])

mid = Y.ciclo == "Midterm"
fwd = [grupo("Todos os anos", Y.index >= 1950),
       grupo("Anos de midterm", mid),
       grupo("Midterm forte (alta > 5% até out.)", mid & (Y.ate_outubro > 5)),
       grupo("Midterm moderado (0% a 5% até out.)", mid & (Y.ate_outubro >= 0) & (Y.ate_outubro <= 5)),
       grupo("Midterm fraco (queda até out.)", mid & (Y.ate_outubro < 0))]

# 3) Retorno médio por mês: midterm x demais anos (1950-2025, mês completo)
mr = spx.pct_change() * 100
mr = mr[(mr.index >= pd.Period("1950-01", "M"))]
mon = []
for k in range(1, 13):
    s = mr[mr.index.month == k]
    is_mid = s.index.year % 4 == 2
    sm, so = s[is_mid], s[~is_mid]
    if k > 10:  # nov e dez de 2026 ainda não existem
        sm = sm[sm.index.year < 2026]
    sm_hist = sm[sm.index.year < 2026]
    mon.append(dict(mes=MESES[k - 1], midterm_media=sm_hist.mean(), midterm_pos=(sm_hist > 0).mean() * 100,
                    midterm_n=int(sm_hist.size), outros_media=so[so.index.year < 2026].mean(),
                    outros_pos=(so[so.index.year < 2026] > 0).mean() * 100,
                    m2026=float(mr.get(pd.Period(f"2026-{k:02d}", "M"), np.nan)) if k <= 10 else None))

mid_rows = Y[mid].sort_index(ascending=False)
anual = [dict(ano=int(a), **{k: (None if pd.isna(v) else (round(v, 2) if isinstance(v, float) else v))
                            for k, v in r.items() if k != "ciclo"}) for a, r in mid_rows.iterrows()]
medias = {k: round(float(mid_rows[k][mid_rows.index <= 2022].mean()), 2)
          for k in ["retorno_ano", "queda_max", "ate_outubro", "out_dez", "out_12m", "minima_12m"]}

# Comparação com o estudo preliminar (valores publicados na versão anterior do painel)
seed_cycle = {"Pós-eleitoral": (8.4, 9.1, 63, -17.4, 31.0), "Midterm": (4.7, 1.1, 58, -29.7, 45.0),
              "Pré-eleitoral": (17.2, 18.9, 89, -0.7, 33.6), "Eleitoral": (8.1, 11.8, 84, -38.5, 25.8)}
seed_years = {2026: (None, -7.7, "mar", 11.1, None, None, None), 2022: (-19.4, -26.7, "out", -18.8, -0.8, 8.3, 20.1),
              2018: (-6.2, -12.2, "dez", 1.4, -7.6, 12.0, 37.7), 2014: (11.4, -6.0, "fev", 9.2, 2.0, 3.0, 21.1),
              2010: (12.8, -9.3, "jul", 6.1, 6.3, 5.9, 27.8), 2006: (13.6, -2.3, "jun", 10.4, 2.9, 12.4, 23.3),
              2002: (-23.4, -33.1, "out", -22.9, -0.7, 18.6, 36.7), 1998: (26.7, -5.9, "jan", 13.2, 11.9, 24.1, 40.2),
              1994: (-1.1, -6.6, "abr", 1.3, -2.4, 23.1, 18.1), 1990: (-6.6, -16.7, "out", -14.0, 8.6, 29.1, 33.3),
              1986: (14.6, -4.1, "jan", 15.5, -0.8, 3.2, 35.3), 1982: (14.8, -16.6, "ago", 9.1, 5.2, 22.3, 60.9),
              1978: (1.1, -9.1, "mar", -2.1, 3.2, 9.3, 17.5), 1974: (-29.7, -37.5, "out", -24.2, -7.2, 20.5, 46.1),
              1970: (0.1, -25.5, "mai", -9.6, 10.7, 13.2, 45.2), 1966: (-13.1, -21.8, "out", -13.2, 0.2, 16.3, 29.1),
              1962: (-11.8, -28.2, "jun", -21.0, 11.6, 30.9, 35.1), 1958: (38.1, 0.9, "jan", 28.4, 7.6, 12.1, 37.5),
              1954: (45.0, -0.0, "jan", 27.7, 13.6, 33.7, 47.7), 1950: (21.7, -0.8, "jan", 16.3, 4.6, 17.5, 30.0)}
cols = ["retorno_ano", "queda_max", "mes_minima", "ate_outubro", "out_dez", "out_12m", "minima_12m"]
diffs, checks = [], 0
for a, sv in seed_years.items():
    for c, s in zip(cols, sv):
        if s is None:
            continue
        v = Y.loc[a, c]
        checks += 1
        if c == "mes_minima":
            if v != s:
                diffs.append(dict(ano=a, campo=c, estudo=s, recalculado=v))
        elif abs(round(v, 1) - s) > 0.15:
            diffs.append(dict(ano=a, campo=c, estudo=s, recalculado=round(v, 1)))
cyc_diffs = []
for r in cyc:
    s = seed_cycle["Midterm" if r["ciclo"] == "Midterm" else r["ciclo"]]
    for name, sv, v in zip(["media", "mediana", "pct_pos", "pior", "melhor"], s,
                           [r["media"], r["mediana"], r["pct_pos"], r["pior"], r["melhor"]]):
        checks += 1
        if abs(v - sv) > (1.0 if name == "pct_pos" else 0.15):
            cyc_diffs.append(dict(ciclo=r["ciclo"], campo=name, estudo=sv, recalculado=round(v, 1)))


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(v) for v in o]
    if isinstance(o, (float, np.floating)):
        return None if np.isnan(o) else round(float(o), 2)
    if isinstance(o, np.integer):
        return int(o)
    return o


res = clean(dict(fonte="S&P 500 (^GSPC), fechamento mensal, retorno de preço; Yahoo Finance; coletado em 2026-11-02",
                 ciclo=cyc, a_partir_de_outubro=fwd, mensal=mon, ano_a_ano=anual, medias_midterm_1950_2022=medias,
                 auditoria=dict(comparacoes=checks, divergencias_ano_a_ano=diffs, divergencias_ciclo=cyc_diffs)))
(OUT / "fase1_midterm.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print(pd.DataFrame(cyc).round(1).drop(columns=[]))
    print(pd.DataFrame(fwd).drop(columns=["anos_lista"]).round(1))
    print(pd.DataFrame(mon).round(2))
    print(Y[mid].round(1))
    print("medias", medias)
    print("checks", checks, "diffs", len(diffs), len(cyc_diffs))
    for d in diffs + cyc_diffs:
        print(d)
    for g in fwd:
        print(g["grupo"], g["anos_lista"])
