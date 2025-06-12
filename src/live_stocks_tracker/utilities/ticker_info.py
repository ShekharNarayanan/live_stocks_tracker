import numpy as np
import pandas as pd
import streamlit as st
import requests

# @st.cache_data(ttl=86400)
# def _get_logo_url_from_symbol(symbol:str, size=100):
#     """
#     Get the logo URL for a given stock symbol from Parqet. Check it out here:
#     https://www.parqet.com/api/logos

#     Args:
#         symbol (str): Stock symbol to get the logo for, e.g. 'AAPL' for Apple Inc.
#         size (int, optional): Size of the logo in pixels. Defaults to 30 x30.

#     Returns:
#         url (str): URL of the logo image
#     """
#     img_url = f"https://assets.parqet.com/logos/symbol/{symbol}?format=jpg&size={size}"
    
#     return img_url


def _rsi(series:pd.Series, n:int=14):
    """
    Calculate the Relative Strength Index (RSI) for a given series. Find more at 
    https://www.investopedia.com/terms/r/rsi.asp

    Args:
        series (pd.Series): closing‐price time series
        n (int, optional): Number of periods. Defaults to 14.

    Returns:
        rs (float): Relative Strength Index value for the series
    """
    delta = series.diff() # take the difference between consecutive values
    gain  = delta.clip(lower=0).rolling(n).mean() # ignore negative changes
    loss  = -delta.clip(upper=0).rolling(n).mean() # ignore positive changes
    rs    = gain / loss.replace(0, np.nan) # compute the relative strength (replace 0 in loss with Nan)
    return 100 - 100 / (1 + rs)

def get_ticker_stats(data,symbols,days):  
    
    """
    For each symbol in `symbols`, calculate the price change over `days` and
    append it to the list of dictionaries `recs`. Each dictionary has the
    following keys:

    - `Symbol`: the symbol
    - `Sector`: the sector (not used yet)
    - `Change`: the price change over `days` in percent
    - `Today`: the price today
    - `Ago`: the price `days` ago
    - `RSI`: the RSI over `days`
    - `AvgVol`: the average volume over the last 30 days

    Returns:
        ticker_metrics (list containg dicts): a list of dictionaries with ticker metrics
    """
    ticker_metrics = []
    for sym in symbols:

        # get closing prices and volumes for the symbol
        closes = data.get(sym, {}).get("Close")
        vols   = data.get(sym, {}).get("Volume")
        if closes is None or len(closes.dropna()) < days + 15:
            continue
        closes, vols = closes.dropna(), vols.dropna()
        ago, now = closes.shift(days).iloc[-1], closes.iloc[-1]
        pct      = (now / ago - 1) * 100
        rsi_val  = _rsi(series=closes).iloc[-1]
        avg_vol  = vols.tail(30).mean()
        sector   = "-"
        ticker_metrics.append({
            "Symbol": sym, "Sector": sector,
            "Change": pct, "Today": now, "Ago": ago,
            "RSI": rsi_val, "AvgVol": avg_vol,
        })

    return ticker_metrics