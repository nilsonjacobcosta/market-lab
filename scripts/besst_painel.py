"""Monitor BESST: coleta preços e proventos, calcula preço-teto (Bazin) e aplica regras de qualidade de dados.

Uso:
  python3 scripts/besst_painel.py --coletar   # baixa dados do Yahoo Finance e recalcula (usado pelo GitHub Actions)
  python3 scripts/besst_painel.py             # recalcula a partir do último arquivo bruto salvo

Caminhos: tudo fica em dados/besst/ (relativo a este arquivo, que fica em scripts/):
  universo.json, estatais.json, situacoes_especiais.json (lista manual versionada),
  brutos/ultimo.json (gravado por --coletar e lido no recálculo; se faltar, usa o yahoo_*.json mais recente)
  e a saída painel.json. Para testes, a pasta pode ser trocada pela variável de ambiente BESST_BASE.

Método v1 (inalterado; todos os campos antigos continuam com o mesmo significado):
  - DPA médio: média simples dos proventos por ação (dividendos + JCP, por data-ex) nos 5 últimos anos completos.
  - DY médio, preço-teto (DPA médio ÷ 6%, Bazin), margem, DY 12m, tendência, status, baixa_liquidez.
  Única mudança de valor em campo da v1: `status` ganha o valor "nao_se_aplica" quando o papel tem alerta grave
  (situação especial, sem negociação ou margem positiva implausível). Os números continuam no JSON e o status
  calculado pela v1 fica em `status_calculado`.

Acréscimos (campos novos, nada removido):
  - dpa_mediana, dpa_aparada, dpa_robusto, preco_teto_robusto, margem_robusta, status_robusto, status_calculado,
    anos_completos, ano_parcial_excluido, nivel_alerta ("ok" | "atencao" | "grave"), alertas (códigos),
    alertas_texto (frases curtas para iniciantes), alertas_detalhe, situacao_especial (dict, se houver).
  - DPA robusto = média aparada (sem o maior e o menor ano) com 5 anos válidos; mediana com 3 ou 4.
    Ficam fora do cálculo robusto o 1º ano de negociação (IPO/listagem no meio do ano) e os anos-lacuna
    (provento zerado entre anos pagadores, típico de falha da fonte).
"""
import json
import os
import statistics
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = Path(os.environ.get("BESST_BASE") or Path(__file__).resolve().parent.parent / "dados" / "besst")
BRUTOS = BASE / "brutos"
TAXA_BAZIN = 0.06
ANOS = 5
LIQ_MIN = 500  # R$ mil por dia (v1: "baixa liquidez")
INICIO_COLETA = 2019  # a coleta começa em 01/01/2019: série que começa depois disso = listagem no meio do período

# --- parâmetros das regras de qualidade (v2) ---
LIQ_SEM_NEGOCIO = 50          # R$ mil/dia: abaixo disso o papel é tratado como "sem negociação"
FATOR_EXTRA = 2.0             # ano > 2× a mediana dos demais anos = provento extraordinário
FATOR_LACUNA = 0.10           # ano < 10% da mediana dos demais (que pagaram) = possível lacuna na fonte
FATOR_DY12M = 1.75            # proventos 12m > 1,75× o DPA robusto = DY 12m não recorrente
MARGEM_MAX, MARGEM_MIN = 60.0, -100.0
TENDENCIA_QUEDA = -25.0       # último ano completo ≤ −25% da média (atenção)
FATOR_DY12M_BAIXO = 0.5       # DY 12m < ½ DY médio = rendimento atual bem abaixo do histórico (atenção)
QUEDA_PRECO = 0.5             # preço atual < 50% do preço médio do último ano completo
DIVERG_CLASSES = (0.8, 1.25)  # razão da soma de proventos entre classes (ON/PN) fora desta faixa
DIVERG_ANO = 1.3              # ou um ano específico com diferença > 30% entre classes

