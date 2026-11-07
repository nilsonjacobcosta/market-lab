#!/usr/bin/env python3
"""Séries anuais 2020–2025 (lucro, ROE, ROIC aproximado, dívida líquida/EBITDA) dos 30 emitentes, a partir dos
relatórios ESEF. Saída: dados/portugal/perfil_series.json. O quadro de perfil é montado em painel_pt.py.
ROIC aproximado = resultado operacional × (1 − taxa efetiva) ÷ (capital próprio total + dívida líquida); ver estudo_observacao.py.
Bancos e seguradoras: sem ROIC (não se aplica). Uso: python3 scripts/portugal/perfil_esef.py [--saida ficheiro]"""
import argparse, csv, importlib.util, json, sys, time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "dados/portugal"


def _carregar(nome):
    s = importlib.util.spec_from_file_location(nome, RAIZ / f"scripts/portugal/{nome}.py")
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


fe = _carregar("fundamentos_esef")
eo = _carregar("estudo_observacao")  # reutiliza ano_dados (usa o módulo fe próprio, equivalente)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default=str(DADOS / "perfil_series.json"))
    a = ap.parse_args()
    universo = json.loads((DADOS / "universo.json").read_text(encoding="utf-8"))
    mapa = {}
    if (DADOS / "mapa_lei.csv").exists():
        with open(DADOS / "mapa_lei.csv", encoding="utf-8") as f:
            mapa = {r["papel"]: r for r in csv.DictReader(f)}
    base = fe.todos_relatorios_pt()
    out = {"gerado_em": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"), "papeis": {}}
    for p in universo["papeis"]:
        t = p["papel"]
        lei = fe.casar(t, base, mapa)
        if not lei:
            out["papeis"][t] = {"erro": "sem relatório ESEF", "anos": []}; print(t, "sem LEI"); continue
        rel = base[lei]["relatorios"]
        anos = {}
        for ano in range(2021, 2026):
            for cand in fe.escolher(rel, ano):
                if not cand.get("json_url"):
                    continue
                try:
                    idx = fe.indexar(fe.get_json(fe.FXO + cand["json_url"]))
                    anos[ano] = eo.ano_dados(idx, ano)
                    if ano == 2021:
                        anos[2020] = eo.ano_dados(idx, 2020)
                    break
                except Exception as e:
                    print(t, ano, "falha", str(e)[:100])
            time.sleep(0.4)
        serie = [{k: v for k, v in anos[y].items() if k in ("ano", "lucro", "receita", "roe", "roic", "dl_ebitda", "divida_liquida")}
                 for y in sorted(anos)]
        out["papeis"][t] = {"lei": lei, "setor": p.get("setor"), "anos": serie}
        print(t, [(s["ano"], s.get("lucro") and round(s["lucro"] / 1e6, 1), s.get("roic")) for s in serie])
    Path(a.saida).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
