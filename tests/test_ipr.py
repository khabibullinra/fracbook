import math

import numpy as np
import pytest

from fracbook import dupuy_rate, vogel_ipr


def test_dupuy_rate_at_pbar_is_zero() -> None:
    q = dupuy_rate(pwf=np.array([10.0]), pbar=10.0, k=10.0, h=10.0, mu=1.0, b=1.2, re=300.0, rw=0.1, s=0.0)
    assert q[0] == pytest.approx(0.0, abs=1e-12)


def test_dupuy_rate_matches_pi_form() -> None:
    """Проверка согласованности с PI = 2π·k·h / (μ·B·(ln(re/rw)+S))."""
    k, h, mu, b, re, rw, s = 5.0, 12.0, 0.9, 1.25, 250.0, 0.108, 2.5
    expected_pi = (2.0 * math.pi * k * h) / (mu * b * (math.log(re / rw) + s))
    pwf = np.array([5.0, 8.0, 12.0])
    pbar = 15.0
    q = dupuy_rate(pwf=pwf, pbar=pbar, k=k, h=h, mu=mu, b=b, re=re, rw=rw, s=s)
    np.testing.assert_allclose(q, expected_pi * (pbar - pwf))


def test_vogel_ipr_at_pwf_is_zero_is_qmax() -> None:
    pwf = np.array([0.0])
    q = vogel_ipr(pwf=pwf, pbar=10.0, qmax=200.0)
    assert q[0] == pytest.approx(200.0, rel=1e-12)


def test_vogel_ipr_at_pwf_equals_pbar_is_zero() -> None:
    pwf = np.array([10.0])
    q = vogel_ipr(pwf=pwf, pbar=10.0, qmax=200.0)
    assert q[0] == pytest.approx(0.0, abs=1e-10)
