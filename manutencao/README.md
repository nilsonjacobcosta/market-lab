# Pasta de manutenção do market-lab (Monitor BESST)

Esta pasta guarda as **instruções exatas** para manter os dados do Monitor BESST que **não se atualizam sozinhos**,
e o que fazer quando uma rotina automática falha. Foi escrita para que qualquer pessoa — ou uma IA em outra sessão —
consiga repetir a manutenção **sem depender da memória de conversas anteriores**.

> Material educativo. Nada aqui é recomendação de investimento (Res. CVM 20/2021).
> Não crie tokens nem credenciais para executar estes procedimentos: tudo é feito pelo navegador do GitHub,
> pelo `gh` já autenticado do dono ou localmente com `python3` (biblioteca padrão).

## Antes de começar (uma vez)

- Ter o repositório clonado (`git clone https://github.com/nilsonjacobcosta/market-lab`) e `python3` 3.10+ instalado.
  Todos os comandos e blocos Python rodam **na raiz do repositório**; os que baixam da CVM precisam de internet sem
  bloqueio a `dados.cvm.gov.br` (ambientes de IA costumam receber 403 — rode no computador do dono).
- Editar JSON pelo editor do navegador do GitHub é possível, mas **sem** a validação do §6 de cada runbook. Use-o só se
  puder rodar a validação localmente antes do commit; não existe hoje checagem automática desses arquivos.
- Nos commits, sempre `git add` com os caminhos listados no runbook (nunca `git add .`): há pastas de cache locais
  (`.cache_cvm/`) fora do `.gitignore`.
- Blocos com `XXXX3` ou CNPJ `00000000000000` são modelos: troque antes de rodar.

## Como usar

1. Veja no [calendário](calendario.md) o que vence hoje (ou abra o runbook do problema que apareceu).
2. Siga o runbook do começo ao fim. Cada um tem: gatilho, arquivos, fontes em ordem de confiança, passo a passo,
   validação, publicação (commit) e plano B se a fonte mudar.
3. Ao terminar, **acrescente uma linha** em [registro.md](registro.md) (data, quem, o que mudou, commit).
4. Se descobrir que uma URL, coluna ou comando mudou, **corrija o runbook no mesmo commit**.

## Índice

| Arquivo | Tarefa | Frequência | Automático? |
|---|---|---|---|
| [calendario.md](calendario.md) | Agenda de todas as tarefas | — | — |
| [MODELO-runbook.md](MODELO-runbook.md) | Modelo para escrever um runbook novo | — | — |
| [registro.md](registro.md) | Log das execuções de manutenção | a cada execução | — |
| [runbooks/01-controle-acionario.md](runbooks/01-controle-acionario.md) | `estatais.json` (estatal, privada, controlador) | a cada 60 dias + eventos | Não (conferência mensal **planejada**) |
| [runbooks/02-situacoes-especiais.md](runbooks/02-situacoes-especiais.md) | `situacoes_especiais.json` (RJ, falência, OPA) | mensal + eventos | Não |
| [runbooks/03-universo-papeis.md](runbooks/03-universo-papeis.md) | `universo.json` (entrada/saída, ticker novo, deslistagem; os 35 sem cotação) | trimestral + eventos | Não |
| [runbooks/04-feriados-b3.md](runbooks/04-feriados-b3.md) | `const FERIADOS` no `index.html` | anual (dezembro) | Não |
| [runbooks/05-mapa-ticker-cvm.md](runbooks/05-mapa-ticker-cvm.md) | `mapa_ticker_cvm.csv` (exceções ticker → CD_CVM) | quando aparecer "sem CD_CVM" | Não |
| [runbooks/06-falha-coleta-precos.md](runbooks/06-falha-coleta-precos.md) | Falha na coleta de preços/proventos (Yahoo) e selo de atraso | quando o selo mostrar ⚠ | Rotina diária automática |
| [runbooks/07-falha-qualidade-financeira.md](runbooks/07-falha-qualidade-financeira.md) | Aceite reprovado na qualidade financeira (beta) | quando a rotina falhar | Rotina diária automática |
| [runbooks/08-revisao-trimestral-balancos.md](runbooks/08-revisao-trimestral-balancos.md) | Conferência pós-ITR/DFP | 4×/ano | Não |
| [runbooks/09-proventos-lacunas.md](runbooks/09-proventos-lacunas.md) | Proventos zerados/lacunas (CPFE3, ISAE3/4, CPLE3, BMEB3/4; AFLT3 e CBEE3 com prioridade baixa) | quando o alerta `lacuna_proventos` aparecer | Não |

## Mapa rápido do sistema (o que é automático e o que não é)

| Peça | Onde | Quem atualiza |
|---|---|---|
| Preços, proventos, alertas | `scripts/besst_painel.py --coletar` → `dados/besst/painel.json` e `dados/besst/brutos/ultimo.json` | **Automático**: `.github/workflows/monitor-besst.yml`, 1×/dia útil após o fechamento (tentativas 18h22, 18h47, 19h23, 20h23, 22h09 de Brasília) |
| Qualidade financeira (beta) | `scripts/fase2/fundamentos_cvm.py` → `aceite.py` → `publicar.py` → `dados/besst/fundamentos.json` | **Automático**: `.github/workflows/fundamentos-besst.yml` (07h43 e 19h13), só publica se testes + aceite passarem |
| Teste/diagnóstico da qualidade | `.github/workflows/fase2-teste.yml` → `dados/besst/fase2_teste/` | **Manual** (botão Run workflow) |
| Lista de papéis | `dados/besst/universo.json` | **Manual** (RB 03) |
| Controle acionário | `dados/besst/estatais.json` | **Manual** (RB 01) |
| Situações especiais | `dados/besst/situacoes_especiais.json` | **Manual** (RB 02) |
| Exceções ticker → CVM | `dados/besst/mapa_ticker_cvm.csv` | **Manual** (RB 05) |
| Feriados da B3 | `carteiras/monitor-besst/index.html` (`const FERIADOS`, linha ~343) | **Manual** (RB 04) |

