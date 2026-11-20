"""Testes da coleta de preços (correções de 20/11/2026): fuso da B3, fallback do meta e nunca voltar no tempo."""
import importlib.util, io, json, os, tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

spec = importlib.util.spec_from_file_location("bp", Path(__file__).resolve().parents[1] / "scripts/besst_painel.py")
bp = importlib.util.module_from_spec(spec); spec.loader.exec_module(bp)
ts = lambda s: int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp())


def resposta(barras, meta_preco=None, meta_hora=None):
    meta = {"gmtoffset": -10800}
    if meta_preco:
        meta.update(regularMarketPrice=meta_preco, regularMarketTime=ts(meta_hora))
    j = {"chart": {"result": [{"meta": meta, "timestamp": [ts(h) for h, _ in barras],
                               "indicators": {"quote": [{"close": [c for _, c in barras], "volume": [1000] * len(barras)}]},
                               "events": {}}]}}
    return io.BytesIO(json.dumps(j).encode())


class Coleta(unittest.TestCase):
    def rodar(self, resp):
        with mock.patch.object(bp.urllib.request, "urlopen", return_value=resp), mock.patch.object(bp.time, "sleep"):
            return bp.coletar(["TESTE3"])["TESTE3"]

    def test_fuso_da_b3(self):
        # barra às 01:30 UTC de 19/11 = 22:30 de 18/11 em Brasília
        r = self.rodar(resposta([("2026-11-17T13:00:00", 10.0), ("2026-11-19T01:30:00", 11.0)]))
        self.assertEqual(r[1], "2026-11-18")

    def test_meta_mais_novo_que_a_serie(self):
        # madrugada: a série perdeu o pregão de 19/11, mas o meta tem o fechamento das 18h de 19/11 (21:00 UTC)
        r = self.rodar(resposta([("2026-11-18T13:00:00", 10.0)], 12.5, "2026-11-19T21:00:00"))
        self.assertEqual((r[0], r[1]), (12.5, "2026-11-19"))

    def test_nunca_volta_no_tempo(self):
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / "ultimo.json"
            arq.write_text(json.dumps({"A3": [20.0, "2026-11-19", {}, {}, 0, "", 1], "B3X": [5.0, "2026-11-19", {}, {}, 0, "", 1]}))
            novos = {"A3": [19.0, "2026-11-18", {"2026": 18}, {}, 0, "", 1]}
            out = bp.sem_regressao(novos, arq)
            self.assertEqual(out["A3"][:2], [20.0, "2026-11-19"])
            self.assertEqual(out["A3"][2], {"2026": 18})   # demais campos vêm da coleta nova
            self.assertIn("B3X", out)                       # papel que faltou na coleta não some


if __name__ == "__main__":
    unittest.main()
