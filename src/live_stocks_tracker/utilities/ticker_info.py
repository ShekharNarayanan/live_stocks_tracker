import numpy as np
import pandas as pd
import streamlit as st
import requests
from typing import Dict, List

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


def _rsi(series: pd.Series, n: int = 14) -> pd.Series:
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(n).mean() # compute avg of positive deltas
    loss  = -delta.clip(upper=0).rolling(n).mean() # compute avg of negative deltas

    # Compute RS (loss==0 → RS=inf → RSI becomes NaN)
    rs  = gain / loss.replace(0, np.nan) # replace all the 0s in loss with NaN to avoid division by zero
    rsi = 100 - 100 / (1 + rs)

    # Build a mask for "pure up-moves" (gain > 0 but loss == 0)
    pure_up = (gain > 0) & (loss == 0)

    # Only there, set RSI to 100
    rsi = rsi.mask(pure_up, 100)

    return rsi

def _price_days_ago(prices: pd.Series, days_back: int) -> float:
    """
    Return the close from exactly `days_back` calendar days earlier.
    If the market was shut on that date (weekend / holiday),
    fall back to the most recent trading day before it.
    """
    latest_date  = prices.index[-1].normalize()          # keep only the date part
    target_date  = latest_date - pd.Timedelta(days=days_back)
    return prices.asof(target_date)                      # pandas handles the fallback
def get_ticker_stats(data,symbols,days_back=30):  
    
    """
    Args:
        data (dict): a dictionary containing the stock data for each symbol.
            The keys are symbols and the values are dictionaries with 'Close' and 'Volume' Series.
        symbols (list of str): a list of stock symbols to calculate metrics for.
        days (int): number of days to look back for price change and RSI calculation.

    Returns:
        ticker_metrics (list of dict): a list of dictionaries containing ticker metrics.

    For each symbol in `symbols`, calculate the price change over `days` and
    append it to the list of dictionaries `ticker_metrics`. Each dictionary has the
    following keys:

    - `Symbol`: the symbol
    - `Sector`: the sector (not used yet)
    - `Change`: the price change over `days` in percent
    - `Today`: the price today
    - `Ago`: the price `days` ago
    - `RSI`: the RSI over `days`
    - `AvgVol`: the average volume (shares traded) over the last 30 days

    Returns:
        ticker_metrics (list containg dicts): a list of dictionaries with ticker metrics
    """
    ticker_metrics = []
    for sym in symbols:

        # get closing prices and volumes for the symbol
        closes = data.get(sym, {}).get("Close") # closing prices at the end of each day
        vols   = data.get(sym, {}).get("Volume") # volume or number of shares traded each day
        
        #skip if no data is available or not enough data for the look-back period
        if closes is None or len(closes.dropna()) < days_back + 15:
            continue
        
        # arrange in ascending order by date, drop NaNs
        closes, vols = closes.dropna().sort_index(), vols.dropna().sort_index() # drop NaNs and sort by date

        # compute vals
        price_then = _price_days_ago(closes, days_back) 
        price_now =  closes.iloc[-1] # compute past and current closing price based on chosen number of days
        
        pct      = (price_now / price_then - 1) * 100
        rsi_val  = _rsi(series=closes).iloc[-1]
        avg_vol  = vols.tail(30).mean() # fix avg volume to last 30 days
        sector   = "-" #TODO: find a way to fetch sector info
        ticker_metrics.append({
            "Symbol": sym, "Sector": sector,
            "Change": pct, "Today": price_now, "Ago": price_then,
            "RSI": rsi_val, "AvgVol": avg_vol,
        })

    return ticker_metrics