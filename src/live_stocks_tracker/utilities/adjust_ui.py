import streamlit as st
import requests
import numpy as np
from bs4 import BeautifulSoup



def render_company_blocks(ticker_stats_df, days=30):
    """
    Render a Streamlit block for each row in the given DataFrame.

    Every block is a bordered div with a header (stock symbol) and 4 rows of text:
    - sector (if available)
    - change (with arrow and color)
    - current price
    - price 30 days ago
    - RSI-14
    - average 30-day volume

    The blocks are arranged in columns of 4, wrapping to the next line if there are more than 4 entries.
    """
    cols = st.columns(4)

    for idx, row in ticker_stats_df.reset_index(drop=True).iterrows():
        with cols[idx % 4]:
            

            st.markdown(
                f"""
<div style="
    position:relative;
    border:6px solid #004080;
    border-radius:6px;
    padding:5px 12px;
    margin-bottom:12px;">




<h3 style="margin:0">{row.Symbol}</h3>
<span style="font-size:25px;color:#aaaaaa;">{row.Sector if row.Sector != "-" else ""}</span><br>
<span style="font-size:25px;color:{"red" if row.Change < 0 else "green"};">
{"↓" if row.Change < 0 else "↑"} {row.Change:+.2f}%
</span><br>
<span style="font-size:25px;color:green;">Now €{row.Today:.2f}</span><br>
<span style="font-size:25px;color:red;">{days} d ago €{row.Ago:.2f}</span><br>
<span style="font-size:20px;">RSI-14: {row.RSI:.1f}</span><br>
<span style="font-size:20px;">Avg Vol (30 d): {row.AvgVol:,.0f}</span>
</div>
""",
                unsafe_allow_html=True,
            )
