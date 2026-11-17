"""Aceite do mercados.json: trava da publicação do painel Mercados e ciclos.

Uso: python3 scripts/mercados/aceite.py caminho/mercados.json [--anterior caminho] [--amostra]
Código de saída 0 = aprovado; 1 = reprovado (o workflow não publica).

Critérios:
- estrutura do contrato (campos de topo e de cada série; todas as séries do catálogo presentes);
- série "ok": mínimo de pontos, último dado dentro de defasagem_max_dias do catálogo;
- toda série com pontos: datas estritamente crescentes, nenhuma data futura, valores numéricos
  dentro da faixa plausível da unidade (ou da "faixa" própria no catálogo);
- pelo menos 60% das séries com status "ok" ou "anterior";
- com --anterior: reprova se alguma série "ok" encolher mais de 5% em número de pontos.
--amostra ignora a defasagem (arquivo sintético de teste) e exige "amostra_sintetica": true;
sem --amostra, um arquivo marcado como sintético é reprovado (não pode ser publicado).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CATALOGO = os.path.join(AQUI, "catalogo_series.json")
MIN_PONTOS = 24
MIN_PROPORCAO = 0.60
MAX_ENCOLHIMENTO = 0.05
STATUS = ("ok", "anterior", "sem dados")
CAMPOS_TOPO = ("gerado_utc", "gerado_brt", "series_ok", "series_total", "series")
CAMPOS_SERIE = ("nome", "fonte", "url_fonte", "codigo", "periodicidade", "unidade", "ajuste_sazonal",
                "ultimo_dado", "coletado_utc", "status", "pontos")
# Faixas plausíveis por unidade: (mínimo, máximo), limites incluídos.
FAIXAS = {
    "% a.a.": (-5, 60),
    "% em 12 meses": (-5, 60),
    "pontos percentuais": (-30, 40),
}
FAIXA_POSITIVA = (1e-9, 1e13)  # preços, índices, câmbio e agregados: sempre positivos


def faixa_da_serie(item: dict) -> tuple[float, float]:
    if item.get("faixa"):
        return tuple(item["faixa"])
    return FAIXAS.get(item["unidade"], FAIXA_POSITIVA)


def validar(dados: dict, catalogo: list[dict], hoje: dt.date, anterior: dict | None = None,
            amostra: bool = False) -> list[str]:
    """Devolve a lista de motivos de reprovação (vazia = aprovado)."""
    erros = []
    for c in CAMPOS_TOPO:
        if c not in dados:
            erros.append(f"campo de topo ausente: {c}")
    if erros:
        return erros
    if amostra and dados.get("amostra_sintetica") is not True:
        erros.append("--amostra exige o campo amostra_sintetica: true")
    if not amostra and dados.get("amostra_sintetica"):
        erros.append("arquivo sintético não pode passar no aceite de publicação (use --amostra só em teste)")
    series = dados["series"]
    hoje_iso = hoje.isoformat()
    for item in catalogo:
        sid = item["id"]
        b = series.get(sid)
        if b is None:
            erros.append(f"{sid}: série do catálogo ausente")
            continue
        faltam = [c for c in CAMPOS_SERIE if c not in b]
        if faltam:
            erros.append(f"{sid}: campos ausentes {faltam}")
            continue
        if b["status"] not in STATUS:
            erros.append(f"{sid}: status inválido {b['status']!r}")
            continue
        pontos = b["pontos"]
        if b["status"] == "sem dados":
            if pontos:
                erros.append(f"{sid}: 'sem dados' com pontos")
            continue
        if not pontos:
            erros.append(f"{sid}: status {b['status']} sem pontos")
            continue
        minimo, maximo = faixa_da_serie(item)
        ant = None
        for p in pontos:
            if not (isinstance(p, list) and len(p) == 2 and isinstance(p[0], str)
                    and isinstance(p[1], (int, float)) and not isinstance(p[1], bool) and math.isfinite(p[1])):
                erros.append(f"{sid}: ponto malformado {p!r}")
                break
            try:
                dt.date.fromisoformat(p[0])
            except ValueError:
                erros.append(f"{sid}: data inválida {p[0]!r}")
                break
            if ant is not None and p[0] <= ant:
                erros.append(f"{sid}: datas fora de ordem ou repetidas em {p[0]}")
                break
            if p[0] > hoje_iso:
                erros.append(f"{sid}: data futura {p[0]}")
                break
            if not minimo <= p[1] <= maximo:
                erros.append(f"{sid}: valor {p[1]} em {p[0]} fora da faixa [{minimo}, {maximo}] ({item['unidade']})")
                break
            ant = p[0]
        else:
            if b["ultimo_dado"] != pontos[-1][0]:
                erros.append(f"{sid}: ultimo_dado {b['ultimo_dado']} difere do último ponto {pontos[-1][0]}")
        if b["status"] != "ok":
            continue
        if len(pontos) < item.get("min_pontos", MIN_PONTOS):
            erros.append(f"{sid}: {len(pontos)} pontos, mínimo {item.get('min_pontos', MIN_PONTOS)}")
        if not amostra:
            try:
                atraso = (hoje - dt.date.fromisoformat(pontos[-1][0])).days
            except ValueError:
                atraso = None
            if atraso is not None and atraso > item["defasagem_max_dias"]:
                erros.append(f"{sid}: último dado há {atraso} dias, máximo {item['defasagem_max_dias']}")
        velho = ((anterior or {}).get("series") or {}).get(sid)
        if velho and velho.get("pontos"):
            n_velho = len(velho["pontos"])
            if len(pontos) < n_velho * (1 - MAX_ENCOLHIMENTO):
                erros.append(f"{sid}: encolheu de {n_velho} para {len(pontos)} pontos (mais de 5%)")
    extras = sorted(set(series) - {i["id"] for i in catalogo})
    if extras:
        erros.append(f"séries fora do catálogo: {extras}")
    validas = sum(1 for b in series.values() if b.get("status") in ("ok", "anterior"))
    if len(catalogo) and validas / len(catalogo) < MIN_PROPORCAO:
        erros.append(f"só {validas}/{len(catalogo)} séries com status ok ou anterior (mínimo 60%)")
    n_ok = sum(1 for b in series.values() if b.get("status") == "ok")
    if dados["series_ok"] != n_ok or dados["series_total"] != len(series):
        erros.append("series_ok/series_total não batem com o conteúdo")
    return erros


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Aceite do mercados.json")
    ap.add_argument("arquivo")
    ap.add_argument("--anterior", help="arquivo publicado antes; reprova se alguma série ok encolher mais de 5%%")
    ap.add_argument("--amostra", action="store_true", help="arquivo sintético: ignora a defasagem")
    args = ap.parse_args(argv)
    try:
        with open(args.arquivo, encoding="utf-8") as f:
            dados = json.load(f)
    except (OSError, ValueError) as e:
        print(f"REPROVADO: não foi possível ler {args.arquivo}: {e}")
        return 1
    anterior = None
    if args.anterior and os.path.exists(args.anterior):
        try:
            with open(args.anterior, encoding="utf-8") as f:
                anterior = json.load(f)
        except ValueError:
            print(f"[aviso] arquivo anterior ilegível, comparação ignorada: {args.anterior}")
    with open(CATALOGO, encoding="utf-8") as f:
        catalogo = json.load(f)["series"]
    hoje = dt.datetime.now(dt.timezone.utc).date()
    if args.amostra and isinstance(dados, dict) and dados.get("gerado_utc"):
        hoje = max(hoje, dt.datetime.fromisoformat(dados["gerado_utc"]).date())
    erros = validar(dados, catalogo, hoje, anterior, args.amostra) if isinstance(dados, dict) else ["raiz não é objeto"]
    cont = {}
    for b in (dados.get("series") or {}).values() if isinstance(dados, dict) else []:
        cont[b.get("status")] = cont.get(b.get("status"), 0) + 1
    print(f"séries por status: {cont}")
    for b_id, b in ((dados.get("series") or {}).items() if isinstance(dados, dict) else []):
        if b.get("status") == "anterior":
            desde = b.get("anterior_desde")
            dias = (dt.date.today() - dt.date.fromisoformat(desde)).days if desde else None
            extra = f"; há {dias} dia(s) sem coleta nova" + (" (ver runbook RB 10)" if dias >= 3 else "") if dias is not None else ""
            print(f"[aviso] {b_id}: mantido da coleta anterior (último dado {b.get('ultimo_dado')}{extra})")
    if erros:
        print(f"REPROVADO: {len(erros)} problema(s)")
        for e in erros:
            print(" -", e)
        return 1
    print("APROVADO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
