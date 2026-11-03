# Monitor BESST: parecer do painel de juízes (02/11/2026)

Juízes: **J1** professor de finanças/estatística · **J2** proteção ao investidor/educação financeira (ótica CVM) · **J3** engenharia de software/acessibilidade.
Base: bruto `dados/besst/brutos/ultimo.json` (pregão 30/10/2026). O script do Time C foi reexecutado sem internet, com `BESST_SAIDA` numa pasta temporária: **os campos da v1 têm 0 diferenças** em relação a `dados/besst/painel.json` (144 papéis), e a saída é idêntica ao `painel_v2.json` entregue. A página do Time B foi testada com Playwright em 1280/390 px, nos temas claro e escuro.

## 1. Notas e vereditos

| Time | Entrega | J1 | J2 | J3 | Nota | Veredito |
|---|---|---|---|---|---|---|
| C | Qualidade de dados (`besst_painel_v2.py`, `painel_v2.json`, `situacoes_especiais.json`) | 8,5 | 8 | 7,5 | **8,0** | **APROVAR COM AJUSTES** (vai primeiro) |
| B | UX iniciantes (`monitor_v2.html`) | 7 | 6,5 | 7,5 | **7,0** | **APROVAR COM AJUSTES** (depois do C, lendo os alertas do JSON) |
| A | Fundamentos: documento | 7 | 5 | – | 6,0 | Aprovar como **especificação da fase 2**, com ajustes |
| A | Fundamentos: `fundamentos_cvm.py` | 4 | – | 3 | **3,5** | **NÃO APROVAR** para produção (código nunca rodou com dados reais) |

## 2. O que foi verificado (amostra de 20 papéis recalculados à mão contra o bruto)
- **Todos os números do Time C conferem**: CEBR5 tem DPA de 2021–25 igual a 18,96/3,54/2,65/1,56/4,48. A média dá 6,24 e o teto 104,00. A média aparada dá 3,558 e o teto robusto 59,30. ITUB4 tem teto 31,29 e teto robusto 22,99 (2025 = 4,45 extraordinário, a bonificação de 2025 está no bruto). BPAR3 tem preço médio 182,07 idêntico de 2020 a 2025 com liquidez 0, o que gera `sem_negociacao`. BRSR3 tem margem de +7,3% e margem robusta de −2,5% (vira "acima"). BEES3 vai de −1,3% para +4,6%. ISAE3 tem 2024 = 0, que gera `lacuna`, e passa de −1,7% para +5,5%. GPAR3 tem teto 52,41 e teto robusto 0,29. AURE3 tem 2022 parcial (IPO) excluído. TAEE11 e BBAS3 ficam próximos da média. Contagens: 48 abaixo do teto na v1, 46 no teto robusto, 76 papéis com alerta, 24 dos 48 "abaixo" com alerta grave.
- **Problemas reais encontrados** (detalhados nos ajustes): CPFE3, PINE3, BPAC11/BPAC3, BBAS3, os graves que continuam "abaixo do teto robusto", os caminhos do script e as regras de alerta duplicadas entre B e C.
- **Página B**: nenhum erro de JavaScript. Os únicos erros são o `fetch` bloqueado em `file://` e as fontes bloqueadas de propósito. Não há rolagem lateral da página em 390 px (a tabela rola dentro do próprio contêiner). O "?" abre e fecha com Esc e devolve o foco. A ficha abre pelo teclado. **O simulador está correto**: R$ 1.000 ÷ 9,96 = 100 ações; 100 × DPA 1,302 = R$ 130,20/ano. Com R$ 5.000 dá 502 ações e R$ 653,60. O aviso "não é recomendação" fica visível acima da dobra nas 4 combinações.
- **Citações do Time A** conferidas: Piotroski (2000), QMJ (Rev. Acc. Studies 24(1), 2019) e Skinner & Soltes (RAS 16, 2011) existem e os DOIs batem. O "BBAS3 margem +41,8%, tendência −30,3%" confere com o painel. **Não foi possível confirmar** as colunas do FCA (`Codigo_Negociacao`, `CNPJ_Companhia`): o dicionário da CVM está apenas no ZIP de metadados.

