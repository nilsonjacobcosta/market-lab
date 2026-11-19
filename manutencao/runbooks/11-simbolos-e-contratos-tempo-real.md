# RB 11 — Símbolos e contratos do painel Mercados em tempo real

> Material educativo. Nada aqui é recomendação de investimento. Não crie tokens nem credenciais.

**Última revisão deste runbook:** 2026-11-19 · **Responsável:** dono do repositório (ou IA em nova sessão)

## 1. Objetivo
Manter o `monitor/tempo-real/conjuntos.json` com símbolos que abrem nos widgets e contratos DI com vencimento a mais de 90 dias.

## 2. Quando fazer
- Todo dia 1º do mês: o workflow `testes-tempo-real.yml` roda e falha se um DI vence em menos de 90 dias.
- Todo mês de dezembro, junto do RB 04 (feriados da B3): trocar os DI que vencem no janeiro seguinte.
- Quando um quadro aparecer vazio, com erro ou sem atraso informado, ou o TradingView mudar um símbolo.
- Todo trimestre: reler os termos do TradingView (seções de uso, atribuição e robôs) e registrar a data.

## 3. Arquivos
`monitor/tempo-real/conjuntos.json` (`simbolos`, `matriz_teste`), `monitor/tempo-real/teste-simbolos.html`, `tests/test_tempo_real.py`.

## 4. Passos
1. Abrir `teste-simbolos.html` no Chrome (com o site publicado ou servido localmente) e olhar a faixa e cada símbolo: valor aparece, linha vazia ou erro.
2. Símbolo novo: só entra no JSON depois de aparecer ali; acrescentar em `simbolos_aprovados` com a data em `data_teste`. Reprovado vai para `reprovados`.
3. Contrato DI a trocar: escolher o próximo vencimento de janeiro com mais de 90 dias, atualizar o `s` e os textos (rótulo, "janeiro de AAAA").
4. Rodar `python3 -m unittest tests/test_tempo_real.py`.
5. Anotar em `manutencao/registro.md`.

## 5. O que nunca fazer
Ler valores de dentro do widget por script, gravar cotações no repositório, republicar cotações, usar widgets de análise técnica, ou trocar o aviso de atraso por "tempo real" sem a fonte confirmar.

## 6. Critério de pronto
Testes verdes, símbolos conferidos no navegador, registro preenchido.
