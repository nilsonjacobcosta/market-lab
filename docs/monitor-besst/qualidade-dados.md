# Monitor BESST — auditoria de qualidade de dados (02/11/2026)

Base: `dados/besst/brutos/ultimo.json` (pregão 30/10/2026), 144 papéis no universo, 109 com cotação. Janela do DPA: 2021–2025.
Arquivos: `besst_painel_v2.py` (script), `painel_v2.json` (saída), `situacoes_especiais.json` (lista manual versionada).

## 1. Achados (evidência → regra)
| Caso | Evidência (DPA R$/ação; preço R$) | Regra |
|---|---|---|
| CEBR3/5/6 | 2021 = 18,96 (CEBR6 20,86) vs 1,6–4,5 nos outros anos; teto v1 104 x preço 23 (margem +78%) | extraordinário + margem extrema |
| ITUB3/4 | 2025 = 4,45 vs 0,80–2,13; DY 12m 3,08 | extraordinário, dy12m_atipico |
| GPAR3 | só 2022 = 15,67 (2021 = 0,05; 2023–25 = 0); liquidez 0; teto v1 52,4 → robusto 0,29 | esporádico + extraordinário + sem negociação |
| EKTR3/4 | 2024 = 10,89 vs 3,5–4,9; liquidez 0–10 mil | extraordinário + sem negociação |
| BAZA3 | DPA crescente (2,58→8,01), 12m = 11,98 (≈1,8× a mediana); liquidez 287 mil | dy12m_atipico (não recorrente) |
| GEPA3/4, SBSP3, EQTL3, PSSA3, AXIA3 | 2025 = 9,16 / 1,25 (vs 0,28) / 2,37 / 3,01 / 4,54 | extraordinário |
| BPAR3 | preço médio 182,07 idêntico 2020–2025; liquidez 0 | sem_negociacao (preço parado) |
| PINE3 | preço médio 9,53 idêntico 2019–2022 | sem_negociacao |
| CEED3/4 | preço 10,00/20,00 redondos; CEED4 20,0 em 2025 e 2026; liquidez 0; sem proventos | sem_negociacao |
| EMAE3/4, CASN3/4 | só 2026 na fonte; EMAE3 = 150,00 fixo, liquidez 0 | histórico curto + sem negociação (+ OPA EMAE) |
| CPFE3 | 2024 = 0 e 2025 = 0 entre 2,89 (2023) e 3,73 (12m) | lacuna_proventos (provável falha da fonte) |
| ISAE3/4 (2024), CPLE3 (2025), BMEB3/4 (2025 = 0,02) | ano zerado/quase zero entre anos pagadores | lacuna_proventos |
| CMIG3 x CMIG4 | 2022: 1,966 x 1,507 | divergencia_classes |
| COCE3 x COCE5 | 12m: 0,24 x 1,48 | divergencia_classes |
| RPAD3/6 x RPAD5, BMIN3 x BMIN4 | ON quase sem proventos; PN com dividendo fixo | divergencia_classes (estrutural, conferir) |
| AXIA7 | classe nova (2025–26), sem proventos | histórico curto |
| BSLI3/4 (BRB) | margem +70%, preço 2,10 vs média 2025 8,53, 0 provento em 12m | situação especial + margem extrema + preço desabou |
| AMBP3 (RJ), OIBR3/4 (falência, deslistada 16/09/2026), LIGT3 (RJ encerrada 09/09/2026, diluição) | AMBP3 0,14 "abaixo do teto" na v1 | situação especial |
| DESK3 (OPA Claro pendente), NEOE3/SRNA3 (OPA concluída) | DESK3 margem −2.615% | situação especial + margem extrema |
| Margens absurdas (20 papéis) | RPAD3/6 −20.000%, DESK3, CBEE3 −330%, SBSP3 −264%, BPAC −280 a −390%, PINE, BMEB, EQTL; +60 a +78%: CEBR, BSLI, EKTR4, GPAR3 | margem_extrema (> 60% ou < −100%) |

Desdobramentos/bonificações: verificados os 70 eventos do bruto; nenhum caso claro de ajuste mal aplicado. Units conferem com ON+PN (SANB11 = SANB3+SANB4; TAEE11/ALUP11 = 3× ON; SAPR11, ENGI11, BPAC11 ok). A regra `ajuste_suspeito` marcou só CEBR5 (salto 2020→2022 ≈ 5×, igual ao desdobramento 5:1) — provável falso positivo (CEB pagou mais após vender a distribuidora), mas vale conferir.

