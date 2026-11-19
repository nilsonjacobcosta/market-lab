"""Testes da página Cotações do BESST. Só biblioteca padrão, sem rede.
São TEXTUAIS (JSON, HTML e JS): não executam a página. A montagem dos widgets é conferida no Chrome do dono.
A ordem é testada em tests/ordem.test.js (node --test)."""
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAIZ = REPO / "carteiras" / "besst-cotacoes"
CFG = json.loads((RAIZ / "conjuntos.json").read_text(encoding="utf-8"))
HTML = (RAIZ / "index.html").read_text(encoding="utf-8")
ORDEM = (RAIZ / "ordem.js").read_text(encoding="utf-8")
TESTE = (RAIZ / "teste-simbolos.html").read_text(encoding="utf-8")
PAINEL = json.loads((REPO / "dados" / "besst" / "painel.json").read_text(encoding="utf-8"))
PROIBIDAS = re.compile(r"\b(barata\w*|oportunidade\w*|melhores|top|destaque\w*|desconto\w*|compre|compra agora|venda agora|"
                       r"recomendad[oa]s?|recomendamos|garantid[oa]|sinal de compra|despenc\w*|dispar\w*|desab\w*|p[âa]nico)\b", re.I)
SETORES = ["Bancos", "Energia", "Seguros", "Saneamento", "Telecomunicações"]
FAIXAS = {"mais30", "10a30", "ate10", "acima", "conferir", "sem_margem"}
MOTIVOS = {"sem_cotacao", "alerta_grave", "baixa_liquidez", "sem_liquidez", "sem_proventos", "historico_curto", "nao_se_aplica", "sem_teto", "outro"}


def visivel(html):
    h = re.sub(r"<style.*?</style>", " ", html, flags=re.S)
    h = re.sub(r"<script.*?</script>", " ", h, flags=re.S)
    return re.sub(r"<[^>]+>", " ", h)


def textos_json():
    def andar(x, caminho):
        if isinstance(x, str):
            yield caminho, x
        elif isinstance(x, dict):
            for k, v in x.items():
                yield from andar(v, f"{caminho}.{k}")
        elif isinstance(x, list):
            for i, v in enumerate(x):
                yield from andar(v, f"{caminho}[{i}]")
    cfg = {k: v for k, v in CFG.items() if k not in ("matriz_teste", "tradingview")}
    yield from andar(cfg, "cfg")


class Esquema(unittest.TestCase):
    def test_cinco_setores_com_campos(self):
        self.assertEqual([s["setor"] for s in CFG["setores"]], SETORES)
        ids = [s["id"] for s in CFG["setores"]]
        self.assertEqual(len(set(ids)), 5)
        for s in CFG["setores"]:
            for k in ("id", "nome", "setor", "o_que_e", "como_ler", "nao_diz"):
                self.assertTrue(s.get(k), f"{s.get('id')}: falta {k}")
            self.assertGreater(len(s["nao_diz"]), 40, s["id"])

    def test_limites(self):
        l = CFG["limites"]
        self.assertEqual(l["pagina"], 8)
        self.assertLessEqual(l["iniciante_max"], 6)
        self.assertLessEqual(l["iframes_max"], 3)
        self.assertEqual(l["iframes_max"], int(re.search(r"LIM_IFRAMES = (\d+)", ORDEM).group(1)))
        self.assertEqual(l["pagina"], int(re.search(r"LIM_PAGINA = (\d+)", ORDEM).group(1)))

    def test_faixas_e_motivos_cobrem_o_codigo(self):
        self.assertEqual(set(CFG["faixas"]), FAIXAS)
        self.assertEqual(set(CFG["motivos_fora"]), MOTIVOS)
        for k in FAIXAS:
            self.assertIn(f'"{k}"', ORDEM)
        for k in MOTIVOS - {"outro"}:
            self.assertIn(f'"{k}"', ORDEM)

    def test_glossario_obrigatorio(self):
        for k in ("preco_teto", "bazin", "margem", "faixa", "liquidez", "conferir", "atrasada", "controle", "unit", "b3"):
            self.assertIn(k, CFG["glossario"])
            self.assertTrue(CFG["glossario"][k]["definicao"])

    def test_painel_real_tem_os_campos_usados(self):
        com_preco = [p for p in PAINEL["papeis"] if p.get("preco") is not None]
        self.assertGreater(len(com_preco), 50)
        for p in com_preco:
            for k in ("ticker", "setor", "empresa", "liquidez_mil", "status_robusto", "nivel_alerta", "baixa_liquidez"):
                self.assertIn(k, p, f"{p.get('ticker')}: falta {k}")
            self.assertIn(p["setor"], SETORES)
        for k in ("pregao_referencia", "gerado_em", "fase"):
            self.assertIn(k, PAINEL)


