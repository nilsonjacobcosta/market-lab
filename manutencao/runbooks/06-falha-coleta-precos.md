# RB 06 — Falha na coleta de preços e proventos (Yahoo) e selo de atraso

**Última revisão deste runbook:** 2026-11-03 · **Responsável:** Nilson (dono)

## 1. Objetivo
Recolocar o painel com o **fechamento do último pregão** quando a rotina automática não rodou, falhou, ou a fonte
(Yahoo Finance) mudou/caiu — sem nunca publicar preço inventado ou de fonte sem reputação.

## 2. Quando fazer (gatilhos)
- O selo do topo mostra **"⚠ Dados do pregão de dd/mm/aaaa: a atualização automática atrasou…"** (regra: depois das
  22h30 de um dia de pregão, espera-se `pregao_referencia` = hoje; fora disso, o pregão anterior, pelo calendário do RB 04).
- O selo mostra "⚠ Preços de dd/mm coletados às hh:mm, antes do fechamento…" (alguém disparou a coleta durante o pregão).
- Execução com ✗ vermelho em **Atualizar Monitor BESST** na aba Actions.
- Falso alarme no selo em feriado → não é este runbook: RB 04.

## 3. Arquivos afetados
| Arquivo | Campos | Quem grava |
|---|---|---|
| `dados/besst/brutos/ultimo.json` | por ticker: `[preço, data, preço médio por ano, proventos por ano, proventos 12m, desdobramentos, liquidez R$ mil]` | `besst_painel.py --coletar` |
| `dados/besst/painel.json` | `gerado_em` (Brasília), `pregao_referencia` (data mais recente entre os papéis), `fase` (`intradiario`/`fechamento`), `coletado_em_utc`, `papeis[]` | idem |

Rotina: `.github/workflows/monitor-besst.yml` ("Atualizar Monitor BESST"), dias úteis, tentativas em UTC
`22,47 21 * * 1-5`, `23 22,23 * * 1-5` e `9 1 * * 2-6` (= 18h22, 18h47, 19h23, 20h23 e 22h09 de Brasília);
grupo de concorrência `monitor-besst-precos`; limite de 20 min. Na prática **toda execução bem-sucedida faz commit**
(até 5 por dia útil): `gerado_em` e `coletado_em_utc` mudam a cada coleta, então "Sem mudanças" quase nunca aparece,
nem em feriado (conferido no código do workflow e de `besst_painel.py` em 03/11/2026).

Comportamento do script em falha (`scripts/besst_painel.py`):
- erro num ticker → imprime `<TICKER> erro <mensagem>` e segue (35 papéis sempre dão erro: RB 03);
- menos de 50 papéis coletados → encerra com **"Coleta incompleta (N papéis); painel mantido."** (execução vermelha,
  `painel.json` intacto);
- resposta em formato diferente (ex.: sem `indicators`/`quote`) → exceção (`KeyError`/`TypeError`) e execução vermelha,
  `painel.json` intacto.
Ou seja: em falha, a página continua com o último dado bom e o selo avisa. Isso é o comportamento desejado.

## 4. Fontes, em ordem de confiança
| Ordem | Fonte | URL | Uso |
|---|---|---|---|
| Atual | Yahoo Finance (API de gráfico, ~15 min de atraso) | `https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}.SA?period1=…&period2=…&interval=1d&events=div%2Csplit` — **verificada indiretamente** (rotina ok em 03/11/2026) | preços, proventos por data-ex, desdobramentos |
| Alt. 1 (mesmo provedor) | Yahoo, outro host | `https://query2.finance.yahoo.com/v8/finance/chart/...` — **não verificada** | só contorna queda do host `query1`; não é fonte independente |
| Alt. 2 (oficial, só preços) | **B3 — COTAHIST** (série histórica oficial) | layout **verificado**: https://www.b3.com.br:443/data/files/33/67/B9/50/D84057102C784E47AC094EA8/SeriesHistoricas_Layout.pdf; download na página "Cotações históricas" da B3 (**não verificada**; padrão de arquivo diário conhecido na comunidade `COTAHIST_DddmmAAAA.ZIP`, **não confirmado**) | conferir/substituir **preço de fechamento** (`PREULT`) e volume (`VOLTOT`). Não traz proventos nem ajuste de desdobramento |
| Proventos | CVM (IPE: avisos aos acionistas; DFP/DVA) e RI | ver RB 09 | conferir proventos |
| Conferência pontual | página da empresa na B3 / site da sua corretora | — | checar 3–5 fechamentos à mão |
| **Não usar** | APIs que exigem cadastro/token, sites de cotação sem reputação | — | (restrição do projeto: não criar credenciais) |

