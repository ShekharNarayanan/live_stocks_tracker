import streamlit as st
import pandas as pd
import requests, io, yfinance as yf, numpy as np, random
from american import load_sp500, load_spmid400, load_spsmall600
from utilities.ticker_info import get_ticker_stats, download_ticker_data
import time

# ── SETTINGS ────────────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_icon="📉📈")
st.title("🏪 Design Portfolio")
st.info("""
    Track specific tickers from a chosen universe.
    """)

# ── RADIO SETTINGS ──────────────────────────────────────────────────────────────────
cap_size = st.radio(
    "Cap Size universe",
    [
        "Large (S&P 500)",
        "Mid (S&P 400)",
        "Small (S&P 600)",
    ],  # categories on the side bar
    horizontal=True,
)
fetch_btn = st.button("Fetch Data")

# ── PLACEHOLDER FOR LOADING MESSAGE ─────────────────────────────────────────
loading_msg = st.empty()


# ── LOAD UNIVERSE DATA  ─────────────────────────────────────────
if not fetch_btn:
    st.write("Please click the 'Fetch Data' button to load the universe data.")
    st.stop()


# Fetch data using yfinance based on universe
loading_msg.info("🔄 Fetching data… please wait.")
universe = (
    load_sp500()
    if cap_size.startswith("Large")
    else load_spmid400()
    if cap_size.startswith("Mid")
    else load_spsmall600()
)
    
symbols = universe # select all symbols

# concatenate all frames into a single DataFrame
frames = download_ticker_data(symbols=symbols) 
# concatenate all frames into a single DataFrame
data = pd.concat(frames, axis=1)
loading_msg.info("Done!")
time.sleep(2)  # pause to let the user see the message
loading_msg.empty()

# ── SEARCH BAR FOR FINDING TICKERS ─────────────────────────────────────────
search_query = st.text_input("Search for a ticker", placeholder="e.g. AAPL, MSFT, etc.")
if search_query:
    # Filter the universe based on the search query
    filtered_symbols = [sym for sym in symbols if search_query.upper() in sym]
    if filtered_symbols:
        st.write(f"Found {len(filtered_symbols)} matching tickers:")
        st.write(filtered_symbols)
    else:
        st.warning("No matching tickers found.")
