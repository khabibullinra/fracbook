import pytest

from fracbook.core import (
    MD_PER_M2,
    PSI_PER_MPA,
    bar_to_psi,
    md_to_m2,
    mpa_to_psi,
    psi_to_mpa,
)


def test_package_version_is_string() -> None:
    import fracbook

    assert isinstance(fracbook.__version__, str)
    assert fracbook.__version__


def test_mpa_to_psi_known_value() -> None:
    assert mpa_to_psi(1.0) == pytest.approx(PSI_PER_MPA, rel=1e-9)


def test_psi_to_mpa_roundtrip() -> None:
    p = 31.5
    assert psi_to_mpa(mpa_to_psi(p)) == pytest.approx(p, rel=1e-12)


def test_bar_to_psi_matches_mpa_to_psi() -> None:
    bar_to_psi(0.1) == pytest.approx(mpa_to_psi(0.01), rel=1e-6)


def test_md_to_m2_uses_constant() -> None:
    assert md_to_m2(1.0) == MD_PER_M2