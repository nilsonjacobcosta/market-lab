"""Testes unitários da fase 2 com amostras no formato real da CVM (contas e descrições como na DFP 2025)."""
import importlib.util, os, unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("f2", Path(__file__).resolve().parents[1] / "scripts/fase2/fundamentos_cvm.py")
f2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(f2)
n = f2.norm

DRE = {"3.11": (n("Lucro/Prejuízo Consolidado do Período"), 1000.0),
       "3.11.01": (n("Atribuído a Sócios da Empresa Controladora"), 900.0),
       "3.11.02": (n("Atribuído a Sócios Não Controladores"), 100.0)}
DFC = {"6.03.04": (n("Dividendos ou juros sobre o capital próprio pagos aos acionistas controladores"), -500.0),
       "6.03.05": (n("Dividendos ou juros sobre o capital próprio pagos aos acionistas não controladores"), -300.0)}
DVA = {"7.08.04": (n("Remuneração de Capitais Próprios"), 1000.0),
       "7.08.04.01": (n("Juros sobre o Capital Próprio"), 300.0),
       "7.08.04.02": (n("Dividendos"), 200.0),
       "7.08.04.03": (n("Lucros Retidos / Prejuízo do Período"), 400.0),
       "7.08.04.04": (n("Part. Não Controladores nos Lucros Retidos"), 100.0)}


class Testes(unittest.TestCase):
    def test_lucro_dos_controladores(self):
        self.assertEqual(f2.fluxo(DRE, DFC)["ll"], 900.0)

    def test_lucro_zero_vira_indisponivel(self):
        z = {"3.11": (n("Lucro/Prejuízo Consolidado do Período"), 0.0)}
        self.assertIsNone(f2.fluxo(z, {})["ll"])

    def test_proventos_sem_nao_controladores(self):
        f = f2.fluxo(DRE, DFC, DVA)
        self.assertEqual(f["prov_decl"], 500.0)   # JCP + dividendos, sem retidos e sem minoritários
        self.assertEqual(f["prov_caixa"], 500.0)  # só a linha dos controladores

    def test_ltm_sem_fallback_silencioso(self):
        out, faltou = f2.ltm({"ll": 100.0}, {"ll": None}, {"ll": 40.0}, chaves=("ll",))
        self.assertIsNone(out["ll"]); self.assertEqual(faltou, ["ll"])
        out, _ = f2.ltm({"ll": 100.0}, {"ll": 60.0}, {"ll": 40.0}, chaves=("ll",))
        self.assertEqual(out["ll"], 120.0)

    def test_dado_antigo_fica_sem_nota(self):
        _, nt = f2.nota("Energia", {"ll": 10, "roe": 20, "payout": 50, "div_liq_ebitda": 1}, ["dado_antigo:23_meses"])
        self.assertIsNone(nt)

    def test_metrica_descartada_nao_sobe_nota(self):
        _, nt = f2.nota("Energia", {"ll": 10, "roe": 20, "payout": 500, "div_liq_ebitda": 1, "descartados": ["payout"]}, [])
        self.assertIsNone(nt)

    def test_nota_e_travas(self):
        self.assertEqual(f2.nota("Energia", {"ll": 10, "roe": 20, "payout": 50, "div_liq_ebitda": 1}, [])[1], 3)
        self.assertEqual(f2.nota("Energia", {"ll": 10, "roe": 20, "payout": 50, "div_liq_ebitda": 9}, [])[1], 1)
        self.assertEqual(f2.nota("Energia", {"ll": -10, "roe": 20, "payout": 50, "div_liq_ebitda": 1}, [])[1], 0)
        self.assertIsNone(f2.nota("Energia", {"ll": None, "roe": 20, "payout": 50}, [])[1])

    def test_falha_de_download_nao_derruba(self):
        os.environ["FASE2_FORCAR_FALHA"] = "teste.zip"
        self.assertIsNone(f2.baixar("https://exemplo.invalido/teste.zip", Path("/tmp/cache_teste")))
        del os.environ["FASE2_FORCAR_FALHA"]


if __name__ == "__main__":
    unittest.main()
