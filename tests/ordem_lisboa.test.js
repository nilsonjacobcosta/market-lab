// Testes da ordem de leitura do Cotações Dividendos Lisboa.
// Rodar com: node --test tests/ordem_lisboa.test.js
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const O = require("../carteiras/cotacoes-dividendos-lisboa/ordem.js");

const RAIZ = path.join(__dirname, "..");
const painel = JSON.parse(fs.readFileSync(path.join(RAIZ, "dados/portugal/painel.json"), "utf8"));
const conj = JSON.parse(fs.readFileSync(path.join(RAIZ, "carteiras/cotacoes-dividendos-lisboa/conjuntos.json"), "utf8"));

const base = (over) => Object.assign({papel: "XXX", grupo: "nucleo", status: "abaixo", preco: 10, teto_robusto: 12, liquidez_mediana_12m_eur: 1e6, data_preco: "2026-11-20", alertas: []}, over);

test("painel real valida e tem 30 linhas, 16 no núcleo", () => {
  const v = O.validar(painel);
  assert.equal(v.ok, true);
  assert.equal(v.linhas.length, 30);
  assert.equal(v.linhas.filter(l => l.grupo === "nucleo").length, 16);
});

test("papel com teto e preço abaixo vai ao grupo abaixo", () => {
  assert.deepEqual(O.classificar(base({})), {grupo: "abaixo", motivo: null});
});

test("abaixo_conferir e acima ficam depois do grupo abaixo", () => {
  assert.equal(O.classificar(base({status: "abaixo_conferir"})).grupo, "acima");
  assert.equal(O.classificar(base({status: "acima"})).grupo, "acima");
});

test("em_cadastro, sem_proventos, sem preço e sem teto ficam fora, com motivo", () => {
  assert.equal(O.classificar(base({status: "em_cadastro", teto_robusto: null})).motivo, "em_cadastro");
  assert.equal(O.classificar(base({status: "sem_proventos", teto_robusto: null})).motivo, "sem_proventos");
  assert.equal(O.classificar(base({preco: null})).motivo, "sem_cotacao");
  assert.equal(O.classificar(base({status: "abaixo", teto_robusto: null})).motivo, "sem_teto");
});

test("margem robusta: positiva quando o teto está acima do preço", () => {
  assert.equal(O.margemRobusta(base({preco: 10, teto_robusto: 12})), 20);
  assert.equal(O.margemRobusta(base({preco: 10, teto_robusto: 9})), -10);
  assert.equal(O.margemRobusta(base({preco: 0, teto_robusto: 9})), null);
});

test("faixas de margem", () => {
  assert.equal(O.faixa(base({status: "abaixo_conferir"})), "conferir");
  assert.equal(O.faixa(base({preco: 10, teto_robusto: 9})), "acima");
  assert.equal(O.faixa(base({preco: 10, teto_robusto: 10.5})), "ate10");
  assert.equal(O.faixa(base({preco: 10, teto_robusto: 12})), "10a30");
  assert.equal(O.faixa(base({preco: 10, teto_robusto: 14})), "mais30");
});

test("ordem: abaixo primeiro, depois por liquidez decrescente e ticker", () => {
  const linhas = [
    base({papel: "B", status: "acima", liquidez_mediana_12m_eur: 5e6}),
    base({papel: "A", status: "abaixo", liquidez_mediana_12m_eur: 1e6}),
    base({papel: "C", status: "abaixo", liquidez_mediana_12m_eur: 3e6}),
    base({papel: "D", status: "abaixo", liquidez_mediana_12m_eur: 3e6}),
  ];
  const r = O.ordenar(linhas, "nucleo");
  assert.deepEqual(r.principal.map(i => i.l.papel), ["C", "D", "A", "B"]);
});

test("grupo: só o grupo pedido entra na lista principal", () => {
  const r = O.ordenar(O.validar(painel).linhas, "observacao");
  assert.ok(r.principal.concat(r.fora).every(i => i.l.grupo === "observacao"));
  assert.equal(r.principal.length + r.fora.length, 14);
});

test("alfabética ordena por papel sem depender da ordem de entrada", () => {
  const itens = [{l: {papel: "ZZZ"}}, {l: {papel: "AAA"}}];
  assert.deepEqual(O.alfabetica(itens).map(i => i.l.papel), ["AAA", "ZZZ"]);
});

test("modo Iniciante corta em 6 e páginas do Avançado têm até 8", () => {
  assert.equal(O.iniciante(new Array(16).fill(0), 6).length, 6);
  assert.deepEqual(O.paginas(new Array(17).fill(0), 8).map(p => p.length), [8, 8, 1]);
});

test("validar descarta linha sem papel ou grupo inválido", () => {
  const v = O.validar({linhas: [{papel: "", grupo: "nucleo"}, {papel: "X", grupo: "outro"}, {papel: "Y", grupo: "nucleo"}]});
  assert.equal(v.linhas.length, 1);
  assert.equal(O.validar({}).ok, false);
});

test("data predominante e defasados com o painel real", () => {
  assert.equal(O.dataPredominante(painel.linhas), "2026-11-20");
  assert.ok(O.defasados(painel.linhas, painel.fecho_esperado) >= 0);
  assert.equal(O.defasados([base({data_preco: "2026-11-18"})], "2026-11-20"), 1);
});

test("textos: grupos e motivos definidos na configuração", () => {
  assert.deepEqual(conj.grupos.map(g => g.id), ["nucleo", "observacao"]);
  for (const m of ["sem_cotacao", "em_cadastro", "sem_proventos", "sem_teto", "outro"]) assert.ok(conj.motivos_fora[m], m);
  assert.equal(conj.tradingview.prefixo, "EURONEXT:");
});

test("símbolos aprovados existem no painel", () => {
  const papeis = new Set(painel.linhas.map(l => l.papel));
  for (const s of conj.matriz_teste.simbolos_aprovados) assert.ok(papeis.has(s), s);
});
