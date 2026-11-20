# Cotações do BESST — Fase 0 (proposta, versão 3)

Data: 19/11/2026. Etapa anterior à construção. **Nenhuma página foi criada e nada será construído antes do "sim" do dono.**
Esta versão incorpora os quatro pareceres (Mercados 6,5; Didática 6,5; Regulatório 6,5; Engenharia 6,5; todos "aprovar com ajustes"). Resumo dos pareceres em `pareceres-fase0.md`.

## 1. Objetivo
Página nova em "Carteiras de dividendos" com cotações atrasadas (widgets do TradingView) dos papéis do Monitor BESST (Bancos, Energia, Seguros, Saneamento, Telecomunicações), uma aba por setor, no modelo Iniciante/Avançado dos painéis do market-lab.
- Nome: **Cotações do BESST**. Pasta: `carteiras/besst-cotacoes/`. Link cruzado com `carteiras/monitor-besst/`.
- Decisões já tomadas pelo dono (19/11/2026): nome e pasta; critério "abaixo do preço-teto robusto primeiro e, dentro deles, por liquidez"; Fase 0 com especialistas, sem construir antes do "sim".

## 2. Dados (corrigido após os pareceres)
- Fonte: `dados/besst/painel.json` (153 KB, ~23 KB comprimido). O arquivo tem 141 papéis, mas **só 107 têm preço**. Os outros 34 só têm `status = sem_cotacao` e nunca entram em widget (aparecem só como texto).
- Com preço, por setor: Energia 50, Bancos 35, Saneamento 9, Telecomunicações 9, Seguros 4. (Sem filtro: 69/39/10/10/13.)
- `pregao_referencia` e `fase` (fechamento ou intradiário) são campos do **topo** do arquivo; por papel existe `data` (hoje: 99 papéis com 17/11, 6 com 19/11, 2 com 22/09, estes OIBR3/OIBR4). O rótulo da página usa o topo e mostra `fase`, `gerado_em` e "carregado às HH:MM".
- Margem: (teto − preço)/teto no fechamento; só aparece rotulada com a data. Liquidez: rótulo a confirmar em `scripts/besst_painel.py` antes de escrever "negociação diária" (pendência de Engenharia).
- Leitura: `fetch("../../dados/besst/painel.json?t=...", {cache:"no-store"})`, padrão do Monitor BESST. Validar esquema (papeis é lista; cada item com ticker e setor; descartar sem preço; tratar liquidez e margem nulas sem deixar `null` virar zero na ordenação).

## 3. Algoritmo de ordem (sem ambiguidade)
1. **Excluir da lista principal** (vão para "Fora dos critérios", só texto e link, sem widget, com o motivo vindo dos campos de alerta, passando por `esc()`): sem preço, `nivel_alerta = grave`, `baixa_liquidez`, `sem_proventos`, `historico_curto`, `nao_se_aplica`, sem preço-teto robusto.
2. Grupo A: `abaixo_teto` (e `abaixo_teto_conferir`, só com a marca "conferir", ver decisão D3). Grupo B: `acima_teto`.
3. Dentro de cada grupo: `liquidez_mil` decrescente; empate por ticker crescente (comparador total, sem `localeCompare`).
4. Resultado simulado hoje: **42 papéis na lista principal** (Energia 16, Bancos 15, Saneamento 5, Seguros 4, Telecomunicações 2); 65 fora com preço; 34 sem cotação. Dos 23 abaixo do teto, 19 entram (4 caem por baixa liquidez, e a página diz isso). Saneamento e Telecomunicações têm 0 papéis abaixo do teto e Seguros 2: a aba diz "N de M papéis abaixo do teto" e não mostra só o grupo B sem aviso.
5. A ordem é uma "ordem de leitura" do fechamento, não ranking. A ordem **nunca** é recalculada com valores do widget.

## 4. Modos e carga
- **Iniciante:** 5 abas; em cada, 5–6 papéis (um por empresa, ver D2) em 1 widget; "O que esta página não diz" visível antes da lista; alerta de cada papel visível; textos abertos.
- **Avançado:** páginas de 8 com "Anterior / Próximos 8" **substituindo** o widget atual (1 iframe por vez, no máximo 2 com pré-carga pedida; limite em constante testada); coluna textual com margem, liquidez, controle e alertas do Monitor BESST; seção "Fora dos critérios".
- Tabela HTML acessível (texto nosso) como parte principal, widget como complemento; abas legíveis no celular; só se montam widgets para tickers **aprovados** na matriz de teste; os demais ficam na lista textual com "sem teste no widget".
- Carregamento: ver decisão D4 (ao abrir ou após clique).