## 5. Passo a passo

### 5.1 Diagnóstico (5 minutos)
1. Veja o que a página tem: abra `https://nilsonjacobcosta.github.io/market-lab/dados/besst/painel.json` e leia
   `gerado_em`, `pregao_referencia`, `fase`. Ou, no repositório:
```python
import json
p = json.load(open("dados/besst/painel.json", encoding="utf-8"))
print(p["gerado_em"], p["pregao_referencia"], p["fase"], p["coletado_em_utc"],
      sum(1 for x in p["papeis"] if x["status"] != "sem_cotacao"), "com cotação")
```
2. Aba **Actions** → **Atualizar Monitor BESST**. Três situações:
   - **Nenhuma execução hoje** depois das 18h22: o GitHub atrasou/descartou os agendamentos (acontece; a documentação
     do GitHub avisa que `schedule` pode atrasar ou ser descartado em horário de pico) → §5.3.
   - **Execução vermelha** → abra-a, clique no passo vermelho e leia as últimas linhas:
     | Mensagem | Causa | Ação |
     |---|---|---|
     | `Coleta incompleta (N papéis); painel mantido.` | Yahoo recusou/limitou (muitos `erro HTTP Error 429/401/403`) ou caiu | esperar 30–60 min e §5.3; se repetir no dia seguinte, §8 |
     | `Traceback … KeyError: 'indicators'` (ou `'quote'`, `'timestamp'`) | formato da resposta mudou | §8.2 |
     | `! [rejected] main -> main (fetch first)` | outro commit chegou antes do push (aconteceu em 03/11/2026 21:36 UTC, antes de existir o `git pull --rebase`) | só rodar de novo (§5.3); a rotina atual já faz `git pull --rebase` |
     | `CONFLICT` no `git pull --rebase` | alguém editou `painel.json`/`ultimo.json` à mão ao mesmo tempo | rodar de novo; se persistir, ver §10 |
     | `This scheduled workflow is disabled…` (aviso no topo da página da rotina) | o GitHub desativa agendamentos em repositório público sem atividade por 60 dias | botão **Enable workflow** |
   - **Execução verde** mas o selo reclama (`pregao_referencia` continua no pregão anterior) → a fonte ainda não tinha
     o fechamento do dia quando rodou; espere a próxima tentativa ou §5.3 depois das 18h30.
3. Teste a fonte para um papel líquido (no seu computador; o ambiente de IA costuma receber 403 do Yahoo):
```bash
curl -s -A "Mozilla/5.0" "https://query1.finance.yahoo.com/v8/finance/chart/BBAS3.SA?range=5d&interval=1d" | head -c 600; echo
```
   Resposta com `"timestamp":[…]` e `"close":[…]` = fonte ok. `Too Many Requests`, `Unauthorized` ou HTML = bloqueio/mudança.

### 5.2 Quando NÃO disparar
Entre 10h e 18h20 (pregão + atraso da fonte) a coleta grava preço intradiário (`fase: "intradiario"`) e o selo passa a
avisar que não é fechamento. Dispare depois das 18h20 (ideal: depois das 18h30).

### 5.3 Disparo manual (botão Run workflow)
Pelo navegador (não precisa de token):
1. github.com/nilsonjacobcosta/market-lab → aba **Actions**.
2. Na lista da esquerda, **Atualizar Monitor BESST**.
3. Botão **Run workflow** (à direita, acima da lista) → *Branch: main* → **Run workflow**.
4. Atualize a página depois de ~1 min; a execução leva 2–4 min. Verde = ok. Depois disso, a rotina
   "pages-build-deployment" republica o site (1–2 min).