TEXTOS = {
    "extraordinario": "Houve provento extraordinário em {anos}; a média simples fica inflada — use o teto robusto.",
    "lacuna_proventos": "Proventos quase zerados em {anos} entre anos pagadores: possível falha da fonte; confira no RI.",
    "dy12m_atipico": "O DY dos últimos 12 meses está bem acima do normal da empresa e pode não se repetir.",
    "sem_negociacao": "Quase não há negócios: o preço mostrado pode ser antigo e pode ser difícil comprar ou vender.",
    "historico_curto": "Histórico curto ({n} anos completos): a média de proventos é pouco confiável.",
    "proventos_esporadicos": "Pagou proventos em poucos anos ({n} de {t}); a média não indica um pagamento regular.",
    "situacao_especial": "Situação especial: {txt}",
    "divergencia_classes": "Proventos diferentes entre as classes da mesma empresa ({outros}); confira os dados.",
    "ajuste_suspeito": "Salto nos proventos perto de um desdobramento/grupamento em {data}; ajuste pode estar errado.",
    "margem_extrema": "Margem de +{m}% sobre o teto, fora do razoável: normalmente indica erro ou evento atípico, não pechincha.",
    "margem_negativa_extrema": "Preço muito acima do teto ({m}%): os proventos são pequenos perto do preço e o método Bazin diz pouco sobre este papel.",
    "tendencia_queda": "Proventos do último ano caíram {t}% em relação à média: o passado pode não se repetir.",
    "dy12m_baixo": "O DY dos últimos 12 meses ({d12}%) está abaixo da metade do DY médio ({dm}%): os proventos recentes caíram.",
    "baixa_liquidez": "Pouca negociação (menos de R$ 500 mil por dia): pode ser difícil comprar ou vender pelo preço mostrado.",
    "preco_desabou": "O preço caiu mais da metade em relação ao ano passado: o mercado vê um problema.",
    "sem_proventos_12m": "Nenhum provento com data-ex nos últimos 12 meses.",
}
GRAVES = {"situacao_especial", "sem_negociacao", "margem_extrema"}  # grave = teto não se aplica
TEXTO_NAO_SE_APLICA = {
    "situacao_especial": "Preço-teto não se aplica: a empresa está em situação especial e os proventos passados não servem de referência.",
    "sem_negociacao": "Preço-teto não se aplica: o papel quase não é negociado e o preço mostrado pode não ser real.",
    "margem_extrema": "Preço-teto não se aplica: o teto calculado fica implausivelmente acima do preço, sinal de erro ou provento atípico.",
}


def _pct(v):
    return f"{v:+.1f}".replace(".", ",") if v is not None else "–"


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
    """Cálculo v1, idêntico ao script original."""
    anos = [str(y) for y in range(ano_ref - ANOS, ano_ref)]
    est = {}
    for e in estatais.get("empresas", []):
        for t in e.get("tickers", []):
            est[t] = e
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
            if dpa > 0 and anos[-1] in pm:
                row["tendencia"] = round((dy.get(anos[-1], 0.0) / dpa - 1) * 100, 1)
        row["status"] = ("historico_curto" if len(validos) < 3 else
                         "sem_proventos" if not row.get("dpa_medio") else
                         "abaixo_teto" if preco <= row["preco_teto"] else "acima_teto")
        row["baixa_liquidez"] = vol < LIQ_MIN
        linhas.append(row)
    return linhas


# ---------------------------------------------------------------- regras v2
def _mediana_demais(vals, i):
    resto = vals[:i] + vals[i + 1:]
    return statistics.median(resto) if resto else 0.0


def _situacoes(dados):
    idx = {}
    for c in dados.get("casos", []):
        for t in c.get("tickers", []):
            idx[t] = c
    return idx


def nao_se_aplica(l):
    """Papel com alerta grave: sem situação de teto (os números continuam no JSON)."""
    l["status_calculado"] = l["status"]
    l["status"] = "nao_se_aplica"
    if "status_robusto" in l:
        l["status_robusto"] = "nao_se_aplica"
    motivo = next(c for c in ("situacao_especial", "sem_negociacao", "margem_extrema") if c in l["alertas"])
    l["motivo_sem_teto"] = TEXTO_NAO_SE_APLICA[motivo]


