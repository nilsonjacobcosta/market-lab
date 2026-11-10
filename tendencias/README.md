# Tendências de mercado (EUA) — matriz porte × estilo

**Status:** em construção. Página, coleta e workflow prontos; a página só mostra números depois da primeira execução do workflow `atualizar-tendencias.yml` (a sandbox de desenvolvimento não acessa o Yahoo, então a coleta real ainda não foi testada).

## O que mostra

Uma matriz 3 × 3 com um ETF público por célula (porte × estilo, base Russell), comparado com o mercado amplo (IWV, Russell 3000):

|        | Value | Core | Growth |
|--------|-------|------|--------|
| Large  | IWD   | IWB  | IWF    |
| Mid    | IWS   | IWR  | IWP    |
| Small  | IWN   | IWM  | IWO    |

Objetivo educativo: mostrar a rotação entre grandes e pequenas empresas e entre valor e crescimento. Não é recomendação de compra ou venda.

## Métricas

- **Retorno relativo** contra o IWV em 1, 3, 6 e 12 meses (`(1+r_etf)/(1+r_IWV) − 1`).
- **Posição em relação à média móvel de 200 dias** (acima ou abaixo).
- *Modo Completo:* retorno absoluto, médias de 50 e 200 dias, volatilidade anualizada e queda máxima de 12 meses.

Janelas em pregões: 1 mês = 21, 3 = 63, 6 = 126, 12 = 252 (aproximação; o cálculo por data de calendário fica para uma revisão).

## Fonte e atualização

- Preços ajustados diários: Yahoo Finance (endpoint `chart`), como nos outros painéis do repositório. Coleta pelo GitHub Actions em dias úteis às 22h30 UTC (depois do fechamento de Nova York em qualquer horário), com uma segunda execução às 10h30 UTC para recuperar falhas. Os dados ficam na branch `dados-tendencias` (arquivo `tendencias.json`), criada pelo próprio workflow.
- Nomes e índices de referência: páginas de produto da iShares (catálogo em `dados/tendencias/catalogo_etfs.json`).
- Cada número mostra a data do último pregão usado; se o dado estiver atrasado, a página avisa em texto.

## Limitações

- Relativo de 1 a 12 meses não prevê o período seguinte; um mês forte não é tendência.
- Os fundos de valor e crescimento se sobrepõem; o painel não resolve isso.
- Os ETFs são negociados nos EUA; para investidores no Brasil, o acesso é por corretoras internacionais.
- Sem custos de corretagem, impostos ou câmbio no cálculo.
- Taxa de administração e liquidez dos ETFs ficaram de fora até haver fonte conferida.
- A página foi testada em navegador apenas com dados sintéticos; os números reais só aparecem após a primeira coleta.

## Arquivos

- `dados/tendencias/catalogo_etfs.json`: os 9 ETFs e a referência.
- `scripts/tendencias/metricas.py`: funções de cálculo (sem rede).
- `scripts/tendencias/coletar_tendencias.py`: coleta no Yahoo, alinha as séries ao IWV e grava o JSON.
- `.github/workflows/atualizar-tendencias.yml`: roda os testes e depois a coleta; se os testes falharem, não atualiza.
- `tendencias/index.html`: a página (modos Iniciante e Completo; aviso de dado atrasado quando o último pregão tem mais de 4 dias).
- `tests/test_tendencias.py`: testes das funções (`python3 -m unittest tests/test_tendencias.py`).

Material educativo. Não é recomendação de investimento. Rentabilidade passada não garante resultado futuro.