Pelo terminal (se o `gh` já estiver autenticado na máquina do dono):
```bash
gh workflow run monitor-besst.yml -R nilsonjacobcosta/market-lab
gh run watch -R nilsonjacobcosta/market-lab
```
(Documentação: https://docs.github.com/actions/using-workflows/manually-running-a-workflow — verificada.)

### 5.4 Coleta local de teste (sem mexer no repositório)
```bash
cp -r dados/besst /tmp/besst_teste
BESST_BASE=/tmp/besst_teste python3 scripts/besst_painel.py --coletar
python3 -c "import json;p=json.load(open('/tmp/besst_teste/painel.json'));print(p['pregao_referencia'],p['fase'])"
```
Se funcionar no seu computador e falhar no GitHub, o Yahoo está bloqueando os servidores do GitHub → §8.1.

## 6. Como validar
- `painel.json`: `pregao_referencia` = último pregão (hoje, se já passou das 18h30 de um dia útil), `fase` = `fechamento`,
  ~109 papéis com cotação (35 sem cotação é o normal até o RB 03 limpar o universo).
- Página: selo "Fechamento do pregão de dd/mm/aaaa · atualizado dd/mm às hh:mm", sem ⚠.
- Conferência por amostragem (recomendada pelos juízes, P1-8): 3–5 papéis líquidos (BBAS3, ITUB4, TAEE11, SAPR11, VIVT3)
  contra o fechamento na página da B3 ou na corretora; diferença esperada ≤ 0,5%.

## 7. Como publicar (commit)
A rotina faz o commit sozinha ("Monitor BESST: atualização automática AAAA-MM-DD HH:MM UTC"). Não faça commit manual de
`painel.json`/`ultimo.json` vindos de coleta local, a não ser como último recurso (§8.3). Registre a ocorrência em
`manutencao/registro.md` (data, sintoma, causa, ação).

## 8. Se a fonte mudar ou falhar
### 8.1 Yahoo fora ou bloqueando (um dia)
Não fazer nada além de §5.3 em horários diferentes; o selo avisa o usuário. Registrar.
### 8.2 Formato da resposta mudou (vários dias)
1. Salve uma resposta de exemplo: `curl -s -A "Mozilla/5.0" "…/chart/BBAS3.SA?range=5d&interval=1d&events=div%2Csplit" > /tmp/amostra.json`.
2. Compare com o que `coletar()` espera: `chart.result[0].timestamp`, `indicators.quote[0].close`/`.volume`,
   `events.dividends{…: {date, amount}}`, `events.splits{…: {date, numerator, denominator}}`.
3. Ajuste `coletar()` em `scripts/besst_painel.py` (mudança de código: testar localmente com §5.4 e comparar
   `painel.json` antes/depois — preços e `proventos_ano` dos 109 papéis devem bater com a versão anterior).
### 8.3 Yahoo indisponível por mais de uma semana (plano B oficial)
- Preços: B3 COTAHIST. Leitura mínima de um arquivo diário já baixado e descompactado (layout oficial; posições 1-based
  do PDF convertidas para Python):
```python
precos = {}
for l in open("COTAHIST_D03112026.TXT", encoding="latin-1"):
    if l[:2] != "01" or l[24:27] != "010":          # 01 = registro de cotação; 010 = mercado à vista
        continue
    precos[l[12:24].strip()] = (l[2:10], int(l[108:121]) / 100, int(l[170:188]) / 100)  # data, PREULT, VOLTOT (R$)
print(precos.get("BBAS3"))
```
  Isso **não** substitui o histórico de proventos e de desdobramentos do Yahoo: usar COTAHIST exige mudar `coletar()`
  (tarefa de desenvolvimento, com revisão). Até lá, mantenha o último dado bom com o selo de atraso.
- Considere avisar na faixa de aviso do topo da página (linha ~200 do `index.html`) que os preços estão parados e por quê.
### 8.4 Nunca
Preencher preços à mão, copiar de site sem reputação ou criar token para outra API.

## 9. Registro de execuções
Em `manutencao/registro.md` (inclua o link da execução do Actions).

## 10. Riscos e cuidados
- Disparo durante o pregão gera `fase: "intradiario"`; se depois alguém recalcular localmente sem `--coletar` após as
  18h20, o script marcaria `fechamento` sobre preço intradiário. Por isso: recálculo local só com bruto coletado após o fechamento.
- Edição manual simultânea de `painel.json` causa conflito no `git pull --rebase` da rotina: prefira deixar o
  recálculo para a rotina (RB 01–03 explicam quando vale recalcular localmente).
- Proventos entram pela **data-ex** (não pelo anúncio): um provento anunciado hoje só aparece na data-ex.
- O agendamento do GitHub não é garantido: em 03/11/2026 só 1 de 9 horários rodou (ver `docs/monitor-besst/primeiro-pregao-dados.md`).
  O commit 65a84c4 registrou a decisão de **não** usar agendador externo (que exigiria token): o plano de contingência
  é este runbook (disparo manual pelo botão).
