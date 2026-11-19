# Cotações do BESST

> Página didática. Material educativo. Não é recomendação de investimento. Não use para operar.

Página: `carteiras/besst-cotacoes/` · Dados: `dados/besst/painel.json` (Monitor BESST) · Proposta e pareceres: `docs/besst-cotacoes/` · Manutenção: `manutencao/runbooks/12-cotacoes-besst.md`.

## O que é
Uma aba por setor do Monitor BESST (Bancos, Energia, Seguros, Saneamento, Telecomunicações), com tabela acessível dos papéis e um widget Market Quotes do TradingView (até 8 papéis por widget) com cotação atrasada. Modos Iniciante (até 6 papéis por setor, um por empresa) e Avançado (todas as páginas de 8, com margem, liquidez, data do preço e controle).

## Ordem de leitura (regra única, igual para todos)
1. Fora da lista: sem preço, alerta grave, baixa liquidez, sem proventos, histórico curto, preço-teto não se aplica, sem teto ou sem liquidez (seção "Fora dos critérios", só texto).
2. Primeiro os papéis `abaixo_teto`; depois `abaixo_teto_conferir` e `acima_teto`.
3. Em cada grupo, liquidez em R$ mil por dia (decrescente) e, no empate, ticker (crescente).
4. Faixas de margem (mais de 30%, 10% a 30%, até 10% abaixo; acima do teto) só descrevem; não mudam a ordem.
5. O leitor pode trocar para ordem alfabética. Com dados de 5 ou mais pregões de atraso ou JSON inválido, a página usa a alfabética e avisa.
6. No Iniciante o corte (até 6 papéis, um por empresa) é feito pela ordem de critério; a ordem alfabética só reordena os papéis mostrados. Decisão registrada em 19/11/2026.
Mudar a regra é decisão do dono.

## Como funciona
- A ordem é calculada no navegador (`ordem.js`, função pura) com dados do `painel.json`. **Nenhum script lê valores dos widgets.**
- Os widgets **só carregam depois do clique** em "Carregar cotações" (ou com a opção "Carregar ao trocar de setor" ligada, guardada em `besst-cotacoes-auto`). No máximo 1 widget por vez (teto de segurança de 2 iframes).
- Só entra em widget o papel de `matriz_teste.simbolos_aprovados`; os demais ficam na tabela com "sem teste no widget".
- Se o widget não carrega em 10 s, a página mostra os símbolos com link.

## Testes
`python3 -m unittest tests/test_besst_cotacoes.py` (textual), `node --test tests/ordem.test.js` (ordem, calendário, invariantes sobre o `painel.json` real) e `tests/pagina.test.js` (executa a página em jsdom: carga por clique, paginação, XSS, painel malformado; precisa de `npm i --no-save jsdom`). Workflow: `.github/workflows/testes-besst-cotacoes.yml` (PR, semanal e manual). Os widgets em si (iframes do TradingView) só se conferem no navegador com `teste-simbolos.html`. O `painel.json` não dispara o workflow (o bot commita direto): ele é coberto pelo teste semanal.

## Pendências
- Símbolos testados em 19/11/2026 no navegador embutido do app Claude: 105 de 107 abriram com valor; OIBR3 e OIBR4 ficaram sem valor (reprovados). Conferir de novo no Chrome do dono quando possível.
- Consulta formal ao TradingView: autorizada pelo dono, ainda não enviada; enquanto isso os widgets carregam só por clique.
- Medir o peso real no navegador e registrar aqui.
- Origem e licença dos preços (Yahoo Finance, via Monitor BESST) a registrar.
