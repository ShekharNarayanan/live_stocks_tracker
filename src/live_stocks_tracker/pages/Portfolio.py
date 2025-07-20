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
    [   "Large (S&P 500)",
        "Mid (S&P 400)",
        "Small (S&P 600)",
    ],  # categories on the side bar
    horizontal=True,
)
loading_msg = st.empty()

# ── INITIALIZE SESSION STATE VARIABLES ────────────────────────────────────────────────────────────────
# we need to track if the data has been loaded, 
# whether the entered tickers are being stored in a watch list, and
# the ticker inputs being entered by the user

# def clear_textbox():
#     # Runs before Streamlit returns to your main code,
#     # so it’s legal to touch the key here.
#     st.session_state["ticker_input"] = ""

session_essentials = {
    "data_loaded": False,
    "watch_list": [],
    "ticker_input": "",
    "universe_tickers": [],
    }

for key,value in session_essentials.items():
    if key not in st.session_state:
        st.session_state[key] = value

    
# ── FETCH DATA AND SEARCH BAR LOGIC ────────────────────────────────────────────────────────────────
fetch_btn = st.button("Fetch Data")

if fetch_btn and not st.session_state.data_loaded:
    loading_msg.info("🔄 Fetching data… please wait.")
    st.session_state.data_loaded = True
    # load universe
    universe = (
        load_sp500()
        if cap_size.startswith("Large")
        else load_spmid400()
        if cap_size.startswith("Mid")
        else load_spsmall600()
    )
    # download dataframes of all tickers in the chosen universe
    frames = download_ticker_data(symbols=universe)

    # concatenate all dataframes into one
    data = pd.concat(frames, axis=1)

    # add ticker data to session state
    st.session_state.universe_tickers = universe

    # compute tickert stats like change, RSI and average volume (default of 30 days)
    # ticker_stats = get_ticker_stats(data=data, symbols=universe)
if st.session_state.data_loaded:
    search_input = st.text_input("Enter ticker symbol",
                                 placeholder="e.g. AAPL, MSFT, TSLA",
                                 key="ticker_input",
                                 ).strip().upper()
    if search_input:
        if search_input not in st.session_state.universe_tickers:
            st.warning(f"Ticker {search_input} not found in universe.")
        elif search_input in st.session_state.watch_list:
            st.warning(f"Ticker {search_input} already in watch list.")
        else:
            st.session_state.watch_list.append(search_input)
            st.success(f"Ticker {search_input} added to watch list.")
        

else:
    loading_msg.info("Please click 'Fetch Data' to load the data.")