**Importante:** editar `estatais.json`, `situacoes_especiais.json` ou `universo.json` **não muda a página na hora**.
O `painel.json` só é recalculado quando a rotina diária roda (ou quando você roda `python3 scripts/besst_painel.py`
localmente e faz commit do `painel.json`). Cada runbook diz qual dos dois caminhos usar. O recálculo local regrava
`gerado_em`/`coletado_em_utc` com a hora atual (o selo dirá "atualizado agora" com os preços da última coleta): ver RB 01 §7.

## Hierarquia de fontes (vale para todos os runbooks)

1. **Regulador**: CVM (Dados Abertos, RAD/Empresas.NET), B3 (ofícios, comunicados, páginas de empresas listadas),
   BCB, ANEEL, SUSEP.
2. **Relações com Investidores (RI)** da própria empresa: fato relevante, aviso aos acionistas, release, Formulário de Referência.
3. **Imprensa reconhecida** (Valor, Estadão, Folha, InfoMoney, Reuters, Bloomberg Línea etc.): só como **reforço** de 1 ou 2.
4. **Fontes alternativas** (portais de investimento, agregadores, Wikipedia): só como **contexto**, sempre rotuladas
   como tal no campo `nota`, e nunca como `fonte` principal quando existir 1 ou 2.

Não usar como fonte serviços privados de recomendação, relatórios pagos nem vídeos de terceiros: os dados do painel vêm só de fontes públicas e verificáveis.

> Situação atual: **51 dos 85** registros de `estatais.json` usam como `fonte` a página genérica de empresas listadas
> da B3 (não aponta para o documento que prova o controle; 38 deles marcados `alta`), os outros 34 usam imprensa ou
> portais de investimento, e as 8 `fonte` de `situacoes_especiais.json` também são imprensa/portais. Ou seja: hoje
> **nenhum** registro cita documento primário. Trocar essas fontes por documento
> primário (Formulário de Referência, fato relevante, ofício da B3) é a primeira pendência de qualidade — ver RB 01 e RB 02.

## Status das URLs principais (conferido em 03/11/2026)

| URL | Status |
|---|---|
| `https://dados.cvm.gov.br/dataset/cia_aberta-cad` e `.../CAD/DADOS/cad_cia_aberta.csv` | **Verificada** (página do conjunto; atualização diária). Colunas confirmadas em `dados/besst/fase2_teste/diagnostico.json` |
| `https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/META/meta_cad_cia_aberta.txt` | **Verificada** (dicionário: `SIT`, `SIT_EMISSOR`, `CONTROLE_ACIONARIO`, `CATEG_REG`, `DT_CANCEL`, `MOTIVO_CANCEL`) |
| `https://dados.cvm.gov.br/dataset/cia_aberta-doc-fre` e `.../DOC/FRE/DADOS/fre_cia_aberta_AAAA.zip` | **Verificada** (semanal; contém `fre_cia_aberta_posicao_acionaria` e `..._posicao_acionaria_classe_acao`). Nomes de colunas **não** conferidos (estão em `.../DOC/FRE/META/meta_fre_cia_aberta.zip`) |
| `https://dados.cvm.gov.br/dataset/cia_aberta-doc-ipe` e `.../DOC/IPE/DADOS/ipe_cia_aberta_AAAA.zip` | **Verificada** (semanal; colunas `Assunto, Categoria, CNPJ_Companhia, Codigo_CVM, Data_Entrega, Data_Referencia, Especie, Link_Download, Nome_Companhia, Protocolo_Entrega, Tipo, Tipo_Apresentacao, Versao`) |
| DFP/ITR/FCA (`.../DOC/DFP/DADOS/dfp_cia_aberta_AAAA.zip`, `.../DOC/ITR/...`, `.../DOC/FCA/...`) | **Verificadas indiretamente**: usadas com sucesso pelas rotinas de 03/11/2026. Inventário da CVM: atualização **semanal** |
| `https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}.SA` | **Verificada indiretamente** (rotina de 03/11/2026 ok). Bloqueada no ambiente de IA (403) |
| Ofícios da B3 sobre feriados 2026 (PDFs `OC 054-2025-VNC`, revogado, e `OC 041-2026-VNC ERRATA`, vigente) | **Verificados** (ver RB 04) |
| Layout COTAHIST da B3 (`SeriesHistoricas_Layout.pdf`) | **Verificado** |
| `https://docs.github.com/actions/using-workflows/manually-running-a-workflow` | **Verificada** |
| Página de feriados da B3, página de cotações históricas, sistema "Empresas listadas" da B3, consulta externa do RAD (`rad.cvm.gov.br`), sites de RI (CPFL, ISA Energia etc.) | **Não verificadas** nesta sessão (acesso bloqueado). Os runbooks dizem como chegar a elas pela navegação |

## Pastas e arquivos de apoio que já existem no repositório

- `docs/monitor-besst/qualidade-dados.md` — regras de alerta e achados da auditoria de 02/11/2026.
- `docs/monitor-besst/fase2-fundamentos.md` — fontes CVM, métricas e faixas da qualidade financeira.
- `docs/monitor-besst/primeiro-pregao-dados.md` e `parecer-primeiro-pregao.md` — operação no 1º pregão (03/11/2026).
- `dados/besst/fase2_teste/diagnostico.json` e `diagnostico_mapa.json` — estrutura real dos arquivos da CVM e
  cadastro/FCA dos emissores problemáticos (ótimos para conferir colunas sem baixar nada).
