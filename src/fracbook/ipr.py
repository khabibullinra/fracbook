"""Модели индикаторных кривых (IPR).

Используются в чанках Quarto для построения графиков и расчётов в методичке.
"""

from __future__ import annotations

import math

import numpy as np


def dupuy_rate(
    pwf: np.ndarray | float,
    pbar: float,
    k: float,
    h: float,
    mu: float,
    b: float,
    re: float,
    rw: float,
    s: float,
) -> np.ndarray | float:
    """Дебит скважины по формуле Дюпюи со скин-фактором.

    Parameters
    ----------
    pwf
        Забойное давление, МПа.
    pbar
        Среднее пластовое давление, МПа.
    k
        Проницаемость, мД.
    h
        Эффективная толщина пласта, м.
    mu
        Вязкость пластового флюида, мПа·с.
    b
        Объёмный коэффициент, м³/м³.
    re
        Радиус контура питания, м.
    rw
        Радиус скважины, м.
    s
        Скин-фактор, безразмерный.

    Returns
    -------
    Дебит, м³/сут, той же формы, что ``pwf``.
    """
    pwf_arr = np.asarray(pwf, dtype=float)
    delta_p = pbar - pwf_arr
    j = (2.0 * math.pi * k * h) / (mu * b * (math.log(re / rw) + s))
    return j * delta_p


def vogel_ipr(
    pwf: np.ndarray | float,
    pbar: float,
    qmax: float,
) -> np.ndarray | float:
    """Безразмерная IPR по Вогелю для режима растворённого газа.

    Parameters
    ----------
    pwf
        Забойное давление, МПа.
    pbar
        Давление насыщения (принимается равным пластовому), МПа.
    qmax
        Максимальный дебит (при pwf = 0), м³/сут.

    Returns
    -------
    Дебит, м³/сут.
    """
    pwf_arr = np.asarray(pwf, dtype=float)
    x = pwf_arr / pbar
    return qmax * (1.0 - 0.2 * x - 0.8 * x * x)


__all__ = ["dupuy_rate", "vogel_ipr"]
