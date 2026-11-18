"""Funções puras do painel Mercados e ciclos: leitura das respostas de cada fonte,
limpeza, redução de frequência e séries derivadas. Nenhuma função aqui usa rede.

Cada leitor recebe o texto bruto da resposta e devolve [(data_iso, valor)] em ordem
crescente de data. Sem dependências externas (biblioteca padrão).
"""
from __future__ import annotations

import bisect
import calendar
import csv
import datetime as dt
import io
import json
import math
import re
from zoneinfo import ZoneInfo

# ---------------------------------------------------------------- utilidades


def _numero(bruto) -> float | None:
    """Converte para float; devolve None para vazio, ".", nulo ou não numérico."""
    if bruto is None:
        return None
    if isinstance(bruto, (int, float)):
        v = float(bruto)
    else:
        txt = str(bruto).strip()
        if txt in ("", ".", "-", "NaN", "null"):
            return None
        try:
            v = float(txt)
        except ValueError:
            return None
    return v if math.isfinite(v) else None


def _ordenar(pontos: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """Ordena por data e elimina datas repetidas (fica o último valor recebido)."""
    return sorted(dict(pontos).items())


def data_do_periodo(periodo: str, fim_do_mes: bool = False) -> str:
    """Normaliza o período da fonte para AAAA-MM-DD.

    Aceita AAAA-MM-DD, AAAA-MM (vira dia 1, ou o último dia com fim_do_mes) e AAAA-Wss (semana ISO; vira a sexta-feira,
    dia de referência do balanço semanal do Eurosistema)."""
    p = periodo.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", p):
        return dt.date.fromisoformat(p).isoformat()
    if re.fullmatch(r"\d{4}-\d{2}", p):
        ano, mes = int(p[:4]), int(p[5:])
        return dt.date(ano, mes, calendar.monthrange(ano, mes)[1] if fim_do_mes else 1).isoformat()
    m = re.fullmatch(r"(\d{4})-W(\d{1,2})", p)
    if m:
        return dt.date.fromisocalendar(int(m.group(1)), int(m.group(2)), 5).isoformat()
    raise ValueError(f"período não reconhecido: {periodo!r}")


# ---------------------------------------------------------------- leitores por fonte


def ler_yahoo(texto: str, granularidade: str | None = "1wk") -> list[tuple[str, float]]:
    """Endpoint chart do Yahoo Finance: preço de fechamento (sem ajuste por dividendos).

    Fechamentos nulos são descartados. Se a resposta informar granularidade diferente da
    pedida (o Yahoo troca semanal por mensal/trimestral em certos pedidos), a leitura falha.

    A data é calculada no fuso da bolsa (meta.exchangeTimezoneName, que respeita o horário
    de verão de cada data). Só se não houver nome de fuso usa-se meta.gmtoffset, que é o
    deslocamento do momento da coleta e erra uma hora metade do ano; sem isso, a barra
    semanal de Nova York ou Lisboa cairia no domingo da semana anterior."""
    dados = json.loads(texto)
    res = dados["chart"]["result"][0]
    meta = res.get("meta") or {}
    recebida = meta.get("dataGranularity")
    if granularidade and recebida and recebida != granularidade:
        raise ValueError(f"Yahoo: granularidade {recebida!r}, esperada {granularidade!r}")
    desloc = int(meta.get("gmtoffset") or 0)
    fuso = None
    nome_fuso = meta.get("exchangeTimezoneName")
    if nome_fuso:
        try:
            fuso = ZoneInfo(nome_fuso)
        except Exception:  # noqa: BLE001 - nome desconhecido: cai no deslocamento fixo
            fuso = None
    fechamentos = res["indicators"]["quote"][0]["close"]
    pontos = []
    for t, p in zip(res["timestamp"], fechamentos):
        v = _numero(p)
        if v is None:
            continue
        if fuso is not None:
            data = dt.datetime.fromtimestamp(t, fuso).date().isoformat()
        else:
            data = dt.datetime.fromtimestamp(t + desloc, dt.timezone.utc).date().isoformat()
        pontos.append((data, v))
    if not pontos:
        raise ValueError("Yahoo: resposta sem preços")
    return _ordenar(pontos)


def ler_fred(texto: str) -> list[tuple[str, float]]:
    """CSV do fredgraph: cabeçalho 'observation_date,CODIGO'; ausente vem vazio ou '.'."""
    linhas = list(csv.reader(io.StringIO(texto.strip())))
    if not linhas or len(linhas[0]) < 2 or "date" not in linhas[0][0].lower():
        raise ValueError("FRED: cabeçalho inesperado")
    pontos = []
    for lin in linhas[1:]:
        if len(lin) < 2:
            continue
        v = _numero(lin[1])
        if v is None:
            continue
        pontos.append((data_do_periodo(lin[0]), v))
    if not pontos:
        raise ValueError("FRED: resposta sem valores")
    return _ordenar(pontos)


def ler_bcb(texto: str) -> list[tuple[str, float]]:
    """SGS do Banco Central: [{"data": "dd/mm/aaaa", "valor": "1.23"}]; valor pode ser nulo.

    A ordem recebida não é confiável (SGS 27810) e podem vir datas futuras (SGS 432);
    aqui só se ordena, o corte de datas futuras é feito em limpar()."""
    dados = json.loads(texto)
    if not isinstance(dados, list):
        raise ValueError("BCB: resposta não é uma lista")
    pontos = []
    for item in dados:
        v = _numero(item.get("valor"))
        if v is None:
            continue
        d, m, a = item["data"].split("/")
        pontos.append((dt.date(int(a), int(m), int(d)).isoformat(), v))
    if not pontos:
        raise ValueError("BCB: resposta sem valores")
    return _ordenar(pontos)


def ler_eurostat(texto: str) -> list[tuple[str, float]]:
    """JSON-stat do Eurostat com uma única série (todas as dimensões fixas, menos o tempo).

    'value' é um dicionário posição -> valor; a posição vem de dimension.time.category.index."""
    dados = json.loads(texto)
    tamanhos = dados.get("size") or []
    ids = dados.get("id") or []
    if "time" not in ids or any(n != 1 for i, n in zip(ids, tamanhos) if i != "time"):
        raise ValueError("Eurostat: esperava uma única série por chamada")
    indice = dados["dimension"]["time"]["category"]["index"]
    valores = dados.get("value") or {}
    if isinstance(valores, list):
        valores = {str(i): v for i, v in enumerate(valores)}
    pontos = []
    for periodo, pos in indice.items():
        v = _numero(valores.get(str(pos)))
        if v is None:
            continue
        pontos.append((data_do_periodo(periodo), v))
    if not pontos:
        raise ValueError("Eurostat: resposta sem valores")
    return _ordenar(pontos)


def ler_bce(texto: str) -> list[tuple[str, float]]:
    """CSV (format=csvdata) do portal de dados do BCE.

    As colunas TIME_PERIOD e OBS_VALUE são localizadas pelo nome do cabeçalho (a posição muda
    de um fluxo para outro e há campos entre aspas com vírgulas). Mensal "2026-08" vira o
    último dia do mês (estoque de fim de mês); semanal "2026-W45" vira a sexta-feira da semana ISO."""
    pontos = []
    for lin in csv.DictReader(io.StringIO(texto, newline="")):
        v = _numero(lin.get("OBS_VALUE"))
        if v is None or not lin.get("TIME_PERIOD"):
            continue
        pontos.append((data_do_periodo(lin["TIME_PERIOD"], fim_do_mes=True), v))
    if not pontos:
        raise ValueError("BCE: resposta sem valores")
    return _ordenar(pontos)


LEITORES = {"yahoo": ler_yahoo, "fred": ler_fred, "bcb": ler_bcb, "eurostat": ler_eurostat, "bce": ler_bce}

# ---------------------------------------------------------------- limpeza e redução


def limpar(pontos, hoje_iso: str, inicio_iso: str | None = None) -> list[tuple[str, float]]:
    """Ordena, elimina repetidas, corta datas futuras e anteriores ao início pedido."""
    return [(d, v) for d, v in _ordenar([(d, v) for d, v in pontos])
            if d <= hoje_iso and (inicio_iso is None or d >= inicio_iso)]


def reduzir_semanal(pontos, manter_fim_de_mes: bool = False) -> list[tuple[str, float]]:
    """Fica com o último ponto de cada semana ISO; a data é a data real desse ponto.

    Com manter_fim_de_mes, o último ponto de cada mês também é mantido."""
    pontos = _ordenar(pontos)
    manter = {}
    for d, v in pontos:
        data = dt.date.fromisoformat(d)
        manter[("s",) + tuple(data.isocalendar()[:2])] = (d, v)
        if manter_fim_de_mes:
            manter[("m", data.year, data.month)] = (d, v)
    return _ordenar(list(manter.values()))


def arredondar(valor: float, algarismos: int = 4) -> float | int:
    """Arredonda para N algarismos significativos (reduz o tamanho do arquivo)."""
    if valor == 0 or not math.isfinite(valor):
        return 0
    casas = algarismos - 1 - int(math.floor(math.log10(abs(valor))))
    r = round(valor, casas)
    return int(r) if casas <= 0 else r


def arredondar_pontos(pontos, algarismos: int = 4) -> list[list]:
    return [[d, arredondar(v, algarismos)] for d, v in pontos]


# ---------------------------------------------------------------- séries derivadas


def _um_ano_antes(data: dt.date) -> dt.date:
    try:
        return data.replace(year=data.year - 1)
    except ValueError:  # 29 de fevereiro
        return data.replace(year=data.year - 1, day=28)


def variacao_12m(pontos, tolerancia_dias: int = 6) -> list[tuple[str, float]]:
    """Variação % frente ao ponto de um ano antes.

    Usa o ponto mais próximo da mesma data do ano anterior; se ele estiver a mais de
    tolerancia_dias do alvo (buraco na série), não calcula."""
    pontos = _ordenar(pontos)
    datas = [d for d, _ in pontos]
    saida = []
    for d, v in pontos:
        alvo = _um_ano_antes(dt.date.fromisoformat(d))
        i = bisect.bisect_right(datas, alvo.isoformat())
        vizinhos = [pontos[j] for j in (i - 1, i) if 0 <= j < len(pontos) and pontos[j][0] < d]
        if not vizinhos:
            continue
        d0, v0 = min(vizinhos, key=lambda p: abs((dt.date.fromisoformat(p[0]) - alvo).days))
        if abs((dt.date.fromisoformat(d0) - alvo).days) > tolerancia_dias or v0 <= 0:
            continue
        saida.append((d, (v / v0 - 1) * 100))
    return saida


def fim_de_mes(pontos) -> dict[str, float]:
    """Último valor de cada mês: {"AAAA-MM": valor}."""
    return {d[:7]: v for d, v in _ordenar(pontos)}


def juro_real(taxa, inflacao_12m) -> list[tuple[str, float]]:
    """Juro real ex-post aproximado: taxa no fim do mês menos inflação em 12 meses do mesmo mês.

    Diferença simples (não a fórmula de Fisher). Data do ponto = data do ponto de inflação."""
    taxa_mes = fim_de_mes(taxa)
    return [(d, taxa_mes[d[:7]] - v) for d, v in _ordenar(inflacao_12m) if d[:7] in taxa_mes]


def razao(numerador, denominador) -> list[tuple[str, float]]:
    """Razão entre duas séries, nas datas em que as duas têm ponto (mesma data exata).

    Usada para comparar dois preços de ativos (ex.: setor defensivo sobre setor de
    crescimento): valor > 1 significa que o numerador custa mais que o denominador."""
    den = dict(_ordenar(denominador))
    saida = []
    for d, v in _ordenar(numerador):
        w = den.get(d)
        if w is None or w <= 0:
            continue
        saida.append((d, v / w))
    return saida


def media_movel(pontos, janela: int = 200) -> list[tuple[str, float]]:
    """Média simples dos últimos `janela` pontos, emitida só quando a janela está completa.

    Para dados semanais, janela=200 é a média de 200 semanas. Data do ponto = data do
    fechamento da última semana da janela."""
    pontos = _ordenar(pontos)
    saida = []
    soma = 0.0
    for i, (d, v) in enumerate(pontos):
        soma += v
        if i >= janela:
            soma -= pontos[i - janela][1]
        if i >= janela - 1:
            saida.append((d, soma / janela))
    return saida


def calcular_derivada(calculo: str, bases: list[list]) -> list[tuple[str, float]]:
    """Aplica o cálculo do catálogo às séries-base (na ordem de derivada_de)."""
    bases = [[(d, v) for d, v in b] for b in bases]
    if calculo == "variacao_12m":
        return variacao_12m(bases[0])
    if calculo == "juro_real":
        return juro_real(bases[0], bases[1])
    if calculo == "razao":
        return razao(bases[0], bases[1])
    if calculo == "media_movel_200":
        return media_movel(bases[0], 200)
    raise ValueError(f"cálculo desconhecido: {calculo}")
