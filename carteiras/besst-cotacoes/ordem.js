/* Ordem de leitura do Cotações do BESST. Função pura: sem DOM, sem relógio e sem comparação por idioma.
   Usada pela página e testada com `node --test tests/ordem.test.js`. */
(function (root) {
  "use strict";
  const LIM_PAGINA = 8;      /* símbolos por widget */
  const LIM_IFRAMES = 2;     /* teto de segurança de iframes ativos */
  const ATRASO_MAX_PREGOES = 5;
  /* Mesma lista de carteiras/monitor-besst/index.html (RB 04). Um teste compara as duas. */
  const FERIADOS = ["2026-01-01","2026-02-16","2026-02-17","2026-04-03","2026-04-21","2026-05-01","2026-06-04","2026-09-07","2026-10-12","2026-11-02","2026-11-20","2026-12-24","2026-12-25","2026-12-31",
    "2027-01-01","2027-02-08","2027-02-09","2027-03-26","2027-04-21","2027-05-27","2027-09-07","2027-10-12","2027-11-02","2027-11-15","2027-12-24","2027-12-31"];
  const FER = new Set(FERIADOS);
  const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
  const num = (x) => (typeof x === "number" && isFinite(x) ? x : null);

  /* Devolve {grupo: "abaixo"|"acima"|"fora", motivo} para um papel. Exclusões primeiro. */
  function classificar(p) {
    if (num(p.preco) === null || p.status === "sem_cotacao") return {grupo: "fora", motivo: "sem_cotacao"};
    if (p.nivel_alerta === "grave") return {grupo: "fora", motivo: "alerta_grave"};
    if (p.baixa_liquidez === true) return {grupo: "fora", motivo: "baixa_liquidez"};
    if (num(p.liquidez_mil) === null) return {grupo: "fora", motivo: "sem_liquidez"};
    const s = p.status_robusto;
    if (s === "sem_proventos" || s === "historico_curto" || s === "nao_se_aplica") return {grupo: "fora", motivo: s};
    if (num(p.preco_teto_robusto) === null) return {grupo: "fora", motivo: "sem_teto"};
    if (s === "abaixo_teto") return {grupo: "abaixo", motivo: null};
    if (s === "abaixo_teto_conferir" || s === "acima_teto") return {grupo: "acima", motivo: null};
    return {grupo: "fora", motivo: "outro"};
  }

  /* Faixa de margem (descritiva; não altera a ordem). */
  function faixa(p) {
    if (p.status_robusto === "abaixo_teto_conferir") return "conferir";
    const m = num(p.margem_robusta);
    if (m === null) return "sem_margem";
    if (m < 0) return "acima";
    if (m < 10) return "ate10";
    if (m < 30) return "10a30";
    return "mais30";
  }

  const RANK = {abaixo: 0, acima: 1};
  function porCriterio(a, b) {
    return (RANK[a.grupo] - RANK[b.grupo]) || (b.p.liquidez_mil - a.p.liquidez_mil) || cmp(a.p.ticker, b.p.ticker);
  }

  /* papeis: lista do painel.json. Devolve {principal, fora}, cada item {p, grupo, motivo, faixa}. */
  function ordenar(papeis, setor) {
    const principal = [], fora = [];
    for (const p of papeis) {
      if (setor && p.setor !== setor) continue;
      const c = classificar(p), item = {p, grupo: c.grupo, motivo: c.motivo, faixa: faixa(p)};
      (c.grupo === "fora" ? fora : principal).push(item);
    }
    principal.sort(porCriterio);
    fora.sort((a, b) => cmp(a.p.ticker, b.p.ticker));
    return {principal, fora};
  }

  /* Ordem alfabética (seletor do leitor, ou plano B com dados muito velhos). */
  function alfabetica(itens) {
    return itens.slice().sort((a, b) => cmp(a.p.ticker, b.p.ticker));
  }

  /* Um papel por empresa (o primeiro da ordem recebida, ou seja, o de maior liquidez no critério). */
  function umPorEmpresa(itens) {
    const vistas = new Set(), saida = [];
    for (const it of itens) {
      const k = it.p.empresa || it.p.ticker;
      if (vistas.has(k)) continue;
      vistas.add(k); saida.push(it);
    }
    return saida;
  }

  function paginas(itens, n) {
    const t = n || LIM_PAGINA, out = [];
    for (let i = 0; i < itens.length; i += t) out.push(itens.slice(i, i + t));
    return out;
  }

  /* Valida o painel.json. Devolve {ok, papeis, erro}. Descarta item sem ticker ou setor. */
  function validar(painel) {
    if (!painel || typeof painel !== "object" || !Array.isArray(painel.papeis)) return {ok: false, papeis: [], erro: "papeis ausente"};
    const papeis = painel.papeis.filter(p => p && typeof p === "object" && typeof p.ticker === "string" && p.ticker && typeof p.setor === "string" && p.setor);
    if (!papeis.length) return {ok: false, papeis: [], erro: "nenhum papel válido"};
    return {ok: true, papeis, erro: null};
  }

  /* Calendário de pregões (datas "AAAA-MM-DD"). */
  const iso = (d) => d.toISOString().slice(0, 10);
  const ehPregao = (s) => { const d = new Date(s + "T12:00:00Z").getUTCDay(); return d > 0 && d < 6 && !FER.has(s); };
  function pregaoAnterior(s) { let d = new Date(s + "T12:00:00Z"); do { d = new Date(d.getTime() - 864e5); } while (!ehPregao(iso(d))); return iso(d); }
  /* agoraMs: milissegundos UTC. O fechamento de hoje é esperado a partir das 22h30 de Brasília. */
  function pregaoEsperado(agoraMs) {
    const b = new Date(agoraMs - 3 * 36e5), hoje = iso(b), hm = b.getUTCHours() * 60 + b.getUTCMinutes();
    return ehPregao(hoje) && hm >= 22 * 60 + 30 ? hoje : pregaoAnterior(hoje);
  }
  /* Quantos pregões separam a referência do esperado, e o estado: ok | atrasado | muito_atrasado | invalido. */
  function situacao(ref, agoraMs) {
    if (typeof ref !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(ref)) return {estado: "invalido", atraso: null, esperado: null};
    const esperado = pregaoEsperado(agoraMs);
    let atraso = 0, d = esperado;
    while (d > ref && atraso < 60) { atraso++; d = pregaoAnterior(d); }
    const estado = atraso === 0 ? "ok" : atraso >= ATRASO_MAX_PREGOES ? "muito_atrasado" : "atrasado";
    return {estado, atraso, esperado};
  }

  const API = {LIM_PAGINA, LIM_IFRAMES, ATRASO_MAX_PREGOES, FERIADOS, classificar, faixa, ordenar, alfabetica, umPorEmpresa, paginas, validar, ehPregao, pregaoAnterior, pregaoEsperado, situacao};
  if (typeof module !== "undefined" && module.exports) module.exports = API; else root.OrdemBESST = API;
})(typeof self !== "undefined" ? self : this);
