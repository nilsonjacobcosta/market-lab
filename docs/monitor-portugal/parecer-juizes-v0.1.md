# Monitor Portugal v0.1 — parecer dos juízes (04/11/2026)

Publicação autorizada pelo dono com link não divulgado (`noindex`). Este parecer regista o que passou, o que ficou pendente
e as condições para divulgar o link.

## J1 — dados e fontes · nota 8,0 · aprovado com pendências
- Proventos só do cadastro próprio, com link por pagamento. Na janela 2021–2025, os eventos estão marcados como `oficial` ou `coincide` em ≥ 90% (teste automático).
- 16 somas anuais conferidas contra documentos das empresas estão fixadas em teste de regressão.
- Detector "evento não cadastrado" achou 5 pagamentos na 1.ª execução (Amorim dez/2021–2023, Mota-Engil out/2022, Altri jul/2021 em espécie); todos resolvidos.
- Fonte de cotações reprovada para proventos (fator ~1,027 na Galp e ~1,03 nos CTT; scrip da EDPR e parcela de dez/2024 da Amorim omitidos). Mantida para preços: 16/16 com fecho de 03/11/2026.
- Taxa: série oficial do BCE lida no Actions (média de 12 meses 3,323%; última observação 09/2026: 3,846%).
- Pendências: Altri 2022–2024 e 2026; JMT, Navigator e Semapa 2026 (exercício 2025); Amorim 2022 (parcelas vs total); TDSA sem documento de "não distribuição".

## J2 — regulatório e comunicação · nota 7,5 · aprovado para link não divulgado
- Aviso "Material educativo, não é recomendação de investimento" no topo e no rodapé; teste bloqueia linguagem de compra.
- Apresentação objetiva (Reg. Delegado 2016/958, aplicado voluntariamente): autor, data/hora, separação factos vs cálculo, fontes, metodologia, riscos, histórico de mudanças de situação (12 meses).
- Sem ordenação por distância ao teto nem por situação.
- Português de Portugal (cotada, fecho, ecrã, telemóvel, englobamento).
- **Condição para divulgar o link:** parecer jurídico sobre o enquadramento do "preço-teto" como recomendação de investimento (MAR art. 20.º) e sobre a eventual comunicação à CMVM (Reg. CMVM 2/2007). Até lá, manter `noindex` e sem link na página inicial do site.

## J3 — engenharia e operabilidade · nota 8,5 · aprovado
- Rotina diária com 4 tentativas após o fecho de Lisboa; testes antes e depois da coleta; publicação só com aceite limpo.
- Falha de fonte não derruba o painel (mantém último dado por papel, taxa e lista).
- Selo de data ligado ao calendário da Euronext (feriados de Páscoa, 1/5, 25–26/12) e hora de verão europeia; avisa em texto quando atrasado.
- Testado em ecrã largo e com 380 px de largura (sem transbordo horizontal da página).
- Runbooks em `manutencao/portugal/README.md`; registo atualizado.
- Pendência: os commits diários incluem a hora de geração mesmo sem novos preços (até 4 por dia).

## Decisão do dono — 04/11/2026, 06h14 (Brasília)
O dono autorizou a publicação aberta no GitHub como **material de estudo**: cartão na página inicial, linha no README e
página indexável. A condição do J2 (parecer jurídico antes de divulgar) fica registada como **risco assumido pelo dono**,
coerente com a decisão de 04/11 de manter o preço-teto. O parecer jurídico continua recomendado e listado nas pendências.

## Paridade com o Monitor BESST — o que falta
| Recurso do BESST | Portugal v0.1 |
|---|---|
| Preços, proventos, DPA médio, rendimento, teto clássico e robusto, margem, liquidez | feito |
| Alertas por regra, "conferir dados", selo de data com calendário da bolsa | feito |
| Modo Iniciante/Completo, ficha, simulador | feito (simulador com líquido de 28%) |
| Qualidade financeira (ROE, payout, dívida líquida/EBITDA, nota) | **falta** — fonte: relatórios anuais ESEF/iXBRL |
| Controlo acionista | **falta** |
| Situações especiais (OPA, saída de bolsa) | parcial — alerta de papel fora da lista da Euronext |
| Runbooks e registo | feito |
