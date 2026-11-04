#!/usr/bin/env python3
"""Monitor Portugal — Fase 0 — teste de cobertura da fonte de cotações (E1, para o J1).

NÃO publica nada. Gera um relatório para os juízes decidirem se a fonte serve para a Euronext Lisbon.

O que faz:
  1. Monta o universo: tenta a lista oficial de ações da Euronext Lisbon (mercado regulamentado, MIC XLIS);
     se falhar, usa a semente manual dados/portugal/semente_lisboa.csv (e diz no relatório qual usou).
  2. Para cada papel, baixa preços diários e proventos desde 2019 (mesma API usada no Monitor BESST, sufixo .LS).
  3. Mede: tem preço recente? quantos anos de histórico? proventos por ano (5 anos), anos sem provento,
     desdobramentos, moeda, liquidez (mediana do volume financeiro diário em 12 meses) e dias sem negócio.
  4. Grava saida/cobertura.csv e saida/relatorio.md (o workflow anexa ambos como artefato da execução).

Uso: python3 scripts/portugal/teste_cobertura.py [--saida DIR] [--so-semente]
"""
import argparse
import csv
import io
import json
import re
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SEMENTE = RAIZ / "dados" / "portugal" / "semente_lisboa.csv"
UA = {"User-Agent": "Mozilla/5.0 (market-lab)"}
EURONEXT_LISTA = "https://live.euronext.com/pd_es/data/stocks/download?mics=XLIS"
ANOS = [str(a) for a in range(datetime.now(timezone.utc).year - 5, datetime.now(timezone.utc).year)]  # 5 anos fechados
CORTES_LIQ = [25_000, 50_000, 100_000, 250_000, 500_000, 1_000_000]  # EUR/dia, para o E1 propor o corte


def baixar(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def universo_euronext():
    """Lê o CSV de ações da Euronext Lisbon. Formato não documentado: parse tolerante (linhas com ISIN)."""
    bruto = baixar(EURONEXT_LISTA).decode("utf-8-sig", errors="replace")
    sep = ";" if bruto.count(";") > bruto.count(",") else ","
    papeis = []
    for linha in csv.reader(io.StringIO(bruto), delimiter=sep):
        isin_i = next((i for i, c in enumerate(linha) if re.fullmatch(r"[A-Z]{2}[A-Z0-9]{9}\d", c.strip())), None)
        if isin_i is None or isin_i + 1 >= len(linha):
            continue
        nome, isin, simbolo = linha[0].strip(), linha[isin_i].strip(), linha[isin_i + 1].strip()
        if not re.fullmatch(r"[A-Z0-9]{1,8}", simbolo):
            continue
        papeis.append({"simbolo": simbolo, "nome": nome, "isin": isin, "yahoo": f"{simbolo}.LS"})
    if len(papeis) < 20:  # sanidade: Lisboa tem bem mais de 20 ações
        raise ValueError(f"lista da Euronext com só {len(papeis)} linhas reconhecidas")
    return papeis


def universo_semente():
    with open(SEMENTE, encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if not r["simbolo"].startswith("#")]


def medir(p, p1, p2, corte12):
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{p['yahoo']}?period1={p1}&period2={p2}"
           "&interval=1d&events=div%2Csplit")
    linha = {k: p.get(k, "") for k in ("simbolo", "nome", "isin", "yahoo")}
    try:
        j = json.loads(baixar(url))
    except Exception as e:
        linha["status"] = f"erro: {str(e)[:60]}"
        return linha
    res = (j.get("chart", {}).get("result") or [None])[0]
    if not res or not res.get("timestamp"):
        linha["status"] = "sem dados"
        return linha
    meta = res.get("meta", {})
    ts, q = res["timestamp"], res["indicators"]["quote"][0]
    dias = [(datetime.fromtimestamp(x, timezone.utc), c, v) for x, c, v in zip(ts, q["close"], q["volume"]) if c is not None]
    if not dias:
        linha["status"] = "sem preços"
        return linha
    ult_d, ult_c, _ = dias[-1]
    ev = res.get("events", {}) or {}
    div_ano = {}
    for e in (ev.get("dividends") or {}).values():
        a = str(datetime.fromtimestamp(e["date"], timezone.utc).year)
        div_ano[a] = div_ano.get(a, 0) + e["amount"]
    d12 = sum(e["amount"] for e in (ev.get("dividends") or {}).values()
              if datetime.fromtimestamp(e["date"], timezone.utc) > corte12)
    ult12 = [(c, v) for d, c, v in dias if d > corte12]
    fin = [c * (v or 0) for c, v in ult12]
    linha.update({
        "status": "ok",
        "moeda": meta.get("currency", ""),
        "bolsa_yahoo": meta.get("exchangeName", ""),
        "ultimo_preco": round(ult_c, 4),
        "ultima_data": ult_d.strftime("%Y-%m-%d"),
        "primeira_data": dias[0][0].strftime("%Y-%m-%d"),
        "anos_com_preco": len({d.year for d, _, _ in dias}),
        **{f"div_{a}": round(div_ano.get(a, 0), 4) for a in ANOS},
        "anos_sem_div_5a": sum(1 for a in ANOS if div_ano.get(a, 0) == 0),
        "div_12m": round(d12, 4),
        "desdobramentos": "|".join(f'{datetime.fromtimestamp(e["date"], timezone.utc):%Y-%m-%d}@{e["numerator"]}:{e["denominator"]}'
                                   for e in sorted((ev.get("splits") or {}).values(), key=lambda e: e["date"])),
        "mediana_vol_fin_12m_eur": round(statistics.median(fin)) if fin else 0,
        "pct_dias_sem_negocio_12m": round(100 * sum(1 for x in fin if x == 0) / len(fin), 1) if fin else 100.0,
    })
    return linha


