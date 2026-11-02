"""Carrega as séries brutas do market-lab em DataFrames mensais e diários.

Arquivos de entrada (pasta data/raw):
  yahoo_compact.txt  - Yahoo Finance: S&P 500 (fechamento e mínima mensal desde 1950), índices, metais, petróleo, dólar.
  fred_compact.txt   - FRED: juros, inflação, recessões, petróleo WTI (desde 1949), juro real e inflação implícita.
  gold_monthly.csv   - datasets/gold-prices (GitHub): ouro mensal desde 1833 (média mensal).
"""
from pathlib import Path
import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "dados" / "brutos"


def _parse_compact(path):
    monthly, daily = {}, {}
    for line in Path(path).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name, *rest = line.split()
        if name.startswith("D_"):
            pts = {}
            for item in rest:
                d, v = item.split(":")
                if v:
                    pts[pd.Timestamp(f"2026-{d[:2]}-{d[2:]}")] = float(v)
            daily[name[2:]] = pd.Series(pts).sort_index()
            continue
        start, vals = rest[0], rest[1:]
        idx = pd.period_range(f"{start[:4]}-{start[4:]}", periods=len(vals), freq="M")
        if "/" in vals[0]:
            close = [float(v.split("/")[0]) for v in vals]
            low = [float(v.split("/")[1]) for v in vals]
            monthly[name] = pd.Series(close, index=idx)
            monthly[name + "_LOW"] = pd.Series(low, index=idx)
        else:
            monthly[name] = pd.Series([None if v == "NA" else float(v) for v in vals], index=idx, dtype=float)
    return monthly, daily


def load():
    m1, d1 = _parse_compact(RAW / "yahoo_compact.txt")
    m2, d2 = _parse_compact(RAW / "fred_compact.txt")
    monthly = {**m1, **m2}
    gold = pd.read_csv(RAW / "gold_monthly.csv")
    gold.index = pd.PeriodIndex(gold["Date"], freq="M")
    monthly["GOLD_LONG"] = gold["Price"].astype(float)
    m = pd.DataFrame(monthly).sort_index()
    m = m[m.index >= pd.Period("1949-01", "M")]
    d = pd.DataFrame({**d1, **d2}).sort_index()
    return m, d


if __name__ == "__main__":
    m, d = load()
    print(m.tail(3).T)
    print(d.tail(3).T)
