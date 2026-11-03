# RB NN — Título curto da tarefa

> Copie este arquivo para `runbooks/NN-nome-da-tarefa.md`, preencha todas as seções e acrescente uma linha no índice
> do `README.md` e no `calendario.md`. Seção que não se aplica: escreva "não se aplica" (não apague).

**Última revisão deste runbook:** AAAA-MM-DD · **Responsável:** nome

## 1. Objetivo
Uma ou duas frases: que dado fica correto ao final e por que isso importa para quem usa o painel.

## 2. Quando fazer (gatilhos)
- Periódico: (ex.: todo 1º dia útil do mês).
- Por evento: (ex.: alerta X apareceu; rotina Y falhou; fato relevante de OPA).
- Sinal de que está atrasado: (ex.: campo `atualizado` com mais de 60 dias).

## 3. Arquivos afetados
| Arquivo | Campos que mudam | Quem lê |
|---|---|---|

## 4. Fontes, em ordem de confiança
| Ordem | Fonte | URL (verificada em AAAA-MM-DD?) | O que procurar |
|---|---|---|---|
| 1 | Regulador (CVM/B3/BCB/ANEEL/SUSEP) | | |
| 2 | RI da empresa | | |
| 3 | Imprensa reconhecida (reforço) | | |
| 4 | Alternativa (só contexto, rotulada) | | |

## 5. Passo a passo
1. `cd market-lab && git pull`
2. ...
(Comandos copiáveis. Quando houver consulta reproduzível, dar o Python mínimo, só biblioteca padrão.)

## 6. Como validar
- Comando de checagem (ex.: `python3 -m json.tool arquivo.json > /dev/null`).
- O que deve aparecer na página / no JSON gerado.

## 7. Como publicar (commit)
```bash
git add <arquivos>
git commit -m "Manutenção: <tarefa> — <resumo> (fonte: <documento>)"
git pull --rebase && git push
```
E acrescentar a linha em `manutencao/registro.md` no mesmo commit.

## 8. Se a fonte mudar ou falhar
- Sintoma → caminho alternativo, em ordem.
- O que **nunca** fazer (ex.: preencher com fonte não confiável sem rótulo).

## 9. Registro de execuções
Não registre aqui: use `manutencao/registro.md` (colunas: data, quem, runbook, o que mudou, fonte, commit).

## 10. Riscos e cuidados
- Risco → mitigação.
