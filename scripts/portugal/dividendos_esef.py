#!/usr/bin/env python3
"""Diagnóstico (não publica): dividendos declarados nos relatórios anuais ESEF.

Para cada papel, lê os relatórios de 2021 a 2025 no filings.xbrl.org e imprime as rubricas com 'dividend' ou 'distribu'
no nome (valor total e por ação, com o período e as dimensões), para fechar o cadastro de proventos pela fonte primária.
Papéis RAM e FLEXD entram como controlo (valores já conferidos nos comunicados).
Uso: python3 scripts/portugal/dividendos_esef.py [PAPEL ...]
"""
import importlib.util
import re
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("fe", RAIZ / "scripts/portugal/fundamentos_esef.py")
fe = importlib.util.module_from_spec(spec); spec.loader.exec_module(fe)

PAPEIS = {"GLINT": r"GLINTT", "ESON": r"ESTORIL.SOL", "RAM": r"RAMADA", "FLEXD": r"FLEXDEAL"}
RX = re.compile(r"dividend|distribu", re.I)


def main():
    pedidos = sys.argv[1:] or list(PAPEIS)
    base = fe.todos_relatorios_pt()
    for papel in pedidos:
        rx = re.compile(PAPEIS[papel])
        leis = [k for k, g in base.items() if rx.search(fe._norm(g["nome"]))]
        if len(leis) != 1:
            print(papel, "associação ambígua ou ausente:", [(k, base[k]["nome"]) for k in leis]); continue
        rel = base[leis[0]]["relatorios"]
        for ano in range(2021, 2026):
            cand = fe.escolher(rel, ano)
            if not cand:
                print(papel, ano, "sem relatório"); continue
            try:
                doc = fe.get_json(fe.FXO + cand[0]["json_url"])
            except Exception as e:
                print(papel, ano, "falha", e); continue
            vistos = set()
            for f in (doc.get("facts") or {}).values():
                d = f.get("dimensions") or {}
                conc = d.get("concept", "")
                if not RX.search(conc):
                    continue
                extra = {k: str(v).split(":")[-1][:40] for k, v in d.items() if k not in ("concept", "entity", "period", "unit", "language")}
                chave = (conc, d.get("period"), tuple(sorted(extra.items())), f.get("value"))
                if chave in vistos:
                    continue
                vistos.add(chave)
                print(f"DIV {papel} {ano} {conc} per={d.get('period', '')[:23]} {extra or ''} valor={str(f.get('value'))[:40]} un={d.get('unit', '')}")
            time.sleep(0.5)
    return 0


if __name__ == "__main__":
    sys.exit(main())
