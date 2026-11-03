# Monitor BESST

Painel com os 144 papéis listados na B3 dos cinco setores perenes (Bancos, Energia, Seguros, Saneamento e Telecomunicações).

**Abrir:** https://nilsonjacobcosta.github.io/market-lab/carteiras/monitor-besst/

## O que mostra

- Preço, **DPA médio**, **DY médio**, **DY 12 meses**, **preço-teto** (Bazin, 6%) e **margem** em relação ao teto.
- **Tendência**: provento do último ano completo comparado com a média dos 5 anos.
- **Liquidez** média diária dos últimos 3 meses e alerta abaixo de R$ 500 mil/dia.
- **Controle acionário**: estatal federal, estadual, estatal estrangeira, participação estatal relevante ou privada, com controlador e fonte.

## Atualização

A rotina `.github/workflows/monitor-besst.yml` roda de hora em hora nos dias úteis durante o pregão, executa `scripts/besst_painel.py --coletar` e publica `dados/besst/painel.json`. A página relê os dados a cada 5 minutos.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `dados/besst/universo.json` | Lista dos 144 papéis por setor |
| `dados/besst/estatais.json` | Controle acionário pesquisado em 02/11/2026, com fontes |
| `dados/besst/brutos/` | Preços e proventos agregados (Yahoo Finance) |
| `dados/besst/painel.json` | Resultado consumido pelo painel |

## Limitações

- Proventos brutos (JCP antes do IR), pela data-ex; extraordinários elevam a média.
- 35 papéis do universo não têm cotação na fonte pública (deslistados ou sem negociação).
- A classificação de controle deve ser revisada periodicamente (privatizações e OPAs).

Material educativo. Não é recomendação de investimento.
