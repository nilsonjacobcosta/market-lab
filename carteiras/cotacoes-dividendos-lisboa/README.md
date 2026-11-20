# Cotações Dividendos Lisboa

> Página didática. Material educativo. Não é recomendação de investimento. Não use para operar.

Página: `carteiras/cotacoes-dividendos-lisboa/` · Dados: `dados/portugal/painel.json` (Monitor Portugal) · Modelo: `carteiras/besst-cotacoes/` (mesma estrutura, outro universo).

## O que é
Dois grupos do Monitor Portugal: **Núcleo** (liquidez mediana de 12 meses ≥ 100 mil € por dia, 16 papéis) e **Em observação** (liquidez média ou baixa, 14 papéis). Cada grupo traz uma tabela acessível e widgets Market Quotes do TradingView (até 8 papéis por widget), com cotação atrasada. Modos Iniciante (até 6 papéis por grupo) e Avançado (todos, com margem, liquidez em mil € por dia, data do preço e controlo acionista).

## Ordem de leitura (regra única, igual para todos)
1. Fora da lista: sem cotação, em cadastro (proventos ainda por conferir no cadastro oficial), sem proventos ou sem preço-teto robusto (seção "Fora dos critérios", só texto).
2. Primeiro os papéis `abaixo` (preço abaixo do teto robusto); depois `abaixo_conferir` e `acima`.
3. Em cada grupo, liquidez mediana de 12 meses (decrescente) e, no empate, papel (crescente).
4. Faixas de margem só descrevem; não mudam a ordem.
5. O leitor pode trocar para ordem alfabética.
6. No Iniciante o corte (até 6 papéis) segue a ordem de critério.
Mudar a regra é decisão do dono.

## Como funciona
- A ordem é calculada no navegador (`ordem.js`, função pura). **Nenhum script lê valores dos widgets.**
- Os widgets **só carregam depois do clique** em "Carregar cotações" (ou com "Carregar ao trocar de grupo" ligado, guardado em `lisboa-cotacoes-auto`). No máximo 2 iframes ao mesmo tempo.
- Só entra em widget o papel de `conjuntos.json › matriz_teste.simbolos_aprovados`; os demais ficam na tabela com "sem teste no widget".
- Prefixo do TradingView: `EURONEXT:` (ex.: `EURONEXT:ALTR`).
- Se o widget não carrega em 10 s, a página mostra os símbolos com link.
- A margem usa o teto robusto: `(teto_robusto − preço) ÷ preço`.

## Testes
- `node --test tests/ordem_lisboa.test.js`: ordem, classificação, margens, faixas, validação e consistência com o `painel.json` real.
- Os widgets em si (iframes do TradingView) só se conferem no navegador com `teste-simbolos.html`. Ao testar, use o navegador do dono, como no BESST.

## Teste de símbolos (pendente de execução completa)
Procedimento: abrir `teste-simbolos.html`, carregar cada grupo, marcar "abriu" ou "não abriu" por papel, clicar em "Gerar JSON" e colar em `conjuntos.json › matriz_teste`. Um papel que não abre fica sem widget e com link.

## Pendências
- Símbolos: os 30 `EURONEXT:` abriram com valor no Chrome do dono em 20/11/2026 (registro em `conjuntos.json › matriz_teste`). Foi conferido que abriram, não o valor de cada um contra o painel.
- Idioma: o widget usa `locale: "br"` (português, testado em 20/11/2026: cabeçalhos "Nome", "Valor", "Variação"). O código `pt` não traduzia os cabeçalhos.
- Parecer jurídico (MAR art. 20.º; Reg. CMVM 2/2007) registrado como pendência do Monitor Portugal; a publicação desta página segue a decisão do dono de 20/11/2026.
- Juízes (J1 dados, J2 regulatório/comunicação, J3 engenharia) antes do merge, como nos outros painéis.
- Origem dos preços (Yahoo Finance) segue a decisão de 20/11/2026 do dono, a mesma do Monitor BESST.

## Limites
Se um quadro ficar vazio ou mostrar erro dentro do widget, a página não consegue detectar. Confira o símbolo pelo link da tabela. Cotação do widget e fecho usado na ordem podem diferir.
