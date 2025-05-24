# american.py  
import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------
@st.cache_data(ttl=86400)
def _scrape_table(url: str, symbol_col: str = "Symbol") -> list[str]:
    """
    Read the first HTML table on *url* and return the column *symbol_col*
    as an uppercase list of tickers.
    """
    df = pd.read_html(url)[0]
    tickers = df[symbol_col].astype(str).str.upper()

    # Yahoo uses hyphen instead of period for class-A/B shares (e.g. BRK-B)
    tickers = tickers.str.replace(r"\.(\w)$", r"-\1", regex=True)
    return tickers.tolist()

# ----------------------------------------------------------------------
# Public loaders
# ----------------------------------------------------------------------
@st.cache_data(ttl=86400)
def load_sp500() -> list[str]:
    """Return the 500 S&P-500 tickers from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    return _scrape_table(url)

@st.cache_data(ttl=86400)
def load_spmid400() -> list[str]:
    """Return the 400 S&P-400 (mid-cap) tickers."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies"
    return _scrape_table(url)

@st.cache_data(ttl=86400)
def load_spsmall600() -> list[str]:
    """Return the 600 S&P-600 (small-cap) tickers."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_600_companies"
    return _scrape_table(url)
