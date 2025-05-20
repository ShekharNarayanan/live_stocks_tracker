# american.py
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

API_KEY  = st.secrets["POLYGON_TOKEN"]
BASE_URL = "https://api.polygon.io"


def _fetch_by_marketcap(count: int) -> list[str]:
    """Try to page through Polygon’s reference/tickers until we have `count` symbols."""
    url = f"{BASE_URL}/v3/reference/tickers"
    params = {
        "market": "stocks",
        "active": "true",
        "sort":   "market_cap",
        "order":  "desc",
        "limit":  100,            # page size
        "apiKey": API_KEY
    }
    tickers = []
    while url and len(tickers) < count:
        resp = requests.get(url, params=params).json()
        results = resp.get("results", [])
        tickers.extend(r["ticker"] for r in results)
        url = resp.get("next_url")  # follow pagination
        params = None                # next_url already includes the key
    return tickers[:count]


@st.cache_data(ttl=86400)
def load_sp500() -> list[str]:
    # Try Polygon first
    try:
        poly = _fetch_by_marketcap(500)
        if len(poly) >= 100:
            return poly
    except Exception:
        pass
    # Fallback to Wikipedia
    df = pd.read_html(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    )[0]
    return df["Symbol"].str.replace(r"\.(\w)$", r"-\1", regex=True).tolist()


@st.cache_data(ttl=86400)
def load_spmid400() -> list[str]:
    try:
        poly = _fetch_by_marketcap(900)[500:900]
        if len(poly) >= 100:
            return poly
    except Exception:
        pass
    df = pd.read_html(
        "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies"
    )[0]
    return df["Symbol"].tolist()


@st.cache_data(ttl=86400)
def load_spsmall600() -> list[str]:
    try:
        poly = _fetch_by_marketcap(1500)[900:1500]
        if len(poly) >= 100:
            return poly
    except Exception:
        pass
    df = pd.read_html(
        "https://en.wikipedia.org/wiki/List_of_S%26P_600_companies"
    )[0]
    return df["Symbol"].tolist()


@st.cache_data(ttl=300)
def get_daily_closes(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Pull daily Close prices from Polygon:
    GET /v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}
    """
    url    = f"{BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}"
    params = {"adjusted": "true", "sort": "asc", "apiKey": API_KEY}
    j      = requests.get(url, params=params).json().get("results", [])
    recs   = [
        {"date": datetime.utcfromtimestamp(r["t"] / 1000), "Close": r["c"]}
        for r in j
    ]
    df = pd.DataFrame(recs).set_index("date")
    return df
