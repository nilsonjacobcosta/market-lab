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


# ---- coleta (sem rede) ----
import datetime as dt  # noqa: E402
import json  # noqa: E402

import coletar_tendencias as col  # noqa: E402

CAT = json.load(open(Path(__file__).resolve().parents[1] / "dados" / "tendencias" / "catalogo_etfs.json", encoding="utf-8"))


def serie_sintetica(n, fim="2026-11-09", passo=0.001, base=100.0):
    fim_d = dt.date.fromisoformat(fim)
    datas, d = [], fim_d
    while len(datas) < n:
        if d.weekday() < 5:
            datas.append(d.isoformat())
        d -= dt.timedelta(days=1)
    datas.reverse()
    return [(dia, base * (1 + passo) ** i) for i, dia in enumerate(datas)]


class ColetaTests(unittest.TestCase):
    def test_extrai_adjclose_e_ignora_nulos(self):
        res = {"timestamp": [1762700000, 1762786400, 1762872800],
               "indicators": {"quote": [{"close": [10, None, 12]}], "adjclose": [{"adjclose": [9.5, None, 11.5]}]}}
        out = col.extrair_serie(res)
        self.assertEqual([p for _, p in out], [9.5, 11.5])

    def test_cai_para_close_sem_adjclose(self):
        res = {"timestamp": [1762700000], "indicators": {"quote": [{"close": [10]}]}}
        self.assertEqual(col.extrair_serie(res)[0][1], 10.0)

    def test_descarta_pregao_do_dia_antes_das_1630(self):
        s = [("2026-11-09", 1.0), ("2026-11-10", 2.0)]
        agora = dt.datetime(2026, 11, 10, 18, 0, tzinfo=dt.timezone.utc)  # 13h NY
        self.assertEqual(col.descartar_pregao_aberto(s, agora), s[:1])

    def test_mantem_pregao_do_dia_depois_das_1630(self):
        s = [("2026-11-09", 1.0), ("2026-11-10", 2.0)]
        agora = dt.datetime(2026, 11, 10, 22, 30, tzinfo=dt.timezone.utc)  # 17h30 NY
        self.assertEqual(col.descartar_pregao_aberto(s, agora), s)

    def test_alinha_por_datas_em_comum(self):
        a = [("2026-01-01", 1.0), ("2026-01-02", 2.0), ("2026-01-05", 3.0)]
        b = [("2026-01-02", 20.0), ("2026-01-05", 30.0)]
        datas, alin = col.alinhar({"A": a, "B": b})
        self.assertEqual(datas, ["2026-01-02", "2026-01-05"])
        self.assertEqual(alin["A"], [2.0, 3.0])

    def test_montar_tudo_ok(self):
        series = {CAT["referencia"]["ticker"]: serie_sintetica(300, passo=0.0005)}
        for c in CAT["celulas"]:
            series[c["ticker"]] = serie_sintetica(300, passo=0.001)
        agora = dt.datetime(2026, 11, 10, 23, 0, tzinfo=dt.timezone.utc)
        out = col.montar(CAT, series, agora)
        self.assertEqual(out["celulas_ok"], 9)
        self.assertEqual(out["ultimo_pregao"], "2026-11-09")
        self.assertTrue(all(c["status"] == "ok" for c in out["celulas"]))
        self.assertGreater(out["celulas"][0]["relativo_12m"], 0)  # sobe mais que a referência

    def test_etf_ausente_vira_sem_dados_sem_derrubar_o_resto(self):
        series = {CAT["referencia"]["ticker"]: serie_sintetica(300)}
        for c in CAT["celulas"][1:]:
            series[c["ticker"]] = serie_sintetica(300)
        out = col.montar(CAT, series, dt.datetime(2026, 11, 10, 23, 0, tzinfo=dt.timezone.utc))
        self.assertEqual(out["celulas"][0]["status"], "sem dados")
        self.assertEqual(out["celulas_ok"], 8)

    def test_historico_curto_vira_sem_dados(self):
        series = {CAT["referencia"]["ticker"]: serie_sintetica(100)}
        for c in CAT["celulas"]:
            series[c["ticker"]] = serie_sintetica(100)
        out = col.montar(CAT, series, dt.datetime(2026, 11, 10, 23, 0, tzinfo=dt.timezone.utc))
        self.assertEqual(out["celulas_ok"], 0)

    def test_sem_referencia_nenhuma_celula(self):
        series = {c["ticker"]: serie_sintetica(300) for c in CAT["celulas"]}
        out = col.montar(CAT, series, dt.datetime(2026, 11, 10, 23, 0, tzinfo=dt.timezone.utc))
        self.assertEqual(out["celulas_ok"], 0)

    def test_saida_serializa_em_json(self):
        series = {CAT["referencia"]["ticker"]: serie_sintetica(300)}
        for c in CAT["celulas"]:
            series[c["ticker"]] = serie_sintetica(300)
        out = col.montar(CAT, series, dt.datetime(2026, 11, 10, 23, 0, tzinfo=dt.timezone.utc))
        json.dumps(out, allow_nan=False)  # sem NaN/Infinity


if __name__ == "__main__":
    unittest.main()
