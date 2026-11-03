# RB 07 — Falha na publicação da qualidade financeira (beta): aceite reprovado

**Última revisão deste runbook:** 2026-11-03 · **Responsável:** Nilson (dono)

## 1. Objetivo
Entender por que a rotina de qualidade financeira não publicou (`fundamentos.json` parado), corrigir o que for **dado**
(mapa, universo) e separar o que for **código** (para revisão), sem nunca afrouxar o aceite para "passar".

## 2. Quando fazer (gatilhos)
- Execução vermelha em **Atualizar qualidade financeira (BETA)** (`.github/workflows/fundamentos-besst.yml`, agendada
  07h43 e 19h13 de Brasília, todo dia).
- `gerado_em` de `dados/besst/fundamentos.json` com mais de 48 h (verificação semanal do calendário).
- Depois de mudar `universo.json` ou `mapa_ticker_cvm.csv` (para confirmar que o aceite continua limpo).

## 3. Arquivos afetados
| Arquivo | Papel |
|---|---|
| `scripts/fase2/fundamentos_cvm.py` | baixa DFP (3 anos), ITR (ano anterior e corrente), FCA (3 anos) e cadastro da CVM; calcula ROE, payout, dívida líquida/EBITDA, semáforo e nota |
| `scripts/fase2/aceite.py` | mede os critérios de aceite (lê também `dados/besst/painel.json` para saber quais papéis estão sem cotação) |
| `scripts/fase2/publicar.py` | grava `dados/besst/fundamentos.json` **só** se o aceite estiver limpo; senão imprime `NÃO PUBLICADO. Falhas no aceite: [...]` e sai com código 1 |
| `tests/test_fase2.py` | testes unitários (8 em 03/11/2026); falha aqui bloqueia tudo |
| `dados/besst/fundamentos.json` | publicado (campos `beta`, `gerado_em`, `fonte`, `data_base_mais_recente`, `aviso`, `aceite`, `papeis`) |
| `dados/besst/fase2_teste/` | saídas do teste manual: `aceite.json`, `fundamentos.json`, `fundamentos_falha_forcada.json`, `log_execucao.json`, `log_fundamentos.txt`, `log_falha_forcada.txt` |

Regras de bloqueio (`publicar.py`): reprova se
- qualquer chave com **"(meta 0)"** não estiver vazia: `payout_acima_150_sem_flag`, `lucro_zero_aceito`,
  `roe_com_pl_negativo`, `nota_com_lucro_ausente`, `nota_com_dado_antigo`, `nota_com_metrica_descartada`, `nota_sem_cotacao`;
- `emissores_mapeados_pct (meta >=95)` < 95; `emissores_com_dado_ate_15m_pct (meta >=90)` < 90;
  `papeis_com_nota_pct (meta >=75)` < 75; `payout_calculado_nos_lucrativos_pct (meta >=90)` < 90;
- `papeis_com_excecao` não vazio.
São **informativos** (não bloqueiam): `flags_verificar`, `sem_mapeamento` (bloqueia indiretamente pelo % mapeado),
`dado_antigo`, `sem_dfp`, `universo_inteiro_com_nota_pct`, `execucao_com_download_forcado_a_falhar`.

Referência de 03/11/2026 (aceite limpo): mapeados 100,0%; dado ≤ 15 meses 96,9%; com nota 88,1%; payout 93,9%;
109 papéis negociados, 65 emissores; `dado_antigo`: AMBP e BSLI (23 meses).

## 4. Fontes, em ordem de confiança
| Ordem | Fonte | URL |
|---|---|---|
| 1 | CVM Dados Abertos (DFP/ITR/FCA/CAD; DFP, ITR e FCA atualizados **semanalmente**, cadastro diário) | `https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/{DFP,ITR,FCA}/DADOS/…` e `.../CAD/DADOS/cad_cia_aberta.csv` |
| 1 | CVM — lista mensal de companhias inadimplentes (para explicar `dado_antigo`) | ex.: https://www.gov.br/cvm/pt-br/assuntos/regulados/consultas-por-participante/companhias/companhias-inadimplentes/2026/companhias-abertas-inadimplentes-marco-2026 — **verificada 03/11/2026** (edital de 05/03/2026; a lista muda todo mês) |
| 2 | Release/ITR no RI da empresa | conferência manual de números |

## 5. Passo a passo

