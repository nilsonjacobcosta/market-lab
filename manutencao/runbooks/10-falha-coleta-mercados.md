# RB 10 — Falha na coleta do painel Mercados e ciclos

> Material educativo. Nada aqui é recomendação de investimento. Não crie tokens nem credenciais.

**Última revisão deste runbook:** 2026-11-17 · **Responsável:** dono do repositório (ou IA em nova sessão)

## 1. Objetivo
Manter o `mercados.json` da branch `dados-mercados` atualizado, ou deixar a página avisando com clareza quando não estiver.

## 2. Quando fazer (gatilhos)
- Periódico: nos primeiros dias depois de ligar o painel, conferir a aba Actions → "Atualizar Mercados e ciclos"; depois, a cada semana.
- Por evento: workflow vermelho; faixa de aviso de coleta atrasada na página; muitas séries com a etiqueta "anterior".
- Sinal de atraso: a página mostra "ATENÇÃO: a última coleta tem N dias" (a partir de 5 dias).
- Falha geral (nenhuma série coletada) ou reprovação no aceite deixa o job vermelho e a publicação não roda; o arquivo publicado antes fica como está e a página avisa quando ele passa de 5 dias. Falha de algumas séries não deixa o job vermelho: elas saem com a etiqueta "anterior" (ver o aviso de 3 dias ou mais).

## 3. Arquivos afetados
| Arquivo | Campos que mudam | Quem lê |
|---|---|---|
| `scripts/mercados/catalogo_series.json` | códigos das séries, `min_pontos`, `defasagem_max_dias`, `coletar` | coleta e aceite |
| `scripts/mercados/aceite.py` | regras de aceite | workflow |
| branch `dados-mercados`, arquivo `mercados.json` | publicado pelo workflow | `monitor/mercados/index.html` |

## 4. Fontes, em ordem de confiança
| Ordem | Fonte | Observação |
|---|---|---|
| 1 | BCB (SGS), FRED, Eurostat, BCE | oficiais; ver a tabela de verificação em `monitor/mercados/README.md` |
| 2 | Yahoo Finance (endpoint chart) | não é oficial; pode bloquear o IP do Actions ou mudar sem aviso |

## 5. Passo a passo
1. Abra Actions → "Atualizar Mercados e ciclos" → última execução. Veja qual passo falhou: testes, coleta ou aceite.
2. Aceite reprovado: leia a lista de erros no log (série, motivo). Causas comuns: série com poucos pontos (ajustar `min_pontos` só se a fonte realmente tem menos histórico), série "ok" com dado velho demais (conferir a fonte; ajustar `defasagem_max_dias` só com justificativa), menos de 60% das séries com dado (fonte fora do ar ou bloqueio).
3. Coleta com muitas séries "anterior": rode localmente `MERCADOS_SAIDA=/tmp/m.json python3 scripts/mercados/coletar_mercados.py` num computador com acesso às fontes e veja os avisos; ambientes de IA costumam receber 403.
4. Yahoo bloqueando o Actions (429 ou 403 nas 25 séries do Yahoo): aguardar e rodar de novo pelo botão "Run workflow"; se persistir, registrar e avaliar outra fonte (não contornar bloqueio).
5. Se uma série foi descontinuada ou mudou de código: corrigir o catálogo, atualizar o campo `verificado` com a data e a evidência, e rodar os testes.

## 6. Como validar
```bash
python3 -m unittest discover -s tests
python3 scripts/mercados/gerar_amostra.py
python3 scripts/mercados/aceite.py --amostra monitor/mercados/_amostra/mercados.json
```
Depois da publicação, abra a página e confira a data da coleta e a contagem de séries atualizadas.

## 7. Como publicar (commit)
```bash
git add scripts/mercados/catalogo_series.json scripts/mercados/aceite.py tests/test_mercados.py
git commit -m "Manutenção: coleta de Mercados — <resumo> (fonte: <documento>)"
git pull --rebase && git push
```
Acrescente a linha em `manutencao/registro.md` no mesmo commit.

## 8. Se a fonte mudar ou falhar
- Não reprovar o painel inteiro por uma série secundária: marque `coletar: false` no catálogo, registre o motivo em `observacao` e avise na página (a série sai como "sem dados").
- Se o FRED, o Eurostat ou o BCE mudarem o formato, atualize `scripts/mercados/fontes.py` e o teste com uma amostra real da nova resposta.
- A branch `dados-mercados` cresce a cada commit (o arquivo tem cerca de 1 MB); se ficar pesada, faça o squash do histórico da branch de dados (ela não tem código).