def relatorio(linhas, fonte_universo, aviso, gerado):
    ok = [l for l in linhas if l.get("status") == "ok"]
    hoje = datetime.now(timezone.utc)
    recentes = [l for l in ok if (hoje - datetime.strptime(l["ultima_data"], "%Y-%m-%d").replace(tzinfo=timezone.utc)).days <= 7]
    cinco = [l for l in ok if l["anos_com_preco"] >= 6]
    pagou = [l for l in ok if l["anos_sem_div_5a"] < 5]
    nao_eur = [l for l in ok if l["moeda"] and l["moeda"] != "EUR"]
    pct = lambda a, b: f"{100 * a / b:.0f}%" if b else "–"
    n = len(linhas)
    md = [
        "# Monitor Portugal — teste de cobertura da fonte de cotações (fase 0)",
        "",
        f"Gerado em {gerado} UTC. **Relatório interno para os juízes — não publicar.**",
        "",
        f"- Universo: **{n} papéis**, origem: {fonte_universo}." + (f" Aviso: {aviso}" if aviso else ""),
        f"- Com dados na fonte: **{len(ok)}** ({pct(len(ok), n)}).",
        f"- Com preço nos últimos 7 dias: **{len(recentes)}** ({pct(len(recentes), n)}).",
        f"- Com ≥ 6 anos-calendário de preços (base para média de 5 anos): **{len(cinco)}** ({pct(len(cinco), n)}).",
        f"- Com algum provento nos 5 anos fechados ({ANOS[0]}–{ANOS[-1]}): **{len(pagou)}**.",
        f"- Cotados em moeda diferente de EUR: **{len(nao_eur)}** " + (f"({', '.join(l['simbolo'] for l in nao_eur)})" if nao_eur else ""),
        "",
        "## Liquidez — quantos papéis passariam em cada corte (mediana do volume financeiro diário, 12 meses)",
        "",
        "| Corte (EUR/dia) | Papéis acima |",
        "|---:|---:|",
        *[f"| {c:,.0f} | {sum(1 for l in ok if l['mediana_vol_fin_12m_eur'] >= c)} |".replace(",", ".") for c in CORTES_LIQ],
        "",
        "## Falhas (para o J1 conferir manualmente)",
        "",
        *([f"- {l['simbolo']} ({l['yahoo']}): {l['status']}" for l in linhas if l.get("status") != "ok"] or ["- nenhuma"]),
        "",
        "## Atenção do J1",
        "",
        "- Proventos da fonte NÃO são fonte oficial: conferir amostra contra comunicados da empresa / SDI da CMVM / Euronext (meta: ≥ 95% dos eventos).",
        "- Verificar se os valores de provento são brutos (antes da retenção de 28%) e se há ajuste por desdobramento.",
        "- Papéis com muitos dias sem negócio podem ter preço 'velho' mesmo com data recente.",
        "",
        "Detalhe por papel: `cobertura.csv`.",
    ]
    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=str(RAIZ / "saida"))
    ap.add_argument("--so-semente", action="store_true")
    a = ap.parse_args()
    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)

    aviso = ""
    if a.so_semente:
        papeis, fonte = universo_semente(), "semente manual (dados/portugal/semente_lisboa.csv)"
    else:
        try:
            papeis, fonte = universo_euronext(), "lista oficial da Euronext Lisbon (MIC XLIS)"
        except Exception as e:
            papeis, fonte = universo_semente(), "semente manual (dados/portugal/semente_lisboa.csv)"
            aviso = f"lista da Euronext indisponível ({str(e)[:80]})."
    print(f"Universo: {len(papeis)} papéis — {fonte}")

    agora = datetime.now(timezone.utc)
    p1, p2 = int(datetime(2019, 1, 1, tzinfo=timezone.utc).timestamp()), int(time.time())
    corte12 = agora - timedelta(days=365)
    linhas = []
    for p in papeis:
        l = medir(p, p1, p2, corte12)
        print(l["simbolo"], l["status"])
        linhas.append(l)
        time.sleep(0.4)

    campos = list(dict.fromkeys(k for l in linhas for k in l))
    with open(saida / "cobertura.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)
    md = relatorio(linhas, fonte, aviso, agora.strftime("%Y-%m-%d %H:%M"))
    (saida / "relatorio.md").write_text(md, encoding="utf-8")
    print(md)
    return 0 if any(l.get("status") == "ok" for l in linhas) else 1


if __name__ == "__main__":
    sys.exit(main())
