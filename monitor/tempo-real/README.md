# Mercados em tempo real

> Material educativo. Não é recomendação de investimento. Não use para operar.

Página: `monitor/tempo-real/` · Origem do código: cópia enxugada de `monitor/mercados/index.html` (sem gráficos próprios e sem coleta). Proposta e pareceres: `docs/monitor-tempo-real/` (Fase 0, versão 2).

## O que é
Quatro conjuntos no modo Iniciante (Câmbio; Ações, com EUA e Brasil em cartões separados; Juros do Brasil; Commodities) e mais conteúdo no Avançado (minicontratos da B3, outros vencimentos DI, juros dos EUA em dado diário, prata e minério, cripto). Cada cartão é **um widget Market Quotes do TradingView**, em largura total (o widget só mostra nome e valor quando está estreito), com texto próprio (o que é, como ler, o que já se observou), termos do glossário, lista de símbolos com atraso e link para o histórico no painel Mercados e ciclos. Uma faixa de cotações (Ticker Tape) fica ligada por padrão, com botão liga/desliga (`tempo-real-ticker`) e desligada com `prefers-reduced-motion`.

## Como funciona
- Os widgets carregam ao abrir a página (decisão do dono, 19/11/2026). Aviso de privacidade no topo.
- **Nenhum script lê valores dos widgets**, e nenhuma cotação é gravada ou republicada. `conjuntos.json` não tem nenhum valor de cotação.
- Se nenhum iframe aparece em 10 s, o cartão mostra os símbolos com link para o TradingView. Quadro vazio ou erro **dentro** do iframe a página não detecta.

## Regras de dados (resumo)
- Só entra símbolo com registro em `matriz_teste.simbolos_aprovados` (teste de 19/11/2026 no Market Quotes) e fora de `reprovados`. O teste automático (`tests/test_tempo_real.py`) impede o contrário.
- Contratos DI só com vencimento a mais de 90 dias (hoje 2028, 2031, 2035 no Iniciante; 2029 e 2033 no Avançado). O teste falha quando um contrato passa dessa margem; ver RB 11.
- Cotações da B3 aparecem sempre como atrasadas; CFDs com "pode diferir da bolsa"; FRED como dado diário.
- Curva DI própria: fora da versão 1 (só com autorização escrita da B3).
- Widgets de análise técnica (compra/venda) ficam fora.

## Pendências
- Teste do dono em 19/11/2026 (`teste-simbolos.html`): os 27 símbolos dos cartões e os 6 da faixa abriram com valores. Não consultada ainda a natureza dos feeds TVC e CAPITALCOM (página do símbolo no TradingView).
- Advanced Chart, Symbol Overview, DXY, VIX e calendário econômico não foram testados e **não entram** na versão 1.
- Consulta formal ao TradingView (uso público educativo e sem receita): autorizada pelo dono, ainda **não enviada** porque o formulário oficial pede nome, e-mail, telefone, cargo e URL pública do projeto. Guardar a resposta em `docs/monitor-tempo-real/`.
- Reconferir os termos do TradingView a cada trimestre (última leitura: 19/11/2026).

## Testes
`python3 -m unittest tests/test_tempo_real.py` (JSON e HTML, sem rede; workflow `testes-tempo-real.yml`, no PR e uma vez por mês). Playwright não foi adotado: os widgets são iframes de terceiros, então um teste simulado só validaria o nosso código de montagem, já coberto pelo teste manual com `teste-simbolos.html`.
