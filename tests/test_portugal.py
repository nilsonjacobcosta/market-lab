"""Testes e critérios de aceite do Monitor Portugal (J1 dados, J2 comunicação, J3 engenharia).

Rodam no workflow ANTES de qualquer publicação; se falharem, nada é publicado.
"""
import csv
import importlib.util
import json
import re
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pt", RAIZ / "scripts/portugal/painel_pt.py")
pt = importlib.util.module_from_spec(spec); spec.loader.exec_module(pt)

UNIVERSO = json.loads((RAIZ / "dados/portugal/universo.json").read_text(encoding="utf-8"))
PARAMS = json.loads((RAIZ / "dados/portugal/parametros.json").read_text(encoding="utf-8"))
EVENTOS = pt.ler_proventos()
PROIBIDAS = re.compile(r"\b(compre|venda já|recomendamos|recomenda-se a compra|recomendação de compra|oportunidade imperdível|top pick)\b", re.I)


def soma(papel, ano):
    return round(sum(e["valor_bruto"] for e in EVENTOS if e["papel"] == papel and e["data_pagamento"][:4] == str(ano)), 6)


class J1Cadastro(unittest.TestCase):
    def test_linhas_validas(self):
        papeis = {p["papel"] for p in UNIVERSO["papeis"]}
        for e in EVENTOS:
            with self.subTest(e=e["papel"] + e["data_pagamento"]):
                self.assertIn(e["papel"], papeis)
                datetime.strptime(e["data_pagamento"], "%Y-%m-%d")
                self.assertGreater(e["valor_bruto"], 0)
                self.assertIn(e["tipo"], {"dinheiro", "scrip", "especie"})
                self.assertIn(e["estado"], {"oficial", "coincide", "a_conferir"})
                if e["estado"] == "oficial":
                    self.assertTrue(e["fonte_url"].startswith("https://"), "linha oficial sem link")

    def test_sem_duplicados(self):
        chaves = [(e["papel"], e["data_pagamento"], e["valor_bruto"]) for e in EVENTOS]
        self.assertEqual(len(chaves), len(set(chaves)))

    def test_valores_conferidos_em_fontes_oficiais(self):
        # Somas por ano de pagamento conferidas na fase 0 (docs/monitor-portugal/).
        casos = {("GALP", 2022): 0.51, ("GALP", 2024): 0.55, ("BCP", 2025): 0.03, ("BCP", 2023): 0.0,
                 ("RENE", 2022): 0.218, ("RENE", 2025): 0.157, ("COR", 2024): 0.29, ("NVG", 2025): 0.24606,
                 ("EDPR", 2023): 0.265, ("CTT", 2022): 0.12, ("JMT", 2025): 0.59, ("EDP", 2025): 0.20,
                 ("NOS", 2023): 0.43, ("SEM", 2022): 1.764, ("IBS", 2023): 0.70, ("EGL", 2025): 0.1497}
        for (p, a), v in casos.items():
            with self.subTest(p=p, a=a):
                self.assertAlmostEqual(soma(p, a), v, places=5)

    def test_cobertura_oficial_minima(self):
        janela = [e for e in EVENTOS if "2021" <= e["data_pagamento"][:4] <= "2025"]
        pct = sum(1 for e in janela if e["estado"] in ("oficial", "coincide")) / len(janela)
        self.assertGreaterEqual(pct, 0.90, f"só {pct:.0%} dos eventos 2021–2025 conferidos")


class J3Calendario(unittest.TestCase):
    def test_pascoa(self):
        self.assertEqual(pt._pascoa(2025), date(2025, 4, 20))
        self.assertEqual(pt._pascoa(2026), date(2026, 4, 5))
        self.assertEqual(pt._pascoa(2027), date(2027, 3, 28))

    def test_feriados(self):
        f = pt.feriados_euronext(2026)
        self.assertIn(date(2026, 4, 3), f)   # Sexta-feira Santa
        self.assertIn(date(2026, 4, 6), f)   # Segunda-feira de Páscoa
        self.assertIn(date(2026, 12, 26), f)

    def test_fecho_esperado(self):
        # Quarta 04/11/2026 10:00 UTC (inverno, Lisboa = UTC): fecho esperado é o de terça.
        self.assertEqual(pt.ultimo_fecho_esperado(datetime(2026, 11, 4, 10, 0, tzinfo=timezone.utc)), date(2026, 11, 3))
        # Mesma quarta às 19:00 UTC: já espera o fecho do dia.
        self.assertEqual(pt.ultimo_fecho_esperado(datetime(2026, 11, 4, 19, 0, tzinfo=timezone.utc)), date(2026, 11, 4))
        # Segunda de Páscoa 2026 às 20:00 UTC: último fecho foi quinta 02/04.
        self.assertEqual(pt.ultimo_fecho_esperado(datetime(2026, 4, 6, 20, 0, tzinfo=timezone.utc)), date(2026, 4, 2))


