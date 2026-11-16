"""Testes do painel Mercados e ciclos. Sem rede: as amostras abaixo reproduzem o formato real
de cada fonte (trechos conferidos em 16/11/2026) e a busca é injetada por função."""
import datetime as dt
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "mercados"))
import aceite  # noqa: E402
import coletar_mercados as col  # noqa: E402
import fontes  # noqa: E402
import gerar_amostra  # noqa: E402

CATALOGO = col.carregar_catalogo()
AGORA = dt.datetime(2026, 11, 16, 23, 10, tzinfo=dt.timezone.utc)
HOJE = AGORA.date()

# ---------------------------------------------------------------- amostras no formato real

FRED_DIARIA = (
    "observation_date,BAMLH0A0HYM2\n2023-12-22,3.39\n2023-12-25,\n2023-12-26,3.36\n"
    "2026-11-09,3.34\n2026-11-11,3.30\n2026-11-12,3.20\n"
)
FRED_SEMANAL = (
    "observation_date,WALCL\n2002-12-18,719542\n2002-12-25,732059\n2003-01-01,730994\n"
    "2026-10-28,6745635\n2026-11-04,6748145\n2026-11-11,6758867\n"
)
BCB_M2 = ('[{"data":"01/08/2001","valor":null},{"data":"01/09/2026","valor":"7870395191"},'
          '{"data":"01/07/2026","valor":"7737572166"},{"data":"01/08/2026","valor":"7804873388"}]')
BCB_SELIC = ('[{"data":"12/11/2026","valor":"13.75"},{"data":"13/11/2026","valor":"13.75"},'
             '{"data":"16/11/2026","valor":"13.75"},{"data":"17/11/2026","valor":"13.75"},'
             '{"data":"31/12/2026","valor":"13.75"}]')
EUROSTAT = json.dumps({
    "version": "2.0", "class": "dataset", "label": "HICP - monthly data (annual rate of change)",
    "source": "ESTAT", "updated": "2026-11-04T11:00:00+0100",
    "value": {"0": 3.2, "1": 3.8, "2": 4.0}, "status": {"2": "e"},
    "id": ["freq", "unit", "coicop18", "geo", "time"], "size": [1, 1, 1, 1, 3],
    "dimension": {"time": {"label": "Time", "category": {
        "index": {"2026-08": 0, "2026-09": 1, "2026-10": 2},
        "label": {"2026-08": "2026-08", "2026-09": "2026-09", "2026-10": "2026-10"}}}},
    "extension": {},
})
# Linhas reais devolvidas pela API do BCE em 16/11/2026 (colunas finais abreviadas); \r\n e campo com vírgula.
BCE_ILM = (
    "KEY,FREQ,REF_AREA,BS_REP_SECTOR,BS_ITEM,COUNT_AREA,CURRENCY_TRANS,TIME_PERIOD,OBS_VALUE,OBS_STATUS,"
    "CONF_STATUS,PRE_BREAK_VALUE,COMMENT_OBS,TIME_FORMAT,TITLE\r\n"
    'ILM.W.U2.C.T000000.Z5.Z01,W,U2,C,T000000,Z5,Z01,2026-W44,5920001,A,F,,,P7D,"Total assets/liabilities - Eurosystem, weekly"\r\n'
    'ILM.W.U2.C.T000000.Z5.Z01,W,U2,C,T000000,Z5,Z01,2026-W45,5913173,A,F,,,P7D,"Total assets/liabilities - Eurosystem, weekly"\r\n'
)
BCE_BSI = (
    "KEY,FREQ,REF_AREA,ADJUSTMENT,BS_REP_SECTOR,BS_ITEM,MATURITY_ORIG,DATA_TYPE,COUNT_AREA,BS_COUNT_SECTOR,"
    "CURRENCY_TRANS,BS_SUFFIX,TIME_PERIOD,OBS_VALUE,OBS_STATUS,CONF_STATUS,TITLE\r\n"
    'BSI.M.U2.Y.V.M30.X.1.U2.2300.Z01.E,M,U2,Y,V,M30,X,1,U2,2300,Z01,E,2026-08,17647597,A,F,"Monetary aggregate M3, Stocks"\r\n'
)


def ts(ano, mes, dia, hora=0):
    return int(dt.datetime(ano, mes, dia, hora, tzinfo=dt.timezone.utc).timestamp())


def yahoo_json(pares, desloc=0, granularidade="1wk"):
    return json.dumps({"chart": {"result": [{
        "meta": {"symbol": "X", "gmtoffset": desloc, "dataGranularity": granularidade},
        "timestamp": [t for t, _ in pares],
        "indicators": {"quote": [{"close": [p for _, p in pares]}]}}], "error": None}})


