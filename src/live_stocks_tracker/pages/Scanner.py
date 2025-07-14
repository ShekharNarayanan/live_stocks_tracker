# app.py  ── Top-20 losers & gainers with cap-size
import streamlit as st
import pandas as pd
import requests, io, yfinance as yf, numpy as np, random
from datetime import datetime
from american import load_sp500, load_spmid400, load_spsmall600
from utilities.ticker_info import get_ticker_stats
from utilities.adjust_ui import render_company_blocks
import time

# ── SETTINGS ────────────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_icon="📉📈")
st.title("📉📈 Top-20 Losers & Gainers")

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
cap_size = st.sidebar.radio(
    "Cap Size universe",
    [
        "Large (S&P 500)",
        "Mid (S&P 400)",
        "Small (S&P 600)",
    ],  # categories on the side bar
)
days = st.sidebar.number_input(
    "Look-back window (days)", 5, 90, 30
)  # number of days to look back
max_scan = st.sidebar.number_input(
    "Max symbols to scan (set to universe size for full scan)", 10, 600, 600
)  # default 600
run_btn = st.sidebar.button("🔍 Run Scan")

# one-time sidebar note
st.sidebar.info("Tip: changing any sidebar value refreshes results automatically.")

# ── PLACEHOLDER FOR LOADING MESSAGE ─────────────────────────────────────────
loading_msg = st.empty()

# tuple of current sidebar values
params = (cap_size, days, max_scan)

# initialize session-state slots
if "prev_params" not in st.session_state:
    st.session_state.prev_params = None
if "losers" not in st.session_state:
    st.session_state.losers = pd.DataFrame()
    st.session_state.gainers = pd.DataFrame()

# refresh needed if button clicked *or* params changed
needs_refresh = run_btn or (params != st.session_state.prev_params)

# ── MAIN SCAN ───────────────────────────────────────────────────────────────
if needs_refresh:
    loading_msg.info("🔄 Fetching data… please wait.")
    # load universe
    universe = (
        load_sp500()
        if cap_size.startswith("Large")
        else load_spmid400()
        if cap_size.startswith("Mid")
        else load_spsmall600()
    )

    # user determines max scan size
    if max_scan >= len(universe):  # full scan
        symbols = universe
        st.sidebar.success(
            f"Scanning entire universe ({len(universe)} tickers). "
            "This gives objective top-20. Will take a bit longer than a sampled scan."
        )
    else:  # sampled scan
        symbols = random.sample(universe, max_scan)
        st.sidebar.warning(
            f"Scanning a random sample of {max_scan} / {len(universe)} "
            "tickers (faster, may miss some extremes)."
        )

    # ── FAST BULK DOWNLOAD (chunked) ───────────────────────────────────────────
    chunk_size = 150
    chunks = [symbols[i : i + chunk_size] for i in range(0, len(symbols), chunk_size)]

    bar_ph = st.progress(0, "⏳ downloading price history…")  # bar placeholder
    text_ph = st.empty()  # timer placeholder
    start_ts = time.time()

    frames = []
    for n, chunk in enumerate(chunks, start=1):
        frames.append(
            yf.download(
                chunk,
                period="1y",
                interval="1d",
                group_by="ticker",
                threads=True,
                progress=False,
                auto_adjust=False,
            )
        )
        elapsed = time.time() - start_ts
        bar_ph.progress(n / len(chunks))
        text_ph.text(f"⏳ downloading price history… {elapsed:0.1f}s")

    # clear widgets
    bar_ph.empty()
    text_ph.empty()

    # concatenate all frames into a single DataFrame
    data = pd.concat(frames, axis=1)

    # compute tickert stats like change, RSI and average volume
    ticker_stats = get_ticker_stats(data=data, symbols=symbols, days_back=days)

    # convert to DataFrame
    df = pd.DataFrame(ticker_stats)

    # if the look back returns no tickers, we need to handle that
    if df.empty:
        loading_msg.empty()
        st.warning("No tickers had enough history for that look-back window.")
        st.session_state.losers = pd.DataFrame()
        st.session_state.gainers = pd.DataFrame()
    else:
        st.session_state.losers = df[df["Change"] < 0].nsmallest(20, "Change")
        st.session_state.gainers = df[df["Change"] > 0].nlargest(20, "Change")

    st.session_state.prev_params = params
    loading_msg.empty()

# ── DISPLAY ─────────────────────────────────────────────────────────────────
if not st.session_state.losers.empty:
    view = st.selectbox("Show", ["Losers", "Gainers"])
    data_subset = (
        st.session_state.losers if view == "Losers" else st.session_state.gainers
    )
    st.header(f"{view} – {cap_size} – last {days} days")
    render_company_blocks(df=data_subset, days=days)
else:
    st.info("No data yet. Adjust sidebar and click run if needed.")
