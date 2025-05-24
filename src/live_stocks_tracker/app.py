# app.py  ── Top-20 losers & gainers with cap-size
import streamlit as st
import pandas as pd
import requests, io, yfinance as yf, numpy as np, random
from datetime import datetime
from american import load_sp500, load_spmid400, load_spsmall600
import time

# ── SETTINGS ────────────────────────────────────────────────────────────────
st.set_page_config(layout="wide")
st.title("📉📈 US Large / Mid / Small — 20-Day Losers & Gainers")

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
cap_size = st.sidebar.radio(
    "Cap Size universe",
    ["Large (S&P 500)", "Mid (S&P 400)", "Small (S&P 600)"] # categories on the side bar
)
days    = st.sidebar.number_input("Look-back window (days)", 5, 90, 30) # number of days to look back
max_scan = st.sidebar.number_input("Max symbols to scan (set to universe size for full scan)",
                                   10, 600, 600)      # default 600
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

# ── HELPERS ─────────────────────────────────────────────────────────────────
def rsi(series, n=14):
    """
    Calculate the Relative Strength Index (RSI) for a given series. Find more at 
    https://www.investopedia.com/terms/r/rsi.asp

    Args:
        series (_type_): _description_
        n (int, optional): Number of periods. Defaults to 14.

    Returns:
        _type_: _description_
    """
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(n).mean()
    loss  = -delta.clip(upper=0).rolling(n).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)

def render_blocks(df):
    cols = st.columns(4)
    for idx, row in df.reset_index(drop=True).iterrows():
        with cols[idx % 4]:
            # every block wrapped in a bordered div
            st.markdown(
                f"""
                <div style="
                     border:6px solid #004080;
                     border-radius:6px;
                     padding:10px 12px;
                     margin-bottom:12px;
                     ">
                    <h3 style="margin:0">{row.Symbol}</h3>
                    <small style="color:#aaaaaa;">{row.Sector if row.Sector!='-' else ''}</small><br>
                    <span style="font-size:18px; color:{'red' if row.Change<0 else 'green'};">
                        {'↓' if row.Change<0 else '↑'} {row.Change:+.2f}%
                    </span><br>
                    <span style="color:green;">Now €{row.Today:.2f}</span><br>
                    <span style="color:red;">{days} d ago €{row.Ago:.2f}</span><br>
                    RSI-14: <b>{row.RSI:.1f}</b><br>
                    Avg Vol (30 d): {row.AvgVol:,.0f}
                </div>
                """,
                unsafe_allow_html=True
            )


# ── MAIN SCAN ───────────────────────────────────────────────────────────────
if needs_refresh:
    loading_msg.info("🔄 Fetching data… please wait.")
    # load universe
    universe = (load_sp500() if cap_size.startswith("Large")
                else load_spmid400() if cap_size.startswith("Mid")
                else load_spsmall600())

    # user determines max scan size
    if max_scan >= len(universe):                 # full scan
        symbols = universe
        st.sidebar.success(f"Scanning entire universe ({len(universe)} tickers). "
                        "This gives objective top-20. Will take a bit longer than a sampled scan.")
    else:                                         # sampled scan
        symbols = random.sample(universe, max_scan)
        st.sidebar.warning(f"Scanning a random sample of {max_scan} / {len(universe)} "
                        "tickers (faster, may miss some extremes).")

# ── FAST BULK DOWNLOAD (chunked) ───────────────────────────────────────────
    chunk_size = 150
    chunks     = [symbols[i:i + chunk_size]
                for i in range(0, len(symbols), chunk_size)]

    bar_ph   = st.progress(0, "⏳ downloading price history…")   # bar placeholder
    text_ph  = st.empty()                                       # timer placeholder
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
                auto_adjust=False
            )
        )
        elapsed = time.time() - start_ts
        bar_ph.progress(n / len(chunks))
        text_ph.text(f"⏳ downloading price history… {elapsed:0.1f}s")

    bar_ph.empty()
    text_ph.empty()                             # clear widgets
    data = pd.concat(frames, axis=1)

    recs = []
    for sym in symbols:
        closes = data.get(sym, {}).get("Close")
        vols   = data.get(sym, {}).get("Volume")
        if closes is None or len(closes.dropna()) < days + 15:
            continue
        closes, vols = closes.dropna(), vols.dropna()
        ago, now = closes.shift(days).iloc[-1], closes.iloc[-1]
        pct      = (now / ago - 1) * 100
        rsi_val  = rsi(closes).iloc[-1]
        avg_vol  = vols.tail(30).mean()
        sector   = "-"
        recs.append({
            "Symbol": sym, "Sector": sector,
            "Change": pct, "Today": now, "Ago": ago,
            "RSI": rsi_val, "AvgVol": avg_vol
        })

    df = pd.DataFrame(recs)

    # if the look back returns no tickers, we need to handle that
    if df.empty:                                     
        loading_msg.empty()
        st.warning("No tickers had enough history for that look-back window.")
        st.session_state.losers  = pd.DataFrame()
        st.session_state.gainers = pd.DataFrame()
    else:                                            
        st.session_state.losers  = df[df["Change"] < 0].nsmallest(20, "Change")
        st.session_state.gainers = df[df["Change"] > 0].nlargest(20, "Change")

    st.session_state.prev_params = params
    loading_msg.empty()

# ── DISPLAY ─────────────────────────────────────────────────────────────────
if not st.session_state.losers.empty:
    view = st.selectbox("Show", ["Losers", "Gainers"])
    subset = (st.session_state.losers if view == "Losers"
              else st.session_state.gainers)
    st.header(f"{view} – {cap_size} – last {days} days")
    render_blocks(subset)
else:
    st.info("No data yet. Adjust sidebar and click run if needed.")
