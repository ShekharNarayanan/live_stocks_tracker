# Home.py  -- the new entry point
import streamlit as st

st.set_page_config(
    page_title="Live-Stocks-Tracker",
    page_icon="💹",
    layout="wide",
)

# -----------------------------------------------------------------------------
# Simple hero section
# -----------------------------------------------------------------------------
st.markdown(
    """
    <h1 style='font-size:3rem; margin-bottom:0;'>Live-Stocks-Tracker</h1>
    <p style='font-size:1.3rem; color:#8c8c8c; margin-top:0.2rem;'>
        Welcome to Live-Stocks-Tracker! A simple add-free web application that helps you keep track of stocks in the US market using yfinance.
    </p>
    """,
    unsafe_allow_html=True,
)

st.write("")  # vertical space

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("🚀 Open the generalized Scanner", use_container_width=True):
        # <--- works on Streamlit ≥ 1.22
        st.switch_page("pages/Scanner.py")

with col2:
    st.info(
        """
        **What does this include?**

        * + 🌐 We pull daily prices for the S&P 500/400/600 via *yfinance*  
        * + 📊 Compute %-change, RSI-14, and average volume  
        * + 📈 Display top-20 gainers and losers in each cap-size category
        """,
        icon="ℹ️",
    )

# Hide sidebar on the landing page so the focus stays on the hero section
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {visibility:hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)
