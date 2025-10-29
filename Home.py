# Home.py  -- the new entry point
import streamlit as st
from utilities.animations import add_half_screen_stock_glow

st.set_page_config(
    page_title="Live-Stocks-Tracker",
    page_icon="💹",
    layout="wide",
)
add_half_screen_stock_glow() 


# -----------------------------------------------------------------------------
# Simple hero section
# -----------------------------------------------------------------------------
st.markdown(
    """
    <h1 style='font-size:3rem; margin-bottom:0;'>Live-Stocks-Tracker</h1>
    <p style='font-size:1.3rem; color:#8c8c8c; margin-top:0.2rem; font-style:italic;'>
        Welcome to Live-Stocks-Tracker! A simple add-free web application that helps you keep track of stocks in the US market using yfinance.

        P.S: Apologies for the load times! 🙏 yfinance is free but slow 
    </p>
    """,
    unsafe_allow_html=True,
)

st.write("")  # vertical space

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("🚀 Open the generalized Scanner", use_container_width=True):
        st.switch_page("pages/Scanner.py")
    st.info(
    """
    **Scanner** \n
    Find out the top-20 gainers and losers in the S&P 500/400/600. 
    
    """,
    icon="ℹ️",
    )
    

with col2:
    if st.button("📊 Open the Portfolio Tracker", use_container_width=False):
        st.switch_page("pages/Make_Your_Portfolio.py")
    st.info(
    """
    **Watchlist** \n
    Track companies of your choice in either of the three S&P universes! You can choose to just explore or sign up so your watchlist is saved for you 🙌
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