# ---------------------------------------------------------------- leitores


class LeitoresTests(unittest.TestCase):
    def test_fred_trata_vazio_e_ponto_como_ausente(self):
        s = fontes.ler_fred(FRED_DIARIA + "2026-11-13,.\n")
        self.assertEqual(s[0], ("2023-12-22", 3.39))
        self.assertNotIn("2023-12-25", dict(s))
        self.assertNotIn("2026-11-13", dict(s))
        self.assertEqual(s[-1], ("2026-11-12", 3.20))

    def test_fred_semanal(self):
        s = fontes.ler_fred(FRED_SEMANAL)
        self.assertEqual(len(s), 6)
        self.assertEqual(s[-1], ("2026-11-11", 6758867.0))

    def test_fred_cabecalho_inesperado_falha(self):
        with self.assertRaises(ValueError):
            fontes.ler_fred("<html>erro</html>")

    def test_bcb_ordena_e_ignora_nulo(self):
        s = fontes.ler_bcb(BCB_M2)
        self.assertEqual([d for d, _ in s], ["2026-07-01", "2026-08-01", "2026-09-01"])
        self.assertEqual(s[-1][1], 7870395191.0)

    def test_bcb_resposta_de_erro_falha(self):
        with self.assertRaises(ValueError):
            fontes.ler_bcb('{"error": "janela máxima de 10 anos"}')

    def test_eurostat_json_stat(self):
        s = fontes.ler_eurostat(EUROSTAT)
        self.assertEqual(s, [("2026-08-01", 3.2), ("2026-09-01", 3.8), ("2026-10-01", 4.0)])

    def test_eurostat_posicao_sem_valor_e_pulada(self):
        d = json.loads(EUROSTAT)
        del d["value"]["1"]
        self.assertEqual([x for x, _ in fontes.ler_eurostat(json.dumps(d))], ["2026-08-01", "2026-10-01"])

    def test_eurostat_mais_de_uma_serie_falha(self):
        d = json.loads(EUROSTAT)
        d["size"] = [1, 1, 1, 2, 3]
        with self.assertRaises(ValueError):
            fontes.ler_eurostat(json.dumps(d))

    def test_bce_semanal_vira_sexta_da_semana_iso(self):
        s = fontes.ler_bce(BCE_ILM)
        self.assertEqual(s, [("2026-10-30", 5920001.0), ("2026-11-06", 5913173.0)])
        self.assertEqual(dt.date(2026, 11, 6).weekday(), 4)

    def test_bce_mensal_vira_ultimo_dia_do_mes(self):
        self.assertEqual(fontes.ler_bce(BCE_BSI), [("2026-08-31", 17647597.0)])

    def test_bce_sem_colunas_esperadas_falha(self):
        with self.assertRaises(ValueError):
            fontes.ler_bce("A,B\r\n1,2\r\n")

    def test_yahoo_descarta_nulos_e_usa_fuso_da_bolsa(self):
        # Barra semanal de Xangai: segunda 00h local = domingo 16h UTC.
        txt = yahoo_json([(ts(2026, 11, 1, 16), 3600.5), (ts(2026, 11, 8, 16), None),
                          (ts(2026, 11, 15, 16), 3663.72)], desloc=8 * 3600)
        self.assertEqual(fontes.ler_yahoo(txt), [("2026-11-02", 3600.5), ("2026-11-16", 3663.72)])

    def test_yahoo_granularidade_trocada_falha(self):
        with self.assertRaises(ValueError):
            fontes.ler_yahoo(yahoo_json([(ts(2026, 10, 1), 1.0)], granularidade="3mo"))

    def test_yahoo_so_nulos_falha(self):
        with self.assertRaises(ValueError):
            fontes.ler_yahoo(yahoo_json([(ts(2026, 11, 2), None)]))

    def test_periodos(self):
        self.assertEqual(fontes.data_do_periodo("2024-02"), "2024-02-01")
        self.assertEqual(fontes.data_do_periodo("2024-02", fim_do_mes=True), "2024-02-29")
        self.assertEqual(fontes.data_do_periodo("2026-W01"), "2026-01-02")
        with self.assertRaises(ValueError):
            fontes.data_do_periodo("2026-Q1")


# ---------------------------------------------------------------- limpeza, redução e derivadas


