#!/usr/bin/env python3
"""Estudo (não publica): histórico de contas das cotadas portuguesas FORA do núcleo do Monitor Portugal.

Para cada candidata, lê os relatórios anuais ESEF de 2021 a 2025 (e os comparativos de 2020) e calcula por ano:
lucro atribuível, receita, ROE, ROIC aproximado e dívida líquida/EBITDA. Saída: linhas JSON no log + resumo.

ROIC aproximado = resultado operacional × (1 − taxa efetiva de imposto, limitada a 0–40%, 25% por omissão)
                  ÷ (capital próprio total + empréstimos + locações − caixa), no fim do ano.
Uso: python3 scripts/portugal/estudo_observacao.py
"""
import importlib.util
import json
import re
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("fe", RAIZ / "scripts/portugal/fundamentos_esef.py")
fe = importlib.util.module_from_spec(spec); spec.loader.exec_module(fe)

CANDIDATAS = {  # papel: (nome, padrão do nome no filings.xbrl.org)
    "RAM": ("Ramada Investimentos e Indústria", r"RAMADA"),
    "NBA": ("Novabase", r"NOVABASE"),
    "GLINT": ("Glintt", r"GLINTT"),
    "MAR": ("Martifer", r"MARTIFER"),
    "SNC": ("Sonaecom", r"SONAECOM"),
    "SCT": ("Toyota Caetano Portugal", r"TOYOTA CAETANO"),
    "ESON": ("Estoril Sol", r"ESTORIL.SOL"),
    "FLEXD": ("Flexdeal SIMFE", r"FLEXDEAL"),
    "MCP": ("Grupo Media Capital", r"MEDIA CAPITAL"),
    "IPR": ("Impresa", r"^IMPRESA"),
    "PHR": ("Pharol", r"PHAROL"),
}


def ano_dados(idx, ano):
    d = fe.extrair(idx, ano)
    dur, fim, _ = fe.periodos(ano)
    d["receita"] = fe.pega(idx, ["Revenue", "RevenueFromContractsWithCustomers"], dur)[0]
    d["pl_total"] = fe.pega(idx, ["Equity"], fim)[0]
    op = d["op"]
    if op is None and d["lai"] is not None and d["fin_liq"] is not None:
        op = d["lai"] - d["fin_liq"]
    elif op is None and d["lai"] is not None and d["desp_fin"] is not None:
        op = d["lai"] + abs(d["desp_fin"]) - abs(d["rec_fin"] or 0)
    d["op_usado"] = op
    m = {"ano": ano, "lucro": d["ll"], "lucro_total": d["ll_total"], "receita": d["receita"]}
    if d["ll"] is not None and d["pl"]:
        base = (d["pl"] + d["pl_ini"]) / 2 if d["pl_ini"] else d["pl"]
        m["roe"] = round(100 * d["ll"] / base, 1) if base > 0 else None
    dl = None
    if d["emprestimos"] is not None and d["caixa"] is not None:
        dl = d["emprestimos"] + (d["locacoes"] or 0) - d["caixa"]
    elif d["caixa"] is not None and d["emprestimos"] is None:
        dl = -d["caixa"] + (d["locacoes"] or 0)
        m["nota_divida"] = "empréstimos não identificados (pode não ter dívida bancária)"
    m["divida_liquida"] = dl
    ebitda = op + abs(d["da"]) if op is not None and d["da"] is not None else None
    if ebitda and ebitda > 0 and dl is not None:
        m["dl_ebitda"] = round(dl / ebitda, 2)
    if op is not None and d["pl_total"] is not None and dl is not None:
        t = 0.25
        if d["lai"] and d["lai"] > 0 and d["ir"] is not None and 0 <= d["ir"] / d["lai"] <= 0.4:
            t = d["ir"] / d["lai"]
        ic = d["pl_total"] + dl
        if ic > 0:
            m["roic"] = round(100 * op * (1 - t) / ic, 1)
    return m


def main():
    base = fe.todos_relatorios_pt()
    print("Entidades PT:", len(base))
    resumo = {}
    for papel, (nome, padrao) in CANDIDATAS.items():
        rx = re.compile(padrao)
        leis = [k for k, g in base.items() if rx.search(fe._norm(g["nome"]))]
        if len(leis) != 1:
            print(papel, "associação ambígua ou ausente:", [(k, base[k]["nome"]) for k in leis]); continue
        lei = leis[0]
        rel = base[lei]["relatorios"]
        anos = {}
        for ano in range(2021, 2026):
            cand = fe.escolher(rel, ano)
            if not cand:
                continue
            try:
                idx = fe.indexar(fe.get_json(fe.FXO + cand[0]["json_url"]))
            except Exception as e:
                print(papel, ano, "falha", e); continue
            anos[ano] = ano_dados(idx, ano)
            if ano == 2021:
                anos[2020] = ano_dados(idx, 2020)
            time.sleep(0.5)
        serie = [anos[a] for a in sorted(anos)]
        resumo[papel] = {"nome": nome, "lei": lei, "entidade": base[lei]["nome"], "anos": serie}
        print("JSON", json.dumps({"papel": papel, **resumo[papel]}, ensure_ascii=False))
    print("\n=== RESUMO ===")
    for p, r in resumo.items():
        luc = [a.get("lucro") for a in r["anos"]]
        pos = sum(1 for v in luc if v is not None and v > 0)
        print(f"{p:6} anos={len(luc)} lucro>0={pos} lucros(M€)={[round(v/1e6,1) if v is not None else None for v in luc]} "
              f"ROE={[a.get('roe') for a in r['anos']]} ROIC={[a.get('roic') for a in r['anos']]} DL/EBITDA={[a.get('dl_ebitda') for a in r['anos']]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
