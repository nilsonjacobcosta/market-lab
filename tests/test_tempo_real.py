"""Testes do painel Mercados em tempo real. Só biblioteca padrão, sem rede.
Verificam o conjuntos.json e o index.html: esquema, limites, símbolos testados, textos."""
import datetime as dt
import json
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1] / "monitor" / "tempo-real"
CFG = json.loads((RAIZ / "conjuntos.json").read_text(encoding="utf-8"))
HTML = (RAIZ / "index.html").read_text(encoding="utf-8")
WIDGETS_PERMITIDOS = {"market_quotes"}
LIM_INICIANTE, LIM_TOTAL, LIM_SIMBOLOS = 4, 6, 8
PROIBIDAS = ["despenca", "dispara", "pânico", "panico", "desaba", "explode", "forte alta", "forte queda",
             "compre", "venda agora", "recomendamos", "garantido", "sinal de compra", "sinal de venda"]
CAMPOS = ["id", "titulo", "widget", "iniciante", "simbolos", "o_que_e", "como_ler", "ja_se_observou", "termos"]


def graficos():
    for c in CFG["conjuntos"]:
        for g in c["graficos"]:
            yield c, g


class Esquema(unittest.TestCase):
    def test_campos_e_widgets(self):
        ids = set()
        for c, g in graficos():
            for k in CAMPOS:
                self.assertIn(k, g, f"{g.get('id')}: falta {k}")
            self.assertIn(g["widget"], WIDGETS_PERMITIDOS, g["id"])
            self.assertNotIn(g["id"], ids, "id repetido")
            ids.add(g["id"])
            self.assertTrue(g["id"].startswith("tr-"))
            self.assertTrue(0 < len(g["simbolos"]) <= LIM_SIMBOLOS, g["id"])
            for x in g["simbolos"]:
                self.assertTrue(x["s"] and x["rotulo"] and x["atraso"], f"{g['id']}: símbolo sem rótulo ou atraso")

    def test_nenhum_widget_de_analise_tecnica(self):
        self.assertNotIn("technical-analysis", HTML)
        self.assertNotIn("technical_analysis", json.dumps(CFG))

    def test_limites_de_cartoes(self):
        for c in CFG["conjuntos"]:
            self.assertLessEqual(len(c["graficos"]), LIM_TOTAL, c["id"])
            self.assertLessEqual(sum(1 for g in c["graficos"] if g["iniciante"]), LIM_INICIANTE, c["id"])

    def test_iniciante_tem_quatro_conjuntos(self):
        com = [c["id"] for c in CFG["conjuntos"] if any(g["iniciante"] for g in c["graficos"])]
        self.assertEqual(com, ["cambio", "acoes", "juros-brasil", "commodities"])

    def test_acoes_eua_e_brasil_em_cartoes_separados(self):
        ac = {g["id"]: g for c, g in graficos() if c["id"] == "acoes"}
        self.assertTrue(all(x["s"].startswith("FOREXCOM:") for x in ac["tr-acoes-eua"]["simbolos"]))
        self.assertEqual([x["s"] for x in ac["tr-acoes-brasil"]["simbolos"]], ["BMFBOVESPA:IBOV"])
        self.assertFalse(ac["tr-acoes-mini"]["iniciante"], "minicontratos só no Avançado")


class Simbolos(unittest.TestCase):
    def usados(self):
        s = [(g["id"], x["s"]) for c, g in graficos() for x in g["simbolos"]]
        s += [("ticker", x["proName"]) for x in CFG["ticker"]["simbolos"]]
        return s

    def test_todo_simbolo_tem_teste_registrado(self):
        ok = set(CFG["matriz_teste"]["simbolos_aprovados"])
        self.assertTrue(CFG["matriz_teste"]["data_teste"])
        for onde, s in self.usados():
            self.assertIn(s, ok, f"{onde}: {s} sem teste registrado")

    def test_nenhum_reprovado_em_uso(self):
        rep = set(CFG["matriz_teste"]["reprovados"])
        for onde, s in self.usados():
            self.assertNotIn(s, rep, f"{onde}: {s} foi reprovado no teste")

    def test_di_so_com_vencimento_a_mais_de_90_dias(self):
        hoje = dt.date.today()
        for onde, s in self.usados():
            m = re.match(r"BMFBOVESPA:DI1([FGHJKMNQUVXZ])(\d{4})$", s)
            if m:
                venc = dt.date(int(m.group(2)), 1, 1)  # DI1F = janeiro
                self.assertEqual(m.group(1), "F", f"{s}: só vencimentos de janeiro (F) são usados")
                self.assertGreater((venc - hoje).days, 90, f"{onde}: {s} vence em menos de 90 dias; trocar o contrato")

    def test_toda_cotacao_da_b3_marcada_como_atrasada(self):
        for c, g in graficos():
            for x in g["simbolos"]:
                if x["s"].startswith("BMFBOVESPA:"):
                    self.assertIn("atrasad", x["atraso"].lower(), f"{x['s']}: B3 deve aparecer como atrasada")

    def test_dados_diarios_rotulados(self):
        for c, g in graficos():
            for x in g["simbolos"]:
                if x["s"].startswith("FRED:"):
                    self.assertIn("dado diário", x["atraso"])

    def test_ticker_com_simbolos_aprovados_e_marcado_pendente(self):
        self.assertIn("pendente", CFG["matriz_teste"]["ticker_tape"])
        self.assertIn(CFG["ticker"]["padrao"], ("ligado", "desligado"))