class Calculo(unittest.TestCase):
    def _brutos(self, preco=5.0):
        hoje = datetime(2026, 11, 4, 19, tzinfo=timezone.utc)
        serie = [[(hoje.date() - timedelta(days=i)).isoformat(), preco, 100000] for i in range(370, -1, -1)]
        return hoje, {"precos": {p["papel"]: {"serie": serie, "precos_mes": {}, "divs_fonte": []} for p in UNIVERSO["papeis"]},
                      "taxa_bce": {"obs": [["2026-%02d" % m, 3.0] for m in range(1, 13)], "lida_em": "2026-11-04"}}

    def test_teto_e_status(self):
        agora, brutos = self._brutos(preco=5.0)
        r = pt.calcular(UNIVERSO, PARAMS, EVENTOS, brutos, agora)
        self.assertEqual(r["anos"], ["2021", "2022", "2023", "2024", "2025"])
        self.assertAlmostEqual(r["taxa"]["taxa_exigida_pct"], 6.0)
        edp = next(l for l in r["linhas"] if l["papel"] == "EDP")
        self.assertAlmostEqual(edp["dpa_medio"], (0.19 + 0.19 + 0.19 + 0.195 + 0.20) / 5, places=6)
        self.assertAlmostEqual(edp["teto"], round(edp["dpa_medio"] / 0.06, 4))
        self.assertEqual(edp["status"], "acima")  # 3,22 € de teto < 5 € de preço
        tdsa = next(l for l in r["linhas"] if l["papel"] == "TDSA")
        self.assertEqual(tdsa["status"], "sem_proventos")
        self.assertIsNone(tdsa["teto"])

    def test_taxa_minima(self):
        agora, brutos = self._brutos()
        brutos["taxa_bce"]["obs"] = [["2026-%02d" % m, 1.0] for m in range(1, 13)]
        r = pt.calcular(UNIVERSO, PARAMS, EVENTOS, brutos, agora)
        self.assertAlmostEqual(r["taxa"]["taxa_exigida_pct"], PARAMS["taxa_minima_pct"])

    def test_evento_nao_cadastrado_gera_alerta(self):
        agora, brutos = self._brutos()
        brutos["precos"]["TDSA"]["divs_fonte"] = [["2024-05-10", 0.05]]
        r = pt.calcular(UNIVERSO, PARAMS, EVENTOS, brutos, agora)
        tdsa = next(l for l in r["linhas"] if l["papel"] == "TDSA")
        self.assertIn("evento_nao_cadastrado", [a["codigo"] for a in tdsa["alertas"]])

    def test_falta_de_preco_nao_derruba(self):
        agora, brutos = self._brutos()
        del brutos["precos"]["BCP"]
        r = pt.calcular(UNIVERSO, PARAMS, EVENTOS, brutos, agora)
        self.assertEqual(next(l for l in r["linhas"] if l["papel"] == "BCP")["status"], "sem_preco")


class J2Pagina(unittest.TestCase):
    def test_pagina_tem_avisos_e_nao_tem_linguagem_de_compra(self):
        html = (RAIZ / "portugal/monitor/index.html").read_text(encoding="utf-8")
        self.assertIn("não é recomendação de investimento", html)
        for termo in ("Metodologia", "Fontes", "Riscos", "Autor", "Histórico de mudanças"):
            self.assertIn(termo, html)
        self.assertIsNone(PROIBIDAS.search(html))


class Aceite(unittest.TestCase):
    """Só roda se o painel.json existir (no workflow, depois da coleta)."""
    def setUp(self):
        arq = RAIZ / "dados/portugal/painel.json"
        if not arq.exists():
            self.skipTest("painel.json ainda não gerado")
        self.p = json.loads(arq.read_text(encoding="utf-8"))

    def test_estrutura(self):
        self.assertIn("não é recomendação de investimento", self.p["aviso"])
        self.assertEqual(len(self.p["linhas"]), len(UNIVERSO["papeis"]))
        self.assertGreaterEqual(self.p["taxa"]["taxa_exigida_pct"], PARAMS["taxa_minima_pct"])

    def test_cobertura_de_precos(self):
        com = sum(1 for l in self.p["linhas"] if l["preco"])
        self.assertGreaterEqual(com, len(self.p["linhas"]) - 1, "mais de um papel sem preço")

    def test_coerencia(self):
        for l in self.p["linhas"]:
            with self.subTest(p=l["papel"]):
                if l["status"].startswith("abaixo"):
                    self.assertTrue(l["teto"] and l["preco"] and l["preco"] <= l["teto"])
                if l["status"] == "acima":
                    self.assertTrue(l["preco"] > l["teto"])
                if l["preco"]:
                    self.assertGreater(l["preco"], 0)


if __name__ == "__main__":
    unittest.main()
