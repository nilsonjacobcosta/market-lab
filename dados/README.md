# Dados e scripts

Todos os números dos painéis saem destes arquivos. Para refazer tudo do zero:

```bash
cd scripts
python3 fase1_auditoria.py   # estudo do midterm do S&P 500 → dados/processados/fase1_midterm.json
python3 fase2_macro.py       # juros, petróleo, dólar, metais, índices e outubro de 2026 → dados/processados/fase2_macro.json
```

Requer Python 3 com `pandas` e `numpy`.

## Dados brutos (`dados/brutos`)

| Arquivo | Conteúdo | Fonte |
|---|---|---|
| `yahoo_compact.txt` | S&P 500 (fechamento e mínima mensal, dez/1949 a nov/2026); Nasdaq, Dow Jones, Russell 2000, RSP, XLK, prata, cobre e DXY mensais; séries diárias de out/2026 de índices, metais, petróleo, dólar e juros | [Yahoo Finance](https://finance.yahoo.com/), coletado em 02/11/2026 |
| `fred_compact.txt` | GS10, GS2, CPIAUCSL, USREC e WTISPLC (médias mensais); DFII10 e T10YIE (fim de mês); diárias de out/2026 de DGS10, DGS2, DFII10, T10YIE, BAA10Y e VIXCLS | [FRED, Federal Reserve Bank of St. Louis](https://fred.stlouisfed.org/), coletado em 02/11/2026 |
| `gold_monthly.csv` | Ouro, preço mensal desde 1833 | [datasets/gold-prices](https://github.com/datasets/gold-prices) |

Formato dos arquivos compactos: `NOME AAAAMM v1 v2 ...` para meses consecutivos (`NA` = mês sem dado) e `D_NOME MMDD:valor` para dados diários de 2026.

## Definições

- Retornos de preço, sem dividendos e sem descontar a inflação.
- Retorno anual: fechamento de dezembro do ano anterior até dezembro do ano.
- Queda máxima: da base (dezembro anterior) até a menor mínima intradiária mensal do ano. Se o índice nunca ficou abaixo da base, vale 0%.
- Juros em pontos-base. GS10, GS2 e WTISPLC são médias mensais oficiais; os demais ativos usam fechamento.
- Ouro analisado a partir de 1972 e WTI a partir de 1974 (antes disso os preços eram fixados).

## Auditoria (02/11/2026)

- 156 valores do estudo-semente comparados com o recálculo; 5 corrigidos, todos com diferença pequena (2026 até outubro, 1994 em duas colunas, melhor ano pré-eleitoral e queda máxima de 1958). O retorno médio de outubro em midterm, citado como cerca de +1%, é +3,0%.
- Revisão independente: um segundo revisor refez todas as métricas com código próprio a partir dos dados brutos; nenhuma divergência acima de 0,1 ponto percentual.
- Ressalvas: amostra de 19 midterms, padrão identificado nos próprios dados (o teste de permutação não corrige isso), janelas de 12 meses sobrepostas ao ano pré-eleitoral.