### 5.1 Ler a falha na própria execução (2 minutos)
Actions → **Atualizar qualidade financeira (BETA)** → execução vermelha → passo vermelho:
| Passo vermelho | Significado | Ação |
|---|---|---|
| **Testes unitários (bloqueiam a publicação)** | o código mudou e quebrou uma regra | não é dado: reverter o último commit de `scripts/fase2/` ou corrigir com revisão |
| **Coletar e calcular** | exceção geral (rede, CVM fora, timeout de 40 min) | ver mensagens `download falhou: <arquivo> <erro>`; tentar de novo mais tarde (§5.3) |
| **Medir aceite** | o JSON de entrada não foi gerado ou está corrompido | ver passo anterior |
| **Publicar só se o aceite estiver limpo** | **aceite reprovado** — o normal deste runbook | a linha `NÃO PUBLICADO. Falhas no aceite: [...]` diz quais critérios; o passo **Medir aceite** mostra o `aceite.json` inteiro (ele é impresso com `cat`) |

### 5.2 Rodar o teste completo e guardar os arquivos (`fase2-teste.yml`)
A rotina diária grava em `/tmp/f2` e **não guarda** os arquivos. Para investigar com calma:
1. Actions → **Fase 2 - teste de fundamentos (CVM)** → **Run workflow** → *Branch: main* → **Run workflow**.
2. Ela roda os testes, os fundamentos, um teste de robustez (download da DFP 2024 forçado a falhar) e o aceite, e faz
   commit em `dados/besst/fase2_teste/` ("Fase 2: resultado do teste de fundamentos (CVM)"). Leva ~5–20 min.
3. `git pull` e leia o aceite:
```python
import json
a = json.load(open("dados/besst/fase2_teste/aceite.json", encoding="utf-8"))
for k, v in a.items():
    if "(meta 0)" in k and v:
        print("FALHA", k, v)
for k, m in (("emissores_mapeados_pct (meta >=95)", 95), ("emissores_com_dado_ate_15m_pct (meta >=90)", 90),
             ("papeis_com_nota_pct (meta >=75)", 75), ("payout_calculado_nos_lucrativos_pct (meta >=90)", 90)):
    if a.get(k, 0) < m:
        print("FALHA", k, a.get(k))
if a.get("papeis_com_excecao"):
    print("FALHA papeis_com_excecao", a["papeis_com_excecao"])
print("sem_mapeamento:", a.get("sem_mapeamento"), "| dado_antigo:", a.get("dado_antigo"), "| sem_dfp:", a.get("sem_dfp"))
print("robustez:", a.get("execucao_com_download_forcado_a_falhar"))
```
4. Para um papel específico: `dados/besst/fase2_teste/fundamentos.json` (chaves `erro`, `erros`, `flags`, `motivo_sem_nota`,
   `mapeamento`, `referencia`); downloads que falharam e motivo de mapeamento: `log_execucao.json`
   (`downloads_falhos`, `mapa`, `conferencia`).

### 5.3 O que fazer para cada falha
| Critério reprovado | Causa provável | Ação |
|---|---|---|
| `emissores_mapeados_pct` < 95 / `sem_mapeamento` cheio | ticker novo/trocado, reorganização | **RB 05** (e RB 03 se for deslistagem) |
| `emissores_com_dado_ate_15m_pct` < 90 | empresas sem entregar balanço (ver `dado_antigo`), ou download de DFP/ITR falhou (`downloads_falhos`) | se download: rodar de novo mais tarde; se inadimplência real: conferir lista de inadimplentes da CVM e o RI; se o papel estiver em crise, RB 02. **Não** reduzir a meta |
| `papeis_com_nota_pct` < 75 | muitos `sem_nota` (`motivo_sem_nota`) | contar motivos (snippet abaixo); se "o lucro do período não aparece" disparar em muitos, a CVM pode ter mudado descrições de contas → código |
| `payout_calculado_nos_lucrativos_pct` < 90 | DVA com descrição nova de "remuneração de capitais próprios" | ver `conferencia` no `log_execucao.json` (linhas da DVA de 12 emissores de referência) → código |
| qualquer "(meta 0)" | uma trava de segurança deixou passar um caso | **código** (ex.: `nota_com_dado_antigo`) — abrir issue com o ticker; não editar dados para esconder |
| `papeis_com_excecao` | erro dentro de um papel (`"erro": "excecao"`, `erros: [...]`) | se `KeyError` com nome de setor → `setor` inválido no `universo.json` (RB 03 §3); outros → código |
```python
import json, collections
f = json.load(open("dados/besst/fase2_teste/fundamentos.json", encoding="utf-8"))
print(collections.Counter(v.get("motivo_sem_nota") or v.get("erro") for v in f.values()).most_common())
```

