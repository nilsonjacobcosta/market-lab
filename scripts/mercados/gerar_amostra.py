"""Gera um mercados.json SINTÉTICO para testar a página localmente, sem rede.

Uso: python3 scripts/mercados/gerar_amostra.py [caminho_de_saida]
Padrão: monitor/mercados/_amostra/mercados.json

Os valores são um passeio aleatório com semente fixa: NÃO são dados reais e não devem ser
publicados. O arquivo leva o campo "amostra_sintetica": true. Uma série sai com status
"anterior" (idx_psi) e uma com "sem dados" (risco_hy), para testar os avisos da página.
As séries derivadas são calculadas pelas mesmas funções da coleta real.
"""
from __future__ import annotations

import calendar
import datetime as dt
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coletar_mercados as col  # noqa: E402
import fontes  # noqa: E402

SAIDA_PADRAO = os.path.join(col.RAIZ, "monitor", "mercados", "_amostra", "mercados.json")
AGORA = dt.datetime(2026, 11, 16, 23, 10, tzinfo=dt.timezone.utc)
SEMENTE = 20261116
SERIE_ANTERIOR, SERIE_SEM_DADOS = "idx_psi", "risco_hy"

# id -> (valor final aproximado, volatilidade por passo, tipo). "nivel": passeio multiplicativo
# com tendência; "taxa": passeio aditivo com retorno à média, dentro de [mín, máx].
PERFIS = {
    "idx_sp500": (7500, 0.022, "nivel"), "idx_nasdaq100": (27000, 0.028, "nivel"),
    "idx_dow": (52000, 0.021, "nivel"), "idx_dax": (26500, 0.026, "nivel"),
    "idx_eurostoxx50": (6300, 0.026, "nivel"), "idx_ftse100": (10800, 0.02, "nivel"),
    "idx_ibovespa": (172000, 0.033, "nivel"), "idx_psi": (8800, 0.025, "nivel"),
    "idx_nikkei": (60000, 0.027, "nivel"), "idx_hangseng": (24500, 0.03, "nivel"),
    "idx_xangai": (3650, 0.03, "nivel"), "idx_emergentes": (55, 0.03, "nivel"),
    "fx_dxy": (101, 0.009, "nivel"), "fx_eurusd": (1.12, 0.011, "nivel"),
    "fx_usdbrl": (5.55, 0.02, "nivel"), "fx_eurbrl": (6.2, 0.021, "nivel"),
    "fx_usdjpy": (158, 0.012, "nivel"), "fx_gbpusd": (1.34, 0.011, "nivel"),
    "com_ouro": (4080, 0.022, "nivel"), "com_prata": (52, 0.038, "nivel"),
    "com_wti": (85, 0.045, "nivel"), "com_cobre": (6.3, 0.033, "nivel"),
    "btc_usd": (74000, 0.09, "nivel"), "eth_btc": (0.035, 0.06, "nivel"),
    "cpi_eua": (337.5, 0.0022, "nivel"), "liq_eua_m2": (23400, 0.004, "nivel"),
    "liq_fed_balanco": (6760000, 0.006, "nivel"), "liq_br_base": (435000000, 0.012, "nivel"),
    "liq_br_m2": (7870000000, 0.008, "nivel"), "liq_ea_m3": (17650000, 0.0035, "nivel"),
    "liq_bce_balanco": (5913000, 0.007, "nivel"),
    "risco_vix": (20, 2.2, "taxa", 9, 80), "juros_eua_2a": (4.86, 0.09, "taxa", 0.1, 7),
    "juros_eua_10a": (5.1, 0.08, "taxa", 0.5, 7), "juros_eua_10a2a": (0.27, 0.06, "taxa", -1.1, 2.9),
    "risco_hy": (3.2, 0.15, "taxa", 2.5, 20), "infl_br_12m": (4.6, 0.35, "taxa", 1.8, 17),
    "juros_br_selic": (13.75, 0.12, "taxa", 2, 26.5), "infl_ea_12m": (4.0, 0.2, "taxa", -0.6, 10.6),
    "infl_pt_12m": (3.9, 0.25, "taxa", -1.8, 10.6),
}
INICIO_PROPRIO = {"btc_usd": "2014-09-15", "eth_btc": "2017-11-06", "idx_psi": "2013-04-29",
                  "idx_eurostoxx50": "2007-03-26", "fx_usdbrl": "2003-12-01", "com_ouro": "2000-08-28", "liq_fed_balanco": "2002-12-18",
                  "liq_br_m2": "2001-12-01"}
ULTIMO_MENSAL = {"cpi_eua": "2026-10-01", "liq_eua_m2": "2026-09-01", "infl_br_12m": "2026-10-01",
                 "liq_br_base": "2026-09-01", "liq_br_m2": "2026-09-01", "infl_ea_12m": "2026-10-01",
                 "infl_pt_12m": "2026-10-01", "liq_ea_m3": "2026-08-01"}


