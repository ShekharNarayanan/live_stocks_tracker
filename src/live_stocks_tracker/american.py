# american.py  
import pandas as pd
import streamlit as st
import requests

# ----------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------
@st.cache_data(ttl=86400) # save the loaded data for 24 hours
# def _scrape_table(url: str, symbol_col: str = "Symbol") -> list[str]:
#     """
#     Read the first HTML table on *url* and return the column *symbol_col*
#     as an uppercase list of tickers.
#     """
#     df = pd.read_html(url)[0]
#     tickers = df[symbol_col].astype(str).str.upper()

#     # Yahoo uses hyphen instead of period for class-A/B shares (e.g. BRK-B)
#     tickers = tickers.str.replace(r"\.(\w)$", r"-\1", regex=True)
#     return tickers.tolist()



def _scrape_table(url: str, symbol_col: str = "Symbol") -> list[str]:
    UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
    
    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    dfs = pd.read_html(r.text)
    if not dfs:
        raise ValueError(f"No HTML tables found at {url}")
    df = dfs[0]

    tickers = (
        df[symbol_col]
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(r"\.(\w)$", r"-\1", regex=True)
    )
    return tickers.tolist()


# ──Public loaders ────────────────────────────────────────────────────────────────
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
