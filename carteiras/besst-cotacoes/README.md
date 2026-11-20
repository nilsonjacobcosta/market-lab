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
- Consulta formal ao TradingView: **dispensada pelo dono em 20/11/2026**, por já existir a opção de ligar e desligar o carregamento dos widgets (padrão: desligado, só por clique).
- Peso medido em 20/11/2026 no Chrome do dono (aba Bancos, modo Iniciante): cerca de 42 KB transferidos do próprio site (HTML, `ordem.js`, `conjuntos.json`, `painel.json`), antes de qualquer widget. O peso do widget do TradingView não é medível pela página (conteúdo de outro domínio, sem tamanho exposto) e não foi medido.
- Reteste dos símbolos em 20/11/2026 (Chrome do dono, 17 grupos, conferência visual do valor no widget): 105 abriram e 2 não (OIBR3, OIBR4), idêntico ao registro de 19/11 em `conjuntos.json`; nada a alterar.
- Conferido no ar em 20/11/2026: aviso de atraso aparece ("faltam 1 pregão(ões)", dados de 18/11, feriado de 20/11), frase de créditos visível e widget com 6 papéis carregou após o clique.
- Origem e licença dos preços: registrada abaixo (leitura de 20/11/2026). Decisão do dono (20/11/2026): seguir como está, sem mudar a fonte nem pedir parecer por ora.

## Origem dos preços e termos do Yahoo (leitura de 20/11/2026)

Os preços do Monitor BESST vêm do Yahoo Finance (cerca de 15 min de atraso). Esta página não exibe esses preços em tabela de cotação: mostra preço-teto, margem e faixa calculados a partir deles; as cotações visíveis são do widget do TradingView.

O que os textos oficiais dizem (lidos em legal.yahoo.com, 20/11/2026; nível B, documento da própria empresa; paráfrase, sem valor jurídico):

- **Termos de Serviço do Yahoo** (`legal.yahoo.com/us/en/yahoo/terms/otos/`): proíbem coletar dados dos serviços por meios automatizados sem permissão prévia (§2(d)(ix)); proíbem reproduzir, distribuir ou transmitir o conteúdo sem autorização escrita (§2(h)); proíbem uso comercial dos serviços (§2(e)); a licença de software e APIs é pessoal, revogável e não transferível (§2(i)). Não há cláusula que cite dados financeiros ou cotações. Lido o texto até o caractere 100.000 de 127.483 (o restante é regional/EMEA e não trata de cotações).
- **Termos da API para desenvolvedores** (`legal.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/`): o Yahoo pode encerrar a licença a qualquer momento (§1(a)), impor limites de uso (preâmbulo) e mudar ou suspender APIs (§§4–5). A página não menciona os dados de cotações do Yahoo Finance, então não dá para afirmar que se aplica a eles.
- Não foi encontrada API pública oficial de cotações do Yahoo Finance **[referência não verificada: apontada só por fontes secundárias]**.

Leitura prática (análise, não decisão): a coleta automatizada feita pelo Monitor BESST e a exibição dos números derivados em página pública são o ponto sensível. A dispensa do TradingView não cobre isso. Se o dono quiser reduzir o risco: (a) buscar licença ou fonte oficial (B3, provedor autorizado); (b) manter só o derivado (teto, margem, faixa) e nunca o preço bruto do Yahoo; (c) pedir parecer de advogado. A decisão (seguir como está, 20/11/2026) e a avaliação jurídica são do dono.

## Tema claro e escuro

A página segue a configuração de aparência do sistema (`prefers-color-scheme`), como a página inicial do market-lab: claro por padrão e escuro quando o sistema está escuro. Não segue a hora do dia por conta própria; se o sistema alterna sozinho entre claro e escuro (por exemplo, no macOS, em Aparência: Automática), a página acompanha. O widget do TradingView também usa o tema do sistema (`colorTheme`) e, se o tema mudar com o widget aberto, é montado de novo. Razões de contraste do tema claro conferidas por cálculo (todas ≥ 4,5:1; texto principal ≈ 16:1). Os testes impedem cores fixas fora das variáveis do `:root`.