## 3. Ajustes obrigatórios

### Time C (antes de ir para `scripts/`)
1. **Caminhos**: o padrão `BESST_DADOS=...` não existe no GitHub Actions. Além disso, `--coletar` grava o bruto em `SAIDA/brutos`, mas o recálculo lê de `BASE/brutos`, então a execução seguinte usa um bruto velho. Use o caminho relativo da v1 (`Path(__file__).parent.parent/"dados"/"besst"`), uma pasta só e saída `painel.json`.
2. **Tirar os anos-lacuna do DPA robusto**, como já é feito no teste de extraordinário. No CPFE3 (2024 = 2025 = 0, quase certamente falha da fonte), a aparada ainda inclui um zero: o teto robusto fica em 34,04, quando deveria ser cerca de 54. Daí saem também, em cascata, `tendencia_queda` e `dy12m_atipico` falsos.
3. **`margem_extrema`**: avaliar também `margem_robusta` (hoje escapam LIGT3 −139%, PSSA3 −103% e BRBI11 +63%). A margem negativa extrema **não deve ser "grave"**: BPAC11/BPAC3 (BTG, líquido) aparecem como grave só porque pagam pouco. Margem negativa extrema vira "atenção"; "grave" fica para dado inválido ou situação especial.
4. **Grave sem teto**: 22 papéis "grave" continuam com `status_robusto = abaixo_teto` (BSLI3/4 +64%, CEBR3/5/6 ~+60%, EKTR4, GEPA, CEEB, ENMT, REDE...). Para eles, criar `status_robusto = "nao_se_aplica"` (ou o campo `exibir_teto: false`).
5. **`sem_negociacao` por preço parado**: olhar só os 2 últimos anos. O PINE3 negocia R$ 111 mil/dia hoje e fica "grave" por preços repetidos entre 2019 e 2022.
6. **Absorver as regras do Time B** que faltam, para o JSON ser a fonte única: `tendencia ≤ −25` ("atenção"), `dy_12m < ½ dy_medio` e `baixa_liquidez` (R$ 50–500 mil). Hoje o BBAS3 sai "ok" no C, mas o provento caiu 30% e o DY 12m está em 4,0% contra 8,1% de média.
7. Corrigir a contagem no `qualidade.md`: são 55 "grave" no JSON (53 com cotação, mais NEOE3/SRNA3).

### Time B
1. **Não recalcular alertas na página.** Ler `nivel_alerta`, `alertas` e `alertas_texto` do JSON (Time C) e apagar a função `alerts()`. Hoje há divergência em 20 papéis (ex.: BRBI11 acusa "anos sem provento" por causa do ano do IPO, que o C já exclui; BPAC aparece sem alerta na página e grave no C).
2. **Três níveis visíveis**: "Grave: teto não se aplica" (esconde teto e margem na linha), "Atenção · n" e **"Nenhum alerta automático"** no lugar de "Sem alertas", que se lê como "seguro".
3. **Situação pelo teto robusto** (`status_robusto`/`preco_teto_robusto`). O Iniciante mostra só o robusto; o Completo mostra os dois, com o rótulo "Bazin clássico (média simples)".
4. **Tirar o verde de "Abaixo do teto"**: usar uma pílula neutra. Verde mais "Nenhum alerta" juntos se leem como sinal de compra.
5. **Ordem padrão**: não usar margem decrescente (hoje a 1ª linha é BRBI11 com +54%). Usar setor/empresa, ou nível de alerta e depois margem.
6. **Simulador**: usar o DPA robusto. Tirar "~R$ X por mês", porque proventos não são mensais e a frase sugere renda regular. Acrescentar "não considera variação do preço, custos nem impostos sobre dividendos futuros".
7. **Acessibilidade**: `--muted` sobre `--surface-2` tem contraste de 3,58:1 e as pílulas Atenção e Abaixo ficam em 4,2–4,3:1, abaixo do mínimo de 4,5:1 para texto pequeno. O botão "?" tem 18×18 px, menos que o alvo de 24 px do WCAG 2.2 (2.5.8).

