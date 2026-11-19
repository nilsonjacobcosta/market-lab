# Monitor em tempo real — pareceres da Fase 0

Data: 19/11/2026. Quatro especialistas, cada um em um agente separado, sem ver o parecer dos outros. Avaliaram a versão 1 da proposta (`85f681b`). Pareceres e correções estão consolidados na seção 8 de `fase0.md`.

| Especialista | Nota | Veredito | Principais pontos |
|---|---|---|---|
| Mercados | 7,0 | Adequado com ajustes | Separar EUA e Brasil; cortar minicontratos do Iniciante; definir os 4 cartões; remover "tempo real" não comprovado; Brent e WTI nomeados; três "dólares"; contradição da curva DI própria; tabela de símbolos como hipótese. |
| Dados e licenças | 7,0 | Adequado com ajustes | Erro da versão 1: os Termos tratam de widgets (seção 4); consulta ao TradingView desde já; aviso de privacidade e carga após clique; regra de não ler valores do widget; checklist da B3; reconferência trimestral. |
| Didática | 5,5 | Inadequado até incorporar os ajustes | Enquadramento no topo; atraso por extenso; sem Ticker Tape, notícias e minicontratos no Iniciante; 4 conjuntos no Iniciante; regras R-TR1 a R-TR5; termos de glossário; rascunho do cartão "Curva DI". |
| Engenharia | 6,0 | Adequado com ajustes | Copiar e enxugar o Mercados; um cartão por widget; matriz símbolo × widget; DI1F2027 vence em janeiro de 2027; teste do JSON, workflow, runbook 11; acessibilidade do Ticker Tape; teste manual no Chrome do dono. |

Conferido pelo coordenador: Selic meta em 13,75% em 19/11/2026 (dados coletados), o que torna o DI1F2029 em 15,3% do widget incomum e não verificado.

Limites: nenhum especialista testou símbolos em widgets; a leitura dos Termos do TradingView veio de resumos de página obtidos por ferramenta, não do texto integral; o texto da B3 não foi lido.