class Textos(unittest.TestCase):
    def textos(self):
        for c, g in graficos():
            for k in ("o_que_e", "como_ler", "ja_se_observou"):
                yield f"{g['id']}.{k}", g[k]
        for c in CFG["conjuntos"]:
            yield f"{c['id']}.nao_diz", c["nao_diz"]
            yield f"{c['id']}.subtitulo", c["subtitulo"]

    def test_sem_palavras_proibidas(self):
        for onde, t in self.textos():
            for p in PROIBIDAS:
                self.assertNotIn(p, t.lower(), f"{onde}: '{p}'")

    def test_nenhum_numero_de_cotacao_no_json(self):
        # R-TR4: texto estático não cita valor atual. Permite anos, vencimentos, "90 dias", "1!", "2 anos".
        for onde, t in self.textos():
            limpo = re.sub(r"\b(19|20)\d{2}\b|\b\d+\s*(dias|anos|ano|pontos? percentuais?|%)\b|\b\d+\s*\.?\s*mil\b|S&P 500|Nasdaq 100|\b(10|2)\b|\b500\b|\b1!", "", t)
            self.assertIsNone(re.search(r"\d+[.,]\d+", limpo), f"{onde}: parece conter valor de cotação")
            self.assertIsNone(re.search(r"\bR\$\s*\d|US\$\s*\d|\$\s*\d", t), f"{onde}: valor monetário")

    def test_termos_existem_no_glossario(self):
        G = CFG["glossario"]
        for c, g in graficos():
            for t in g["termos"]:
                self.assertIn(t, G, f"{g['id']}: termo {t} fora do glossário")
        for k in ("tempo_real", "cfd", "contrato_futuro", "vencimento", "di", "ponto_percentual", "ticker",
                  "minicontrato", "alavancagem", "widget_terceiros", "ruido", "dado_diario", "cotacao", "fechamento",
                  "variacao_dia", "pregao"):
            self.assertIn(k, G, f"termo obrigatório ausente: {k}")

    def test_variacao_dia_tem_ancora_e_neutralidade(self):
        d = CFG["glossario"]["variacao_dia"]["definicao"].lower()
        self.assertIn("fechamento", d)
        self.assertIn("não significam bom nem ruim", d)

    def test_nao_diz_em_todo_conjunto(self):
        for c in CFG["conjuntos"]:
            self.assertGreater(len(c["nao_diz"]), 60, c["id"])

    def test_observacao_estatica_sem_valor(self):
        for c, g in graficos():
            self.assertTrue(g["ja_se_observou"].startswith("Este quadro mostra o valor do momento"), g["id"])


class Pagina(unittest.TestCase):
    def test_avisos_obrigatorios(self):
        for t in ("Para estudo", "Material educativo", "Privacidade", "tradingview.com/privacy-policy", "by TradingView",
                  "Pular este quadro", "Você não precisa acompanhar isto durante o dia"):
            self.assertTrue(t in HTML or t in json.dumps(CFG, ensure_ascii=False), t)
        self.assertIn("Para estudo. Não use para operar.", CFG["faixa"]["texto"])

    def test_ticker_respeita_movimento_reduzido_e_tem_botao(self):
        self.assertIn("prefers-reduced-motion", HTML)
        self.assertIn("btn-ticker", HTML)
        self.assertIn("tempo-real-ticker", HTML)

    def test_widgets_so_de_dominio_do_tradingview(self):
        hosts = set(re.findall(r"https://([a-z0-9.\-]+)/", HTML))
        self.assertTrue(hosts <= {"s3.tradingview.com", "www.tradingview.com", "github.com"}, hosts)

    def test_nenhum_script_le_valores_do_widget(self):
        self.assertNotIn("contentDocument", HTML)
        self.assertNotIn("postMessage", HTML)

    def test_iframe_com_titulo_no_contentor(self):
        self.assertIn("cont.title", HTML)

    def test_usa_prefixo_proprio_de_armazenamento(self):
        for k in re.findall(r'(?:guardar|ler)\("([^"]+)"', HTML):
            self.assertTrue(k.startswith("tempo-real-"), k)


if __name__ == "__main__":
    unittest.main()
