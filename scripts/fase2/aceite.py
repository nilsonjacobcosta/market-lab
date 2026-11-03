"""Fase 2: mede os critérios de aceite definidos pelos juízes sobre a saída de fundamentos_cvm.py."""
import json, sys
from pathlib import Path

f = json.loads(Path(sys.argv[1]).read_text())
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
    "emissores": len(emis),
    "emissores_mapeados_pct (meta >=95)": pct(mapeados, emis),
    "emissores_com_dado_ate_15m_pct (meta >=90)": pct(recentes, emis),
    "papeis_com_nota_pct (meta >=75)": pct(nota, f),
    "payout_calculado_nos_lucrativos_pct (meta >=90)": pct(pay, pag),
    "payout_acima_150_sem_flag (meta 0)": alto_sem_flag,
    "lucro_zero_aceito (meta 0)": ll0,
    "roe_com_pl_negativo (meta 0)": roe_pl_neg,
    "nota_com_lucro_ausente (meta 0)": nota_sem_ll,
    "sem_mapeamento": sorted({raiz(t): v.get("motivo") for t, v in f.items() if v.get("erro") == "sem CD_CVM"}.items()),
    "sem_dfp": sorted({raiz(t) for t, v in f.items() if v.get("erro") == "sem DFP"}),
    "execucao_com_download_forcado_a_falhar": (None if falha is None else
        f"concluiu: {sum(1 for v in falha.values() if 'erro' not in v)} papéis com dados"),
}
print(json.dumps(r, ensure_ascii=False, indent=1))
