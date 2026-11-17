"""Coleta as séries do painel Mercados e ciclos e grava mercados.json.

Uso: MERCADOS_SAIDA=caminho/mercados.json python3 scripts/mercados/coletar_mercados.py
     MERCADOS_ANTERIOR (opcional): arquivo da execução anterior; padrão = o próprio MERCADOS_SAIDA.
Sem dependências externas (biblioteca padrão).

Regras:
- Uma série por entrada de catalogo_series.json; a leitura de cada fonte está em fontes.py.
- Pontos em ordem crescente, sem datas futuras, a partir do início definido no catálogo.
- Séries diárias são reduzidas a um ponto por semana (último valor da semana ISO).
- Se uma série falhar, o bloco inteiro do arquivo anterior é reaproveitado com status "anterior";
  sem arquivo anterior, a série sai com status "sem dados" e pontos vazios.
- Séries derivadas são recalculadas das séries-base do próprio arquivo e herdam "anterior".
- Se TODAS as séries coletadas falharem, o arquivo não é regravado e o código de saída é 1.
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
import fontes  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
CATALOGO = os.path.join(AQUI, "catalogo_series.json")
SAIDA = os.environ.get("MERCADOS_SAIDA") or os.path.join(RAIZ, "monitor", "mercados", "data", "mercados.json")
ANTERIOR = os.environ.get("MERCADOS_ANTERIOR") or SAIDA
BRT = ZoneInfo("America/Sao_Paulo")
UA = "Mozilla/5.0 (X11; Linux x86_64) painel-mercados/1.0"
INICIO_PADRAO = "2000-01-01"

# period1/period2 em vez de range=max: com range=max o Yahoo devolve barras mensais ou trimestrais
# mesmo pedindo interval=1wk (teste real de 16/11/2026). period1 = 01/01/2000 (UTC).
URL_YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{}?period1={}&period2={}&interval=1wk"
PERIOD1_YAHOO = 946684800
URL_FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"
URL_BCB = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados?formato=json"
URL_EUROSTAT = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_minr"
                "?format=JSON&geo={}&unit=RCH_A&coicop18=TOTAL&sinceTimePeriod=2000-01")
URL_BCE = "https://data-api.ecb.europa.eu/service/data/{}?format=csvdata"

NOME_FONTE = {
    "yahoo": "Yahoo Finance ({codigo})",
    "fred": "FRED, Federal Reserve Bank of St. Louis ({codigo})",
    "bcb": "Banco Central do Brasil (SGS {codigo})",
    "eurostat": "Eurostat (prc_hicp_minr, geo={geo})",
    "bce": "Banco Central Europeu ({codigo})",
}
CAMPOS_BLOCO = ("nome", "url_fonte", "codigo", "periodicidade", "unidade", "ajuste_sazonal")


def baixar(url: str, tentativas: int = 2, timeout: int = 45) -> str:
    """Baixa o texto de um endereço; repete uma vez em caso de falha."""
    erro = None
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8-sig")
        except Exception as e:  # noqa: BLE001 - qualquer falha de rede vale nova tentativa
            erro = e
            if i + 1 < tentativas:
                time.sleep(2)
    raise erro


def carregar_catalogo(caminho: str = CATALOGO) -> list[dict]:
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)["series"]


def enderecos(serie: dict, hoje: dt.date) -> list[str]:
    """Endereços a chamar para uma série (mais de um quando a API exige janelas de datas)."""
    fonte, codigo = serie["fonte"], serie["codigo"]
    if fonte == "yahoo":
        fim = dt.datetime.combine(hoje + dt.timedelta(days=1), dt.time(), dt.timezone.utc)
        return [URL_YAHOO.format(urllib.parse.quote(codigo), PERIOD1_YAHOO, int(fim.timestamp()))]
    if fonte == "fred":
        return [URL_FRED.format(codigo)]
    if fonte == "eurostat":
        return [URL_EUROSTAT.format(serie["geo"])]
    if fonte == "bce":
        return [URL_BCE.format(serie["caminho"])]
    if fonte == "bcb":
        base = URL_BCB.format(codigo)
        anos = serie.get("janela_anos")
        if not anos:
            return [base]
        # Séries diárias do SGS: a API exige dataInicial/dataFinal com janela de até 10 anos.
        urls, ano = [], int((serie.get("inicio") or INICIO_PADRAO)[:4])
        while ano <= hoje.year:
            fim = min(dt.date(ano + anos - 1, 12, 31), hoje)
            urls.append(f"{base}&dataInicial=01/01/{ano}&dataFinal={fim.strftime('%d/%m/%Y')}")
            ano += anos
        return urls
    raise ValueError(f"fonte desconhecida: {fonte}")


def coletar_serie(serie: dict, buscar, hoje: dt.date, pausa: float = 0.0) -> list[list]:
    """Busca, lê, limpa, reduz e arredonda uma série. Levanta exceção se não houver pontos."""
    leitor = fontes.LEITORES[serie["fonte"]]
    pontos = []
    for url in enderecos(serie, hoje):
        pontos.extend(leitor(buscar(url)))
        if pausa:
            time.sleep(pausa)
    pontos = fontes.limpar(pontos, hoje.isoformat(), serie.get("inicio"))
    if serie.get("reduzir_semanal") or serie["fonte"] == "yahoo":
        pontos = fontes.reduzir_semanal(pontos, bool(serie.get("manter_fim_de_mes")))
    if not pontos:
        raise ValueError("nenhum ponto válido depois da limpeza")
    return fontes.arredondar_pontos(pontos, serie.get("algarismos", 4))


def nome_fonte(serie: dict, catalogo: list[dict]) -> str:
    if serie["fonte"] == "derivada":
        nomes = {s["id"]: s["nome"] for s in catalogo}
        return "Cálculo do market-lab a partir de: " + "; ".join(nomes[i] for i in serie["derivada_de"])
    return NOME_FONTE[serie["fonte"]].format(**serie)


def semana_corrente(data_iso: str | None, hoje: dt.date) -> bool:
    """Verdadeiro se a data cai na mesma semana ISO de hoje."""
    return bool(data_iso) and dt.date.fromisoformat(data_iso).isocalendar()[:2] == hoje.isocalendar()[:2]


def bloco(serie: dict, catalogo: list[dict], pontos: list[list], status: str, coletado: str | None,
          hoje: dt.date | None = None) -> dict:
    b = {k: serie.get(k) for k in CAMPOS_BLOCO}
    b["fonte"] = nome_fonte(serie, catalogo)
    b["ultimo_dado"] = pontos[-1][0] if pontos else None
    b["coletado_utc"] = coletado
    b["status"] = status
    if serie["fonte"] == "yahoo":
        # A barra da semana em andamento traz a cotação mais recente, não um fechamento semanal.
        b["ultimo_parcial"] = bool(hoje and pontos and semana_corrente(pontos[-1][0], hoje))
    if serie.get("observacao"):
        b["nota"] = serie["observacao"]
    b["pontos"] = pontos
    return b


def _reaproveitar(serie: dict, catalogo: list[dict], anterior: dict | None, hoje: dt.date | None = None) -> dict:
    """Bloco do arquivo anterior com status "anterior"; sem anterior, bloco vazio "sem dados"."""
    antigo = ((anterior or {}).get("series") or {}).get(serie["id"])
    if antigo and antigo.get("pontos"):
        novo = dict(antigo)
        novo["status"] = "anterior"
        # Dia da primeira falha seguida: mantido enquanto a série seguir em "anterior".
        desde = antigo.get("anterior_desde") if antigo.get("status") == "anterior" else None
        novo["anterior_desde"] = desde or (hoje.isoformat() if hoje else None)
        if "ultimo_parcial" in novo:
            novo["ultimo_parcial"] = bool(hoje and semana_corrente(novo.get("ultimo_dado"), hoje))
        return novo
    return bloco(serie, catalogo, [], "sem dados", None)


def coletar(catalogo: list[dict], buscar=baixar, anterior: dict | None = None,
            agora_utc: dt.datetime | None = None, pausa: float = 0.0) -> dict | None:
    """Monta o conteúdo de mercados.json. Devolve None se todas as séries coletadas falharem."""
    agora_utc = agora_utc or dt.datetime.now(dt.timezone.utc)
    hoje = agora_utc.date()
    carimbo = agora_utc.isoformat(timespec="minutes")
    series, tentadas, obtidas = {}, 0, 0
    for s in catalogo:
        if s["fonte"] == "derivada":
            continue
        if s.get("coletar") is False:  # série desligada no catálogo (ver observação)
            series[s["id"]] = bloco(s, catalogo, [], "sem dados", None)
            continue
        tentadas += 1
        try:
            series[s["id"]] = bloco(s, catalogo, coletar_serie(s, buscar, hoje, pausa), "ok", carimbo, hoje)
            obtidas += 1
        except Exception as e:  # noqa: BLE001 - falha de rede/formato vira "anterior" ou "sem dados"
            print(f"[aviso] {s['id']} ({s['fonte']} {s['codigo']}): {type(e).__name__}: {e}", file=sys.stderr)
            series[s["id"]] = _reaproveitar(s, catalogo, anterior, hoje)
    if tentadas and obtidas == 0:
        return None
    for s in catalogo:
        if s["fonte"] != "derivada":
            continue
        bases = [series.get(i) for i in s["derivada_de"]]
        if any(b is None or not b["pontos"] for b in bases):
            series[s["id"]] = _reaproveitar(s, catalogo, anterior, hoje)
            continue
        try:
            pontos = fontes.limpar(fontes.calcular_derivada(s["calculo"], [b["pontos"] for b in bases]),
                                   hoje.isoformat())
            if not pontos:
                raise ValueError("derivada sem pontos")
        except Exception as e:  # noqa: BLE001
            print(f"[aviso] {s['id']} (derivada): {e}", file=sys.stderr)
            series[s["id"]] = _reaproveitar(s, catalogo, anterior, hoje)
            continue
        herdado = "anterior" if any(b["status"] == "anterior" for b in bases) else "ok"
        coletado = min((b["coletado_utc"] for b in bases if b.get("coletado_utc")), default=carimbo)
        series[s["id"]] = bloco(s, catalogo, fontes.arredondar_pontos(pontos, 4), herdado, coletado)
    ordenadas = {s["id"]: series[s["id"]] for s in catalogo}
    return {
        "gerado_utc": carimbo,
        "gerado_brt": agora_utc.astimezone(BRT).strftime("%d/%m/%Y %H:%M"),
        "series_ok": sum(1 for b in ordenadas.values() if b["status"] == "ok"),
        "series_total": len(ordenadas),
        "series": ordenadas,
    }


def ler_anterior(caminho: str) -> dict | None:
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def gravar(saida: dict, caminho: str) -> None:
    """Grava em formato compacto, primeiro em arquivo temporário (não deixa arquivo pela metade)."""
    os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
    tmp = caminho + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, caminho)


def main(buscar=baixar, caminho_saida: str | None = None, caminho_anterior: str | None = None,
         pausa: float = 0.4) -> int:
    caminho_saida = caminho_saida or SAIDA
    anterior = ler_anterior(caminho_anterior or (ANTERIOR if caminho_saida == SAIDA else caminho_saida))
    saida = coletar(carregar_catalogo(), buscar, anterior, pausa=pausa)
    if saida is None:
        print("Nenhuma série coletada; arquivo anterior mantido.", file=sys.stderr)
        return 1
    gravar(saida, caminho_saida)
    cont = {}
    for b in saida["series"].values():
        cont[b["status"]] = cont.get(b["status"], 0) + 1
    print(f"ok: {saida['series_ok']}/{saida['series_total']} séries; {cont}; gravado em {caminho_saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
