"""Базовые константы и перевод единиц."""

PSI_PER_MPA = 145.0377377
PSI_PER_BAR = 14.5037738
MD_PER_M2 = 1.01325e15


def mpa_to_psi(pressure_mpa: float) -> float:
    return pressure_mpa * PSI_PER_MPA


def psi_to_mpa(pressure_psi: float) -> float:
    return pressure_psi / PSI_PER_MPA


def bar_to_psi(pressure_bar: float) -> float:
    return pressure_bar * PSI_PER_BAR


def md_to_m2(permeability_md: float) -> float:
    return permeability_md * MD_PER_M2