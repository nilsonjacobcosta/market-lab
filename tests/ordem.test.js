// Testes da ordem de leitura do Cotações do BESST. Rodar: node --test tests/ordem.test.js
const test = require("node:test"), assert = require("node:assert/strict"), fs = require("fs"), path = require("path");
const O = require("../carteiras/besst-cotacoes/ordem.js");
const P = (o) => Object.assign({ticker: "XXXX3", empresa: "X", setor: "Bancos", preco: 10, status_robusto: "acima_teto", margem_robusta: -5, liquidez_mil: 1000,
  nivel_alerta: "ok", baixa_liquidez: false, preco_teto_robusto: 9}, o);
const painelReal = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "dados", "besst", "painel.json"), "utf8"));

test("abaixo do teto vem antes de acima; liquidez decrescente; empate por ticker", () => {
  const r = O.ordenar([P({ticker: "B3", status_robusto: "acima_teto", liquidez_mil: 9000}), P({ticker: "A4", status_robusto: "abaixo_teto", liquidez_mil: 10}),
    P({ticker: "A3", status_robusto: "abaixo_teto", liquidez_mil: 10}), P({ticker: "A5", status_robusto: "abaixo_teto", liquidez_mil: 500})]);
  assert.deepEqual(r.principal.map(i => i.p.ticker), ["A5", "A3", "A4", "B3"]);
});
test("abaixo_teto_conferir não vem à frente", () => {
  const r = O.ordenar([P({ticker: "C3", status_robusto: "abaixo_teto_conferir", liquidez_mil: 99999}), P({ticker: "A3", status_robusto: "abaixo_teto", liquidez_mil: 1})]);
  assert.deepEqual(r.principal.map(i => i.p.ticker), ["A3", "C3"]);
});
test("exclusões: grave, baixa liquidez, sem preço, sem teto, sem liquidez, status especiais", () => {
  const casos = [["alerta_grave", {nivel_alerta: "grave"}], ["baixa_liquidez", {baixa_liquidez: true, status_robusto: "abaixo_teto"}], ["sem_cotacao", {preco: null}],
    ["sem_teto", {preco_teto_robusto: null}], ["sem_liquidez", {liquidez_mil: null}], ["sem_proventos", {status_robusto: "sem_proventos"}],
    ["historico_curto", {status_robusto: "historico_curto"}], ["nao_se_aplica", {status_robusto: "nao_se_aplica"}]];
  for (const [motivo, o] of casos) { const c = O.classificar(P(o)); assert.equal(c.grupo, "fora", motivo); assert.equal(c.motivo, motivo); }
  assert.equal(O.classificar(P({preco: null, status: "sem_cotacao"})).motivo, "sem_cotacao");
});
test("nulos não quebram a ordenação", () => {
  const r = O.ordenar([P({ticker: "N3", liquidez_mil: null}), P({ticker: "M3", margem_robusta: null}), P({ticker: "L3", liquidez_mil: undefined})]);
  assert.equal(r.fora.length, 2); assert.equal(r.principal.length, 1);
});
test("partição completa e sem duplicados", () => {
  const r = O.ordenar(painelReal.papeis), ts = [...r.principal, ...r.fora].map(i => i.p.ticker);
  assert.equal(ts.length, painelReal.papeis.length); assert.equal(new Set(ts).size, ts.length);
});
test("resultado idêntico com a entrada embaralhada (propriedade)", () => {
  const base = JSON.stringify(O.ordenar(painelReal.papeis).principal.map(i => i.p.ticker));
  let seed = 7; const rnd = () => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
  for (let k = 0; k < 20; k++) {
    const a = painelReal.papeis.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    assert.equal(JSON.stringify(O.ordenar(a).principal.map(i => i.p.ticker)), base);
  }
});
test("invariantes sobre o painel.json real", () => {
  const r = O.ordenar(painelReal.papeis); let ultimoGrupo = 0, ultima = Infinity;
  for (const i of r.principal) {
    assert.notEqual(i.p.nivel_alerta, "grave"); assert.notEqual(i.p.baixa_liquidez, true); assert.notEqual(i.p.preco_teto_robusto, null);
    const g = i.grupo === "abaixo" ? 0 : 1; assert.ok(g >= ultimoGrupo, "abaixo antes de acima");
    if (g !== ultimoGrupo) { ultimoGrupo = g; ultima = Infinity; }
    assert.ok(i.p.liquidez_mil <= ultima, "liquidez não crescente"); ultima = i.p.liquidez_mil;
  }
});
test("um por empresa mantém o de maior liquidez e a ordem", () => {
  const r = O.ordenar([P({ticker: "A3", empresa: "A", liquidez_mil: 5}), P({ticker: "A4", empresa: "A", liquidez_mil: 50}), P({ticker: "B3", empresa: "B", liquidez_mil: 20})]);
  assert.deepEqual(O.umPorEmpresa(r.principal).map(i => i.p.ticker), ["A4", "B3"]);
});
test("páginas de 8", () => { assert.deepEqual(O.paginas(Array.from({length: 19}, (_, i) => i)).map(p => p.length), [8, 8, 3]); });
test("faixas de margem", () => {
  assert.equal(O.faixa(P({margem_robusta: 45})), "mais30"); assert.equal(O.faixa(P({margem_robusta: 30})), "mais30"); assert.equal(O.faixa(P({margem_robusta: 29.9})), "10a30");
  assert.equal(O.faixa(P({margem_robusta: 9.9})), "ate10"); assert.equal(O.faixa(P({margem_robusta: -0.1})), "acima");
  assert.equal(O.faixa(P({margem_robusta: null})), "sem_margem"); assert.equal(O.faixa(P({status_robusto: "abaixo_teto_conferir"})), "conferir");
});
test("validação do painel", () => {
  assert.equal(O.validar(null).ok, false); assert.equal(O.validar({papeis: "x"}).ok, false); assert.equal(O.validar({papeis: [{ticker: "A3"}]}).ok, false);
  assert.equal(O.validar({papeis: [{ticker: "A3", setor: "Bancos"}, null, {setor: "x"}]}).papeis.length, 1);
});
test("calendário de pregões", () => {
  const utc = (s, h) => Date.parse(`${s}T${h}:00Z`);
  assert.equal(O.ehPregao("2026-11-20"), false); assert.equal(O.ehPregao("2026-11-21"), false); assert.equal(O.ehPregao("2026-11-19"), true);
  assert.equal(O.pregaoAnterior("2026-11-23"), "2026-11-19");
  assert.equal(O.pregaoEsperado(utc("2026-11-19", "20:00")), "2026-11-18"); /* 17h BRT: ainda sem fechamento */
  assert.equal(O.pregaoEsperado(utc("2026-11-19", "02:00").valueOf() + 24 * 36e5), "2026-11-19"); /* 23h BRT do dia 19 */
  assert.equal(O.situacao("2026-11-18", utc("2026-11-19", "20:00")).estado, "ok");
  assert.equal(O.situacao("2026-11-17", utc("2026-11-19", "20:00")).estado, "atrasado");
  assert.equal(O.situacao("2026-11-10", utc("2026-11-19", "20:00")).estado, "muito_atrasado");
  assert.equal(O.situacao("lixo", Date.now()).estado, "invalido"); assert.equal(O.situacao(null, Date.now()).estado, "invalido");
  assert.equal(O.situacao("2026-11-19", utc("2026-11-23", "12:00")).atraso, 0); /* 20/11 feriado e fim de semana não contam */
  assert.equal(O.situacao("2026-11-18", utc("2026-11-23", "12:00")).atraso, 1);
});
test("feriados iguais aos do Monitor BESST", () => {
  const h = fs.readFileSync(path.join(__dirname, "..", "carteiras", "monitor-besst", "index.html"), "utf8");
  const m = h.match(/const FERIADOS=new Set\(\[([^\]]*)\]/s), lista = m[1].match(/\d{4}-\d{2}-\d{2}/g);
  assert.deepEqual([...O.FERIADOS].sort(), [...lista].sort());
});
test("data predominante usa a data mais frequente, não a mais recente", () => {
  const l = [P({data: "2026-11-17"}), P({data: "2026-11-17"}), P({data: "2026-11-19"}), P({data: "2026-09-22"}), P({data: "2026-11-17", preco: null})];
  assert.equal(O.dataPredominante(l), "2026-11-17"); assert.equal(O.dataPredominante([]), null); assert.equal(O.dataPredominante([P({data: "lixo"})]), null);
  assert.equal(O.dataPredominante([P({data: "2026-11-17"}), P({data: "2026-11-19"})]), "2026-11-19"); /* empate: a mais recente */
});
test("constantes de segurança", () => { assert.equal(O.LIM_PAGINA, 8); assert.ok(O.LIM_IFRAMES <= 3); });
