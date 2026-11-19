// Executa a página Cotações do BESST em jsdom, com fetch simulado. Rodar: npm i --no-save jsdom && node --test tests/pagina.test.js
const test = require("node:test"), assert = require("node:assert/strict"), fs = require("fs"), path = require("path");
let JSDOM; try { ({JSDOM} = require("jsdom")); } catch (e) { console.log("jsdom ausente: teste ignorado"); process.exit(0); }
const R = path.join(__dirname, "..");
const html = fs.readFileSync(path.join(R, "carteiras/besst-cotacoes/index.html"), "utf8");
const ordemJs = fs.readFileSync(path.join(R, "carteiras/besst-cotacoes/ordem.js"), "utf8");
const cfg0 = JSON.parse(fs.readFileSync(path.join(R, "carteiras/besst-cotacoes/conjuntos.json"), "utf8"));
const painel0 = JSON.parse(fs.readFileSync(path.join(R, "dados/besst/painel.json"), "utf8"));
const clone = (x) => JSON.parse(JSON.stringify(x));

async function abrir({painel = painel0, aprovar = false, query = "?setor=energia&modo=avancado", agora} = {}) {
  const cfg = clone(cfg0); cfg.matriz_teste.simbolos_aprovados = []; if (aprovar) cfg.matriz_teste.simbolos_aprovados = painel.papeis.map(p => p.ticker).filter(Boolean).filter(t => typeof t === "string");
  const erros = [];
  const dom = new JSDOM(html, {url: "https://x.test/carteiras/besst-cotacoes/" + query, runScripts: "dangerously", pretendToBeVisual: true,
    beforeParse(w) {
      w.fetch = (u) => Promise.resolve({ok: true, json: () => Promise.resolve(clone(u.includes("painel.json") ? painel : cfg))});
      w.matchMedia = () => ({matches: false}); w.eval(ordemJs);
      if (agora) { const D = w.Date; w.Date = class extends D { constructor(...a) { super(...(a.length ? a : [agora])); } static now() { return agora; } }; }
      w.addEventListener("error", (e) => erros.push(e.message));
    }});
  await new Promise(r => setTimeout(r, 300));
  return {w: dom.window, d: dom.window.document, erros, fechar: () => dom.window.close()};
}
const widgets = (d) => [...d.querySelectorAll("script")].filter(s => /tradingview/.test(s.src));

test("carga só por clique: nenhum script do TradingView antes; um com ≤ 8 símbolos depois", async () => {
  const {d, erros, fechar} = await abrir({aprovar: true});
  assert.equal(erros.length, 0); assert.equal(widgets(d).length, 0);
  d.getElementById("btn-carregar").click();
  const ws = widgets(d); assert.equal(ws.length, 1);
  const cfg = JSON.parse(ws[0].textContent); assert.ok(cfg.symbolsGroups[0].symbols.length <= 8);
  assert.ok(cfg.symbolsGroups[0].symbols.every(s => s.name.startsWith("BMFBOVESPA:")));
  fechar();
});
test("sem matriz de teste não há botão nem widget", async () => {
  const {d, fechar} = await abrir({aprovar: false});
  assert.equal(d.getElementById("btn-carregar"), null); assert.equal(widgets(d).length, 0); assert.ok(d.querySelectorAll("tbody tr").length > 0); fechar();
});
test("paginação do Avançado: intervalo, botões e foco fora do body", async () => {
  const {d, fechar} = await abrir({aprovar: true});
  assert.match(d.querySelector(".pager .nota").textContent, /^1–8 de \d+/);
  assert.ok(d.getElementById("btn-ant").disabled);
  d.getElementById("btn-prox").click();
  assert.match(d.querySelector(".pager .nota").textContent, /^9–/);
  assert.notEqual(d.activeElement, d.body); assert.equal(widgets(d).length, 0, "trocar de página volta ao botão de carregar");
  fechar();
});
test("Iniciante: até 6 linhas, uma empresa por linha, corte explicado", async () => {
  const {d, fechar} = await abrir({query: "?setor=bancos&modo=iniciante"});
  const n = d.querySelectorAll("tbody tr").length; assert.ok(n <= 6 && n > 0);
  const emp = [...d.querySelectorAll("tbody tr td:first-of-type")].map(t => t.textContent); assert.equal(new Set(emp).size, emp.length);
  assert.match(d.getElementById("painel").textContent, /não aparecer aqui não significa pior nem melhor/); fechar();
});
test("XSS: dados com HTML não viram elementos", async () => {
  const p = clone(painel0), x = '<img src=x onerror="window.__pwn=1">';
  p.papeis.filter(a => a.setor === "Energia").forEach(a => { a.empresa = x; a.alertas_texto = [x]; a.controle = x; a.motivo_sem_teto = x; });
  p.gerado_em = x;
  for (const modo of ["iniciante", "avancado"]) {
    const {w, d, erros, fechar} = await abrir({painel: p, query: `?setor=energia&modo=${modo}&ordem=${encodeURIComponent(x)}`});
    d.querySelectorAll("details").forEach(e => (e.open = true));
    assert.equal(d.querySelectorAll("img").length, 0, modo); assert.equal(w.__pwn, undefined); assert.equal(erros.length, 0); fechar();
  }
});
test("painel malformado não derruba a página", async () => {
  const p = clone(painel0); p.pregao_referencia = null; p.gerado_em = {a: 1};
  p.papeis.forEach(a => { a.data = null; a.alertas = "constructor"; a.alertas_texto = "texto"; });
  p.papeis.push(null, {ticker: 5}, {ticker: "ZZZZ3", setor: "Bancos"});
  const {d, erros, fechar} = await abrir({painel: p});
  assert.equal(erros.length, 0); assert.doesNotMatch(d.getElementById("painel").textContent, /Erro ao montar/);
  assert.match(d.getElementById("status").textContent, /não pôde ser lida|alfabética/); fechar();
});
test("alerta chamado constructor não renderiza função", async () => {
  const p = clone(painel0); p.papeis.forEach(a => { a.alertas = ["constructor", "__proto__"]; });
  const {d, fechar} = await abrir({painel: p, query: "?setor=bancos&modo=iniciante"});
  assert.doesNotMatch(d.getElementById("painel").textContent, /native code/); fechar();
});
test("dados velhos: ordem alfabética e aviso", async () => {
  const {d, fechar} = await abrir({agora: Date.parse("2026-12-10T20:00:00Z")});
  assert.match(d.getElementById("status").textContent, /ordem passou a ser alfabética/);
  const t = [...d.querySelectorAll("tbody tr th a")].map(a => a.textContent); assert.deepEqual(t.slice(0, 8), t.slice(0, 8).slice().sort()); fechar();
});
test("carregamento automático guarda só chave com prefixo e monta ao abrir", async () => {
  const {w, d, fechar} = await abrir({aprovar: true});
  d.getElementById("btn-auto").click();
  assert.equal(w.localStorage.getItem("besst-cotacoes-auto"), "ligado"); assert.equal(widgets(d).length, 1);
  for (let i = 0; i < w.localStorage.length; i++) assert.ok(w.localStorage.key(i).startsWith("besst-cotacoes-")); fechar();
});
