# Cotações do BESST — Pareceres da Fase 1 (19/11/2026)

Resumo dos três juízes sobre a página construída. Correções aplicadas antes do merge (PR #18).

## J1 conteúdo e redação — 7,0, aprovar com ajustes
- Data do "fechamento" não batia com os preços (arquivo indica 19/11; 99 papéis têm preço de 17/11): a página passou a usar a data mais frequente dos preços e avisa atraso em pregões.
- Fórmula incompleta (mediana com 3–4 anos, data-ex, ano parcial e lacunas): corrigida; liquidez com período; histórico curto com rótulo exato.
- Resumo "N de M" inconsistente: refeito (conferir, baixa liquidez, empresas no Iniciante); corte do Iniciante explicado; controle "a confirmar"; textos de Energia.

## J2 engenharia e acessibilidade — 8,0, aprovar com ajustes
- Sem bloqueantes. Página robusta a XSS e carga só por clique; 56 mutações, 21 sobreviveram (comportamento em execução).
- Aplicado: tolerância a painel malformado, foco na paginação, `Object.hasOwn`, `noreferrer`, workflow com gatilho no calendário do Monitor, teste jsdom da página (9 testes), testes de limites.

## J3 didática e regulatório — 7,0, aprovar com ajustes
- Cumpre os pedidos dos pareceres da Fase 0 e as decisões do dono; sem bloqueante além da data e do corte do Iniciante (corrigidos).
- Registrado para o dono: a origem dos preços é Yahoo Finance (frase do rodapé ajustada); termos de redistribuição e TradingView não conferidos [referência não verificada]; conclusão sobre a Resolução CVM 20/2021 é de advogado.

## Teste de símbolos (19/11/2026)
105 de 107 papéis abriram com valor no widget Market Quotes; OIBR3 e OIBR4 sem valor (reprovados).
