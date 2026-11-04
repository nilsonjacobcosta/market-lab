# Manutenção do Monitor Portugal (Euronext Lisbon)

Instruções para manter o que **não se atualiza sozinho** no Monitor Portugal e o que fazer quando a rotina falha.
Página: `portugal/monitor/` (link não divulgado; `noindex`). Dados: `dados/portugal/`. Código: `scripts/portugal/`.

> Material educativo, não é recomendação de investimento. O dono assumiu o risco regulatório de manter o preço-teto
> (decisão de 04/11/2026); por isso a página segue voluntariamente os requisitos de apresentação objetiva do
> Regulamento Delegado (UE) 2016/958: autor, data, factos vs cálculo, fontes, metodologia, riscos e histórico.
> Ponto em aberto: parecer jurídico sobre comunicação à CMVM (Reg. CMVM 2/2007) antes de qualquer divulgação do link.

## O que é automático
- `.github/workflows/monitor-portugal.yml`, dias úteis às 17h23, 17h48, 18h37 e 20h12 UTC (depois do fecho de Lisboa, 16h30 locais):
  testes → coleta (preços .LS, taxa do BCE, lista da Euronext) → critérios de aceite → commit de `painel.json`, `brutos/ultimo.json`, `historico_status.json`.
- Se uma fonte falhar, o script mantém o último dado guardado (preço por papel, taxa, lista) e a página mostra a data real.
- Se os testes falharem, **nada é publicado** e a página continua com a versão anterior.

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
- Fase seguinte: indicadores de qualidade financeira a partir dos relatórios anuais ESEF/iXBRL; controlo acionista.
- Parecer jurídico (J2) antes de divulgar o link.
