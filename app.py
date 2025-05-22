# app.py  ── Top-20 losers & gainers with cap-size
import streamlit as st
import pandas as pd
import requests, io, yfinance as yf, numpy as np, random
from datetime import datetime
from american import load_sp500, load_spmid400, load_spsmall600

# ── SETTINGS ────────────────────────────────────────────────────────────────
st.set_page_config(layout="wide")
st.title("📉📈 US Large / Mid / Small — 20-Day Losers & Gainers")

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
cap_size = st.sidebar.radio(
    "Cap Size universe",
    ["Large (S&P 500)", "Mid (S&P 400)", "Small (S&P 600)"]
)
days    = st.sidebar.number_input("Look-back window (days)", 5, 90, 30)
max_scan = st.sidebar.number_input("Max symbols to scan (set to universe size for full scan)",
                                   10, 600, 600)      # default 600
run_btn = st.sidebar.button("🔍 Run Scan")

# one-time sidebar note
st.sidebar.info("Tip: changing any sidebar value refreshes results automatically.\nPicking the whole universe will take longer to load.")

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
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(n).mean()
    loss  = -delta.clip(upper=0).rolling(n).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)

def render_blocks(df):
    cols = st.columns(4)
    for idx, row in df.reset_index(drop=True).iterrows():
        with cols[idx % 4]:
            st.subheader(row.Symbol)
            st.caption(row.Sector or "—")
            arrow = "↓" if row.Change < 0 else "↑"
            color = "red" if row.Change < 0 else "green"
            st.markdown(
                f"<div style='text-align:center;font-size:18px;color:{color}'>"
                f"{arrow} {row.Change:+.2f}%</div>", unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='text-align:center;'>"
                f"<span style='color:green;'>Now €{row.Today:.2f}</span><br>"
                f"<span style='color:red;'>{days} d ago €{row.Ago:.2f}</span><br>"
                f"RSI-14: <b>{row.RSI:.1f}</b><br>"
                f"Avg Vol (30 d): {row.AvgVol:,.0f}"
                f"</div>", unsafe_allow_html=True
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
                        "This gives objective top-20.")
    else:                                         # sampled scan
        symbols = random.sample(universe, max_scan)
        st.sidebar.warning(f"Scanning a random sample of {max_scan} / {len(universe)} "
                        "tickers (faster, may miss some extremes).")

# ── FAST BULK DOWNLOAD (chunked) ───────────────────────────────────────────
    chunk_size = 150                        # tweak if you like
    frames = []
    for i in range(0, len(symbols), chunk_size):
        chunk = symbols[i:i + chunk_size]
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

    # concat along columns → same structure as a single big call
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
        sector   = yf.Ticker(sym).info.get("sector", "—")
        recs.append({
            "Symbol": sym, "Sector": sector,
            "Change": pct, "Today": now, "Ago": ago,
            "RSI": rsi_val, "AvgVol": avg_vol
        })

    df = pd.DataFrame(recs)
    st.session_state.losers  = df[df.Change < 0].nsmallest(20, "Change")
    st.session_state.gainers = df[df.Change > 0].nlargest(20, "Change")
    st.session_state.prev_params = params
    loading_msg.empty()  # ← clear one-time / refresh spinner

# ── DISPLAY ─────────────────────────────────────────────────────────────────
if not st.session_state.losers.empty:
    view = st.selectbox("Show", ["Losers", "Gainers"])
    subset = (st.session_state.losers if view == "Losers"
              else st.session_state.gainers)
    st.header(f"{view} – {cap_size} – last {days} days")
    render_blocks(subset)
else:
    st.info("No data yet. Adjust sidebar and click run if needed.")
