"""Publica dados/besst/fundamentos.json (fase 2, BETA) só se o aceite estiver limpo.

Regras de bloqueio (ressalva 9 dos juízes): qualquer contador "(meta 0)" diferente de vazio, ou metas mínimas não
atingidas, ou papel com exceção => não publica (sai com código 1 e o arquivo público fica como estava).
"""
import json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

fund = json.loads(Path(sys.argv[1]).read_text())
ace = json.loads(Path(sys.argv[2]).read_text())
destino = Path(sys.argv[3])
falhas = [k for k, v in ace.items() if "(meta 0)" in k and v]
for k, minimo in (("emissores_mapeados_pct (meta >=95)", 95), ("emissores_com_dado_ate_15m_pct (meta >=90)", 90),
                  ("papeis_com_nota_pct (meta >=75)", 75), ("payout_calculado_nos_lucrativos_pct (meta >=90)", 90)):
    if ace.get(k, 0) < minimo:
        falhas.append(f"{k} = {ace.get(k)}")
if ace.get("papeis_com_excecao"):
    falhas.append("papeis_com_excecao")
if falhas:
    print("NÃO PUBLICADO. Falhas no aceite:", falhas)
    sys.exit(1)
CAMPOS = ("ll", "roe", "roe_medio_exercicios", "roe_medio_n", "payout", "payout_caixa", "base_payout", "div_liq_ebitda",
          "div_liq_pl", "semaforo", "nota", "nota_provisoria", "motivo_sem_nota", "padrao", "referencia", "base",
          "componentes_lucro", "flags", "erro", "motivo")
papeis = {t: {k: v[k] for k in CAMPOS if k in v} for t, v in fund.items()}
refs = sorted({v["referencia"] for v in fund.values() if v.get("referencia")})
agora = datetime.now(timezone(timedelta(hours=-3))).strftime("%Y-%m-%d %H:%M")
saida = {"beta": True, "gerado_em": agora, "fonte": "CVM — Portal de Dados Abertos (DFP, ITR, FCA)",
         "data_base_mais_recente": refs[-1] if refs else None,
         "aviso": "Material educativo, não é recomendação de investimento (Res. CVM 20/2021). Faixas são convenções do painel.",
         "aceite": {k: v for k, v in ace.items() if "pct" in k}, "papeis": papeis}
destino.write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")))
print("Publicado:", destino, len(papeis), "papéis")
