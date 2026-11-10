"""Coleta preços diários ajustados (Yahoo Finance, endpoint chart), calcula as métricas
da matriz porte x estilo e grava tendencias.json.

Uso: TENDENCIAS_SAIDA=caminho/tendencias.json python3 scripts/tendencias/coletar_tendencias.py
Sem dependências externas (biblioteca padrão).

Regras:
- Usa preço ajustado (dividendos e desdobramentos) quando disponível.
- Descarta o pregão do dia se ainda estiver aberto ou recém-fechado (antes das 16h30 de Nova York).
- Alinha cada ETF ao IWV pelas datas em comum antes de calcular qualquer relativo.
- Se algum ETF falhar, ele sai com status "sem dados" e o resto é publicado.
- Se TODOS falharem, o arquivo anterior é preservado (não sobrescreve com vazio).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metricas  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CATALOGO = os.path.join(RAIZ, "dados", "tendencias", "catalogo_etfs.json")
SAIDA = os.environ.get("TENDENCIAS_SAIDA") or os.path.join(RAIZ, "tendencias", "data", "tendencias.json")
NY = ZoneInfo("America/New_York")
BRT = ZoneInfo("America/Sao_Paulo")
URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}?interval=1d&range=5y"
UA = "Mozilla/5.0 (X11; Linux x86_64) painel-tendencias/1.0"
MIN_PREGOES = 260  # um ano de pregões + folga para as médias


def buscar(ticker: str) -> list[tuple[str, float]]:
    """Retorna [(data_iso, preço ajustado)] em ordem cronológica ou levanta exceção."""
    req = urllib.request.Request(URL.format(urllib.parse.quote(ticker)), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        dados = json.load(r)
    res = dados["chart"]["result"][0]
    return extrair_serie(res)


def extrair_serie(res: dict) -> list[tuple[str, float]]:
    ts = res["timestamp"]
    ind = res["indicators"]
    precos = (ind.get("adjclose") or [{}])[0].get("adjclose") or ind["quote"][0]["close"]
    serie = []
    for t, p in zip(ts, precos):
        if p is None or p <= 0:
            continue
        data = dt.datetime.fromtimestamp(t, dt.timezone.utc).astimezone(NY).date().isoformat()
        serie.append((data, float(p)))
    return serie


def descartar_pregao_aberto(serie: list[tuple[str, float]], agora_utc: dt.datetime) -> list[tuple[str, float]]:
    """Remove o último ponto se for o dia de hoje em Nova York e ainda antes das 16h30."""
    if not serie:
        return serie
    agora = agora_utc.astimezone(NY)
    if serie[-1][0] == agora.date().isoformat() and (agora.hour, agora.minute) < (16, 30):
        return serie[:-1]
    return serie


def alinhar(series: dict[str, list[tuple[str, float]]]) -> tuple[list[str], dict[str, list[float]]]:
    """Mantém só as datas presentes em TODAS as séries recebidas."""
    comuns = None
    for s in series.values():
        datas = {d for d, _ in s}
        comuns = datas if comuns is None else comuns & datas
    datas_ord = sorted(comuns or [])
    mapas = {t: dict(s) for t, s in series.items()}
    return datas_ord, {t: [mapas[t][d] for d in datas_ord] for t in series}


def montar(catalogo: dict, series: dict[str, list[tuple[str, float]]], agora_utc: dt.datetime) -> dict:
    ref_t = catalogo["referencia"]["ticker"]
    series = {t: descartar_pregao_aberto(s, agora_utc) for t, s in series.items()}
    celulas, cotacoes_ok = [], 0
    ultimo = None
    ref = series.get(ref_t)
    for c in catalogo["celulas"]:
        item = {k: c[k] for k in ("porte", "estilo", "ticker", "nome", "indice")}
        s = series.get(c["ticker"])
        if not s or not ref:
            item["status"] = "sem dados"
            celulas.append(item)
            continue
        datas, alinhadas = alinhar({c["ticker"]: s, ref_t: ref})
        if len(datas) < MIN_PREGOES:
            item["status"] = "sem dados"
            celulas.append(item)
            continue
        item.update(metricas.calcular_celula(alinhadas[c["ticker"]], alinhadas[ref_t]))
        item["ultimo_preco"] = alinhadas[c["ticker"]][-1]
        item["ultimo_pregao"] = datas[-1]
        item["status"] = "ok"
        ultimo = max(ultimo or datas[-1], datas[-1])
        cotacoes_ok += 1
        celulas.append(item)
    ref_info = dict(catalogo["referencia"])
    if ref:
        ref_info["ultimo_pregao"] = ref[-1][0]
        ref_info["retornos"] = {n: metricas.retorno([p for _, p in ref], k) for n, k in metricas.JANELAS.items()}
    return {
        "gerado_utc": agora_utc.isoformat(timespec="minutes"),
        "gerado_brt": agora_utc.astimezone(BRT).strftime("%d/%m/%Y %H:%M"),
        "ultimo_pregao": ultimo,
        "fonte": "Yahoo Finance (endpoint chart), preços ajustados diários; métricas calculadas pelo market-lab",
        "janelas_pregoes": metricas.JANELAS,
        "referencia": ref_info,
        "celulas_ok": cotacoes_ok,
        "celulas": celulas,
    }


def main() -> int:
    with open(CATALOGO, encoding="utf-8") as f:
        catalogo = json.load(f)
    tickers = [catalogo["referencia"]["ticker"]] + [c["ticker"] for c in catalogo["celulas"]]
    series = {}
    for t in tickers:
        try:
            series[t] = buscar(t)
        except Exception as e:  # noqa: BLE001 - falha de rede/formato vira "sem dados"
            print(f"[aviso] {t}: {e}", file=sys.stderr)
        time.sleep(0.3)
    saida = montar(catalogo, series, dt.datetime.now(dt.timezone.utc))
    if saida["celulas_ok"] == 0:
        print("Nenhuma célula calculada; arquivo anterior mantido.", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    print(f"ok: {saida['celulas_ok']}/9 células; último pregão {saida['ultimo_pregao']}; gravado em {SAIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
