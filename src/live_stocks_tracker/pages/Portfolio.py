import streamlit as st
import pandas as pd
import requests, io, yfinance as yf, numpy as np, random
from american import load_sp500, load_spmid400, load_spsmall600

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
if fetch_btn:
    loading_msg.info("🔄 Fetching data… please wait.")
    # load universe
    universe = (
        load_sp500()
        if cap_size.startswith("Large")
        else load_spmid400()
        if cap_size.startswith("Mid")
        else load_spsmall600()
    )

    # Downbload data using yfinance
    symbols = universe

    

# ── SEARCH BAR FOR FINDING TICKERS ─────────────────────────────────────────