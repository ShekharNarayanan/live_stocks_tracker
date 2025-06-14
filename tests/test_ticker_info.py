import streamlit.testing.v1 as st_test
from src.live_stocks_tracker.utilities.ticker_info import get_ticker_stats, _rsi
import pandas as pd
from datetime import datetime
import numpy as np
import pytest

# ---------------------------------------------------------------------------
# rsi related tests
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Ticker stats tests
# ---------------------------------------------------------------------------

# create fake yfinance data
def _make_fake_data(num_days: int, symbols: list[str]) -> dict:
    """
    Create a dict shaped like the yfinance output expected by `ticker_metrics`.

    * Prices rise linearly from 100 to 110 so math is easy.
    * Volume is constant (1 000 000).
    """
    idx    = pd.date_range(end=datetime.today(), periods=num_days, freq="D")
    close  = pd.Series(np.linspace(100, 110, num_days), idx)
    volume = pd.Series(1_000_000, idx)
    return {sym: {"Close": close, "Volume": volume} for sym in symbols}

# stub _rsi- use monkey patch to avoid calling the real _rsi and replace it with a temporary fake function
@pytest.fixture(autouse=True)
def _stub_rsi(monkeypatch):
    """Replace `_rsi` with a dummy that always returns 50."""
    def fake_rsi(series, n=14):          # accept the same args as the real one
        return pd.Series(50, index=series.index)
    
    monkeypatch.setattr("src.live_stocks_tracker.utilities.ticker_info._rsi", fake_rsi)

# parametric test with different situaations
@pytest.mark.parametrize(
    "days, n_symbols, history_len",
    [
        (7,   1,   60),   # short window, single stock
        (14, 10,   90),   # typical everyday use
        (30, 50,  400),   # many symbols, long history
        (5,   3,   25),   # near-minimum length (days + 15 rule)
    ],
)
def test_get_ticker_stats(days, n_symbols, history_len):
    """
    Run `ticker_metrics` with different windows, symbol counts, and data sizes.
    """
    # ---------- arrange ----------
    symbols = [f"S{i}" for i in range(n_symbols)]
    data    = _make_fake_data(history_len, symbols)

    # ---------- act --------------
    rows = get_ticker_stats(data, symbols, days)

    # ---------- assert -----------
    assert len(rows) == n_symbols          # every symbol processed
    for row in rows:
        today  = row["Today"]
        ago    = row["Ago"]
        expect = (today / ago - 1) * 100
        assert pytest.approx(expect, rel=1e-6) == row["Change"]
        assert row["RSI"] == 50