### 5.4 Disparar a publicação de novo
Depois de corrigir **dado** (commit feito): Actions → **Atualizar qualidade financeira (BETA)** → **Run workflow** →
*main*. Ou: `gh workflow run fundamentos-besst.yml -R nilsonjacobcosta/market-lab`.

### 5.5 Rodar localmente (opcional; baixa ~150–200 MB)
```bash
python3 -m unittest tests/test_fase2.py -v
mkdir -p /tmp/f2
python3 scripts/fase2/fundamentos_cvm.py --painel dados/besst/painel.json --saida /tmp/f2/fundamentos.json \
  --log /tmp/f2/log.json --cache /tmp/cache_cvm
python3 scripts/fase2/aceite.py /tmp/f2/fundamentos.json > /tmp/f2/aceite.json
python3 scripts/fase2/publicar.py /tmp/f2/fundamentos.json /tmp/f2/aceite.json /tmp/f2/publicado_teste.json
```
Use `--cache` fora do repositório: o padrão é `.cache_cvm` na pasta atual e ele **não** está no `.gitignore`
(cuidado para não commitar). Rode da raiz do repo (o `aceite.py` lê `dados/besst/painel.json` por caminho relativo).

## 6. Como validar
- Execução verde e a linha `Publicado: dados/besst/fundamentos.json 144 papéis` no passo de publicação.
- `fundamentos.json`: `gerado_em` novo; `aceite` com os 4 percentuais acima das metas; `data_base_mais_recente`
  coerente (ex.: `2026-09-30` em 03/11/2026).
- Página: rodapé "Dados financeiros até dd/mm/aaaa · gerado em dd/mm".
- Se nada de novo entrou na CVM, a publicação muda só `gerado_em` — normal (aconteceu em 03/11/2026).

## 7. Como publicar (commit)
A rotina faz o commit ("Qualidade financeira (beta): atualização …"). Correções de dado seguem o runbook de cada
arquivo (RB 03, RB 05). Mudanças em `scripts/fase2/` ou `tests/` precisam de: testes passando localmente + teste
`fase2-teste.yml` com aceite limpo **antes** de ir para a rotina diária. Registre em `manutencao/registro.md`.

## 8. Se a fonte mudar ou falhar
- **CVM fora do ar:** o script registra `download falhou` e segue; o aceite tende a reprovar e o arquivo público
  continua o anterior (seguro). Esperar e rodar de novo; não há fonte alternativa automática.
- **Nomes de arquivos/colunas mudaram** (ex.: novo leiaute de DFP): rode `python3 scripts/fase2/diagnostico_cvm.py`
  (grava em `dados/besst/fase2_teste/diagnostico.json` os arquivos de cada ZIP, as colunas e contas de referência)
  e compare com o que `fundamentos_cvm.py` espera (`URL_DFP`, `URL_ITR`, `URL_FCA`, `URL_CAD`, padrões `_(BPA|BPP|DRE|DFC_MI|DFC_MD|DVA)_(con|ind)_AAAA.csv`,
  colunas `CD_CVM`, `ORDEM_EXERC`, `DT_FIM_EXERC`, `DT_INI_EXERC`, `CD_CONTA`, `DS_CONTA`, `VL_CONTA`, `ESCALA_MOEDA`, `VERSAO`).
- **Mudança de ano:** em janeiro, o script passa a pedir `itr_cia_aberta_<ano novo>.zip`, que pode ainda não existir →
  `download falhou` para esse arquivo; o LTM cai para o exercício anterior (flag `sem ITR`), sem bloquear. Verificar em janeiro.

## 9. Registro de execuções
Em `manutencao/registro.md`.

## 10. Riscos e cuidados
- Nunca editar `publicar.py`/`aceite.py` para baixar metas sem decisão do dono registrada (foram exigência dos juízes).
- O `fase2-teste.yml` faz commit em `dados/besst/fase2_teste/` mesmo com erros (passos com `continue-on-error`): é
  área de diagnóstico, não de publicação.
- A qualidade financeira é **beta** e o lucro é **contábil** (IFRS/Cosif), não "recorrente": não é recomendação.