class LimpezaTests(unittest.TestCase):
    def test_filtra_datas_futuras_e_ordena(self):
        s = fontes.limpar(fontes.ler_bcb(BCB_SELIC) + [("1999-12-31", 19.0)], "2026-11-16", "2000-01-01")
        self.assertEqual([d for d, _ in s], ["2026-11-12", "2026-11-13", "2026-11-16"])

    def test_limpar_remove_repetidas(self):
        s = fontes.limpar([("2026-01-02", 1.0), ("2026-01-01", 5.0), ("2026-01-02", 2.0)], "2026-12-31")
        self.assertEqual(s, [("2026-01-01", 5.0), ("2026-01-02", 2.0)])

    def test_reducao_semanal_ultimo_valor_da_semana_iso(self):
        dias = [("2026-11-02", 1.0), ("2026-11-04", 2.0), ("2026-11-06", 3.0),  # semana 45
                ("2026-11-09", 4.0), ("2026-11-12", 5.0),                       # semana 46 (sem sexta)
                ("2026-11-16", 6.0)]                                            # semana 47
        self.assertEqual(fontes.reduzir_semanal(dias),
                         [("2026-11-06", 3.0), ("2026-11-12", 5.0), ("2026-11-16", 6.0)])

    def test_reducao_semanal_na_virada_do_ano(self):
        # 31/12/2025 (quarta) e 02/01/2026 (sexta) estão na mesma semana ISO (2026-W01).
        self.assertEqual(fontes.reduzir_semanal([("2025-12-31", 1.0), ("2026-01-02", 2.0)]), [("2026-01-02", 2.0)])

    def test_reducao_semanal_mantendo_fim_de_mes(self):
        dias = [("2026-09-28", 15.0), ("2026-09-30", 14.75), ("2026-10-01", 14.75), ("2026-10-04", 14.75)]
        self.assertEqual(fontes.reduzir_semanal(dias, manter_fim_de_mes=True),
                         [("2026-09-30", 14.75), ("2026-10-04", 14.75)])
        dias = [("2026-10-28", 14.75), ("2026-10-31", 14.5), ("2026-11-01", 14.5)]
        self.assertEqual(fontes.reduzir_semanal(dias, manter_fim_de_mes=True),
                         [("2026-10-31", 14.5), ("2026-11-01", 14.5)])

    def test_arredondar_quatro_algarismos(self):
        self.assertEqual(fontes.arredondar(7549.94), 7550)
        self.assertEqual(fontes.arredondar(172817), 172800)
        self.assertEqual(fontes.arredondar(5.5531), 5.553)
        self.assertEqual(fontes.arredondar(0.035123), 0.03512)
        self.assertEqual(fontes.arredondar(-0.4673219), -0.4673)
        self.assertEqual(fontes.arredondar(0), 0)
        self.assertEqual(fontes.arredondar(337.476, 6), 337.476)


class DerivadasTests(unittest.TestCase):
    def test_variacao_12m_mensal(self):
        s = [("2025-10-01", 320.0), ("2025-11-01", 321.0), ("2026-10-01", 336.0)]
        v = fontes.variacao_12m(s)
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0][0], "2026-10-01")
        self.assertAlmostEqual(v[0][1], 5.0)

    def test_variacao_12m_sem_ponto_de_um_ano_antes(self):
        self.assertEqual(fontes.variacao_12m([("2025-07-01", 100.0), ("2026-10-01", 110.0)]), [])

    def test_variacao_12m_semanal_usa_ponto_mais_proximo(self):
        s = [("2025-11-05", 100.0), ("2025-11-12", 200.0), ("2025-11-19", 400.0), ("2026-11-11", 220.0)]
        v = fontes.variacao_12m(s)
        self.assertEqual(v[-1][0], "2026-11-11")
        self.assertAlmostEqual(v[-1][1], 10.0)

    def test_variacao_12m_fim_de_mes_em_ano_bissexto(self):
        s = [("2024-02-29", 100.0), ("2025-02-28", 104.0), ("2026-02-28", 106.08)]
        v = dict(fontes.variacao_12m(s))
        self.assertAlmostEqual(v["2025-02-28"], 4.0)
        self.assertAlmostEqual(v["2026-02-28"], 2.0)

    def test_juro_real_usa_selic_do_fim_do_mes(self):
        selic = [("2026-09-06", 15.0), ("2026-09-30", 14.75), ("2026-10-04", 14.75), ("2026-10-31", 14.5),
                 ("2026-11-15", 13.75)]
        ipca = [("2026-09-01", 4.58), ("2026-10-01", 4.63)]
        r = fontes.juro_real(selic, ipca)
        self.assertEqual([d for d, _ in r], ["2026-09-01", "2026-10-01"])
        self.assertAlmostEqual(r[0][1], 14.75 - 4.58)
        self.assertAlmostEqual(r[1][1], 14.5 - 4.63)

    def test_juro_real_sem_selic_no_mes_nao_calcula(self):
        self.assertEqual(fontes.juro_real([("2026-09-30", 14.75)], [("2026-10-01", 4.63)]), [])

    def test_calculo_desconhecido(self):
        with self.assertRaises(ValueError):
            fontes.calcular_derivada("media", [[]])


