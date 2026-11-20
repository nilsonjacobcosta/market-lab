# Cotações Dividendos Lisboa: pareceres antes do merge (20/11/2026)

Revisão feita pelo coordenador (Claude) sobre o PR de rascunho, sem agentes independentes. Os três papéis do método do projeto (J1 dados, J2 regulatório/comunicação, J3 engenharia) foram verificados em sequência; isto deve ser lido como revisão própria, não como parecer de juízes independentes.

## J1 · dados e fontes
- Todos os valores vêm de `dados/portugal/painel.json`; a página não busca nada além dele e dos widgets.
- Teto robusto e margem conferidos com o painel: margem = (teto robusto − preço) ÷ preço.
- Defasagem: a página avisa quando algum preço é anterior ao `fecho_esperado`. No teste de 20/11, 3 papéis (FLEXD, MCP, SCT) aparecem com preço de 19/11 e o aviso aparece.
- Ajuste feito: o resumo agora diz quantos papéis ficaram fora dos critérios (TDSA, no núcleo) em vez de só contar os que estão no critério.
- Ressalva: o preço vem da mesma fonte do Monitor Portugal (Yahoo Finance), decisão já registrada pelo dono em 20/11/2026.

## J2 · regulatório e comunicação
- Termos com rótulo de compra ou venda: nenhum. Rótulos usados: "Abaixo do teto", "Acima do teto", "conferir dados".
- Busca de palavras proibidas ("vai", "deve", "sinal", "oportunidade", "barato", "alvo"): só aparecem em frases negadas ("não é sinal de qualidade", "não um sinal de compra").
- Aviso de material educativo e de não recomendação presente no topo e no rodapé.
- Pendência que continua aberta: parecer jurídico sobre MAR art. 20.º e Reg. CMVM 2/2007 (registrado no Monitor Portugal). Esta página não o resolve.

## J3 · engenharia e operabilidade
- `node --test tests/ordem_lisboa.test.js`: 14 testes passam; o workflow `testes-cotacoes-dividendos-lisboa.yml` roda os mesmos testes em PR.
- Página executada em jsdom com dados reais: 2 grupos, carga de widget só após o clique (0 scripts do TradingView antes do clique, 1 depois), modo Iniciante com 6 linhas, sem erros de JavaScript.
- Sintaxe do JavaScript inline verificada com `node --check`.
- Símbolos: os 30 `EURONEXT:` abriram com valor no Chrome do dono (20/11/2026).
- Pendência aberta: cabeçalhos do widget saem em inglês com `locale: "pt"`.

## Decisão
Passou nos três, com os ajustes listados. Merge autorizado pelo dono após os juízes.
