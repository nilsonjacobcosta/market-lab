"""Fase 2: mede os critérios de aceite definidos pelos juízes sobre a saída de fundamentos_cvm.py."""
import json, sys
from pathlib import Path

todos = json.loads(Path(sys.argv[1]).read_text())
painel = {p["ticker"]: p for p in json.loads(Path("dados/besst/painel.json").read_text())["papeis"]}
sem_cot = sorted(t for t in todos if painel.get(t, {}).get("preco") is None)
f = {t: v for t, v in todos.items() if t not in sem_cot}  # aceite medido só nos papéis negociados
falha = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 and Path(sys.argv[2]).exists() else None
raiz = lambda t: t[:4]
emis = {raiz(t) for t in f}
mapeados = {raiz(t) for t, v in f.items() if v.get("erro") != "sem CD_CVM"}
com_dado = {raiz(t) for t, v in f.items() if "erro" not in v}
recentes = {raiz(t) for t, v in f.items() if "erro" not in v and not any(x.startswith("dado_antigo") for x in v["flags"])}
nota = [t for t, v in f.items() if v.get("nota") is not None]
pag = [t for t, v in f.items() if "erro" not in v and (v.get("ll") or 0) > 0]
pay = [t for t in pag if f[t].get("payout") is not None]
alto_sem_flag = [t for t, v in f.items() if (v.get("payout") or 0) > 150 and not any("payout" in x for x in v.get("flags", []))]
ll0 = [t for t, v in f.items() if v.get("ll") == 0]
roe_pl_neg = [t for t, v in f.items() if v.get("roe") is not None and "patrimonio_negativo" in v.get("flags", [])]
nota_sem_ll = [t for t, v in f.items() if v.get("nota") is not None and v.get("ll") is None]
pct = lambda a, b: round(100 * len(a) / len(b), 1) if b else 0
r = {
    "papeis_no_universo": len(todos),
    "papeis_sem_cotacao_excluidos_do_aceite": sem_cot,
    "papeis_negociados": len(f),
    "emissores": len(emis),
    "emissores_mapeados_pct (meta >=95)": pct(mapeados, emis),
    "emissores_com_dado_ate_15m_pct (meta >=90)": pct(recentes, emis),
    "papeis_com_nota_pct (meta >=75)": pct(nota, f),
    "payout_calculado_nos_lucrativos_pct (meta >=90)": pct(pay, pag),
    "payout_acima_150_sem_flag (meta 0)": alto_sem_flag,
    "lucro_zero_aceito (meta 0)": ll0,
    "roe_com_pl_negativo (meta 0)": roe_pl_neg,
    "nota_com_lucro_ausente (meta 0)": nota_sem_ll,
    "nota_com_dado_antigo (meta 0)": [t for t, v in todos.items() if v.get("nota") is not None and any(x.startswith("dado_antigo") for x in v.get("flags", []))],
    "nota_com_metrica_descartada (meta 0)": [t for t, v in todos.items() if v.get("nota") is not None and v.get("descartados")],
    "nota_sem_cotacao (meta 0)": [t for t, v in todos.items() if v.get("nota") is not None and t in sem_cot],
    "papeis_com_excecao": [t for t, v in todos.items() if v.get("erro") == "excecao"],
    "universo_inteiro_com_nota_pct": round(100 * sum(1 for v in todos.values() if v.get("nota") is not None) / len(todos), 1),
    "flags_verificar": sorted({t: [x for x in v.get("flags", []) if x.startswith("verificar")] for t, v in f.items()
                               if any(x.startswith("verificar") for x in v.get("flags", []))}.items()),
    "sem_mapeamento": sorted({raiz(t): v.get("motivo") for t, v in f.items() if v.get("erro") == "sem CD_CVM"}.items()),
    "dado_antigo": sorted({raiz(t): [x for x in v["flags"] if x.startswith("dado_antigo")][0] for t, v in f.items()
                           if "erro" not in v and any(x.startswith("dado_antigo") for x in v["flags"])}.items()),
    "sem_dfp": sorted({raiz(t) for t, v in f.items() if v.get("erro") == "sem DFP"}),
    "execucao_com_download_forcado_a_falhar": (None if falha is None else
        f"concluiu: {sum(1 for v in falha.values() if 'erro' not in v)} papéis com dados"),
}
print(json.dumps(r, ensure_ascii=False, indent=1))