# ---------------------------------------------------------------- catálogo


class CatalogoTests(unittest.TestCase):
    OBRIGATORIOS = ("id", "nome", "fonte", "codigo", "url_fonte", "periodicidade", "unidade",
                    "ajuste_sazonal", "verificado", "defasagem_max_dias")
    IDS_FIXOS = {
        "idx_sp500", "idx_nasdaq100", "idx_dow", "idx_dax", "idx_eurostoxx50", "idx_ftse100", "idx_ibovespa",
        "idx_psi", "idx_nikkei", "idx_hangseng", "idx_xangai", "idx_emergentes", "risco_vix", "fx_dxy",
        "fx_eurusd", "fx_usdbrl", "fx_eurbrl", "fx_usdjpy", "fx_gbpusd", "com_ouro", "com_prata", "com_wti",
        "com_cobre", "btc_usd", "eth_btc", "juros_eua_2a", "juros_eua_10a", "juros_eua_10a2a", "risco_hy",
        "cpi_eua", "liq_eua_m2", "liq_fed_balanco", "infl_eua_12m", "liq_eua_m2_var12m",
        "liq_fed_balanco_var12m", "infl_br_12m", "juros_br_selic", "liq_br_base", "liq_br_m2", "juros_br_real",
        "liq_br_m2_var12m", "liq_br_base_var12m", "infl_ea_12m", "infl_pt_12m", "liq_ea_m3", "liq_bce_balanco",
        "liq_ea_m3_var12m", "liq_bce_balanco_var12m",
    }

    def test_ids_unicos_e_fixos(self):
        ids = [s["id"] for s in CATALOGO]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(self.IDS_FIXOS - set(ids), set())

    def test_campos_obrigatorios(self):
        for s in CATALOGO:
            for c in self.OBRIGATORIOS:
                self.assertIn(c, s, f"{s.get('id')}: falta {c}")
            self.assertIn(s["fonte"], ("yahoo", "fred", "bcb", "eurostat", "bce", "derivada"), s["id"])
            self.assertIn(s["periodicidade"], ("semanal", "mensal"), s["id"])
            self.assertIn(s["ajuste_sazonal"], (True, False, None), s["id"])
            self.assertTrue(s["verificado"].strip(), s["id"])
            self.assertGreater(s["defasagem_max_dias"], 0, s["id"])
            self.assertTrue(str(s["url_fonte"]).startswith("https://"), s["id"])

    def test_derivadas_apontam_para_series_existentes(self):
        ids = {s["id"]: s for s in CATALOGO}
        for s in CATALOGO:
            if s["fonte"] != "derivada":
                self.assertNotIn("derivada_de", s, s["id"])
                continue
            self.assertIn(s["calculo"], ("variacao_12m", "juro_real"), s["id"])
            self.assertTrue(s["derivada_de"], s["id"])
            for base in s["derivada_de"]:
                self.assertIn(base, ids, f"{s['id']} aponta para {base}")
                self.assertNotEqual(ids[base]["fonte"], "derivada", f"{s['id']}: base não pode ser derivada")

    def test_enderecos_por_fonte(self):
        por_id = {s["id"]: s for s in CATALOGO}
        u = col.enderecos(por_id["idx_sp500"], HOJE)[0]
        self.assertIn("/chart/%5EGSPC?period1=946684800&period2=", u)
        self.assertIn("interval=1wk", u)
        self.assertNotIn("range=max", u)
        self.assertEqual(col.enderecos(por_id["cpi_eua"], HOJE),
                         ["https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"])
        self.assertIn("geo=PT", col.enderecos(por_id["infl_pt_12m"], HOJE)[0])
        self.assertEqual(col.enderecos(por_id["liq_ea_m3"], HOJE)[0],
                         "https://data-api.ecb.europa.eu/service/data/BSI/M.U2.Y.V.M30.X.1.U2.2300.Z01.E?format=csvdata")
        self.assertEqual(len(col.enderecos(por_id["infl_br_12m"], HOJE)), 1)

    def test_selic_em_janelas_de_ate_10_anos(self):
        selic = next(s for s in CATALOGO if s["id"] == "juros_br_selic")
        urls = col.enderecos(selic, HOJE)
        self.assertGreater(len(urls), 2)
        self.assertIn("dataInicial=01/01/2000", urls[0])
        self.assertTrue(urls[-1].endswith("dataFinal=16/11/2026"))
        for u in urls:
            ini = int(u.split("dataInicial=01/01/")[1][:4])
            fim = int(u.split("dataFinal=")[1][-4:])
            self.assertLess(fim - ini, 10)

    def test_eventos_halvings(self):
        with open(Path(col.AQUI) / "eventos.json", encoding="utf-8") as f:
            h = json.load(f)["halvings"]
        self.assertEqual([x["bloco"] for x in h], [210000, 420000, 630000, 840000])
        self.assertEqual([x["data"][:4] for x in h], ["2012", "2016", "2020", "2024"])
        for x in h:
            dt.date.fromisoformat(x["data"])
            self.assertTrue(x["fonte"].startswith("https://"))


