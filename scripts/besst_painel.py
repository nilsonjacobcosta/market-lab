"""Monitor BESST: coleta preços e proventos e calcula preço-teto, DPA médio e DY médio.

Uso:
  python3 scripts/besst_painel.py --coletar   # baixa dados do Yahoo Finance e recalcula (usado pelo GitHub Actions)
  python3 scripts/besst_painel.py             # recalcula a partir do último arquivo bruto salvo

Método (documentado no painel):
  - DPA médio: média dos proventos por ação (dividendos + JCP, por data-ex) nos 5 últimos anos completos.
  - DY médio: média anual de (proventos do ano ÷ preço médio de fechamento do ano), mesmos 5 anos.
  - Preço-teto: DPA médio ÷ 6% (método de Décio Bazin).
  - Margem: quanto o preço atual está abaixo (+) ou acima (−) do preço-teto.
  - DY 12m: proventos com data-ex nos últimos 12 meses ÷ preço atual.
Valores ajustados por desdobramentos e bonificações pela própria fonte.
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "dados" / "besst"
BRUTOS = BASE / "brutos"
TAXA_BAZIN = 0.06
ANOS = 5
LIQ_MIN = 500  # R$ mil por dia


def coletar(tickers):
    p1 = int(datetime(2019, 1, 1, tzinfo=timezone.utc).timestamp())
    p2 = int(time.time())
    corte = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")
    out = {}
    for t in tickers:
        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{t}.SA?period1={p1}&period2={p2}"
               "&interval=1d&events=div%2Csplit")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (market-lab)"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                j = json.load(r)
        except Exception as e:  # sem cotação na fonte
            print(t, "erro", e)
            continue
        res = (j.get("chart", {}).get("result") or [None])[0]
        if not res or not res.get("timestamp"):
            continue
        ts, q = res["timestamp"], res["indicators"]["quote"][0]
        cl, vol = q["close"], q["volume"]
        soma, n, last, last_d = {}, {}, None, None
        for x, c in zip(ts, cl):
            if c is None:
                continue
            d = datetime.fromtimestamp(x, timezone.utc)
            y = str(d.year)
            soma[y] = soma.get(y, 0) + c
            n[y] = n.get(y, 0) + 1
            last, last_d = c, d.strftime("%Y-%m-%d")
        pm = {y: round(soma[y] / n[y], 2) for y in soma}
        ev = res.get("events", {}) or {}
        dy, d12 = {}, 0.0
        for e in (ev.get("dividends") or {}).values():
            d = datetime.fromtimestamp(e["date"], timezone.utc).strftime("%Y-%m-%d")
            dy[d[:4]] = round(dy.get(d[:4], 0) + e["amount"], 6)
            if d > corte:
                d12 += e["amount"]
        spl = "|".join(f'{datetime.fromtimestamp(e["date"], timezone.utc):%Y-%m-%d}@{e["numerator"]}:{e["denominator"]}'
                       for e in sorted((ev.get("splits") or {}).values(), key=lambda e: e["date"]))
        fin = [c * v for c, v in zip(cl[-63:], vol[-63:]) if c is not None and v is not None]
        out[t] = [round(last, 2) if last is not None else None, last_d, pm,
                  {k: round(v, 4) for k, v in dy.items()}, round(d12, 4), spl,
                  round(sum(fin) / len(fin) / 1000) if fin else 0]
        time.sleep(0.4)
    return out


def calcular(univ, brutos, estatais, ano_ref):
    anos = [str(y) for y in range(ano_ref - ANOS, ano_ref)]
    est = {}
    for e in estatais.get("empresas", []):
        for t in e.get("tickers", []):
            est[t] = e
            # tickers informados só pela raiz (ex.: "SANB") valem para todas as classes
            est.setdefault("RAIZ:" + t[:4], e)
    linhas = []
    for p in univ["papeis"]:
        t = p["ticker"]
        r = brutos.get(t)
        e = est.get(t) or est.get("RAIZ:" + t[:4]) or {}
        row = dict(ticker=t, empresa=p["empresa"], setor=p["setor"],
                   controle=e.get("categoria"), controlador=e.get("controlador"), controle_nota=e.get("nota"),
                   controle_fonte=e.get("fonte"))
        if not r or r[0] is None:
            row["status"] = "sem_cotacao"
            linhas.append(row)
            continue
        preco, data, pm, dy, d12, spl, vol = r
        validos = [a for a in anos if a in pm]
        dpas = [dy.get(a, 0.0) for a in validos]
        dys = [dy.get(a, 0.0) / pm[a] * 100 for a in validos if pm[a]]
        row.update(preco=preco, data=data, liquidez_mil=vol,
                   anos_historico=len(validos), anos_com_provento=sum(1 for v in dpas if v > 0),
                   proventos_ano={a: round(dy.get(a, 0.0), 4) for a in anos + [str(ano_ref)] if a in pm},
                   dy_12m=round(d12 / preco * 100, 2) if preco else None)
        if len(validos) >= 3:
            dpa = sum(dpas) / len(dpas)
            teto = dpa / TAXA_BAZIN
            row.update(dpa_medio=round(dpa, 4), dy_medio=round(sum(dys) / len(dys), 2),
                       preco_teto=round(teto, 2),
                       margem=round((teto - preco) / teto * 100, 1) if teto > 0 else None)
            # tendência: último ano completo comparado com a média (queda forte = alerta)
            if dpa > 0 and anos[-1] in pm:
                row["tendencia"] = round((dy.get(anos[-1], 0.0) / dpa - 1) * 100, 1)
        row["status"] = ("historico_curto" if len(validos) < 3 else
                         "sem_proventos" if not row.get("dpa_medio") else
                         "abaixo_teto" if preco <= row["preco_teto"] else "acima_teto")
        row["baixa_liquidez"] = vol < LIQ_MIN
        linhas.append(row)
    return linhas


def main():
    univ = json.loads((BASE / "universo.json").read_text())
    tickers = [p["ticker"] for p in univ["papeis"]]
    if "--coletar" in sys.argv:
        brutos = coletar(tickers)
        if len(brutos) < 50:
            sys.exit(f"Coleta incompleta ({len(brutos)} papéis); painel mantido.")
        BRUTOS.mkdir(parents=True, exist_ok=True)
        (BRUTOS / "ultimo.json").write_text(json.dumps(brutos, ensure_ascii=False))
    else:
        arqs = sorted(BRUTOS.glob("*.json"), key=lambda p: (p.name != "ultimo.json", p.name), reverse=False)
        brutos = json.loads(((BRUTOS / "ultimo.json") if (BRUTOS / "ultimo.json").exists() else sorted(BRUTOS.glob("yahoo_*.json"))[-1]).read_text())
    estatais = json.loads((BASE / "estatais.json").read_text()) if (BASE / "estatais.json").exists() else {}
    agora = datetime.now(timezone(timedelta(hours=-3)))
    datas = [r[1] for r in brutos.values() if r and r[1]]
    ref = max(datas) if datas else agora.strftime("%Y-%m-%d")
    linhas = calcular(univ, brutos, estatais, int(ref[:4]))
    painel = dict(gerado_em=agora.strftime("%Y-%m-%d %H:%M"), pregao_referencia=ref,
                  metodo=dict(anos=ANOS, taxa_bazin=TAXA_BAZIN, liquidez_minima_mil=LIQ_MIN),
                  fonte_precos="Yahoo Finance (fechamento diário, ajustado por proventos em ações)",
                  papeis=linhas)
    (BASE / "painel.json").write_text(json.dumps(painel, ensure_ascii=False, separators=(",", ":")))
    ok = [l for l in linhas if l["status"] != "sem_cotacao"]
    print(f"{len(linhas)} papéis, {len(ok)} com cotação, {sum(1 for l in ok if l['status']=='abaixo_teto')} abaixo do teto")


if __name__ == "__main__":
    main()
