#!/usr/bin/env python3
"""Aceite da qualidade financeira (J1). Publica o ficheiro novo só se todas as metas passarem.

Uso: python3 scripts/portugal/aceite_fundamentos.py NOVO.json DESTINO.json
"""
import json
import sys

# Lucro atribuível do exercício de 2025 divulgado pelas empresas (milhões de euros) e onde foi conferido.
LUCRO_REFERENCIA_2025 = {
    "BCP": (1018.6, "Millennium bcp, resultados de 2025 (Forbes Portugal, 2026)"),
    "GALP": (1120.0, "Galp, resultados de 2025 (Forbes España, 2026)"),
    "JMT": (646.0, "Jerónimo Martins, resultados de 2025 (ECO, 18/03/2026)"),
    "EDP": (1150.0, "EDP, resultados de 2025 (Observador e RTP, 25/02/2026)"),
    "NOS": (245.9, "NOS, resultados de 2025 (RTP e Dinheiro Vivo, 03/2026)"),
    "EDPR": (216.0, "EDP Renováveis, resultados de 2025 (Renascença, 25/02/2026)"),
}
METAS = {"com_relatorio_pct (meta >=90)": 90, "lucro_encontrado_pct (meta >=90)": 90, "com_nota_pct (meta >=75)": 75}


def main(novo, destino):
    d = json.loads(open(novo, encoding="utf-8").read())
    falhas, conf = [], {}
    for k, meta in METAS.items():
        if d["aceite"].get(k, 0) < meta:
            falhas.append(f"{k} = {d['aceite'].get(k)}")
    ok_lucro = 0
    for p, (ref, fonte, *campo) in LUCRO_REFERENCIA_2025.items():
        v = d["papeis"].get(p, {})
        val = v.get("ll") if not campo else (v.get("componentes") or {}).get(campo[0])
        if v.get("exercicio") != 2025 or val is None:
            conf[p] = "sem dado de 2025"; continue
        dif = abs(val / 1e6 - ref) / ref * 100
        conf[p] = f"{val / 1e6:.1f} vs {ref} M€ ({dif:.2f}%) — {fonte}"
        ok_lucro += dif <= 2
    if ok_lucro < len(LUCRO_REFERENCIA_2025):
        falhas.append(f"lucro conferido: {ok_lucro}/{len(LUCRO_REFERENCIA_2025)} dentro de 2%")
    d["aceite"]["conferencia_lucro_2025"] = conf
    print(json.dumps(d["aceite"], ensure_ascii=False, indent=1))
    if falhas:
        print("ACEITE REPROVADO — nada publicado:", "; ".join(falhas))
        return 1
    open(destino, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print("ACEITE APROVADO — publicado em", destino)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