# ---------------------------------------------------------------- coleta com busca injetada


def semanas(n, valor0, fim=HOJE, passo=1.0):
    seg = fim - dt.timedelta(days=fim.weekday())
    return [(seg - dt.timedelta(days=7 * (n - 1 - i)), valor0 + passo * i) for i in range(n)]


def meses(n, valor0, ultimo=(2026, 10), passo=1.0):
    a, m = ultimo
    saida = []
    for i in range(n):
        saida.append((a, m, valor0 + passo * (n - 1 - i)))
        a, m = (a - 1, 12) if m == 1 else (a, m - 1)
    return saida[::-1]


def busca_falsa(falhar=()):
    """Devolve uma função de busca que responde no formato real de cada fonte, sem rede."""
    chamadas = []

    def buscar(url):
        chamadas.append(url)
        if any(f in url for f in falhar):
            raise OSError("falha forçada")
        if "finance.yahoo.com" in url:
            return yahoo_json([(int(dt.datetime.combine(d, dt.time(), dt.timezone.utc).timestamp()), v)
                               for d, v in semanas(60, 100.0)])
        if "fred.stlouisfed.org" in url:
            cod = url.split("id=")[1]
            if cod in ("CPIAUCSL", "M2SL"):
                linhas = [f"{a}-{m:02d}-01,{v}" for a, m, v in meses(40, 300.0)]
            elif cod == "WALCL":
                linhas = [f"{(d + dt.timedelta(days=2)).isoformat()},{v}" for d, v in semanas(120, 6000000.0, HOJE - dt.timedelta(days=7), 1000.0)]
            else:  # diárias: cinco dias úteis por semana, com um feriado vazio
                linhas = []
                for d, v in semanas(60, 4.0, HOJE - dt.timedelta(days=7), 0.01):
                    linhas += [f"{(d + dt.timedelta(days=k)).isoformat()},{v + k / 1000:.3f}" for k in range(5)]
                linhas.insert(3, "2025-01-01,")
            return f"observation_date,{cod}\n" + "\n".join(linhas) + "\n"
        if "api.bcb.gov.br" in url:
            if "sgs.432/" in url:
                ini = int(url.split("dataInicial=01/01/")[1][:4])
                fim = min(int(url.split("dataFinal=")[1][-4:]), 2026)
                itens = [{"data": f"{d:02d}/{m:02d}/{a}", "valor": "13.75"}
                         for a in range(ini, fim + 1) for m in range(1, 13) for d in (5, 15, 28)]
                return json.dumps(itens)  # inclui datas futuras (fim de 2026), como a API real
            itens = [{"data": f"01/{m:02d}/{a}", "valor": str(v)} for a, m, v in meses(40, 4.0, passo=0.5)]
            return json.dumps(itens[::-1])  # fora de ordem, como a SGS 27810
        if "ec.europa.eu" in url:
            ms = meses(40, 2.0, passo=0.1)
            return json.dumps({"id": ["freq", "unit", "coicop18", "geo", "time"], "size": [1, 1, 1, 1, len(ms)],
                               "value": {str(i): v for i, (_, _, v) in enumerate(ms)},
                               "dimension": {"time": {"category": {"index": {f"{a}-{m:02d}": i for i, (a, m, _) in enumerate(ms)}}}}})
        if "ecb.europa.eu" in url:
            if "/ILM/" in url:
                lin = [f"ILM.W,W,{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d},{v},A" for d, v in semanas(120, 5900000.0, HOJE - dt.timedelta(days=7), 100.0)]
            else:
                lin = [f"BSI.M,M,{a}-{m:02d},{v},A" for a, m, v in meses(40, 17000000.0, (2026, 8), 1000.0)]
            return "KEY,FREQ,TIME_PERIOD,OBS_VALUE,OBS_STATUS\r\n" + "\r\n".join(lin) + "\r\n"
        raise AssertionError(f"endereço inesperado: {url}")

    buscar.chamadas = chamadas
    return buscar


class ColetaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.completa = col.coletar(CATALOGO, busca_falsa(), None, AGORA)

    def test_contrato_do_json(self):
        s = self.completa
        for c in aceite.CAMPOS_TOPO:
            self.assertIn(c, s)
        self.assertEqual(s["gerado_brt"], "16/11/2026 20:10")
        self.assertEqual(s["series_total"], len(CATALOGO))
        self.assertEqual(list(s["series"]), [x["id"] for x in CATALOGO])
        for sid, b in s["series"].items():
            for c in aceite.CAMPOS_SERIE:
                self.assertIn(c, b, f"{sid}: falta {c}")
            datas = [p[0] for p in b["pontos"]]
            self.assertEqual(datas, sorted(set(datas)), sid)
            self.assertTrue(all(d <= "2026-11-16" for d in datas), sid)
            if b["pontos"]:
                self.assertEqual(b["ultimo_dado"], datas[-1], sid)

    def test_fonte_legivel(self):
        s = self.completa["series"]
        self.assertEqual(s["infl_br_12m"]["fonte"], "Banco Central do Brasil (SGS 13522)")
        self.assertEqual(s["idx_sp500"]["fonte"], "Yahoo Finance (^GSPC)")
        self.assertEqual(s["infl_pt_12m"]["fonte"], "Eurostat (prc_hicp_minr, geo=PT)")
        self.assertIn("Selic", s["juros_br_real"]["fonte"])

    def test_serie_desligada_sai_sem_dados_e_nao_e_buscada(self):
        buscar = busca_falsa()
        s = col.coletar(CATALOGO, buscar, None, AGORA)
        self.assertEqual(s["series"]["risco_hy"]["status"], "sem dados")
        self.assertEqual(s["series"]["risco_hy"]["pontos"], [])
        self.assertFalse(any("BAMLH0A0HYM2" in u for u in buscar.chamadas))
        self.assertEqual(s["series_ok"], len(CATALOGO) - 1)

    def test_selic_sem_datas_futuras_e_semanal(self):
        p = self.completa["series"]["juros_br_selic"]["pontos"]
        self.assertEqual(p[0][0], "2000-01-05")
        self.assertEqual(p[-1][0], "2026-11-15")

    def test_diaria_do_fred_reduzida_para_semanal(self):
        p = self.completa["series"]["juros_eua_10a"]["pontos"]
        self.assertEqual(len(p), 60)
        self.assertTrue(all(dt.date.fromisoformat(d).weekday() == 4 for d, _ in p))

    def test_yahoo_ultimo_parcial(self):
        b = self.completa["series"]["idx_sp500"]
        self.assertEqual(b["ultimo_dado"], "2026-11-16")
        self.assertIs(b["ultimo_parcial"], True)
        self.assertNotIn("ultimo_parcial", self.completa["series"]["juros_eua_10a"])
        domingo = dt.datetime(2026, 11, 22, 12, tzinfo=dt.timezone.utc)
        # Na semana seguinte, o mesmo último ponto deixa de ser parcial.
        self.assertFalse(col.semana_corrente("2026-11-16", (domingo + dt.timedelta(days=1)).date()))
        self.assertTrue(col.semana_corrente("2026-11-16", domingo.date()))

    def test_derivadas_calculadas_das_bases_do_arquivo(self):
        s = self.completa["series"]
        esperado = fontes.arredondar_pontos(fontes.variacao_12m([tuple(p) for p in s["cpi_eua"]["pontos"]]))
        self.assertEqual(s["infl_eua_12m"]["pontos"], esperado)
        self.assertEqual(len(esperado), 28)
        real = dict(map(tuple, s["juros_br_real"]["pontos"]))
        ipca = dict(map(tuple, s["infl_br_12m"]["pontos"]))
        self.assertAlmostEqual(real["2026-10-01"], 13.75 - ipca["2026-10-01"])
        self.assertEqual(s["juros_br_real"]["status"], "ok")

    def test_valores_com_quatro_algarismos(self):
        for d, v in self.completa["series"]["juros_eua_10a"]["pontos"]:
            self.assertEqual(v, fontes.arredondar(v, 4))

    def test_falha_de_uma_serie_vira_anterior_com_bloco_antigo(self):
        anterior = json.loads(json.dumps(self.completa))
        anterior["series"]["cpi_eua"]["pontos"][-1][1] = 999.0  # marca para reconhecer o bloco antigo
        depois = AGORA + dt.timedelta(days=1)
        s = col.coletar(CATALOGO, busca_falsa(falhar=("CPIAUCSL",)), anterior, depois)
        b = s["series"]["cpi_eua"]
        self.assertEqual(b["status"], "anterior")
        self.assertEqual(b["pontos"], anterior["series"]["cpi_eua"]["pontos"])
        self.assertEqual(b["coletado_utc"], anterior["series"]["cpi_eua"]["coletado_utc"])
        # A derivada é recalculada do bloco antigo e herda o status.
        self.assertEqual(s["series"]["infl_eua_12m"]["status"], "anterior")
        self.assertEqual(s["series"]["infl_eua_12m"]["pontos"],
                         fontes.arredondar_pontos(fontes.variacao_12m([tuple(p) for p in b["pontos"]])))
        self.assertEqual(s["series"]["liq_eua_m2"]["status"], "ok")
        self.assertEqual(s["series"]["liq_eua_m2_var12m"]["status"], "ok")
        self.assertEqual(s["series_ok"], len(CATALOGO) - 3)

    def test_falha_sem_arquivo_anterior_vira_sem_dados(self):
        s = col.coletar(CATALOGO, busca_falsa(falhar=("sgs.432/",)), None, AGORA)
        self.assertEqual(s["series"]["juros_br_selic"]["status"], "sem dados")
        self.assertEqual(s["series"]["juros_br_selic"]["pontos"], [])
        self.assertIsNone(s["series"]["juros_br_selic"]["ultimo_dado"])
        self.assertEqual(s["series"]["juros_br_real"]["status"], "sem dados")
        self.assertEqual(s["series"]["infl_br_12m"]["status"], "ok")

    def test_resposta_malformada_conta_como_falha(self):
        def buscar(url):
            if "M2SL" in url:
                return "<html>Too many requests</html>"
            return busca_falsa()(url)
        s = col.coletar(CATALOGO, buscar, self.completa, AGORA)
        self.assertEqual(s["series"]["liq_eua_m2"]["status"], "anterior")

    def test_todas_falham_nao_regrava_e_sai_com_1(self):
        def sempre_falha(url):
            raise OSError("sem rede")
        self.assertIsNone(col.coletar(CATALOGO, sempre_falha, self.completa, AGORA))
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "mercados.json")
            col.gravar(self.completa, caminho)
            antes = Path(caminho).read_bytes()
            self.assertEqual(col.main(sempre_falha, caminho, pausa=0), 1)
            self.assertEqual(Path(caminho).read_bytes(), antes)
            vazio = os.path.join(pasta, "novo", "mercados.json")
            self.assertEqual(col.main(sempre_falha, vazio, pausa=0), 1)
            self.assertFalse(os.path.exists(vazio))

    def test_main_grava_compacto_e_reaproveita_o_proprio_arquivo(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "sub", "mercados.json")
            self.assertEqual(col.main(busca_falsa(), caminho, pausa=0), 0)
            bruto = Path(caminho).read_text(encoding="utf-8")
            self.assertNotIn("\n", bruto)
            self.assertNotIn('", "', bruto)
            self.assertEqual(col.main(busca_falsa(falhar=("WALCL",)), caminho, pausa=0), 0)
            s = json.loads(Path(caminho).read_text(encoding="utf-8"))
            self.assertEqual(s["series"]["liq_fed_balanco"]["status"], "anterior")
            self.assertTrue(s["series"]["liq_fed_balanco"]["pontos"])