class Simbolos(unittest.TestCase):
    def test_matriz_coerente(self):
        m = CFG["matriz_teste"]
        ok, rep = m["simbolos_aprovados"], m["reprovados"]
        self.assertEqual(len(ok), len(set(ok)))
        self.assertFalse(set(ok) & set(rep), "símbolo aprovado e reprovado ao mesmo tempo")
        if ok or rep:
            self.assertTrue(m["data_teste"], "matriz com símbolos exige data_teste")
        tickers = {p["ticker"] for p in PAINEL["papeis"]}
        for t in ok + rep:
            self.assertRegex(t, r"^[A-Z]{4}\d{1,2}$")
            if t not in tickers:
                print(f"::warning::{t} está na matriz mas não está mais no painel.json (RB 12)")

    def test_prefixo_da_b3(self):
        self.assertEqual(CFG["tradingview"]["prefixo"], "BMFBOVESPA:")
        self.assertIn("atrasad", CFG["tradingview"]["atraso"].lower())

    def test_aviso_de_papel_com_cotacao_sem_teste(self):
        # Não falha: o universo muda todo dia. A página só monta widget de papel aprovado (RB 12).
        testados = set(CFG["matriz_teste"]["simbolos_aprovados"]) | set(CFG["matriz_teste"]["reprovados"])
        sem = sorted(p["ticker"] for p in PAINEL["papeis"] if p.get("preco") is not None and p["ticker"] not in testados)
        if sem:
            print(f"::warning::{len(sem)} papéis com cotação sem teste no widget (ficam só na tabela): {', '.join(sem[:12])}…")

    def test_pagina_so_monta_widget_de_papel_aprovado(self):
        self.assertIn("const aprovado = (t) =>", HTML)
        self.assertIn("itens.filter(it => aprovado(it.p.ticker))", HTML)
        self.assertIn("simbolos_aprovados", HTML)
        self.assertIn("reprovados", HTML)