## 5. Regras de redação (herdam R-TR1 a R-TR5; R-B1 a R-B5 da v1 mantidas e acrescentadas)
- R-B1 a R-B5 como na v1.
- R-B6: proibido "melhores", "top", "destaque", "desconto", "oportunidade", "barata", "compre", "recomendada"; teste automático com radicais.
- R-B7: critério único, mecânico, igual para todos os leitores; sem personalização, sem filtro por perfil.
- R-B8: sem receita, anúncio, afiliado, doação ou captação de contato.
- R-B9: declaração de conflito de interesse visível: o autor trabalha no mercado financeiro e pode ter posições nos papéis; sem nome, cargo ou logotipo do empregador.
- R-B10: aviso de privacidade antes do primeiro widget (terceiro, TradingView, recebe dados de acesso).
- R-B11: fórmula pública (método Bazin 6%, média aparada de 5 anos) e data do fechamento escritas na própria página.

## 6. Engenharia
- `index.html` derivado de `monitor/tempo-real/index.html`; `conjuntos.json` só com textos, glossário, limites e `matriz_teste`; prefixo `besst-cotacoes-*`.
- Ordenação em função pura `ordem.js` (sem DOM, sem `Date.now`), testada com `node --test` sobre fixtures (partição completa, resultado igual com entrada embaralhada, nenhum grave/baixa liquidez/sem teto na principal, abaixo antes de acima, liquidez não crescente) e teste vivo de invariantes sobre o `painel.json` real (avisa, não falha).
- `tests/test_besst_cotacoes.py` adaptado de `test_tempo_real.py` (regex de números com lista permitida para margem e liquidez rotuladas; `rotularIframe` passa a 1 ocorrência).
- `teste-simbolos.html` novo: 107 símbolos (não 141), em lotes de 3 iframes e grupos de 8, o dono marca aprovado/reprovado e exporta JSON para `matriz_teste`. Prioridade: os 42 da principal, AXIA3/AXIA7, units (…11) e uma amostra das classes 3, 4, 5, 6.
- **Nenhuma ação da B3 está registrada como testada** no repositório; o formato `BMFBOVESPA:XXXX` é provável, mas o teste do dono é pré-condição.
- Painel velho: usar o calendário de pregões do Monitor BESST (copiar FERIADOS; registrar no RB 04). Atrasado: aviso claro e mantém a ordem do arquivo; cai para ordem alfabética só com atraso ≥ 5 pregões ou JSON inválido. Falha de leitura: mensagem + link ao Monitor BESST.
- Workflow como o do tempo real (PR, cron e dispatch; sem gatilho em `painel.json`, que o bot commita direto); runbook 12; ajustar RB 03 (34 sem cotação) e RB 04; `calendario.md` trimestral; cartão "Em construção" na página inicial.

## 7. Decisões do dono (19/11/2026, 17:50)
- **D1 Ordem:** mantida a que o dono pediu: "abaixo do teto robusto primeiro, por liquidez". A página oferece também ordem alfabética (seletor do leitor).
- **D2 Uma empresa por vez no Iniciante:** aprovado (o papel de maior liquidez de cada empresa).
- **D3 Faixas de margem** descritivas, sem cortar a lista; `abaixo_teto_conferir` não vem à frente: aprovado.
- **D4 Carregamento:** só após o clique.
- **D5 Empregador:** não será feita consulta; o dono entende que, por ser conteúdo de estudo e sem consultoria, não é necessária, e a página explicita isso. (Os especialistas de Regulatório recomendaram a consulta como pré-condição; fica registrado que a decisão é do dono.)
- **D6 TradingView:** carregamento com opção de ligar (botão "Carregar ao trocar de setor", desligado por padrão, guardado em `besst-cotacoes-auto`). Em 20/11/2026 o dono dispensou a consulta formal ao TradingView, por já existir a opção de ligar e desligar o carregamento dos widgets.
- **D7 Conflito de interesse:** a página não faz declaração pessoal sobre o autor; reforça que é didática (teste automático impede declaração pessoal).
- **Construção e publicação autorizadas** pelo dono (19/11/2026), com a rodada de juízes antes do merge.

## 8. O que esta proposta não resolve
- Nenhum teste ao vivo no TradingView foi feito (sem acesso de rede neste ambiente); símbolos, peso e comportamento com 8 símbolos dependem do Chrome do dono.
- Risco CVM 20/2021 avaliado como baixo a moderado por Regulatório, sem porto seguro textual; conclusão jurídica é de advogado.
- Origem e licença do `painel.json` (preços e proventos) a registrar.
