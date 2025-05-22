# app.py  ── Top-20 losers & gainers with cap-size
import streamlit as st
import pandas as pd
import requests, io, yfinance as yf, numpy as np, random          # ← CHANGED
from datetime import datetime
from american import load_sp500, load_spmid400, load_spsmall600

# ── SETTINGS ─────────────────────────────────────────────────────────────────
st.set_page_config(layout="wide")
st.title("📉📈 US Large / Mid / Small — 20-Day Losers & Gainers")

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
cap_size = st.sidebar.radio("Cap Size universe",
                            ["Large (S&P 500)", "Mid (S&P 400)", "Small (S&P 600)"])
days     = st.sidebar.number_input("Look-back window (days)", 5, 90, 30)
max_tks  = st.sidebar.number_input("Max symbols to scan", 10, 600, 100)
run_btn  = st.sidebar.button("🔍 Run Scan")

# ─── PLACEHOLDER FOR ONE-TIME LOADING MESSAGE ────────────────────────────────
loading_msg = st.empty()                     # empty place holder for automatic loading

if "has_run" not in st.session_state:
    st.session_state.has_run = True
    run = True
    loading_msg.info("🕵️‍♂️ Initial scan running…")   
else:
    run = run_btn

# ── HELPERS ──────────────────────────────────────────────────────────────────
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
            st.markdown(f"<div style='text-align:center;font-size:18px;color:{color}'>"
                        f"{arrow} {row.Change:+.2f}%</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='text-align:center;'>"
                f"<span style='color:green;'>Now €{row.Today:.2f}</span><br>"
                f"<span style='color:red;'>{days} d ago €{row.Ago:.2f}</span><br>"
                f"RSI-14: <b>{row.RSI:.1f}</b><br>"
                f"Avg Vol (30 d): {row.AvgVol:,.0f}"
                f"</div>", unsafe_allow_html=True
            )

# ── MAIN SCAN ───────────────────────────────────────────────────────────────
if run:
    # pick universe
    base = (load_sp500() if cap_size.startswith("Large")
            else load_spmid400() if cap_size.startswith("Mid")
            else load_spsmall600())

    random.shuffle(base)                                             #  always return some losers or winners
    symbols = base[:max_tks]

    if not symbols:
        st.error("❌ Ticker list empty.")
        st.stop()

    data = yf.download(symbols, period="1y", interval="1d",
                       group_by="ticker", threads=True,
                       progress=False, auto_adjust=False)

    recs = []
    for sym in symbols:
        closes = data.get(sym, {}).get("Close")
        vols   = data.get(sym, {}).get("Volume")
        if closes is None or len(closes.dropna()) < days + 15:
            continue
        closes, vols = closes.dropna(), vols.dropna()
        ago, now     = closes.shift(days).iloc[-1], closes.iloc[-1]
        pct          = (now / ago - 1) * 100
        rsi_val      = rsi(closes).iloc[-1]
        avg_vol      = vols.tail(30).mean()
        sector       = yf.Ticker(sym).info.get("sector", "—")

        # keep everything; RSI just for display  ← CHANGED (old filter removed)
        recs.append({
            "Symbol": sym, "Sector": sector,
            "Change": pct, "Today": now, "Ago": ago,
            "RSI": rsi_val, "AvgVol": avg_vol
        })

    df = pd.DataFrame(recs)
    st.session_state["losers"]  = df[df.Change < 0].nsmallest(20, "Change")
    st.session_state["gainers"] = df[df.Change > 0].nlargest(20, "Change")

# ── DISPLAY ─────────────────────────────────────────────────────────────────
if "losers" in st.session_state:
    view   = st.selectbox("Show", ["Losers", "Gainers"])
    subset = st.session_state["losers"] if view == "Losers" else st.session_state["gainers"]
    st.header(f"{view} – {cap_size} – last {days} days")
    render_blocks(subset)
else:
    st.info("Set parameters and click 🔍 Run Scan.")