class Textos(unittest.TestCase):
    PERMITIDOS = [r"\b5 anos\b", r"\b6%", r"\b0,06\b", r"R\$ 500 mil", r"\b(10|30)%", r"\bB3\b", r"\bterminados em 11\b", r"\bat[ée] 5\b"]

    def test_sem_palavras_proibidas_no_json_e_no_html(self):
        for onde, t in textos_json():
            m = PROIBIDAS.search(t)
            self.assertIsNone(m, f"{onde}: '{m.group(0) if m else ''}'")
        m = PROIBIDAS.search(visivel(HTML))
        self.assertIsNone(m, f"HTML: '{m.group(0) if m else ''}'")

    def test_lista_proibida_pega_variantes_e_nao_pega_compreender(self):
        for ruim in ("as melhores ações", "top 10", "em destaque", "com desconto", "ação barata", "uma oportunidade", "Compre agora", "recomendada"):
            self.assertIsNotNone(PROIBIDAS.search(ruim), ruim)
        for bom in ("Para compreender melhor", "compreensão do critério", "estoque"):
            self.assertIsNone(PROIBIDAS.search(bom), bom)

    def test_nenhum_numero_de_cotacao_nos_textos(self):
        # R-B5: nada de preço ou margem escritos à mão; só prazos, taxa do método e limites explicados.
        for onde, t in textos_json():
            limpo = t
            for p in self.PERMITIDOS:
                limpo = re.sub(p, "", limpo)
            self.assertIsNone(re.search(r"\d", limpo), f"{onde}: dígito fora da lista permitida ({limpo!r})")
        self.assertIsNone(re.search(r"R\$\s*\d", visivel(HTML)), "valor monetário escrito à mão no HTML")

    def test_detector_pega_exemplos_ruins(self):
        for ruim in ("BBAS3 a 14,62", "margem de 45%", "dólar a 5 reais"):
            limpo = ruim
            for p in self.PERMITIDOS:
                limpo = re.sub(p, "", limpo)
            self.assertIsNotNone(re.search(r"\d", limpo), ruim)

    def test_regras_de_redacao(self):
        self.assertIn("Não é recomendação de investimento", CFG["aviso_fixo"])
        self.assertIn("proventos passados, que podem não se repetir", CFG["aviso_fixo"])
        self.assertIn("critério matemático", CFG["aviso_fixo"])
        self.assertIn("A ordem não indica qualidade, risco nem preço justo", CFG["ordem_texto"])
        self.assertIn("igual para todos", CFG["ordem_texto"])
        self.assertIn("Bazin", CFG["formula"])
        self.assertIn("fechamento", CFG["formula"])
        self.assertIn("pode estar em outro nível", CFG["nao_diz_geral"])

    def test_nao_diz_visivel_antes_das_listas(self):
        self.assertLess(HTML.index("O que esta página não diz"), HTML.index('id="painel"'))
        self.assertIn("O que este setor não diz", HTML)

    def test_sem_afirmacao_de_quem_e_o_autor(self):
        # Decisão do dono (19/11/2026): a página não faz declaração pessoal; reforça que é didática.
        for t in ("trabalho", "meu empregador", "Banco do Brasil", "bb.com.br"):
            self.assertNotIn(t, HTML + json.dumps(CFG, ensure_ascii=False), t)
        self.assertIn("Página didática", HTML)


