#!/usr/bin/env python3
"""Monitor Portugal — coleta e cálculo do painel (Euronext Lisbon, público residente em Portugal).

Material educativo. Não é recomendação de investimento.

Uso:
  python3 scripts/portugal/painel_pt.py --coletar   # baixa preços (fonte de cotações), lista da Euronext e taxa do BCE; recalcula
  python3 scripts/portugal/painel_pt.py             # só recalcula a partir de dados/portugal/brutos/ultimo.json

Regras (decididas na fase 0, ver docs/monitor-portugal/):
  - Proventos vêm SÓ do cadastro dados/portugal/proventos_oficiais.csv (comunicados oficiais).
    A fonte de cotações serve para preços, liquidez e como ALERTA de evento não cadastrado.
  - Base: ano de pagamento; média de 5 anos civis completos.
  - Preço-teto = DPA médio / taxa exigida; taxa exigida = OT 10 anos (BCE, média de 12 meses) + prémio, com mínimo.
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
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "dados" / "portugal"
BRUTOS = DADOS / "brutos"
UA = {"User-Agent": "Mozilla/5.0 (market-lab)"}
EURONEXT_LISTA = "https://live.euronext.com/pd_es/data/stocks/download?mics=XLIS"

# Feriados da Euronext Lisbon (bolsa fechada): 1/1, Sexta-feira Santa, Segunda-feira de Páscoa, 1/5, 25/12, 26/12.
def _pascoa(a):
    """Domingo de Páscoa (algoritmo anónimo gregoriano, Meeus/Jones/Butcher)."""
    a1 = a % 19; b1, c1 = divmod(a, 100); d1, e1 = divmod(b1, 4)
    f1 = (b1 + 8) // 25; g1 = (b1 - f1 + 1) // 3
    h1 = (19 * a1 + b1 - d1 - g1 + 15) % 30
    i1, k1 = divmod(c1, 4)
    l1 = (32 + 2 * e1 + 2 * i1 - h1 - k1) % 7
    m1 = (a1 + 11 * h1 + 22 * l1) // 451
    mes = (h1 + l1 - 7 * m1 + 114) // 31
    dia = (h1 + l1 - 7 * m1 + 114) % 31 + 1
    return date(a, mes, dia)


def feriados_euronext(ano):
    p = _pascoa(ano)
    return {date(ano, 1, 1), p - timedelta(days=2), p + timedelta(days=1), date(ano, 5, 1), date(ano, 12, 25), date(ano, 12, 26)}


def dia_util(d):
    return d.weekday() < 5 and d not in feriados_euronext(d.year)


def ultimo_fecho_esperado(agora_utc):
    """Último dia com fecho publicado esperado. Euronext Lisbon fecha às 16:30 de Lisboa; damos margem até 18:30 de Lisboa."""
    lisboa = agora_utc + timedelta(hours=1 if _verao(agora_utc) else 0)
    d = lisboa.date()
    if not (dia_util(d) and (lisboa.hour, lisboa.minute) >= (18, 30)):
        d -= timedelta(days=1)
        while not dia_util(d):
            d -= timedelta(days=1)
    return d


def _verao(t):
    """Hora de verão europeia: último domingo de março 01:00 UTC até último domingo de outubro 01:00 UTC."""
    def ult_dom(ano, mes):
        d = date(ano, mes + 1, 1) - timedelta(days=1) if mes < 12 else date(ano, 12, 31)
        return d - timedelta(days=(d.weekday() + 1) % 7)
    ini = datetime.combine(ult_dom(t.year, 3), datetime.min.time(), timezone.utc) + timedelta(hours=1)
    fim = datetime.combine(ult_dom(t.year, 10), datetime.min.time(), timezone.utc) + timedelta(hours=1)
    return ini <= t < fim


def baixar(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ---------------------------------------------------------------- dados manuais
def ler_json(nome):
    return json.loads((DADOS / nome).read_text(encoding="utf-8"))


def ler_proventos():
    eventos = []
    with open(DADOS / "proventos_oficiais.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not r["papel"] or r["papel"].startswith("#"):
                continue
            r["valor_bruto"] = float(r["valor_bruto"])
            eventos.append(r)
    return eventos


# ---------------------------------------------------------------- coleta
def coletar_precos(papeis):
    p1 = int(datetime(2019, 1, 1, tzinfo=timezone.utc).timestamp())
    p2 = int(time.time())
    out = {}
    for t in papeis:
        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{t}.LS?period1={p1}&period2={p2}"
               "&interval=1d&events=div%2Csplit")
        try:
            j = json.loads(baixar(url))
        except Exception as e:
            print(t, "erro", e)
            continue
        res = (j.get("chart", {}).get("result") or [None])[0]
        if not res or not res.get("timestamp"):
            print(t, "sem dados")
            continue
        q = res["indicators"]["quote"][0]
        serie = [(datetime.fromtimestamp(x, timezone.utc).strftime("%Y-%m-%d"), c, v)
                 for x, c, v in zip(res["timestamp"], q["close"], q["volume"]) if c is not None]
        divs = sorted((datetime.fromtimestamp(e["date"], timezone.utc).strftime("%Y-%m-%d"), round(e["amount"], 6))
                      for e in ((res.get("events") or {}).get("dividends") or {}).values())
        out[t] = {"serie": [[d, round(c, 4), int(v or 0)] for d, c, v in serie[-400:]],
                  "precos_mes": _medias_mensais(serie),
                  "divs_fonte": divs,
                  "moeda": res.get("meta", {}).get("currency", "")}
        time.sleep(0.4)
    return out


def _medias_mensais(serie):
    acc = {}
    for d, c, _ in serie:
        acc.setdefault(d[:7], []).append(c)
    return {m: round(sum(v) / len(v), 4) for m, v in acc.items()}


def coletar_euronext():
    bruto = baixar(EURONEXT_LISTA).decode("utf-8-sig", errors="replace")
    sep = ";" if bruto.count(";") > bruto.count(",") else ","
    lista = {}
    for linha in csv.reader(io.StringIO(bruto), delimiter=sep):
        i = next((k for k, c in enumerate(linha) if re.fullmatch(r"[A-Z]{2}[A-Z0-9]{9}\d", c.strip())), None)
        if i is not None and i + 1 < len(linha):
            lista[linha[i + 1].strip()] = {"nome": linha[0].strip(), "isin": linha[i].strip()}
    return lista


def coletar_taxa_bce(serie):
    url = f"https://data-api.ecb.europa.eu/service/data/{serie}?lastNObservations=12&format=csvdata"
    bruto = baixar(url).decode("utf-8")
    obs = []
    for r in csv.DictReader(io.StringIO(bruto)):
        try:
            obs.append([r["TIME_PERIOD"], float(r["OBS_VALUE"])])
        except (KeyError, ValueError):
            continue
    if len(obs) < 6:
        raise ValueError("série do BCE com poucas observações")
    return sorted(obs)


# ---------------------------------------------------------------- cálculo
def faixa_liquidez(liq, universo):
    """Alta (>= corte do núcleo), Média, Baixa; None sem dados."""
    if liq is None:
        return None
    if liq >= universo["corte_liquidez_eur"]:
        return "alta"
    if liq >= universo.get("corte_media_eur", 25000):
        return "media"
    return "baixa"


def regra_grupo(grupo, liq, liq_revisao_anterior, universo):
    """Regra de entrada e saída do núcleo. Usada só nas revisões do universo (runbook 2), nunca na coleta diária.

    Entra no núcleo com liquidez >= corte. Sai só se a liquidez ficar abaixo do corte de saída
    nesta revisão e também na revisão anterior (evita entra-e-sai a cada trimestre).
    """
    if liq is None:
        return grupo
    if grupo == "observacao" and liq >= universo["corte_liquidez_eur"]:
        return "nucleo"
    if (grupo == "nucleo" and liq < universo["corte_saida_eur"]
            and liq_revisao_anterior is not None and liq_revisao_anterior < universo["corte_saida_eur"]):
        return "observacao"
    return grupo


def calcular(universo, params, eventos, brutos, agora):
    hoje = agora.date()
    ano_fim = hoje.year - 1
    anos = [str(a) for a in range(ano_fim - params["anos_media"] + 1, ano_fim + 1)]
    inicio12 = (hoje - timedelta(days=365)).isoformat()

    taxa = brutos.get("taxa_bce") or {}
    obs = taxa.get("obs") or []
    if obs:
        ot10 = round(sum(v for _, v in obs) / len(obs), 3)
        taxa_info = {"ot10_media12m_pct": ot10, "ultima_obs": obs[-1], "n_obs": len(obs), "origem": "BCE",
                     "lida_em": taxa.get("lida_em")}
    else:
        ot10 = params["taxa_reserva_pct"]
        taxa_info = {"ot10_media12m_pct": ot10, "ultima_obs": None, "n_obs": 0, "origem": "reserva (BCE indisponível)",
                     "lida_em": None}
    exigida = max(ot10 + params["premio_pp"], params["taxa_minima_pct"])
    taxa_info.update({"premio_pp": params["premio_pp"], "taxa_minima_pct": params["taxa_minima_pct"],
                      "taxa_exigida_pct": round(exigida, 3), "faixa_pp": params["faixa_pp"]})

    precos = brutos.get("precos", {})
    fecho_esperado = ultimo_fecho_esperado(agora).isoformat()
    linhas = []
    for p in universo["papeis"]:
        t = p["papel"]
        todos = [e for e in eventos if e["papel"] == t]
        ev = [e for e in todos if e["tipo"] in ("dinheiro", "scrip")]  # distribuições em espécie não entram no cálculo
        especie = [e for e in todos if e["tipo"] == "especie"]
        capital = [e for e in todos if e["tipo"] == "capital"]  # devolução de capital (redução do valor nominal): não é dividendo
        por_ano = {a: round(sum(e["valor_bruto"] for e in ev if e["data_pagamento"][:4] == a), 6) for a in anos}
        d12 = round(sum(e["valor_bruto"] for e in ev if inicio12 < e["data_pagamento"] <= hoje.isoformat()), 6)
        vals = [por_ano[a] for a in anos]
        dpa_medio = round(sum(vals) / len(vals), 6)
        ordenados = sorted(vals)
        dpa_aparado = round(sum(ordenados[1:-1]) / (len(ordenados) - 2), 6) if len(ordenados) > 2 else dpa_medio
        anos_zero = [a for a in anos if por_ano[a] == 0]
        est_anos = {a: sorted({e["estado"] for e in ev if e["data_pagamento"][:4] == a}) for a in anos}
        a_conferir = sorted({e["data_pagamento"][:4] for e in ev if e["estado"] == "a_conferir"})
        ev_janela = [e for e in ev if e["data_pagamento"][:4] in anos or e["data_pagamento"] > inicio12]
        pct_oficial = round(100 * sum(1 for e in ev_janela if e["estado"] == "oficial") / len(ev_janela)) if ev_janela else None
        tem_scrip = any(e["tipo"] == "scrip" for e in ev_janela)

        pr = precos.get(t) or {}
        serie = pr.get("serie") or []
        preco, data_preco = (serie[-1][1], serie[-1][0]) if serie else (None, None)
        ult12 = [(c, v) for d, c, v in serie if d > inicio12]
        fin = [c * v for c, v in ult12]
        liq = round(statistics.median(fin)) if fin else None
        sem_neg = round(100 * sum(1 for x in fin if x == 0) / len(fin), 1) if fin else None
        variacao_12m = round(100 * (preco / ult12[0][0] - 1), 1) if preco and ult12 else None

        grupo = p.get("grupo", "nucleo")
        cadastro_ok = p.get("cadastro_proventos", "completo") == "completo"
        teto = round(dpa_medio / (exigida / 100), 4) if dpa_medio > 0 and cadastro_ok else None
        teto_robusto = round(dpa_aparado / (exigida / 100), 4) if dpa_aparado > 0 and cadastro_ok else None
        faixa = None
        if dpa_medio > 0 and cadastro_ok:
            faixa = [round(dpa_medio / ((exigida + params["faixa_pp"]) / 100), 4),
                     round(dpa_medio / (max(exigida - params["faixa_pp"], 0.5) / 100), 4)]
        margem = round(100 * (teto / preco - 1), 1) if teto and preco else None
        dy12 = round(100 * d12 / preco, 2) if preco else None
        dy_medio = round(100 * dpa_medio / preco, 2) if preco else None

        alertas = []
        def add(nivel, cod, texto):
            alertas.append({"nivel": nivel, "codigo": cod, "texto": texto})
        if not serie:
            add("grave", "sem_preco", "Sem cotação na fonte: o painel não calcula margem.")
        elif data_preco < fecho_esperado:
            add("atencao", "preco_atrasado", f"Último preço é de {data_preco}; esperado o fecho de {fecho_esperado}.")
        if anos_zero and cadastro_ok:  # com cadastro pendente, "zero" quer dizer "não conferido", não "não pagou"
            add("atencao", "anos_sem_proventos", f"Sem proventos em {', '.join(anos_zero)}: a média de 5 anos fica mais baixa e o teto também.")
        if a_conferir:
            add("atencao", "proventos_a_conferir", f"Proventos de {', '.join(a_conferir)} ainda sem documento oficial no cadastro.")
        if especie:
            add("info", "especie", "Houve distribuição em espécie (" + ", ".join(e["data_pagamento"] for e in especie) + "), não contada nos proventos.")
        if capital:
            add("info", "devolucao_capital", "Houve devolução de capital (" + ", ".join(f"{e['data_pagamento']}: {e['valor_bruto']:g}" for e in capital) + "), não contada nos proventos.")
        if tem_scrip:
            add("info", "scrip", "Parte dos proventos foi paga em ações (scrip). Conta-se o valor de referência por ação indicado pela empresa.")
        if grupo == "observacao":
            add("info", "fora_nucleo", "Em observação: fora do núcleo de alta liquidez (faixa " + (faixa_liquidez(liq, universo) or "sem dados") + ").")
        elif liq is not None and liq < universo["corte_liquidez_eur"]:
            add("atencao", "liquidez", f"Liquidez abaixo do corte do núcleo ({liq:,.0f} €/dia).".replace(",", "."))
        if sem_neg is not None and sem_neg > 20:
            add("atencao", "negociacao_intermitente", f"Negociação intermitente: {sem_neg}% dos dias sem negócio em 12 meses; o último preço pode não corresponder a um negócio real.")
        elif sem_neg is not None and sem_neg > universo["max_pct_dias_sem_negocio"]:
            add("atencao", "dias_sem_negocio", f"{sem_neg}% de dias sem negócio em 12 meses.")
        if not cadastro_ok:
            add("info", "cadastro_pendente", "Proventos ainda não conferidos no cadastro oficial: sem preço-teto até estarem conferidos.")
        if vals[-1] > 0 and vals[-2] > 0 and vals[-1] < 0.7 * vals[-2]:
            add("atencao", "queda_proventos", f"Proventos de {anos[-1]} caíram mais de 30% face a {anos[-2]}.")
        # Fonte de cotações como detector: evento de provento na fonte sem evento no cadastro até 45 dias.
        cad_datas = [datetime.strptime(e["data_pagamento"], "%Y-%m-%d").date() for e in todos]
        orfaos = []
        for d, v in pr.get("divs_fonte", []):
            dd = datetime.strptime(d, "%Y-%m-%d").date()
            if dd.isoformat() < f"{anos[0]}-01-01":
                continue
            if not any(abs((dd - c).days) <= 45 for c in cad_datas):
                orfaos.append(f"{d} ({v:g})")
        if orfaos:
            add("atencao", "evento_nao_cadastrado", "A fonte de cotações mostra provento sem registo oficial no cadastro: " + "; ".join(orfaos) + ".")

        if not serie:
            status, rotulo = "sem_preco", "Sem cotação"
        elif not cadastro_ok:
            status, rotulo = "em_cadastro", "Em cadastro: proventos por conferir"
        elif dpa_medio == 0:
            status, rotulo = "sem_proventos", "Sem proventos nos últimos 5 anos"
        elif preco <= teto:
            status, rotulo = ("abaixo_conferir", "Abaixo do teto · conferir dados") if (anos_zero or a_conferir) else ("abaixo", "Abaixo do teto calculado")
        else:
            status, rotulo = "acima", "Acima do teto calculado"

        linhas.append({
            **p,
            "grupo": grupo, "faixa_liquidez": faixa_liquidez(liq, universo), "cadastro_completo": cadastro_ok,
            "preco": preco, "data_preco": data_preco, "variacao_12m_pct": variacao_12m,
            "proventos_por_ano": por_ano, "estado_por_ano": est_anos,
            "proventos_12m": d12, "dpa_medio": dpa_medio, "dpa_aparado": dpa_aparado,
            "dy_12m_pct": dy12, "dy_medio_pct": dy_medio,
            "teto": teto, "teto_robusto": teto_robusto, "faixa_teto": faixa, "margem_pct": margem,
            "status": status, "status_rotulo": rotulo,
            "liquidez_mediana_12m_eur": liq, "pct_dias_sem_negocio_12m": sem_neg,
            "pct_eventos_oficiais": pct_oficial, "tem_scrip": tem_scrip,
            "eventos": [{k: e[k] for k in ("data_pagamento", "valor_bruto", "tipo", "exercicio", "estado", "fonte_url", "nota")}
                        for e in sorted(todos, key=lambda e: e["data_pagamento"], reverse=True)],
            "alertas": alertas,
            "historico_preco_mensal": dict(list((pr.get("precos_mes") or {}).items())[-60:]),
        })
    return {"anos": anos, "taxa": taxa_info, "linhas": linhas, "fecho_esperado": fecho_esperado}


def atualizar_historico(linhas, agora):
    arq = DADOS / "historico_status.json"
    hist = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
    for l in linhas:
        h = hist.setdefault(l["papel"], [])
        if not h or h[-1]["status"] != l["status"]:
            h.append({"data": agora.strftime("%Y-%m-%d"), "status": l["status"], "rotulo": l["status_rotulo"],
                      "preco": l["preco"], "teto": l["teto"]})
    corte = (agora - timedelta(days=366)).strftime("%Y-%m-%d")
    for k in hist:
        antigos = [x for x in hist[k] if x["data"] < corte]
        hist[k] = antigos[-1:] + [x for x in hist[k] if x["data"] >= corte]
    arq.write_text(json.dumps(hist, ensure_ascii=False, indent=1), encoding="utf-8")
    return hist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coletar", action="store_true")
    a = ap.parse_args()
    universo, params = ler_json("universo.json"), ler_json("parametros.json")
    eventos = ler_proventos()
    BRUTOS.mkdir(parents=True, exist_ok=True)
    ult = BRUTOS / "ultimo.json"
    anterior = json.loads(ult.read_text(encoding="utf-8")) if ult.exists() else {}
    agora = datetime.now(timezone.utc)

    if a.coletar:
        brutos = {"coletado_em": agora.isoformat(timespec="minutes")}
        papeis = [p["papel"] for p in universo["papeis"]]
        precos = coletar_precos(papeis)
        # Falha de download não derruba o painel: mantém o último preço guardado do papel que falhou.
        for t in papeis:
            if t not in precos and t in (anterior.get("precos") or {}):
                precos[t] = anterior["precos"][t]
                print(t, "mantido do último dado guardado")
        brutos["precos"] = precos
        try:
            obs = coletar_taxa_bce(params["serie_bce"])
            brutos["taxa_bce"] = {"obs": obs, "lida_em": agora.strftime("%Y-%m-%d")}
        except Exception as e:
            print("BCE indisponível:", e)
            brutos["taxa_bce"] = anterior.get("taxa_bce")
        try:
            brutos["euronext"] = coletar_euronext()
        except Exception as e:
            print("Lista Euronext indisponível:", e)
            brutos["euronext"] = anterior.get("euronext")
        ult.write_text(json.dumps(brutos, ensure_ascii=False), encoding="utf-8")
    else:
        brutos = anterior

    res = calcular(universo, params, eventos, brutos, agora)
    euronext = brutos.get("euronext") or {}
    universo_alertas = []
    for p in universo["papeis"]:
        e = euronext.get(p["papel"])
        if euronext and not e:
            universo_alertas.append(f"{p['papel']} não aparece na lista atual da Euronext Lisbon (saída da bolsa ou mudança de código?).")
        elif e and e["isin"] != p["isin"]:
            universo_alertas.append(f"{p['papel']}: ISIN no cadastro ({p['isin']}) difere da Euronext ({e['isin']}).")
    fund_arq = DADOS / "fundamentos.json"
    fund = json.loads(fund_arq.read_text(encoding="utf-8")) if fund_arq.exists() else {}
    for l in res["linhas"]:
        q = (fund.get("papeis") or {}).get(l["papel"])
        if q:
            l["qualidade"] = {k: q.get(k) for k in ("nota", "nota_provisoria", "motivo_sem_nota", "roe", "roe_medio_2a", "payout",
                                                    "payout_caixa", "div_liq_ebitda", "divida_liquida", "ebitda", "ll", "lpa",
                                                    "dpa_exercicio", "exercicio", "regra", "semaforo", "relatorio", "relatorio_url",
                                                    "flags", "erro")}
    ctrl_arq = DADOS / "controlo.json"
    ctrl = json.loads(ctrl_arq.read_text(encoding="utf-8")) if ctrl_arq.exists() else {}
    cmap = {c["papel"]: c for c in ctrl.get("empresas", [])}
    idade_ctrl = (agora.date() - datetime.strptime(ctrl["atualizado"], "%Y-%m-%d").date()).days if ctrl else None
    for l in res["linhas"]:
        c = cmap.get(l["papel"])
        if c:
            l["controlo"] = {k: c.get(k) for k in ("categoria", "estrutura", "controlador", "nota", "fonte", "data_ref", "confianca")}
        if idade_ctrl is not None and idade_ctrl > 90:
            l["alertas"].append({"nivel": "info", "codigo": "controlo_antigo",
                                 "texto": f"A classificação do controlo acionista tem {idade_ctrl} dias; pode estar desatualizada."})
    hist = atualizar_historico(res["linhas"], agora)
    painel = {
        "gerado_em": agora.isoformat(timespec="minutes"),
        "precos_coletados_em": brutos.get("coletado_em"),
        "autor": params["autor"],
        "aviso": "Material educativo, não é recomendação de investimento.",
        "parametros": params,
        "universo": {k: universo[k] for k in ("revisado_em", "proxima_revisao", "criterio", "corte_liquidez_eur", "corte_media_eur",
                                             "corte_saida_eur", "max_pct_dias_sem_negocio", "regra_grupo")},
        "universo_alertas": universo_alertas,
        "n_euronext_xlis": len(euronext) or None,
        **res,
        "historico_status": hist,
        "controlo_meta": {k: ctrl.get(k) for k in ("atualizado", "proxima_revisao", "criterio")} if ctrl else None,
        "qualidade_meta": {k: fund.get(k) for k in ("gerado_em", "fonte", "aceite")} if fund else None,
    }
    (DADOS / "painel.json").write_text(json.dumps(painel, ensure_ascii=False, indent=1), encoding="utf-8")
    n = {s: sum(1 for l in res["linhas"] if l["status"] == s) for s in {l["status"] for l in res["linhas"]}}
    print("Painel gerado:", len(res["linhas"]), "papéis", n, "| taxa exigida", res["taxa"]["taxa_exigida_pct"], "%", "|", res["taxa"]["origem"])
    for m in universo_alertas:
        print("UNIVERSO:", m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
