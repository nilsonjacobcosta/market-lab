# RB 12 — Página Cotações do BESST (símbolos, universo, feriados e termos do TradingView)

**Última revisão deste runbook:** 2026-11-19 · **Responsável:** Nilson (dono)

## 1. Objetivo
Manter correta a página `carteiras/besst-cotacoes/`: só papéis com teste registrado abrem em widget, a ordem de leitura segue o critério escrito na página, o calendário de pregões coincide com o do Monitor BESST e os termos do TradingView foram relidos.

## 2. Quando fazer (gatilhos)
- Periódico: todo trimestre (junto do RB 11): reler os termos do TradingView e rodar `teste-simbolos.html` para papéis novos.
- Por evento: o universo do Monitor BESST mudou (RB 03: papel novo, renomeado ou que passou a ter cotação, como AXIA3/AXIA7); widget vazio ou com erro; feriados do ano seguinte (RB 04, o `ordem.js` tem uma cópia da lista).
- Sinal de atraso: o workflow semanal mostra `::warning::` de papéis com cotação sem teste, ou o teste de feriados falha.

## 3. Arquivos afetados
| Arquivo | Campos que mudam | Quem lê |
|---|---|---|
| `carteiras/besst-cotacoes/conjuntos.json` | `matriz_teste` (`simbolos_aprovados`, `reprovados`, `data_teste`), textos, glossário | página |
| `carteiras/besst-cotacoes/ordem.js` | `FERIADOS`, regras de ordem (mudar regra é decisão do dono) | página e testes |
| `dados/besst/painel.json` | gerado pelo Monitor BESST; **não editar à mão** | página |

## 4. Fontes, em ordem de confiança
| Ordem | Fonte | O que procurar |
|---|---|---|
| 1 | Teste do dono no navegador (`teste-simbolos.html`) | o papel aparece com valor no widget Market Quotes |
| 2 | Termos do TradingView (`tradingview.com/policies/`) | mudança de uso permitido de widgets |
| 3 | Ofício circular da B3 | feriados (RB 04) |

## 5. Passo a passo
1. `cd market-lab && git pull`
2. Abrir `carteiras/besst-cotacoes/teste-simbolos.html` no navegador (grupos de 8; no máximo 3 carregados ao mesmo tempo).
3. Para cada papel novo, marcar "abriu" ou "não abriu" e clicar em "Gerar JSON".
4. Colar o resultado em `matriz_teste` de `conjuntos.json`, **somando** aos símbolos já registrados, e atualizar `data_teste`.
5. Rodar os testes (seção 6) e anotar em `registro.md`.
6. Observação: o teste atual do `painel.json` tinha 107 papéis com preço e 34 sem cotação em 19/11/2026 (o RB 03 cita 35 em 03/11/2026, valor datado).

## 6. Como validar
```bash
python3 -m unittest tests/test_besst_cotacoes.py -v
node --test tests/ordem.test.js
```
Na página: abrir um setor, clicar em "Carregar cotações" e conferir que cada papel aparece com valor. Papéis sem teste devem mostrar "sem teste no widget" na tabela.

## 7. Como publicar (commit)
```bash
git add carteiras/besst-cotacoes manutencao/registro.md
git commit -m "Manutenção: Cotações do BESST — <resumo>"
```

## 8. Plano B
Se o widget deixar de abrir para todos os papéis, a página continua útil: a tabela e os links para o TradingView não dependem do widget. Se o TradingView proibir o uso, remover `montarWidget` e deixar só a tabela.
