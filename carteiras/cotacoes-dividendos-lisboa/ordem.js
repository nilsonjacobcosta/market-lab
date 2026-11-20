/* Ordem de leitura do Cotações Dividendos Lisboa. Função pura: sem DOM, sem relógio e sem comparação por idioma.
   Usada pela página e testada com `node --test tests/ordem_lisboa.test.js`.
   Espelha carteiras/besst-cotacoes/ordem.js, com os campos do dados/portugal/painel.json. */
(function (root) {
  "use strict";
  const LIM_PAGINA = 8;      /* símbolos por widget */
  const LIM_IFRAMES = 2;     /* teto de segurança de iframes ativos */
  const INICIANTE_MAX = 6;   /* papéis por grupo no modo Iniciante */
  const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
  const num = (x) => (typeof x === "number" && isFinite(x) ? x : null);

  /* Devolve {grupo: "abaixo"|"acima"|"fora", motivo} para um papel. Exclusões primeiro. */
  function classificar(l) {
    if (num(l.preco) === null) return {grupo: "fora", motivo: "sem_cotacao"};
    if (l.status === "em_cadastro") return {grupo: "fora", motivo: "em_cadastro"};
    if (l.status === "sem_proventos") return {grupo: "fora", motivo: "sem_proventos"};
    if (num(l.teto_robusto) === null) return {grupo: "fora", motivo: "sem_teto"};
    if (l.status === "abaixo") return {grupo: "abaixo", motivo: null};
    if (l.status === "abaixo_conferir" || l.status === "acima") return {grupo: "acima", motivo: null};
    return {grupo: "fora", motivo: "outro"};
  }

  /* Margem em relação ao teto robusto, em % do preço: positiva = preço abaixo do teto. */
  function margemRobusta(l) {
    if (num(l.preco) === null || num(l.teto_robusto) === null || l.preco <= 0) return null;
    return ((l.teto_robusto - l.preco) / l.preco) * 100;
  }

  /* Faixa de margem (descritiva; não altera a ordem). */
  function faixa(l) {
    if (l.status === "abaixo_conferir") return "conferir";
    const m = margemRobusta(l);
    if (m === null) return "sem_margem";
    if (m < 0) return "acima";
    if (m < 10) return "ate10";
    if (m < 30) return "10a30";
    return "mais30";
  }

  /* Nível de alerta a partir da lista do painel: grave > atencao > ok. */
  function nivelAlerta(l) {
    const a = Array.isArray(l.alertas) ? l.alertas : [];
    if (a.some(x => x && x.nivel === "grave")) return "grave";
    if (a.some(x => x && x.nivel === "atencao")) return "atencao";
    return "ok";
  }

  const RANK = {abaixo: 0, acima: 1};
  function porCriterio(a, b) {
    return (RANK[a.grupo] - RANK[b.grupo]) || (b.l.liquidez_mediana_12m_eur - a.l.liquidez_mediana_12m_eur) || cmp(a.l.papel, b.l.papel);
  }

  /* linhas: lista do painel.json. grupo: "nucleo" | "observacao". Devolve {principal, fora}, cada item {l, grupo, motivo, faixa}. */
  function ordenar(linhas, grupo) {
    const principal = [], fora = [];
    for (const l of linhas) {
      if (grupo && l.grupo !== grupo) continue;
      const c = classificar(l), item = {l, grupo: c.grupo, motivo: c.motivo, faixa: faixa(l)};
      (c.grupo === "fora" ? fora : principal).push(item);
    }
    principal.sort(porCriterio);
    fora.sort((a, b) => cmp(a.l.papel, b.l.papel));
    return {principal, fora};
  }

  /* Ordem alfabética (seletor do leitor). */
  function alfabetica(itens) {
    return itens.slice().sort((a, b) => cmp(a.l.papel, b.l.papel));
  }

  /* Corte do modo Iniciante: primeiros N da ordem de critério. */
  function iniciante(itens, n) {
    return itens.slice(0, n || INICIANTE_MAX);
  }

  function paginas(itens, n) {
    const t = n || LIM_PAGINA, out = [];
    for (let i = 0; i < itens.length; i += t) out.push(itens.slice(i, i + t));
    return out;
  }

  /* Valida o painel.json (campo linhas). Devolve {ok, linhas, erro}. Descarta item sem papel ou grupo. */
  function validar(painel) {
    if (!painel || typeof painel !== "object" || !Array.isArray(painel.linhas)) return {ok: false, linhas: [], erro: "linhas ausente"};
    const linhas = painel.linhas.filter(l => l && typeof l === "object" && typeof l.papel === "string" && l.papel && (l.grupo === "nucleo" || l.grupo === "observacao"));
    if (!linhas.length) return {ok: false, linhas: [], erro: "nenhuma linha válida"};
    return {ok: true, linhas, erro: null};
  }

  /* Data do preço mais frequente entre os papéis com cotação. */
  function dataPredominante(linhas) {
    const c = {};
    for (const l of linhas) if (num(l.preco) !== null && typeof l.data_preco === "string" && /^\d{4}-\d{2}-\d{2}$/.test(l.data_preco)) c[l.data_preco] = (c[l.data_preco] || 0) + 1;
    let melhor = null;
    for (const d of Object.keys(c).sort()) if (melhor === null || c[d] >= c[melhor]) melhor = d;
    return melhor;
  }

  /* Quantos papéis têm preço de data anterior ao último fechamento esperado (fecho_esperado do painel). */
  function defasados(linhas, fecho) {
    if (typeof fecho !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(fecho)) return 0;
    return linhas.filter(l => num(l.preco) !== null && typeof l.data_preco === "string" && l.data_preco < fecho).length;
  }

  const API = {LIM_PAGINA, LIM_IFRAMES, INICIANTE_MAX, classificar, margemRobusta, faixa, nivelAlerta, ordenar, alfabetica, iniciante, paginas, validar, dataPredominante, defasados};
  if (typeof module !== "undefined" && module.exports) module.exports = API; else root.OrdemLisboa = API;
})(typeof self !== "undefined" ? self : this);
