# Manutenção do Monitor Portugal (Euronext Lisbon)

Instruções para manter o que **não se atualiza sozinho** no Monitor Portugal e o que fazer quando a rotina falha.
Página: `portugal/monitor/` (publicada como material de estudo; cartão na página inicial desde 04/11/2026). Dados: `dados/portugal/`. Código: `scripts/portugal/`.

> Material educativo, não é recomendação de investimento. O dono assumiu o risco regulatório de manter o preço-teto
> (decisão de 04/11/2026); por isso a página segue voluntariamente os requisitos de apresentação objetiva do
> Regulamento Delegado (UE) 2016/958: autor, data, factos vs cálculo, fontes, metodologia, riscos e histórico.
> Ponto em aberto: parecer jurídico sobre comunicação à CMVM (Reg. CMVM 2/2007); publicação aberta foi decisão do dono.

## O que é automático
- `.github/workflows/monitor-portugal.yml`, dias úteis às 17h23, 17h48, 18h37 e 20h12 UTC (depois do fecho de Lisboa, 16h30 locais):
  testes → coleta (preços .LS, taxa do BCE, lista da Euronext) → critérios de aceite → commit de `painel.json`, `brutos/ultimo.json`, `historico_status.json`.
- Se uma fonte falhar, o script mantém o último dado guardado (preço por papel, taxa, lista) e a página mostra a data real.
- Se os testes falharem, **nada é publicado** e a página continua com a versão anterior.

## Qualidade financeira (BETA) — automática, semanal
- `.github/workflows/portugal-fundamentos.yml` (segundas, 06h41 UTC, e manual). Lê os relatórios anuais ESEF de cada empresa em
  filings.xbrl.org (lista de relatórios com país PT; associação por nome em `NOMES` do script), calcula ROE, payout declarado
  (DPA do exercício no cadastro ÷ lucro por ação básico) e dívida líquida/EBITDA, com as faixas e a regra de nota do Monitor BESST.
- `scripts/portugal/aceite_fundamentos.py` só publica `dados/portugal/fundamentos.json` se: ≥ 90% com relatório, ≥ 90% com lucro,
  ≥ 75% com nota **e** o lucro de 2025 de BCP, Galp, Jerónimo Martins, EDP, NOS e EDP Renováveis bater com o divulgado (≤ 2%).
- Rubricas próprias das empresas (extensões ESEF) ficam no dicionário `EXTENSOES` do script — mapa explícito, conferido à mão.
- Diagnóstico: correr o workflow com "descobrir" ligado; o log mostra LEI, relatórios, rubricas usadas e candidatas.

### Runbook 4 — nova época de relatórios (abril/maio de cada ano)
1. Na 1.ª segunda-feira de maio, confirme no log que o exercício mais recente passou a ser o novo ano.
2. Atualize `LUCRO_REFERENCIA_<ano>` no aceite com o lucro atribuível divulgado (comunicado de resultados) de pelo menos 6 empresas.
3. Empresa sem EBITDA ou dívida: corra o diagnóstico, procure a rubrica nas candidatas e acrescente-a a `EXTENSOES` com nota no registo.

## O que é manual

| Tarefa | Arquivo | Quando |
|---|---|---|
| Cadastrar proventos novos | `dados/portugal/proventos_oficiais.csv` | após cada comunicado de pagamento; revisão geral em **junho** (fim da época de AG) e **janeiro** (antecipados de dezembro) |
| Resolver alerta "evento não cadastrado" | idem | sempre que aparecer na ficha |
| Promover linhas `a_conferir` para `oficial` | idem | mensal até zerar |
| Revisão do universo (corte de liquidez) | `dados/portugal/universo.json` | trimestral (próxima: ver `proxima_revisao`) + saída de bolsa / OPA |
| Revisão dos parâmetros do teto (prémio, mínimo) | `dados/portugal/parametros.json` | anual (novembro); mudar só com nota no registo |
| Feriados da Euronext | `scripts/portugal/painel_pt.py` (`feriados_euronext`) | anual (dezembro), conferir calendário da Euronext |

## Runbook 1 — cadastrar um provento
1. Fonte, por ordem: comunicado da empresa (página de investidores ou anexo em live.euronext.com) → sistema de difusão da CMVM → página "dividendos" da empresa. Imprensa só como reforço, nunca como `oficial`.
2. Acrescente uma linha **por pagamento** (não por ano): `papel,data_pagamento,valor_bruto,tipo,exercicio,estado,fonte_url,nota`.
   - `valor_bruto`: antes da retenção de 28%. `tipo`: `dinheiro`, `scrip` (valor de referência/preço fixo do direito) ou `especie` (não entra no cálculo).
   - `estado`: `oficial` só com link para documento da empresa. Data aproximada → dia 15 e nota "dia aproximado".
3. Rode `python3 -m unittest tests/test_portugal.py` e `python3 scripts/portugal/painel_pt.py` (recalcula sem coletar).
4. Confira na ficha que o alerta "evento não cadastrado" sumiu. Commit só com os caminhos alterados. Linha no `manutencao/registro.md`.

Sites que bloqueiam leitura automática da nuvem (abrir no Chrome do dono): Millennium bcp, Navigator, Altri (links gerados por script), CMVM.

## Runbook 2 — revisão do universo
1. Rode o workflow **"Portugal - teste de cobertura"** (manual). Leia no log a tabela de liquidez e o detalhe por papel.
2. Regra: mediana do volume financeiro diário ≥ 100 mil € e ≤ 5% de dias sem negócio; sem emitentes estrangeiros.
3. Papel novo: acrescente em `universo.json` (ISIN da lista da Euronext) **e** os proventos de 5 anos no cadastro antes de publicar.
4. Atualize `revisado_em` e `proxima_revisao`; registo em `manutencao/registro.md`.

## Runbook 3 — falha da rotina
- Selo "Atrasado" na página: veja a última execução em Actions. Erro de fonte (403/timeout) → espere a próxima tentativa; repetido 2 dias → registe e abra investigação.
- Teste vermelho: leia qual. `J1Cadastro` = erro no CSV; `Aceite.test_cobertura_de_precos` = mais de um papel sem preço (fonte fora do ar ou código mudou → ver lista da Euronext).
- Taxa com origem "reserva": a API do BCE falhou e não havia valor guardado; confira a série `IRS/M.PT.L.L40.CI.0000.EUR.N.Z`.

## Pendências (04/11/2026)
- Altri 2022–2024 e 2026: obter comunicados (numerário/espécie) e passar a `oficial`.
- Jerónimo Martins, Navigator e Semapa 2026: confirmar valores do exercício de 2025.
- Corticeira Amorim 2022: a tabela da empresa tem parcelas que somam 0,275 e total 0,29 — confirmar no comunicado.
- Galp: EBITDA não etiquetado (sem resultado operacional nem antes de impostos no ESEF) — dívida/EBITDA em branco; nota com ROE e payout.
- Altri e Ibersol: payout do exercício de 2025 acima de 150% (dividendos acima do lucro) → "sem nota" pela regra de plausibilidade.
- Controlo acionista e situações especiais.
- Parecer jurídico (J2) recomendado; publicação aberta decidida pelo dono com risco assumido (04/11/2026).