## 2. Regras implementadas (campo `alertas`)
- **DPA robusto**: média aparada (tira o maior e o menor ano) com 5 anos completos; mediana com 3–4. O 1º ano de séries iniciadas após 2019 (IPO) é tratado como parcial e fica de fora. Novos campos: `dpa_mediana`, `dpa_aparada`, `dpa_robusto`, `preco_teto_robusto`, `margem_robusta`, `status_robusto`.
- `extraordinario`: ano > 2× a mediana dos demais (sem os anos-lacuna) **e** > 1,5× cada ano vizinho (pico, não crescimento gradual).
- `lacuna_proventos`: ano < 10% da mediana dos anos pagadores, com pagamento antes e depois (inclui o ano corrente). Só para quem pagou em ≥ 3 anos.
- `proventos_esporadicos`: pagou em ≤ 2 dos anos. `dy12m_atipico`: proventos 12m > 1,75× o DPA robusto.
- `sem_negociacao`: liquidez < R$ 50 mil/dia **ou** preço médio anual idêntico em anos seguidos (substituto do "preço não muda em X% dos pregões", porque o bruto não guarda a série diária).
- `historico_curto`: < 5 anos completos. `situacao_especial`: lista manual `situacoes_especiais.json` (por ticker; com fonte, data e texto para iniciante).
- `divergencia_classes`: ON x PN da mesma empresa com soma 5 anos fora de 0,8–1,25, um ano com diferença > 30% ou 12m > 2× (units ficam de fora).
- `ajuste_suspeito`, `margem_extrema`, `tendencia_queda` (último ano ≤ −50% da média), `preco_desabou` (preço < 50% da média do último ano), `sem_proventos_12m`.
- `nivel_alerta`: "grave" (situação especial, sem negociação ou margem extrema), "atencao" (outros) ou "ok"; `alertas_texto` traz uma frase curta por alerta.

## 3. Mediana x média para o preço-teto
- **Média (Bazin original)**: o livro usa a média dos dividendos recentes (6% sobre ela). É fiel ao método, simples de explicar e capta a tendência. Mas um único ano atípico desloca o teto: CEBR 104 → 59, GPAR3 52 → 0,3.
- **Mediana**: imune a até 2 anos atípicos em 5, mas ignora a magnitude e é "degrau" com poucos pontos (um ano a mais muda bastante o valor). Penaliza quem cresce o dividendo (ITUB teto 31 → 23) e é instável com n = 3–4.
- **Média aparada (escolhida com n = 5)**: meio-termo. Usa 3 anos e corta 1 extremo de cada lado. Resiste a um ano extraordinário e a uma lacuna. É conservadora (bom para iniciante) e fica perto da média quando os dados são limpos (BBAS3 28,3 x 28,7; TAEE11 63,5 x 62,6).
- Recomendação: mostrar **os dois** valores. Usar o robusto para a cor/semáforo e manter a média simples como "Bazin clássico", com o rótulo explícito.

## 4. Resultado v1 x v2 (mesmo bruto; campos v1 idênticos aos do painel do repo)
- **Abaixo → acima do teto (5)**: BRSR5, BRSR3 (margem pequena: 10% → −0,5%; 7% → −2,5%), AURE3 (+27% → −63%; 2023 extraordinário), GPAR3 (+62% → −6.700%), AMBP3 (+12% → −22%; RJ).
- **Acima → abaixo (3)**: BEES3, BEES4 (−1% → +5%), ISAE3 (−2% → +5,5%; lacuna 2024 puxava a média). Total abaixo do teto: 48 (v1) → 46 (robusto).
- **Alertas**: 76 papéis (74 dos 109 com cotação, mais NEOE3/SRNA3). Nível: 53 grave, 21 atenção, 35 ok. Mais frequentes: sem_negociacao 37, extraordinario 29, dy12m_atipico 20, margem_extrema 20, historico_curto 12, situacao_especial 11.
- **Ponto central**: dos 48 papéis "abaixo do teto" na v1, **24 têm alerta grave** e 7 têm atenção; só 17 ficam limpos (BBAS3, SANB3/4/11, BRSR6, BBDC3/4, ABCB4, BRSR3, BMGB4, TAEE3/4/11, EGIE3, EQPA3, WIZC3, BBSE3). As maiores "pechinchas" da v1 (CEBR +78%, BSLI +71%, EKTR4 +63%, GPAR3 +62%, GEPA, CEEB, ENMT, REDE) são todas artefatos: provento extraordinário, papel sem negócio ou crise.

## 5. Recomendações
1. No painel, ordenar/filtrar por `status_robusto` e esconder por padrão os "grave" (com um botão "mostrar todos"). Exibir `alertas_texto` como ícone de alerta com tooltip.
2. Versionar `situacoes_especiais.json` no repo (dados/besst/) e revisar todo mês (RI, fatos relevantes da CVM). Casos a acompanhar: Desktop (edital da OPA), EMAE (2ª etapa da OPA), BRB (balanços/aumento de capital), Ambipar (AGC), Light (pós-RJ).
3. Guardar no bruto a contagem de pregões com negócio e a variação diária no ano (ou o nº de dias com volume > 0). Assim `sem_negociacao` passa a usar "% de pregões sem negócio" (ex.: > 50%) em vez do proxy de preço médio repetido.
4. Conferir na fonte primária (RI/B3) as lacunas: CPFE3 2024–25, ISAE 2024, CPLE3 2025, BMEB 2025. Se confirmadas como falha do Yahoo, criar um arquivo de correções manuais (`proventos_correcoes.json`).
5. Remover ou isolar do universo papéis deslistados (OIBR3/4, NEOE3, SRNA3) para não poluir as contagens.
6. Para integrar ao repo: copiar o script para `scripts/` com `BESST_SAIDA` apontando para `dados/besst` e `painel_v2.json` → `painel.json` (o formato só acrescenta campos, então é compatível com a página atual).