### Time A (para ser reavaliado)
1. Rodar uma vez com internet, salvar fixtures (amostras de CSV) e criar testes para os 10 emissores listados, conferidos contra os releases. Sem isso, não entra no workflow.
2. Bugs: `nota()` dá **0 quando o lucro é desconhecido** (`ll=None`), contrariando "sem nota, não 0" (afeta Telecom, onde FCF e dívida existem sem o lucro). `pl_med` mistura o PL do ITR (jun/2026) com o PL de dez/2024: precisa ser o PL do início da janela LTM. `ltm()` volta ao dado anual em silêncio quando falta um componente. Uma falha no download da DFP derruba a execução inteira. Faltam limites de sanidade (ROE > 100%, payout negativo).
3. Payout = proventos **pagos** (DFC, caixa) ÷ lucro LTM (competência): há um descasamento de exercícios. Usar os proventos declarados (DMPL) ou deixar claro.
4. No texto: o art. 202 da Lei 6.404 diz que, com estatuto omisso, o dividendo obrigatório é **50%** do lucro ajustado. O piso de 25% vale para alteração do estatuto, e há exceções. As faixas do semáforo não têm fonte: apresentar como "convenção do painel".
5. **Matriz de rótulos**: "Oportunidade a estudar", "Evitar" e "Possível armadilha" atribuídos por ticker se leem como recomendação de compra ou venda, que é atividade de analista (Res. CVM 20/2021). Trocar por rótulos descritivos ("preço abaixo do teto · indicadores sem alerta", "preço abaixo do teto · indicadores fracos").

## 4. Discordâncias entre juízes
- **Teto clássico x robusto**: J1 quer mostrar os dois sempre, por fidelidade ao Bazin e transparência. J2 quer só o robusto para o iniciante, porque dois tetos confundem. *Resolução*: Iniciante mostra só o robusto; Completo mostra os dois.
- **Esconder os "grave" por padrão** (recomendação do C): J3 e J1 a favor. J2 prefere manter a linha visível com o teto oculto e o motivo em destaque, para o iniciante ver *por que* a "pechincha" de outros sites não vale. *Resolução*: a linha aparece, sem teto nem margem, e o filtro "esconder graves" vem desligado.
- **Faixa neutra**: J1 pede uma "perto do teto" (|margem robusta| < 10%), porque BRSR3 (−2,5%), BRSR5 (−0,5%), BEES3 (+4,6%) e ISAE3 (+5,5%) trocam de lado com qualquer centavo. J3 considera isso fora de escopo agora. Fica como **recomendado**, não obrigatório.
- **Time A**: J1 aproveitaria só a parte de bancos (ROE e payout) já na próxima versão. J3 veta qualquer integração sem teste. Prevalece o veto.

## 5. Plano de integração no repositório
1. **PR 1 (dados, Time C)**: aplicar os ajustes C1–C7. O script substitui `scripts/besst_painel.py`, `situacoes_especiais.json` vai para `dados/besst/` e a saída continua em `painel.json` (só acrescenta campos, a página atual segue funcionando). Teste no CI: os campos da v1 devem ter 0 diferenças contra o painel anterior com o mesmo bruto, e as contagens de alertas devem aparecer no log.
2. **PR 2 (página, Time B)**: aplicar B1–B7 com a página lendo os alertas do JSON. Smoke test com Playwright (1280/390, claro/escuro, sem `pageerror`, com `scrollWidth` igual à largura da janela). Publicar.
3. **Rotina**: revisar `situacoes_especiais.json` todo mês (Desktop/OPA, EMAE, BRB, Ambipar, Light). Trocar as fontes de notícia por fato relevante (CVM/B3) quando houver.
4. **Depois**: `proventos_correcoes.json` (CPFE3 2024–25, ISAE 2024, CPLE3 2025, BMEB 2025, conferidos no RI); contagem de pregões com negócio no bruto; tirar os deslistados (OIBR, NEOE3, SRNA3) do universo; cartões no celular; teste com 3 a 5 iniciantes.
5. **Fase 2 (Time A)**: workflow semanal separado gerando `fundamentos.json`, só depois de A1–A5 e da conferência manual. A página só exibe a nota depois de uma revisão do J2 sobre os rótulos. IF.data e SUSEP ficam para depois.