# ---------------------------------------------------------------- aceite


class AceiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.amostra = gerar_amostra.gerar(CATALOGO)
        cls.hoje = gerar_amostra.AGORA.date()

    def copia(self):
        return json.loads(json.dumps(self.amostra))

    def erros(self, dados, **kw):
        kw.setdefault("amostra", True)
        return aceite.validar(dados, CATALOGO, kw.pop("hoje", self.hoje), **kw)

    def test_amostra_e_aprovada(self):
        self.assertEqual(self.erros(self.amostra), [])

    def test_amostra_tem_todos_os_ids_um_anterior_e_um_sem_dados(self):
        a = self.amostra
        self.assertIs(a["amostra_sintetica"], True)
        self.assertEqual(set(a["series"]), {s["id"] for s in CATALOGO})
        status = [b["status"] for b in a["series"].values()]
        self.assertEqual(status.count("anterior"), 1)
        self.assertEqual(status.count("sem dados"), 1)

    def test_amostra_e_deterministica(self):
        self.assertEqual(json.dumps(gerar_amostra.gerar(CATALOGO)), json.dumps(self.amostra))

    def test_amostra_no_disco_passa_pela_linha_de_comando(self):
        caminho = gerar_amostra.SAIDA_PADRAO
        if not os.path.exists(caminho):
            self.skipTest("amostra não gerada")
        self.assertEqual(aceite.main([caminho, "--amostra"]), 0)
        self.assertEqual(aceite.main([caminho]), 1)  # sintético nunca passa no aceite de publicação

    def test_coleta_simulada_passa_no_aceite_real(self):
        s = col.coletar(CATALOGO, busca_falsa(), None, AGORA)
        self.assertEqual(aceite.validar(s, CATALOGO, HOJE), [])

    def test_sintetico_reprovado_sem_opcao_amostra(self):
        self.assertTrue(self.erros(self.amostra, amostra=False))

    def test_reprova_data_futura(self):
        d = self.copia()
        d["series"]["idx_sp500"]["pontos"].append(["2027-01-04", 7600])
        d["series"]["idx_sp500"]["ultimo_dado"] = "2027-01-04"
        self.assertTrue(any("data futura" in e for e in self.erros(d)))

    def test_reprova_datas_fora_de_ordem_e_repetidas(self):
        d = self.copia()
        p = d["series"]["cpi_eua"]["pontos"]
        p[10], p[11] = p[11], p[10]
        self.assertTrue(any("fora de ordem" in e for e in self.erros(d)))
        d = self.copia()
        p = d["series"]["cpi_eua"]["pontos"]
        p[11] = list(p[10])
        self.assertTrue(any("fora de ordem" in e for e in self.erros(d)))

    def test_reprova_valor_fora_da_faixa(self):
        d = self.copia()
        d["series"]["juros_br_selic"]["pontos"][5][1] = 75.0
        self.assertTrue(any("fora da faixa" in e for e in self.erros(d)))
        d = self.copia()
        d["series"]["idx_ibovespa"]["pontos"][5][1] = -1
        self.assertTrue(any("fora da faixa" in e for e in self.erros(d)))
        d = self.copia()
        d["series"]["idx_ibovespa"]["pontos"][5][1] = None
        self.assertTrue(any("malformado" in e for e in self.erros(d)))

    def test_reprova_poucos_pontos(self):
        d = self.copia()
        d["series"]["infl_pt_12m"]["pontos"] = d["series"]["infl_pt_12m"]["pontos"][-5:]
        self.assertTrue(any("mínimo" in e for e in self.erros(d)))

    def test_defasagem_reprova_fora_da_amostra_e_e_ignorada_nela(self):
        d = self.copia()
        d.pop("amostra_sintetica")
        tarde = self.hoje + dt.timedelta(days=40)
        e = self.erros(d, amostra=False, hoje=tarde)
        self.assertTrue(any("idx_sp500: último dado há" in x for x in e))
        self.assertFalse(any("idx_psi: último dado" in x for x in e))  # "anterior" só gera aviso
        self.assertEqual(self.erros(self.amostra, hoje=tarde), [])

    def test_reprova_menos_de_60_por_cento(self):
        d = self.copia()
        for i, b in enumerate(d["series"].values()):
            if i % 2 == 0:
                b.update(status="sem dados", pontos=[], ultimo_dado=None)
        d["series_ok"] = sum(1 for b in d["series"].values() if b["status"] == "ok")
        self.assertTrue(any("mínimo 60%" in e for e in self.erros(d)))

    def test_reprova_encolhimento_maior_que_5_por_cento(self):
        d = self.copia()
        p = d["series"]["idx_dow"]["pontos"]
        d["series"]["idx_dow"]["pontos"] = p[len(p) // 10:]
        self.assertTrue(any("encolheu" in e for e in self.erros(d, anterior=self.amostra)))
        d = self.copia()
        d["series"]["idx_dow"]["pontos"] = d["series"]["idx_dow"]["pontos"][10:]  # menos de 5%: aceito
        self.assertEqual(self.erros(d, anterior=self.amostra), [])

    def test_reprova_serie_ausente_campo_ausente_e_status_invalido(self):
        d = self.copia()
        del d["series"]["btc_usd"]
        d["series_total"] -= 1
        d["series_ok"] -= 1
        self.assertTrue(any("btc_usd: série do catálogo ausente" in e for e in self.erros(d)))
        d = self.copia()
        del d["series"]["btc_usd"]["unidade"]
        self.assertTrue(any("campos ausentes" in e for e in self.erros(d)))
        d = self.copia()
        d["series"]["btc_usd"]["status"] = "parcial"
        self.assertTrue(any("status inválido" in e for e in self.erros(d)))
        self.assertTrue(self.erros({"series": {}}))

    def test_linha_de_comando_reprova_arquivo_ilegivel(self):
        with tempfile.TemporaryDirectory() as pasta:
            ruim = os.path.join(pasta, "x.json")
            Path(ruim).write_text("{", encoding="utf-8")
            self.assertEqual(aceite.main([ruim]), 1)
            self.assertEqual(aceite.main([os.path.join(pasta, "nao_existe.json")]), 1)


if __name__ == "__main__":
    unittest.main()
