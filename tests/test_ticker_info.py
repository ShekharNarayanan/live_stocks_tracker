import streamlit.testing.v1 as st_test
from src.live_stocks_tracker.utilities.ticker_info import get_ticker_stats, _rsi
import pandas as pd
import numpy as np
import pytest


@pytest.mark.parametrize(
    "series, n, expected_last",
    [
        # flat series ⇒ no gains/losses ⇒ all NaN
        (pd.Series([100.0] * 20), 14, None),

        # strict increase ⇒ loss=0 ⇒ NaN (division by zero)
        (pd.Series(range(1, 21), dtype=float), 14, 100.0),

        # alternating up/down with n=2 ⇒ RSI ≈50
        (pd.Series([1, 2, 1, 2, 1, 2, 1, 2], dtype=float), 2, 50.0),

        # decreasing series with n=3 ⇒ gain=0 ⇒ RSI=0
        (pd.Series([5, 4, 3, 2, 1, 0], dtype=float), 3, 0.0),
    ],
    ids=["flat", "increasing", "alternating", "decreasing"]
)
def test_rsi(series, n, expected_last):
    out = _rsi(series, n)

    if expected_last is None:
        # expect every value to be NaN
        assert out.isna().all()
    else:
        # only check the last point against our hand‐calc
        assert out.iloc[-1] == pytest.approx(expected_last, rel=1e-3)

def test_get_ticker_stats():
    return