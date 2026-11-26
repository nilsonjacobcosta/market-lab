# Mercados e ciclos: notas educativas (novembro de 2026)

Documento de apoio para os conjuntos **Liquidez e moeda**, **Risco e crédito**, **Juros (EUA)** e **Commodities** do painel [Mercados e ciclos](../../monitor/mercados/). É material educativo, não é recomendação de investimento, e não indica compra ou venda de nenhum ativo.

Cada afirmação traz um nível de evidência:

- **A**: aritmética ou definição consolidada.
- **B**: dado oficial ou estudo empírico revisado por pares.
- **C**: prática de mercado ou interpretação de especialistas, sem teste estatístico público.
- **Controverso**: evidências em conflito ou conceito que organismos de referência não endossam.

## 1. Recuperar uma queda exige uma alta maior (A)

Se um ativo cai 50%, ele precisa subir 100% para voltar ao preço original. Quanto maior a queda, mais desproporcional fica a recuperação:

| Queda | Alta necessária para voltar ao preço inicial |
|---|---|
| 10% | 11,1% |
| 20% | 25% |
| 30% | 42,9% |
| 50% | 100% |
| 70% | 233% |

Uso no painel: uma calculadora no modo Iniciante, com a fórmula exibida.

## 2. Cobre como indicador antecedente (C / controverso)

O cobre é muito usado industrialmente, e muitos analistas o acompanham como sinal da atividade econômica. A relação com o crescimento é real, mas não é precisa: o cobre também sobe e cai por oferta, estoques e demanda da China. Leitura recomendada: observar o cobre junto com outros indicadores, e não isolado.

Dados: série de preço do cobre do conjunto **Commodities** (`com-cobre`). Fonte a confirmar no painel.

## 3. Curva de juros e ciclo (B / controverso)

Quando o juro curto fica acima do longo (curva invertida), o mercado costuma precificar juros mais baixos adiante. Essa relação tem histórico, mas o intervalo entre a inversão e a recessão varia muito, e o sinal já foi falso. Leitura recomendada: acompanhar a diferença entre o juro de 10 anos e o de 2 anos (`je-10a2a` e `rc-curva`), com a data de cada inversão.

## 4. Liquidez, dívida e desalavancagem (controverso)

Há uma tese, defendida por alguns analistas, de que a dívida global é grande demais para que o crescimento a acompanhe, e que só uma queda de preços (desalavancagem) reduziria os juros de forma duradoura. Não há consenso sobre essa tese. Bancos centrais, como o Federal Reserve, costumam responder a crises com liquidez, e o efeito depende da situação. Leitura recomendada: observar os balanços dos bancos centrais (`liq-fed`, `liq-bce`) e o M2 (`liq-m2-eua`) como fatos, e tratar a interpretação como uma hipótese.

## 5. Restrições a vendas a descoberto (controverso)

Proibições temporárias de venda a descoberto foram usadas em crises (por exemplo, em 2008 nos EUA). Há estudos com resultados mistos sobre o efeito no preço de curto prazo, e o efeito sobre a liquidez é debatido. Não é um sinal confiável por si só.

## 6. Preço/lucro projetado (B / controverso)

O índice preço/lucro projetado depende de estimativas de analistas, que costumam ser otimistas e revisadas para baixo perto da divulgação de resultados. Em ciclos de lucro em queda, o índice pode parecer barato justamente quando os lucros estão caindo. Leitura recomendada: usar o indicador junto com o lucro realizado, com a média histórica e com o tamanho da dívida das empresas.

## 7. Ouro e índices em moeda real (C / controverso)

Medir um índice de ações em onças de ouro, e não em dólares, é uma forma de tirar o efeito da inflação e da expansão monetária da comparação. A razão entre o índice e o ouro subiu e caiu em ciclos longos, mas a leitura de topos e suportes com razões de Fibonacci não tem validação estatística pública. O painel pode mostrar a razão Dow Jones/ouro como histórico, sem marcar níveis de compra ou venda.

## 8. Ciclos com sequência de topos (C / controverso)

Há analistas que apontam sequências de topos em vários índices e ativos em datas próximas. Datas de máximas são fatos verificáveis; a conclusão de que elas formam um padrão de ciclo é uma interpretação, e não tem validação estatística pública.

## 9. Câmbio e dólar (C / controverso)

O dólar global (DXY) e o câmbio com o real dependem de juros, inflação, preço de commodities e fluxos de capital. Previsões de faixas de câmbio por níveis técnicos ou por ajuste pela inflação passada costumam falhar. O painel pode mostrar USD/BRL e DXY com a fonte e a data, sem projeção.

## 10. Como sinais combinados confundem iniciantes (C)

Quando vários indicadores são lidos juntos, o iniciante tende a tratar a combinação como certeza. A recomendação do projeto é explicar cada indicador separadamente, mostrar a data de cada leitura e deixar claro que um conjunto de sinais não é um sinal de compra ou venda.

## Próximos passos (não implementados nesta nota)

- Calculadora de recuperação (modo Iniciante), com a fórmula e a tabela do item 1.
- Razão Dow Jones/ouro e curva de juros em um conjunto próprio ou dentro de **Risco e crédito**, com fonte oficial e data.
- Revisão dos textos pelos juízes J1 (dados e fontes), J2 (regulatório e comunicação) e J3 (engenharia e operabilidade) antes de qualquer publicação.

## Fontes

Os dados dos gráficos vêm das fontes listadas em cada conjunto do painel. Esta nota não cita vídeos, canais nem autores de análise, conforme a regra do projeto.
