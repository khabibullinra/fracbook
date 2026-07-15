"""Расчётная библиотека методички по гидравлическому разрыву пласта."""

from fracbook.core import mpa_to_psi
from fracbook.ipr import dupuy_rate, vogel_ipr

__version__ = "0.0.1"
__all__ = ["__version__", "dupuy_rate", "mpa_to_psi", "vogel_ipr"]
