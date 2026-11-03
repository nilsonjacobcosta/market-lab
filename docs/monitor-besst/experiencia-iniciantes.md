# Monitor BESST: avaliação de UX para iniciantes (02/11/2026)

Base: `work/monitor.html` + `dados/besst/painel.json` (144 papéis, 84 empresas, pregão 30/10/2026).

## 1. Avaliação heurística (Nielsen + clareza para leigos)

| # | Problema | Heurística | Risco para o iniciante | Grav. |
|---|---|---|---|---|
| 1 | Pílula verde "Abaixo do teto" é o sinal mais forte da tela | Correspondência com o mundo real; prevenção de erro | Ler verde = comprar. 48 papéis "abaixo do teto", vários com provento em queda ou ilíquidos | Alta |
| 2 | Jargão sem definição no ponto de uso (DPA, DY, teto, margem, tendência) | Reconhecer em vez de lembrar; ajuda | Definições só no rodapé; quem lê a tabela não as encontra | Alta |
| 3 | DY 12m e DY médio lado a lado, sem explicação | Correspondência; consistência | Confundir rendimento atual com média histórica (ex.: BBAS3 4,0% contra 8,1%) | Alta |
| 4 | Uma linha por código: 144 linhas para 84 empresas | Minimalismo; modelo mental | Achar que SANB3/SANB4/SANB11 são três empresas; "diversificar" na mesma empresa | Alta |
| 5 | Ordenação padrão por margem traz no topo papéis com margem de 60–78% | Prevenção de erro | CEBR3/5/6, BSLI3/4, EKTR4 têm margem enorme e liquidez de R$ 0–180 mil/dia; teto inflado por anos que não se repetem | Alta |
| 6 | Alertas espalhados (cor da tendência, ⚠ de liquidez, texto na ficha) | Visibilidade do estado | Sem resumo por linha, o iniciante não percebe 2–3 problemas somados | Média |
| 7 | Proventos extraordinários elevam a média e não são sinalizados | Visibilidade; prevenção de erro | 41 papéis com um ano ≥ 2× a mediana dos outros (ex.: ITUB 2025) | Média |
| 8 | Ficha só com números; sem tradução para "quanto eu recebo" | Correspondência com o mundo real | Não consegue ligar % a reais | Média |
| 9 | Estatais rotuladas, sem explicar o que isso muda | Ajuda e documentação | Badge colorido sem leitura de risco/benefício | Média |
| 10 | "Não é recomendação" só no rodapé | Prevenção de erro | Aviso aparece depois da conclusão | Média |
| 11 | Cabeçalhos ordenáveis só por clique no `<th>` (sem teclado); 11 colunas | Acessibilidade; flexibilidade | Ordenar sem mouse é impossível; tabela larga em 390px sem coluna fixa | Média |
| 12 | Ficha dentro de tabela de 980px: em 390px o texto exige rolagem lateral | Estética/uso móvel | Leitura cortada no celular | Baixa |

## 2. Melhorias priorizadas (valor × esforço)

1. Aviso visível no topo + reescrita de "Abaixo do teto" como filtro, não sinal (alto/baixo). **Feito**
2. "?" em cada coluna com definição de uma frase + glossário completo (alto/baixo). **Feito**
3. Modo **Iniciante** padrão: uma linha por `empresa` (papel de maior `liquidez_mil`), 8 colunas; "Completo" mostra os 144 papéis e 12 colunas (alto/médio). **Feito**
4. Coluna **Alertas** (semáforo "Atenção · n" / "Sem alertas" / "–") com regras explícitas + filtro "Só sem alertas" (alto/médio). **Feito**
5. Guia "Como ler este painel em 4 passos", recolhível e lembrado (alto/baixo). **Feito**
6. Frase-resumo e simulador "se eu investir R$ X" na ficha (alto/baixo). **Feito**
7. Caixa de estatal (benefício/risco) e tabela "outros códigos da mesma empresa" com classe ON/PN/Unit (médio/baixo). **Feito**
8. Acessibilidade e celular: ordenação por `<button>`, `aria-sort`, `caption`, contagem `aria-live`, popover fecha com Esc e devolve o foco, foco preservado ao abrir ficha; 1ª coluna fixa; no celular o controle vira selo sob o nome; ficha com largura da tela (alto/baixo). **Feito**

### Regras de alerta (todas sobre campos do JSON)
- `tendencia` ≤ −25 → provento em queda.
- `baixa_liquidez` → pouca negociação (< R$ 500 mil/dia).
- `anos_historico` < `metodo.anos` → histórico curto.
- 0 < `anos_com_provento` < `anos_historico` → anos sem provento (o zero entra na média).
- Ano completo (anterior ao ano do pregão) com provento ≥ 2× a mediana dos demais → possível extraordinário.
- `dy_12m` < ½ `dy_medio` ou > 2× `dy_medio` → últimos 12 meses fora do padrão.
- `margem` ≥ 50 → margem exagerada, investigar.

Frase-resumo: `dpa_medio`, `dpa_medio/preco` (rendimento da média ao preço de hoje), `dy_12m`, `preco_teto`, `margem`. Simulador: nº de ações = ⌊valor/preço⌋; renda/ano = ações × `dpa_medio` e ações × preço × `dy_12m`; valores brutos, com nota sobre os 15% de IR no JCP. Classe pelo sufixo do código (3 ON; 4/5/6 PN; 11 Unit).

## 3. Implementação e testes
- Arquivo: `work/times/monitor_v2.html` (mesmos tokens claro/escuro, fontes, placeholder `/*DADOS*/null`, fetch de `../../dados/besst/painel.json` com fallback). Sem bibliotecas novas, sem alert/confirm; localStorage só via try/catch (modo, filtros, guia, valor do simulador).
- Versão com dados: `work/times/monitor_v2_built.html`. `node --check` OK.
- Playwright: 1280px e 390px (claro e escuro) sem erros de página (único erro é o bloqueio intencional de fontes/JSON no teste); `scrollWidth` = largura da janela nos dois modos e com a ficha aberta. Testados: popover, simulador, agrupamento (Taesa → TAEE11 + TAEE4/TAEE3), abrir a ficha pelo teclado.
- Capturas: `v2_1280*.png`, `v2_390*.png`, `v2_390_dark*.png`, `v2_390_tabela.png`, `v2_390_classes.png`.

## 4. Fica para depois
- Visão em cartões no celular, no lugar da tabela, para o modo Iniciante.
- Proventos sem IR (separar JCP de dividendos exige o tipo de provento no JSON, que hoje não existe).
- Sinalizar ano de IPO, porque o ano zerado de BRBI11 em 2021 dispara "anos sem provento"; precisa da data de listagem no JSON.
- Mostrar a regra de alerta que disparou também em texto curto na linha, sem precisar abrir a ficha.
- Teste de uso com 3 a 5 iniciantes: entendem "teto" como filtro? Leem os alertas?
- `th` fixo no topo ao rolar a página, hoje impedido pelo `overflow-x` do contêiner.
- Contraste de `--muted` sobre `--surface-2` em textos de 0,72rem: auditar com ferramenta.