class Pagina(unittest.TestCase):
    def test_avisos_obrigatorios(self):
        for t in ("Para estudo. Não use para operar.", "Material educativo", "Privacidade", "tradingview.com/privacy-policy", "by TradingView",
                  "Não é recomendação de investimento", "Glossário"):
            self.assertIn(t, HTML, t)

    def test_privacidade_antes_do_primeiro_widget_e_carga_so_por_clique(self):
        self.assertRegex(HTML, r'<h2 id="h-priv"[^>]*>Privacidade</h2>')
        self.assertLess(HTML.index('id="h-priv"'), HTML.index('id="painel"'))
        self.assertIn("só carregam depois que você clicar", HTML)
        self.assertIn('estado.auto = ler("besst-cotacoes-auto") === "ligado"', HTML)  # padrão desligado
        chamadas = re.findall(r"montarWidget\(", HTML)
        self.assertEqual(len(chamadas), 3, "definição, carregamento automático e clique")
        self.assertIn('b.addEventListener("click", () => { b.remove(); montarWidget(', HTML)
        self.assertIn("} else if (estado.auto) {", HTML)

    def test_widgets_so_de_dominio_do_tradingview_e_um_arquivo(self):
        self.assertNotIn("http://", HTML)
        hosts = set(re.findall(r"https?://([a-z0-9.\-]+)", HTML))
        self.assertTrue(hosts <= {"s3.tradingview.com", "www.tradingview.com", "github.com"}, hosts)
        self.assertEqual(set(re.findall(r"embed-widget-[a-z\-]+\.js", HTML)), {"embed-widget-market-quotes.js"})
        for palavra in ("analys", "technical", "eval(", "document.write", "new Function", "<iframe", "ticker-tape"):
            self.assertNotIn(palavra, HTML, palavra)

    def test_dados_so_do_proprio_repositorio(self):
        urls = set(re.findall(r'(?:PAINEL_URL|CONJ_URL) = "([^"]+)"', HTML))
        self.assertEqual(urls, {"./conjuntos.json", "../../dados/besst/painel.json"})
        self.assertIn('<script src="ordem.js"></script>', HTML)

    def test_nenhum_script_le_valores_do_widget(self):
        for arq in (HTML, TESTE, ORDEM):
            self.assertNotIn("contentDocument", arq)
            self.assertNotIn("postMessage", arq)
            self.assertNotIn("contentWindow", arq)

    def test_titulo_de_iframe_e_limite(self):
        self.assertEqual(len(re.findall(r"rotularIframe\(cont, [\"`]", HTML)), 1)
        self.assertIn("f.title = titulo", HTML)
        self.assertIn("document.querySelectorAll(\"#painel iframe\").length >= O.LIM_IFRAMES", HTML)

    def test_tabela_acessivel_e_abas(self):
        for t in ("<caption", 'scope="col"', 'scope="row"', 'role="tablist"', 'role="tabpanel"', 'aria-live="status"' if False else "role=\"status\""):
            self.assertIn(t, HTML, t)
        self.assertIn("<noscript>", HTML)
        self.assertIn("alertas_texto", HTML)  # alerta de cada papel visível, inclusive no Iniciante

    # Expressões de ${...} que não precisam de esc(): números, textos fixos ou HTML já montado com esc().
    EXATAS = {"abaixo", "abaixoFora", "cab", "comTeste.length", "fase", "fora.length", "li", "linhas", "pager", "resumo", "s.nome", "sel",
              "sem", "titulo", "total", "estado.carregadoEm", "sel ? 0 : -1"}
    SEGURAS = ("esc(", "fmt1(", "fmtInt(", "dbr(", "dcurta(", "s.slice(", "encodeURIComponent(", "htmlAlerta(", "htmlFora(", "htmlTabela(",
               "estado.auto ?", "estado.cfg.limites", "pg ", "itens.length", "i + 1", "sit.atraso", '" selected"', '" disabled"')

    def test_dados_do_json_passam_por_esc(self):
        for m in re.finditer(r"\$\{([^}]*)\}", HTML):
            e = m.group(1).strip()
            self.assertTrue(e in self.EXATAS or any(k in e for k in self.SEGURAS), f"interpolação sem esc(): ${{{e}}}")

    def test_detector_de_esc_pega_dado_cru(self):
        for ruim in ("p.empresa", "p.alertas_texto.join(' ')", "it.p.ticker", "s.o_que_e"):
            self.assertFalse(ruim in self.EXATAS or any(k in ruim for k in self.SEGURAS), ruim)

    def test_datas_em_html_sempre_com_esc_e_status_em_texto_puro(self):
        for m in re.finditer(r"(?<!esc\()\b(dbr|dcurta)\(", HTML):
            linha = HTML[HTML.rfind("\n", 0, m.start()) + 1:HTML.find("\n", m.end())]
            self.assertTrue(linha.startswith(("const dbr", "const dcurta", "  const ref8", "  let t = ")), f"data sem esc(): {linha[:80]}")
        self.assertIn("el.textContent = t", HTML)
        self.assertNotIn("el.innerHTML = t", HTML)

    def test_innerhtml_nao_recebe_dado_cru(self):
        for m in re.finditer(r"innerHTML = ([^;]*);", HTML):
            e = m.group(1)
            if "`" not in e and "'" not in e and '"' not in e:
                self.assertIn("map(", e, f"innerHTML com expressão sem template: {e[:60]}")

    def test_prefixo_proprio_de_armazenamento(self):
        chaves = re.findall(r'(?:guardar|ler)\("([^"]+)"', HTML)
        self.assertTrue(chaves)
        for k in chaves:
            self.assertTrue(k.startswith("besst-cotacoes-"), k)

    def test_ordem_nao_depende_de_widget_nem_relogio(self):
        for proibido in ("document", "window", "Date.now", "localeCompare", "Math.random", "fetch("):
            self.assertNotIn(proibido, ORDEM, proibido)

    def test_ordem_alfabetica_por_seletor_e_plano_b(self):
        for t in ('data-ordem="alfabetica"', "muito_atrasado", "invalido"):
            self.assertIn(t, HTML, t)

    def test_teste_de_simbolos_em_lotes(self):
        self.assertIn("ativos.length > 3", TESTE)
        self.assertIn("BMFBOVESPA:", TESTE)
        self.assertNotIn("<iframe", TESTE)


if __name__ == "__main__":
    unittest.main()
