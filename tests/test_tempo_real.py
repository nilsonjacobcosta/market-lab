"""Testes do painel Mercados em tempo real. Só biblioteca padrão, sem rede.
Verificam o conjuntos.json e o index.html: esquema, limites, símbolos testados, textos."""
import datetime as dt
import json
import os
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1] / "monitor" / "tempo-real"
CFG = json.loads((RAIZ / "conjuntos.json").read_text(encoding="utf-8"))
HTML = (RAIZ / "index.html").read_text(encoding="utf-8")
WIDGETS_PERMITIDOS = {"market_quotes"}
LIM_INICIANTE, LIM_TOTAL, LIM_SIMBOLOS = 4, 6, 8
PROIBIDAS = re.compile(r"\b(despenc\w*|dispar\w*|desab\w*|explod\w*|explos\w*|p[âa]nico|forte alta|forte queda|"
                       r"compre|compra agora|venda agora|recomendamos|garantid[oa]|sinal de compra|sinal de venda)\b", re.I)
DOCS_TESTE = "Estes testes são TEXTUAIS (JSON e HTML), não executam a página. A montagem dos widgets é conferida no Chrome do dono."
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

    def test_di_formato_do_codigo(self):
        for onde, s in self.usados():
            if s.startswith("BMFBOVESPA:DI1"):
                self.assertRegex(s, r"^BMFBOVESPA:DI1F20\d{2}$", f"{onde}: {s} fora do formato DI1FAAAA (janeiro, ano com 4 dígitos)")

    def test_di_so_com_vencimento_a_mais_de_90_dias(self):
        hoje = dt.date.today()
        # Em pull request só avisa: a data entra como entrada e não deve quebrar mudanças sem relação com o contrato.
        so_avisa = os.environ.get("GITHUB_EVENT_NAME") == "pull_request"
        for onde, s in self.usados():
            m = re.match(r"BMFBOVESPA:DI1F(\d{4})$", s)
            if m:
                dias = (dt.date(int(m.group(1)), 1, 1) - hoje).days
                if dias <= 90 and so_avisa:
                    print(f"::warning::{onde}: {s} vence em {dias} dias; trocar o contrato (RB 11)")
                    continue
                self.assertGreater(dias, 90, f"{onde}: {s} vence em {dias} dias; trocar o contrato (RB 11)")

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

    def test_ticker_testado_pelo_dono(self):
        self.assertIn("testado em 19/11/2026", CFG["matriz_teste"]["ticker_tape"])
        self.assertTrue(CFG["matriz_teste"]["teste_dono"]["data"])
        self.assertIn(CFG["ticker"]["padrao"], ("ligado", "desligado"))


