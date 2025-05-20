# app.py
import streamlit as st
import pandas as pd
import requests
import io
import yfinance as yf
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📉📈 S&P 100 — Top 20 Losers & Gainers (30-Day)")

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
days    = st.sidebar.number_input("Lookback period (days)", 5, 90, 30)
max_tks = st.sidebar.number_input("Max S&P 100 tickers to scan", 10, 100, 100)
run     = st.sidebar.button("🔍 Run Scan")

# ─── HELPERS ────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=86400)
def fetch_sp100(n):
    url  = "https://en.wikipedia.org/wiki/S%26P_100"
    html = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}).text
    tables = pd.read_html(io.StringIO(html))
    for df in tables:
        cols = [str(c).lower() for c in df.columns]
        if "symbol" in cols:
            symcol = df.columns[cols.index("symbol")]
            return df[symcol].astype(str).tolist()[:n]
    return []

def render_blocks(df):
    cols = st.columns(4)
    for idx, row in df.reset_index(drop=True).iterrows():
        col = cols[idx % 4]
        with col:
            # logo
            logo = row.Logo
            if logo:
                st.image(logo, use_column_width=True)
            else:
                st.write("⛔️")  # placeholder

            # symbol
            st.subheader(row.Symbol)

            # change arrow + pct
            arrow = "🔻" if row.Change < 0 else "🔺"
            color = "red" if row.Change < 0 else "green"
            st.markdown(f"<span style='font-size:20px;color:{color}'>{arrow} {row.Change:+.2f}%</span>",
                        unsafe_allow_html=True)

            # prices
            st.markdown(f"""
                <div>
                  <span style='color:green;'>Now: €{row.Today:.2f}</span><br>
                  <span style='color:red;'>{days}d ago: €{row.Ago:.2f}</span>
                </div>
            """, unsafe_allow_html=True)

# ─── RUN SCAN ───────────────────────────────────────────────────────────────────
if run:
    tickers = fetch_sp100(max_tks)
    if not tickers:
        st.error("Could not load S&P 100 tickers.")
    else:
        data = yf.download(
            tickers,
            period="1y",
            interval="1d",
            group_by="ticker",
            threads=True,
            progress=False,
            auto_adjust=False
        )

        records = []
        for t in tickers:
            try:
                closes = data[t]["Close"].dropna()
                if len(closes) < days + 1:
                    continue
                ago = closes.shift(days).iloc[-1]
                now = closes.iloc[-1]
                pct = (now / ago - 1) * 100
                # fetch logo once
                logo = yf.Ticker(t).info.get("logo_url")
                records.append({
                    "Symbol": t,
                    "Change": pct,
                    "Today":  now,
                    "Ago":    ago,
                    "Logo":   logo
                })
            except Exception:
                continue

        df = pd.DataFrame(records)
        # top 20 losers (strictly negative)
        losers  = df[df.Change < 0].nsmallest(20, "Change")
        gainers = df[df.Change > 0].nlargest(20, "Change")

        st.session_state["losers"]  = losers
        st.session_state["gainers"] = gainers

# ─── DISPLAY ────────────────────────────────────────────────────────────────────
if "losers" in st.session_state and "gainers" in st.session_state:
    choice = st.selectbox("Category", ["Losers", "Gainers"])
    st.header(f"Top 20 {choice} over last {days} days")
    subdf = st.session_state["losers"] if choice == "Losers" else st.session_state["gainers"]
    render_blocks(subdf)
else:
    st.info("Set parameters and click 🔍 Run Scan to view results.")
