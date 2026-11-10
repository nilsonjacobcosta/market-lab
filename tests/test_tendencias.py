import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "tendencias"))
import metricas as m  # noqa: E402


class RetornoTests(unittest.TestCase):
    def test_retorno_simples(self):
        self.assertAlmostEqual(m.retorno([100, 110, 121], 2), 0.21)

    def test_historico_insuficiente(self):
        self.assertIsNone(m.retorno([100, 110], 5))

    def test_relativo_mesmo_retorno_da_zero(self):
        self.assertAlmostEqual(m.retorno_relativo(0.10, 0.10), 0.0)

    def test_relativo_com_ref_negativa(self):
        # ETF cai 5%, mercado cai 10%: ETF rendeu mais que o mercado
        self.assertGreater(m.retorno_relativo(-0.05, -0.10), 0)

    def test_relativo_com_none(self):
        self.assertIsNone(m.retorno_relativo(None, 0.1))


class MediaETendenciaTests(unittest.TestCase):
    def test_media_movel(self):
        self.assertAlmostEqual(m.media_movel([1, 2, 3, 4], 2), 3.5)

    def test_acima_media_200_sem_historico(self):
        self.assertIsNone(m.acima_media([1.0] * 50, 200))

    def test_acima_media_true(self):
        serie = [10.0] * 199 + [20.0]
        self.assertTrue(m.acima_media(serie, 200))


class RiscoTests(unittest.TestCase):
    def test_volatilidade_serie_constante_e_zero(self):
        self.assertAlmostEqual(m.volatilidade_anual([100.0] * 300), 0.0)

    def test_volatilidade_positiva(self):
        serie = [100 * (1.01 if i % 2 else 0.99) ** i for i in range(300)]
        self.assertGreater(m.volatilidade_anual(serie), 0)

    def test_queda_maxima(self):
        self.assertAlmostEqual(m.queda_maxima([100, 150, 75, 120]), -0.5)

    def test_queda_maxima_sem_queda(self):
        self.assertEqual(m.queda_maxima([100, 110, 120]), 0.0)


class CelulaTests(unittest.TestCase):
    def test_chaves_completas(self):
        serie = [100 + i * 0.1 for i in range(300)]
        out = m.calcular_celula(serie, serie)
        for nome in m.JANELAS:
            self.assertIn(f"retorno_{nome}", out)
            self.assertIn(f"relativo_{nome}", out)
        # mesma série que a referência: relativo deve ser 0 onde existe
        self.assertAlmostEqual(out["relativo_12m"], 0.0)
        self.assertTrue(out["acima_mm200"])


if __name__ == "__main__":
    unittest.main()