class Textos(unittest.TestCase):
    def textos(self):
        for c, g in graficos():
            for k in ("titulo", "o_que_e", "como_ler", "ja_se_observou"):
                yield f"{g['id']}.{k}", g[k]
            for x in g["simbolos"]:
                yield f"{g['id']}.{x['s']}.rotulo", x["rotulo"]
                yield f"{g['id']}.{x['s']}.atraso", x["atraso"]
        for c in CFG["conjuntos"]:
            yield f"{c['id']}.nome", c["nome"]
            yield f"{c['id']}.nao_diz", c["nao_diz"]
            yield f"{c['id']}.subtitulo", c["subtitulo"]
        for k, v in CFG["glossario"].items():
            yield f"glossario.{k}.termo", v["termo"]
            yield f"glossario.{k}.definicao", v["definicao"]
        for x in CFG["ticker"]["simbolos"]:
            yield f"ticker.{x['proName']}", x["title"]
        yield "ticker.nota", CFG["ticker"]["nota"]
        yield "faixa", CFG["faixa"]["texto"]
        yield "legenda_cores", CFG["legenda_cores"]

    def test_sem_palavras_proibidas(self):
        for onde, t in self.textos():
            m = PROIBIDAS.search(t)
            self.assertIsNone(m, f"{onde}: '{m.group(0) if m else ''}'")

    def test_lista_proibida_pega_variantes_e_nao_pega_compreender(self):
        for ruim in ("o dólar despencou", "o índice disparou", "desabou", "Compre agora", "pânico", "forte queda"):
            self.assertIsNotNone(PROIBIDAS.search(ruim), ruim)
        for bom in ("Para compreender melhor", "compreensão do contrato"):
            self.assertIsNone(PROIBIDAS.search(bom), bom)

    PERMITIDOS = [r"\bDe 10% para 11%", r"\b1 ponto percentual\b", r"\b10% de aumento\b", r"\bDI1F\d{4}\b", r"\b(19|20)\d{2}\b", r"\b\d+ (dias|anos|ano)\b", r"\bS&P 500\b", r"\bNasdaq 100\b", r"\b1!",
                  r"\bH\.15\b", r"\bB3\b", r"\b(2|10)\b"]

    def test_nenhum_numero_de_cotacao_no_json(self):
        # R-TR4: texto estático não cita valor atual. Só passam anos, prazos, nomes de índice e o exemplo do glossário.
        for onde, t in self.textos():
            limpo = t
            for p in self.PERMITIDOS:
                limpo = re.sub(p, "", limpo)
            self.assertIsNone(re.search(r"\d", limpo), f"{onde}: dígito fora da lista permitida ({limpo!r})")
            self.assertIsNone(re.search(r"(R|US)?\$\s*\d", t), f"{onde}: valor monetário")

    def test_detector_de_numero_pega_exemplos_ruins(self):
        for ruim in ("subiu 14,5 pontos percentuais", "Ibovespa em 130 mil pontos", "dólar a 5 reais", "preço de 5000"):
            limpo = ruim
            for p in self.PERMITIDOS:
                limpo = re.sub(p, "", limpo)
            self.assertIsNotNone(re.search(r"\d", limpo), ruim)

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
            self.assertEqual(g["ja_se_observou"], "Ainda sem observação registrada neste painel.", g["id"])


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
        self.assertNotIn("http://", HTML)
        hosts = set(re.findall(r"https?://([a-z0-9.\-]+)", HTML))
        self.assertTrue(hosts <= {"s3.tradingview.com", "www.tradingview.com", "github.com"}, hosts)

    def test_so_dois_arquivos_de_widget_e_nenhum_de_analise_tecnica(self):
        arquivos = set(re.findall(r"embed-widget-[a-z\-]+\.js", HTML))
        self.assertEqual(arquivos, {"embed-widget-market-quotes.js", "embed-widget-ticker-tape.js"})
        for palavra in ("analys", "technical", "eval(", "document.write", "new Function", "<iframe"):
            self.assertNotIn(palavra, HTML, palavra)

    def test_movimento_reduzido_desliga_a_faixa(self):
        self.assertRegex(HTML, r"if \(reduz\(\)\) \{[^}]*btn\.hidden = true[^}]*return;")

    def test_todo_titulo_de_iframe_e_rotulado(self):
        self.assertEqual(len(re.findall(r"rotularIframe\(cont, [\"`]", HTML)), 2, "faixa e cartões devem rotular o iframe")

    def test_dados_do_json_passam_por_esc_nos_templates(self):
        # toda interpolação ${...} com dado do JSON dentro de template deve usar esc() ou ser número/ligação segura
        seguras = ("esc(", "n}", "altura", "i + 1", "WIDGETS", "listaAlternativa(", "htmlTermos(", "htmlTextos(", "atribuicao(",
                   "urlSimbolo(", "encodeURIComponent(", "\" selected\"", "blocos", "ts.map", "g.simbolos.map", "itens", "TV_BASE", "escape")
        for m in re.finditer(r"\$\{([^}]*)\}", HTML):
            linha = HTML[HTML.rfind("\n", 0, m.start()) + 1:HTML.find("\n", m.end())]
            if "setAttribute(" in linha or "rotularIframe(" in linha or "document.title" in linha:
                continue  # atributo ou propriedade de texto puro, não HTML
            e = m.group(1).strip()
            self.assertTrue(e in ("sel", "sel ? 0 : -1") or any(k in e for k in seguras), f"interpolação sem esc(): ${{{e}}}")

    def test_nenhum_script_le_valores_do_widget(self):
        self.assertNotIn("contentDocument", HTML)
        self.assertNotIn("postMessage", HTML)

    def test_iframe_com_titulo_e_contentor_rotulado(self):
        self.assertIn("f.title = titulo", HTML)

    def test_faixa_estatica_no_html_e_privacidade_sem_afirmar_cookies(self):
        self.assertIn("Para estudo. Não use para operar.", HTML)
        self.assertNotIn("não gravam cookies", HTML.lower())
        self.assertIn("Como usar este painel", HTML)

    def test_ticker_sem_cripto_e_com_legenda_de_cores(self):
        self.assertNotIn("BITSTAMP", json.dumps(CFG["ticker"]))
        self.assertIn("não significa bom nem ruim", CFG["ticker"]["nota"])
        self.assertIn("não significam bom nem ruim", CFG["legenda_cores"])

    def test_usa_prefixo_proprio_de_armazenamento(self):
        for k in re.findall(r'(?:guardar|ler)\("([^"]+)"', HTML):
            self.assertTrue(k.startswith("tempo-real-"), k)

    def test_widgets_nao_sao_transparentes(self):
        # Com isTransparent: true o widget sai com fundo branco em página escura (visto no Chrome em 20/11/2026).
        self.assertNotIn("isTransparent: true", HTML)
        self.assertGreaterEqual(HTML.count("isTransparent: false"), 2)

    def test_tema_segue_o_sistema(self):
        self.assertIn("prefers-color-scheme: dark", HTML)
        self.assertNotIn('colorTheme: "dark"', HTML)
        self.assertEqual(HTML.count("colorTheme: temaSistema()"), 2)

    def test_cores_so_nas_variaveis(self):
        css = HTML[HTML.index("<style>"):HTML.index("</style>")]
        fora = re.sub(r":root\{[^}]*\}", "", css)
        fora = re.sub(r"@media \(prefers-color-scheme: dark\)\{\}", "", fora)
        self.assertEqual(re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)", fora), [])


if __name__ == "__main__":
    unittest.main()
