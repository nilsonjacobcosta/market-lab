"""Coleta as cotações (Yahoo Finance, endpoint chart) e grava dados/cotacoes.json.

Uso: python3 scripts/ativos/coletar_ativos.py [COTACOES_SAIDA=caminho/cotacoes.json]
Sem dependências externas (biblioteca padrão).

Regras:
- Se a coleta de um ticker falhar, o item mantém o valor da captura e aparece com status "captura".
- Se TODAS as coletas falharem, o arquivo anterior é preservado (não sobrescreve com vazio).
- Cada item registra a hora da cotação devolvida pela fonte (regularMarketTime).
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(__file__))
from catalogo import ITENS, SECOES  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAIDA = os.environ.get("COTACOES_SAIDA") or os.path.join(RAIZ, "monitor", "ativos", "dados", "cotacoes.json")
BRT = ZoneInfo("America/Sao_Paulo")
URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}?interval=1d&range=5d"
UA = "Mozilla/5.0 (X11; Linux x86_64) painel-ativos/1.0"


def buscar(ticker):
    """Retorna (preco, anterior, epoch) ou levanta exceção."""
    req = urllib.request.Request(URL.format(urllib.parse.quote(ticker)), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        dados = json.load(r)
    meta = dados["chart"]["result"][0]["meta"]
    preco = meta.get("regularMarketPrice")
    anterior = meta.get("chartPreviousClose") or meta.get("previousClose")
    epoch = meta.get("regularMarketTime")
    if preco is None or anterior in (None, 0):
        raise ValueError("sem preço")
    return float(preco), float(anterior), epoch


def carregar_anterior():
    if os.path.exists(SAIDA):
        with open(SAIDA, encoding="utf-8") as f:
            return json.load(f)
    return None


def main():
    agora = dt.datetime.now(dt.timezone.utc)
    anterior_arquivo = carregar_anterior()
    cache = {}
    if anterior_arquivo:
        for s in anterior_arquivo.get("secoes", []):
            for i in s["itens"]:
                cache[i["nome"]] = i

    secoes = {s: [] for s in SECOES}
    destaques = []
    ok = 0

    for secao, nome, ticker, captura_v, captura_p, inverter, destaque in ITENS:
        item = {"nome": nome, "ticker": ticker, "valor": captura_v, "var": captura_p,
                "hora": None, "status": "captura" if captura_v is not None else "sem fonte"}
        if ticker:
            try:
                p, a, epoch = buscar(ticker)
                if inverter:
                    p, a = 1 / p, 1 / a
                item.update(valor=p, var=(p / a - 1) * 100,
                            hora=dt.datetime.fromtimestamp(epoch, dt.timezone.utc).isoformat() if epoch else None,
                            status="ok")
                ok += 1
            except Exception as e:  # noqa: BLE001 - qualquer falha de rede/formato cai no fallback
                print(f"[aviso] {ticker}: {e}", file=sys.stderr)
                antigo = cache.get(nome)
                if antigo and antigo.get("status") == "ok":
                    item.update(valor=antigo["valor"], var=antigo["var"], hora=antigo["hora"], status="anterior")
            time.sleep(0.2)

        if destaque:
            destaques.append(item)
        if secao in secoes:
            secoes[secao].append(item)

    if ok == 0 and anterior_arquivo:
        print("Nenhuma cotação coletada; arquivo anterior mantido.", file=sys.stderr)
        return 1

    saida = {
        "gerado_utc": agora.isoformat(timespec="minutes"),
        "gerado_brt": agora.astimezone(BRT).strftime("%d/%m/%Y %H:%M"),
        "fonte": "Yahoo Finance (endpoint chart), atraso variável; captura de 10/11/2026 onde não há fonte",
        "cotacoes_ok": ok,
        "destaques": destaques,
        "secoes": [{"titulo": s, "itens": secoes[s]} for s in SECOES],
    }
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    print(f"ok: {ok} cotações atualizadas; gravado em {SAIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
