# Calendário de manutenção — Monitor BESST

Horários em Brasília (UTC−3). "RB" = runbook em `runbooks/`. Ao concluir, registre em `registro.md`.

## Todo dia útil (2 minutos, opcional)
| Quando | O quê | Runbook |
|---|---|---|
| Depois das 22h30 | Abrir o painel e ler o selo do topo. Texto normal = "Fechamento do pregão de dd/mm/aaaa · atualizado …". Se aparecer "⚠ … a atualização automática atrasou" | RB 06 |

## Toda segunda-feira (10 minutos)
| O quê | Runbook |
|---|---|
| Aba **Actions** do GitHub: há execução com ✗ vermelho em "Atualizar Monitor BESST" ou "Atualizar qualidade financeira (BETA)" na semana? | RB 06 / RB 07 |
| `dados/besst/fundamentos.json`: o campo `gerado_em` tem menos de 48 h? (se não, o aceite está reprovando ou a rotina não roda) | RB 07 |
| Novos fatos relevantes de OPA, recuperação judicial, falência, incorporação, mudança de controle (a CVM atualiza o IPE toda semana) | RB 02 / RB 01 |

## Todo mês (1º dia útil)
| O quê | Runbook |
|---|---|
| Revisão completa de `situacoes_especiais.json` (encerrar casos, abrir novos) | RB 02 |
| Conferência rápida do controle acionário contra o cadastro da CVM (`CONTROLE_ACIONARIO`). **Planejado:** uma rotina mensal fará isso e abrirá uma issue; enquanto não existir, rodar o script do RB 01 §5.2 à mão | RB 01 |
| Conferir se algum papel com cotação passou a "sem cotação" (ou o contrário) | RB 03 |

## A cada 60 dias (no máximo)
| O quê | Próxima data-limite | Runbook |
|---|---|---|
| Revisão manual completa do controle acionário (campo `atualizado` de `estatais.json`). **Planejado:** aviso na página quando a revisão passar de 60 dias | **01/01/2027** (última: 02/11/2026). Fazer até **15/12/2026** | RB 01 |

## Trimestral — depois dos balanços (ITR/DFP)
Prazos legais: ITR até 45 dias após o fim do trimestre; DFP até 3 meses após o fim do exercício. Os arquivos de
Dados Abertos da CVM são atualizados **semanalmente**, por isso a conferência fica ~1 semana depois do prazo.

| Período | Prazo legal | Conferência | Runbook |
|---|---|---|---|
| 3T26 (ITR) | 14/11/2026 | **23/11/2026** | RB 08 (+ RB 03, RB 09) |
| 2026 (DFP) | 31/03/2027 | **07/04/2027** | RB 08 (+ revisão anual das faixas) |
| 1T27 (ITR) | 15/05/2027 | **24/05/2027** | RB 08 |
| 2T27 (ITR) | 14/08/2027 | **23/08/2027** | RB 08 |
| 3T27 (ITR) | 14/11/2027 | **22/11/2027** | RB 08 |

## Anual
| Quando | O quê | Runbook |
|---|---|---|
| **Dezembro** (a B3 publicou o calendário de 2026 em 04/12/2025) — a partir de ~05/12, concluir até 20/12 | Trocar os feriados provisórios do ano seguinte pelos oficiais da B3 e criar os provisórios do ano depois | RB 04 |
| Abril (com a DFP) | Revisar faixas do semáforo da qualidade financeira (Selic/custo de capital) — decisão do dono, ver `docs/monitor-besst/fase2-fundamentos.md` §5 | RB 08 §5.6 |
| Abril (com a DFP) | Revisão completa do universo (novas listagens nos 5 setores, deslistagens) | RB 03 |

## Por evento (sem data)
| Gatilho | Runbook |
|---|---|
| Selo ⚠ de atraso; execução vermelha em "Atualizar Monitor BESST" | RB 06 |
| "NÃO PUBLICADO. Falhas no aceite" na rotina de qualidade | RB 07 |
| `sem_mapeamento` não vazio no aceite ou `"erro": "sem CD_CVM"` em algum papel | RB 05 |
| Alerta `lacuna_proventos` novo, ou status "Abaixo do teto · conferir dados" | RB 09 |
| Fato relevante de OPA, RJ, falência, incorporação, mudança de ticker | RB 02 + RB 03 (+ RB 01 se mudar o controle) |
| Privatização, venda de controle, mudança de controlador | RB 01 |