def qualidade(linhas, brutos, ano_ref, situacoes):
    anos = [str(y) for y in range(ano_ref - ANOS, ano_ref)]
    sit = _situacoes(situacoes)
    por_empresa = {}
    for l in linhas:
        if l["status"] != "sem_cotacao" and not l["ticker"].endswith(("11", "12")):  # units têm outra proporção
            por_empresa.setdefault(l["empresa"], []).append(l["ticker"])

    for l in linhas:
        t = l["ticker"]
        alertas, textos, extra = [], [], {}

        def add(cod, **kw):
            if cod not in alertas:
                alertas.append(cod)
                textos.append(TEXTOS[cod].format(**kw))

        c = sit.get(t)
        if c:
            l["situacao_especial"] = {k: c.get(k) for k in ("tipo", "descricao", "data", "fonte")}
            add("situacao_especial", txt=c.get("texto_iniciante") or c.get("descricao"))
        r = brutos.get(t)
        if l["status"] == "sem_cotacao" or not r:
            if alertas:
                l.update(alertas=alertas, alertas_texto=textos, nivel_alerta="grave")
            continue
        preco, data, pm, dy, d12, spl, vol = r

        # (d) histórico curto: 1º ano de uma série iniciada após 2019 é parcial (listagem/IPO no meio do ano)
        serie = sorted(pm)
        parcial = serie[0] if serie and int(serie[0]) > INICIO_COLETA else None
        completos = [a for a in anos if a in pm and a != parcial]
        l["anos_completos"] = len(completos)
        if parcial in anos:
            l["ano_parcial_excluido"] = parcial
        if len(completos) < ANOS:
            add("historico_curto", n=len(completos))

        vals = [dy.get(a, 0.0) for a in completos]
        lac = []
        if len(vals) >= 3:
            # (b1) lacuna: ano(s) quase zerado(s) "cercado(s)" por anos pagadores (antes e depois, incluindo
            #      o ano corrente) — padrão típico de falha da fonte, não de corte real de proventos.
            #      Só faz sentido para quem paga com regularidade (>= 3 anos pagadores).
            pagos_ref = [v for v in vals if v > 0]
            base = statistics.median(pagos_ref) if len(pagos_ref) >= 3 else 0.0
            ate_hoje = [str(y) for y in range(int(min(pm)), ano_ref + 1)]
            baixo = {a: dy.get(a, 0.0) < FATOR_LACUNA * base for a in ate_hoje}
            for a in completos:
                if base <= 0 or not baixo[a]:
                    continue
                i = ate_hoje.index(a)
                esq = next((x for x in reversed(ate_hoje[:i]) if not baixo[x]), None)
                dir_ = next((x for x in ate_hoje[i + 1:] if not baixo[x]), None)
                if esq and dir_:
                    lac.append(a)
            if lac:
                add("lacuna_proventos", anos=", ".join(lac))
                extra["anos_lacuna"] = lac

            # DPA robusto: sem o ano parcial (já fora de `completos`) e sem os anos-lacuna,
            # desde que sobrem pelo menos 3 anos; senão usa todos os anos completos.
            uteis = [v for a, v in zip(completos, vals) if a not in lac]
            if len(uteis) < 3:
                uteis = vals
            med = statistics.median(uteis)
            apar = (sum(sorted(uteis)[1:-1]) / (len(uteis) - 2)) if len(uteis) >= 5 else med
            rob = apar
            l["dpa_mediana"] = round(med, 4)
            l["dpa_aparada"] = round(apar, 4)
            l["dpa_robusto"] = round(rob, 4)
            teto_r = rob / TAXA_BAZIN
            l["preco_teto_robusto"] = round(teto_r, 2)
            l["margem_robusta"] = round((teto_r - preco) / teto_r * 100, 1) if teto_r > 0 else None
            l["status_robusto"] = ("sem_proventos" if teto_r <= 0 else
                                   "abaixo_teto" if preco <= teto_r else "acima_teto")

            # (b2) extraordinário: ano > 2× a mediana dos demais (sem os anos-lacuna) E pico em relação
            #      aos anos vizinhos (> 1,5× cada vizinho completo) — evita marcar crescimento gradual
            pagos = sum(1 for v in vals if v > 0)
            if pagos <= 2 and any(v > 0 for v in vals):
                add("proventos_esporadicos", n=pagos, t=len(vals))
            ext = []
            for i, a in enumerate(completos):
                demais = [v for j, (b, v) in enumerate(zip(completos, vals)) if j != i and b not in lac]
                if vals[i] < 0.05 or not demais:
                    continue
                md = statistics.median(demais)
                viz = [dy.get(str(int(a) + k), 0.0) for k in (-1, 1)
                       if str(int(a) + k) in pm and str(int(a) + k) != str(ano_ref) and str(int(a) + k) != parcial]
                pico = all(vals[i] > 1.5 * v for v in viz)
                if (md == 0 or vals[i] > FATOR_EXTRA * md) and pico:
                    ext.append(a)
            if ext:
                add("extraordinario", anos=", ".join(ext))
                extra["anos_extraordinarios"] = ext
            if rob > 0 and d12 > FATOR_DY12M * rob:
                add("dy12m_atipico")
        else:
            l["status_robusto"] = l["status"]

        # (c) sem negociação: olha a situação ATUAL — liquidez recente muito baixa ou preço médio anual idêntico
        #     em anos seguidos dentro da janela recente (2 últimos anos completos + ano corrente).
        #     Preços parados em anos antigos (ex.: PINE3 2019–2022) não contam se o papel negocia hoje.
        recentes = [str(y) for y in range(ano_ref - 2, ano_ref + 1) if str(y) in pm]
        parados = [a for a, b in zip(recentes, recentes[1:]) if pm[a] == pm[b]]
        if vol < LIQ_SEM_NEGOCIO or parados:
            add("sem_negociacao")
        elif vol < LIQ_MIN:
            add("baixa_liquidez")
            if parados:
                extra["anos_preco_parado"] = sorted(set(parados + [str(int(a) + 1) for a in parados]))

        # desdobramento/bonificação: provento salta pelo mesmo fator do evento sem o preço acompanhar
        for s in (spl.split("|") if spl else []):
            dt, rz = s.split("@")
            num, den = map(float, rz.split(":"))
            k = num / den
            y = int(dt[:4])
            if 0.67 < k < 1.5 or str(y) not in anos:
                continue
            a, b = str(y - 1), str(y + 1)
            if dy.get(a, 0) > 0 and dy.get(b, 0) > 0 and pm.get(a) and pm.get(b):
                fd, fp = dy[b] / dy[a], pm[b] / pm[a]
                for alvo in (k, 1 / k):
                    if abs(fd / alvo - 1) < 0.2 and abs(fp / alvo - 1) > 0.5:
                        add("ajuste_suspeito", data=dt)

        # (f) consistência entre classes da mesma empresa
        outros = ([] if t.endswith(("11", "12")) else
                  [o for o in por_empresa.get(l["empresa"], [])
                   if o != t and len([a for a in anos if a in brutos[o][2]]) >= 3])
        div = []
        for o in outros:
            ro = brutos.get(o)
            if not ro:
                continue
            a1 = [dy.get(a, 0.0) for a in anos]
            a2 = [ro[3].get(a, 0.0) for a in anos]
            s1, s2 = sum(a1), sum(a2)
            if s1 == 0 and s2 == 0:
                continue
            razao = (s1 / s2) if s2 else 99
            ano_div = any(min(x, y) > 0 and max(x, y) / min(x, y) > DIVERG_ANO for x, y in zip(a1, a2))
            d12o = ro[4]
            d12_div = min(d12, d12o) > 0 and max(d12, d12o) / min(d12, d12o) > 2
            if not (DIVERG_CLASSES[0] <= razao <= DIVERG_CLASSES[1]) or ano_div or d12_div:
                div.append(o)
        if div:
            add("divergencia_classes", outros=", ".join(div))

        # margens absurdas (clássica OU robusta). Positiva implausível = grave (teto não se aplica);
        # negativa extrema = só atenção (ex.: BPAC11, banco líquido que paga pouco em relação ao preço).
        ms = [v for v in (l.get("margem"), l.get("margem_robusta")) if v is not None]
        if ms and max(ms) > MARGEM_MAX:
            add("margem_extrema", m=f"{max(ms):.1f}".replace(".", ","))
        elif ms and min(ms) < MARGEM_MIN:
            add("margem_negativa_extrema", m=_pct(min(ms)))
        # tendência (campo v1) — ignorada quando o último ano completo é um ano-lacuna (provável falha da fonte)
        if (l.get("tendencia") is not None and l["tendencia"] <= TENDENCIA_QUEDA and anos[-1] not in lac):
            add("tendencia_queda", t=f"{abs(l['tendencia']):.1f}".replace(".", ","))
        dm, d12p = l.get("dy_medio"), l.get("dy_12m")
        if dm and d12 > 0 and d12p is not None and d12p < FATOR_DY12M_BAIXO * dm:
            add("dy12m_baixo", d12=f"{d12p:.1f}".replace(".", ","), dm=f"{dm:.1f}".replace(".", ","))
        ult = anos[-1]
        if pm.get(ult) and preco < QUEDA_PRECO * pm[ult]:
            add("preco_desabou")
        if l.get("dpa_medio") and d12 == 0:
            add("sem_proventos_12m")

        l["alertas"] = alertas
        l["alertas_texto"] = textos
        l["nivel_alerta"] = ("grave" if GRAVES & set(alertas) else "atencao" if alertas else "ok")
        if l["nivel_alerta"] == "grave":
            nao_se_aplica(l)
        if extra:
            l["alertas_detalhe"] = extra
    return linhas


