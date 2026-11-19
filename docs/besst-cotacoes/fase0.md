# Cotações do BESST — Fase 0 (proposta, versão 1)

Data: 19/11/2026. Etapa anterior à construção. Nenhuma página nova foi criada.

## 1. Objetivo
Página nova em "Carteiras de dividendos" com cotações atrasadas (widgets do TradingView) dos papéis do Monitor BESST (5 setores perenes: Bancos, Energia, Seguros, Saneamento, Telecomunicações), organizada por setor e ordenada por critério nosso, para iniciantes e completo, seguindo a estrutura dos painéis do market-lab (modo Iniciante/Avançado, glossário, "o que esta página não diz", juízes).

- Nome: **Cotações do BESST**. Pasta: `carteiras/besst-cotacoes/`. Link cruzado com `carteiras/monitor-besst/`.
- Decisões do dono (19/11/2026): nome e pasta aprovados; critério de ordem: **primeiro os papéis abaixo do preço-teto robusto, e dentro deles por liquidez**; Fase 0 com quatro especialistas, sem construir antes do "sim".

## 2. Origem dos dados e regra central
- Universo e métricas: `dados/besst/painel.json` (141 papéis com cotação: Energia 69, Bancos 39, Seguros 13, Saneamento 10, Telecomunicações 10), atualizado por dia útil pelo workflow do Monitor BESST. Campos usados: `ticker`, `setor`, `status_robusto`, `margem_robusta`, `liquidez_mil`, `nivel_alerta`, `baixa_liquidez`, `pregao_referencia`.
- A ordem é calculada **no navegador, com dados nossos** (fechamento do dia anterior). **Nenhum script lê valores dos widgets** (regra herdada do painel em tempo real e dos termos do TradingView). A página diz por extenso que a ordem vem do fechamento de DD/MM e que o widget mostra cotação atrasada, que pode estar em outro nível.
- Widgets: Market Quotes, no máximo 8 símbolos por widget (várias páginas de 8 por setor). Só símbolos testados no widget real (matriz símbolo × widget, como no painel em tempo real). Símbolos que não abrirem ficam fora, com aviso.

## 3. Ordem dentro de cada setor
1. Papéis com `status_robusto` = `abaixo_teto` (e `abaixo_teto_conferir`, marcados "conferir"), ordenados por `liquidez_mil` decrescente.
2. Demais papéis com cotação e sem alerta grave, por `liquidez_mil` decrescente.
3. Papéis com alerta grave, baixa liquidez, sem proventos, histórico curto ou sem teto: fora da lista principal, em seção recolhida "Fora dos critérios", com o motivo.
Empate: ordem alfabética do ticker. A regra fica escrita na página e no README; mudar a regra é decisão do dono.

## 4. Modos
- **Iniciante:** 5 abas (setores); em cada, a primeira página de 8 papéis (os primeiros pela ordem acima), textos abertos (o que é o preço-teto robusto, o que é liquidez, o que o widget mostra e não mostra), aviso de atraso por extenso, link para o Monitor BESST.
- **Avançado:** todas as páginas de 8 do setor (botão "Próximos 8", máx. 3 iframes ativos por vez), seção "Fora dos critérios", coluna textual com margem e liquidez do Monitor BESST ao lado de cada widget (texto nosso, do fechamento, sem ler o widget).

## 5. Regras de redação (herdam R-TR1 a R-TR5 do painel em tempo real e acrescentam)
- R-B1: nunca "barata", "oportunidade", "compre", "recomendada"; usar "abaixo do preço-teto robusto (método Bazin, 6%) no fechamento de DD/MM".
- R-B2: aviso fixo no topo de cada aba: "Lista organizada por critério matemático sobre dividendos passados. Não é recomendação de investimento. O preço-teto depende de proventos passados, que podem não se repetir."
- R-B3: a ordem não indica qualidade, risco nem preço justo.
- R-B4: nenhuma frase liga o preço-teto à cotação do widget do momento.
- R-B5: nenhum número de cotação em texto estático; margem e liquidez só como dados do Monitor BESST, rotulados com a data do fechamento.

## 6. Engenharia
- `carteiras/besst-cotacoes/index.html` (cópia enxugada de `monitor/tempo-real/index.html`), lê `painel.json` de `../../dados/besst/painel.json`; `conjuntos.json` só com textos, glossário e limites (sem listas de papéis).
- Prefixo de armazenamento `besst-cotacoes-*`; carga de um setor por vez; limite de iframes; tempo de espera e reserva (lista de símbolos com link).
- `teste-simbolos.html` ampliado (lê `painel.json` e testa os 141 símbolos em páginas de 8) e `matriz_teste` com os símbolos aprovados e reprovados.
- `tests/test_besst_cotacoes.py` (ordem, limites, textos proibidos, símbolos aprovados, sem leitura de widget, dados do painel); workflow como o do tempo real; runbook 12; cartão na página inicial em "Carteiras de dividendos" com "Em construção".
- Se `painel.json` estiver velho (> 5 dias), a página avisa e usa a ordem alfabética.

## 7. Riscos que a Fase 0 deve avaliar
1. Parece "filtro de ações baratas" mesmo com aviso. Há risco regulatório de recomendação não autorizada? (CVM Res. 20/2021: análise de valores mobiliários.)
2. Conflito de interesse e conduta: o dono trabalha em instituição financeira; a lista inclui papéis de empresas de interesse dela. Verificação com o empregador é decisão do dono.
3. Os 141 símbolos podem não abrir todos no widget (alguns sem cotação ou com código diferente, como units).
4. Peso da página e limite de iframes.
5. A ordem pelo fechamento pode contradizer o widget do momento; como dizer isso para iniciantes.
6. Licenças: exibição de cotações da B3 via TradingView; mesma consulta formal pendente (e-mail, telefone e site do dono ainda por definir).

## 8. Pendências
- Consulta formal ao TradingView (autorizada, não enviada; faltam e-mail, telefone e URL).
- Decisão do dono: política do empregador.
