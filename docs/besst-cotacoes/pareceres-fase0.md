# Cotações do BESST — Pareceres da Fase 0 (19/11/2026)

Resumos dos quatro especialistas sobre a proposta v1. Notas e achados abaixo; a proposta v2 incorpora os ajustes. Não há texto jurídico literal aqui; a conclusão jurídica cabe a advogado.

## Mercados — 6,5, aprovar com ajustes
- Saneamento e Telecom têm 0 papéis abaixo do teto; Seguros 2.
- Várias classes da mesma empresa (Santander, Bradesco, Taesa, Cemig) ocupariam metade das páginas.
- Corte binário abaixo/acima cria degrau artificial; liquidez favorece estatais e papéis populares.
- `abaixo_teto_conferir` não deveria vir à frente.
- Datas por papel inconsistentes; limite de painel velho deve ser em dias úteis.
- Mostrar controle acionário e alertas.

## Didática — 6,5, aprovar com ajustes
- "Ordem de leitura" sem numeração, com seletor alfabético.
- "O que esta página não diz" antes das listas; linha "N de M abaixo do teto" por aba.
- Alerta de cada papel visível no Iniciante; 5–6 papéis por aba.
- Tabela HTML acessível como parte principal; abas no celular; rascunhos de glossário.

## Regulatório e licenças — 6,5, aprovar com ajustes
- Risco CVM 20/2021 baixo a moderado, sem porto seguro textual; ordem "abaixo do teto primeiro" é o elemento que mais lembra um filtro de oportunidades.
- Sem receita, anúncio, afiliado ou doação; critério mecânico e único; declarar conflito de interesse.
- Proibir "melhores/top/destaque/desconto"; aviso de privacidade antes do primeiro widget.
- Carregamento por clique recomendado; resposta escrita do empregador e do TradingView como pré-condições; registrar origem e licença do `painel.json`.

## Engenharia e operação — 6,5, aprovar com ajustes
- Erros factuais da v1: 107 papéis com preço (não 141); `pregao_referencia` é do topo, por papel é `data`.
- Algoritmo da seção 3 ambíguo; resultado simulado: 42 na principal, 65 fora com preço, 34 sem cotação.
- Nenhuma ação B3 testada no widget; teste do dono antes de construir (units, classes 5/6, AXIA3/AXIA7).
- Painel velho: usar pregões esperados, manter ordem com aviso; validar esquema (null na ordenação).
- Ordenação em `ordem.js` com `node --test`; "Próximos 8" substitui o widget; `teste-simbolos` em lotes.
- Runbook 12, RB 03 (34 sem cotação) e RB 04 (FERIADOS).
- Não conferido: qualquer coisa ao vivo no TradingView; TTL do CDN do Pages; definição exata de `liquidez_mil`.
