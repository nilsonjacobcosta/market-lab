"""Métricas de força relativa para o painel de tendências (funções puras, sem rede).

Convenção: séries de preços ajustados diários, em ordem cronológica.
Janelas em pregões: 1m=21, 3m=63, 6m=126, 12m=252 (aproximação; ver README).
"""
from __future__ import annotations

import math

JANELAS = {"1m": 21, "3m": 63, "6m": 126, "12m": 252}
DIAS_ANO = 252


def retorno(precos: list[float], pregoes: int) -> float | None:
    """Retorno simples dos últimos `pregoes` pregões."""
    if len(precos) <= pregoes or precos[-1 - pregoes] <= 0:
        return None
    return precos[-1] / precos[-1 - pregoes] - 1


def retorno_relativo(r_etf: float | None, r_ref: float | None) -> float | None:
    """Retorno do ETF em relação ao mercado amplo: (1+r_etf)/(1+r_ref) - 1."""
    if r_etf is None or r_ref is None or r_ref <= -1:
        return None
    return (1 + r_etf) / (1 + r_ref) - 1


def media_movel(precos: list[float], janela: int) -> float | None:
    if len(precos) < janela:
        return None
    return sum(precos[-janela:]) / janela


def acima_media(precos: list[float], janela: int) -> bool | None:
    m = media_movel(precos, janela)
    return None if m is None else precos[-1] > m


def volatilidade_anual(precos: list[float], pregoes: int = DIAS_ANO) -> float | None:
    """Desvio-padrão dos retornos diários dos últimos `pregoes` pregões, anualizado."""
    if len(precos) < pregoes + 1:
        return None
    trecho = precos[-(pregoes + 1):]
    rets = [trecho[i] / trecho[i - 1] - 1 for i in range(1, len(trecho)) if trecho[i - 1] > 0]
    if len(rets) < 2:
        return None
    media = sum(rets) / len(rets)
    var = sum((r - media) ** 2 for r in rets) / (len(rets) - 1)
    return math.sqrt(var) * math.sqrt(DIAS_ANO)


def queda_maxima(precos: list[float], pregoes: int = DIAS_ANO) -> float | None:
    """Maior queda do pico ao vale nos últimos `pregoes` pregões (valor <= 0)."""
    if len(precos) < 2:
        return None
    trecho = precos[-pregoes:]
    pico = trecho[0]
    pior = 0.0
    for p in trecho:
        pico = max(pico, p)
        if pico > 0:
            pior = min(pior, p / pico - 1)
    return pior


def calcular_celula(precos: list[float], precos_ref: list[float]) -> dict:
    """Todas as métricas de uma célula, com o mercado amplo como referência."""
    saida: dict = {}
    for nome, n in JANELAS.items():
        r = retorno(precos, n)
        rr = retorno(precos_ref, n)
        saida[f"retorno_{nome}"] = r
        saida[f"relativo_{nome}"] = retorno_relativo(r, rr)
    saida["acima_mm200"] = acima_media(precos, 200)
    saida["mm50"] = media_movel(precos, 50)
    saida["mm200"] = media_movel(precos, 200)
    saida["volatilidade_12m"] = volatilidade_anual(precos)
    saida["queda_maxima_12m"] = queda_maxima(precos)
    return saida
