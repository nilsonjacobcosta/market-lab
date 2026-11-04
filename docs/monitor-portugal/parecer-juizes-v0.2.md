# Monitor Portugal v0.2 — parecer dos juízes (04/11/2026)

Entrega: qualidade financeira (BETA) a partir dos relatórios anuais ESEF e página com o mesmo sistema visual do Monitor BESST.

## J1 — dados e fontes · nota 8,5 · aprovado
- 16/16 empresas associadas ao relatório anual ESEF de 2025 (filings.xbrl.org); lucro encontrado em 16/16.
- Conferência de lucro (meta ≤ 2%): BCP 1.018,6 = 1.018,6 M€; Galp 1.120,0 = 1.120,0; Jerónimo Martins 646,0 = 646,0;
  EDP 1.149,7 vs 1.150 (0,02%); NOS 245,9 = 245,9; EDP Renováveis 215,8 vs 216 (0,09%). **6 de 6.**
- 14 de 16 com nota (87,5%; meta 75%). Sem nota: Altri e Ibersol (payout acima de 150%, regra de plausibilidade do BESST).
- Rubricas próprias usadas (mapa explícito no script): empréstimos de Altri e Mota-Engil, depreciações de Galp e CTT, EBITDA da EDP.
- Ressalvas: Galp sem dívida/EBITDA; locações não separadas em várias empresas (aviso na ficha); CTT exclui depósitos do Banco CTT da dívida.

## J2 — comunicação · nota 8,0 · aprovado
- Avisos do BESST adaptados (fecho de Lisboa, "não é recomendação"), guia em 5 passos, legenda, pílulas neutras (sem verde de "compra").
- Coluna Qualidade com BETA, motivo de "sem nota" e ressalvas na ficha; sem ordenação por margem nem por situação.
- Apresentação objetiva mantida: autor, data, fontes, metodologia, riscos, histórico de mudanças.

## J3 — engenharia · nota 8,5 · aprovado
- Workflow semanal com aceite que bloqueia a publicação; diagnóstico separado; testes de regressão (leitura de factos, regra da nota, bancos).
- Página validada em ecrã largo (iframe 1240 px) e estreito; JS validado.
- Ressalva: o GitHub devolveu erros 500 intermitentes no envio; os scripts de envio repetem automaticamente.