def datas_da_serie(serie: dict, hoje: dt.date) -> list[dt.date]:
    inicio = dt.date.fromisoformat(INICIO_PROPRIO.get(serie["id"]) or serie.get("inicio") or "2000-01-01")
    if serie["periodicidade"] == "mensal":
        fim = dt.date.fromisoformat(ULTIMO_MENSAL.get(serie["id"], "2026-10-01"))
        datas, d = [], inicio.replace(day=1)
        while d <= fim:
            # O BCE data o mês pelo último dia; as demais fontes, pelo dia 1.
            datas.append(d.replace(day=calendar.monthrange(d.year, d.month)[1]) if serie["fonte"] == "bce" else d)
            d = dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)
        return datas
    # Semanal: Yahoo data a barra pela segunda-feira; as demais fontes, pelo último dia útil da semana.
    alvo = 0 if serie["fonte"] == "yahoo" else (2 if serie["id"] == "liq_fed_balanco" else 4)
    d = inicio + dt.timedelta(days=(alvo - inicio.weekday()) % 7)
    datas = []
    while d <= hoje:
        datas.append(d)
        d += dt.timedelta(days=7)
    return datas


def passeio(rng: random.Random, n: int, perfil: tuple) -> list[float]:
    """Passeio aleatório gerado de trás para frente, para terminar perto do valor final desejado."""
    final, vol, tipo = perfil[:3]
    valores = [float(final)]
    if tipo == "nivel":
        deriva = vol * vol * 2.2  # tendência de alta suave no sentido do tempo
        for _ in range(n - 1):
            valores.append(valores[-1] / math.exp(rng.gauss(deriva, vol)))
    else:
        minimo, maximo = perfil[3], perfil[4]
        centro = (final + (minimo + maximo) / 2) / 2
        for _ in range(n - 1):
            v = valores[-1] + rng.gauss(0, vol) + 0.01 * (centro - valores[-1])
            valores.append(min(max(v, minimo), maximo))
    return valores[::-1]


def gerar(catalogo: list[dict], agora: dt.datetime = AGORA) -> dict:
    hoje = agora.date()
    carimbo = agora.isoformat(timespec="minutes")
    antigo = (agora - dt.timedelta(days=3)).isoformat(timespec="minutes")
    series = {}
    for s in catalogo:
        if s["fonte"] == "derivada":
            continue
        if s["id"] == SERIE_SEM_DADOS:
            series[s["id"]] = col.bloco(s, catalogo, [], "sem dados", None)
            continue
        rng = random.Random(f"{SEMENTE}:{s['id']}")
        datas = datas_da_serie(s, hoje)
        if s["id"] == SERIE_ANTERIOR:  # bloco "anterior": parou alguns dias antes
            datas = [d for d in datas if d <= hoje - dt.timedelta(days=5)]
        valores = passeio(rng, len(datas), PERFIS[s["id"]])
        pontos = fontes.arredondar_pontos([(d.isoformat(), v) for d, v in zip(datas, valores)],
                                          s.get("algarismos", 4))
        if s["id"] == SERIE_ANTERIOR:
            series[s["id"]] = col.bloco(s, catalogo, pontos, "anterior", antigo, hoje)
        else:
            series[s["id"]] = col.bloco(s, catalogo, pontos, "ok", carimbo, hoje)
    for s in catalogo:
        if s["fonte"] != "derivada":
            continue
        bases = [series[i] for i in s["derivada_de"]]
        pontos = fontes.calcular_derivada(s["calculo"], [b["pontos"] for b in bases])
        status = "anterior" if any(b["status"] == "anterior" for b in bases) else "ok"
        series[s["id"]] = col.bloco(s, catalogo, fontes.arredondar_pontos(pontos, 4), status, carimbo)
    series = {s["id"]: series[s["id"]] for s in catalogo}
    return {
        "amostra_sintetica": True,
        "aviso": "Dados SINTÉTICOS (passeio aleatório com semente fixa). Servem só para testar a página.",
        "gerado_utc": carimbo,
        "gerado_brt": agora.astimezone(col.BRT).strftime("%d/%m/%Y %H:%M"),
        "series_ok": sum(1 for b in series.values() if b["status"] == "ok"),
        "series_total": len(series),
        "series": series,
    }


def main() -> int:
    caminho = sys.argv[1] if len(sys.argv) > 1 else SAIDA_PADRAO
    saida = gerar(col.carregar_catalogo())
    col.gravar(saida, caminho)
    print(f"amostra sintética: {saida['series_ok']}/{saida['series_total']} séries ok; "
          f"{os.path.getsize(caminho) // 1024} KiB em {caminho}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