def contagens(linhas):
    ok = [l for l in linhas if l["status"] != "sem_cotacao"]
    niv = lambda n: [l for l in linhas if l.get("nivel_alerta") == n]
    return dict(
        papeis=len(linhas), com_cotacao=len(ok),
        abaixo_teto_v1=sum(1 for l in ok if l.get("status_calculado", l["status"]) == "abaixo_teto"),
        abaixo_teto_robusto_sem_grave=sum(1 for l in ok if l.get("status_robusto") == "abaixo_teto"),
        abaixo_teto_robusto_ok=sum(1 for l in ok if l.get("status_robusto") == "abaixo_teto"
                                   and l.get("nivel_alerta") == "ok"),
        nao_se_aplica=sum(1 for l in ok if l["status"] == "nao_se_aplica"),
        com_alertas=sum(1 for l in linhas if l.get("alertas")),
        grave=len(niv("grave")), grave_com_cotacao=sum(1 for l in niv("grave") if l["status"] != "sem_cotacao"),
        atencao=len(niv("atencao")), ok=len(niv("ok")),
    )


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
        arq = BRUTOS / "ultimo.json"
        if not arq.exists():
            arq = sorted(BRUTOS.glob("yahoo_*.json"))[-1]
        brutos = json.loads(arq.read_text())
    estatais = json.loads((BASE / "estatais.json").read_text()) if (BASE / "estatais.json").exists() else {}
    arq_sit = BASE / "situacoes_especiais.json"
    situacoes = json.loads(arq_sit.read_text()) if arq_sit.exists() else {}
    agora = datetime.now(timezone(timedelta(hours=-3)))
    datas = [r[1] for r in brutos.values() if r and r[1]]
    ref = max(datas) if datas else agora.strftime("%Y-%m-%d")
    linhas = calcular(univ, brutos, estatais, int(ref[:4]))
    linhas = qualidade(linhas, brutos, int(ref[:4]), situacoes)
    painel = dict(gerado_em=agora.strftime("%Y-%m-%d %H:%M"), pregao_referencia=ref,
                  metodo=dict(anos=ANOS, taxa_bazin=TAXA_BAZIN, liquidez_minima_mil=LIQ_MIN,
                              dpa_robusto=("média aparada (sem maior e menor ano) com 5 anos válidos; mediana com 3-4; "
                                           "sem o ano parcial de listagem e sem anos-lacuna"),
                              liquidez_sem_negociacao_mil=LIQ_SEM_NEGOCIO, fator_extraordinario=FATOR_EXTRA,
                              margem_plausivel=[MARGEM_MIN, MARGEM_MAX], tendencia_queda=TENDENCIA_QUEDA,
                              nivel_grave=sorted(GRAVES),
                              status_nao_se_aplica="papel com alerta grave: preço-teto não se aplica",
                              situacoes_especiais_versao=situacoes.get("atualizado")),
                  fonte_precos="Yahoo Finance (fechamento diário, ajustado por proventos em ações)",
                  papeis=linhas)
    (BASE / "painel.json").write_text(json.dumps(painel, ensure_ascii=False, separators=(",", ":")))
    c = contagens(linhas)
    print(f"{c['papeis']} papéis, {c['com_cotacao']} com cotação, {c['abaixo_teto_v1']} abaixo do teto (v1, antes "
          f"dos alertas), {c['abaixo_teto_robusto_sem_grave']} abaixo do teto robusto sem alerta grave "
          f"({c['abaixo_teto_robusto_ok']} sem nenhum alerta), {c['nao_se_aplica']} com teto não aplicável")
    print(f"alertas: {c['com_alertas']} papéis com alerta; nível grave {c['grave']} "
          f"({c['grave_com_cotacao']} com cotação), atenção {c['atencao']}, ok {c['ok']}")


if __name__ == "__main__":
    main()
