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
# ── SET UP BUTTONS  ──────────────────────────────────────────────────────────────────
def add_ticker():
    st.button("Add Ticker")
    return True


fetch_btn = st.button("Fetch Data")



if not fetch_btn:
    loading_msg.info("Please click the 'Fetch Data' button to load the universe data.")
    st.stop()
else:
    loading_msg.info("🔄 Fetching data… please wait.")
    # load universe
    # Fetch data using yfinance based on universe
    universe = (
        load_sp500()
        if cap_size.startswith("Large")
        else load_spmid400()
        if cap_size.startswith("Mid")
        else load_spsmall600()
    )
        
    symbols = universe # select all symbols

    frames = download_ticker_data(symbols=symbols) 
    # concatenate all frames into a single DataFrame
    data = pd.concat(frames, axis=1)
    loading_msg.empty()
    time.sleep(2)  # pause to let the user see the message
    x = add_ticker()

    if x:
        if 'ss_text' and "result_list" not in st.session_state:
            st.session_state.ss_text = "ON RENDER"
            st.session_state.result_list = []

                
        def _set_ss_text():
            st.session_state.ss_text = st.session_state.key_ss_text


        st.session_state.ss_text = st.text_input(
                label="Persistent text_input",
                value=st.session_state.ss_text,
                on_change=_set_ss_text,
                key='key_ss_text'
        )
        st.session_state.result_list.append(st.session_state.ss_text)

        st.write(f"Current ticker array: `{st.session_state.result_list}`")
        

    


# ── LOAD UNIVERSE DATA  ─────────────────────────────────────────


# # ── SEARCH BAR FOR FINDING TICKERS ─────────────────────────────────────────

# # check if something can persist
# if 'ss_text' and "result_list" not in st.session_state:
#     st.session_state.ss_text = "ON RENDER"
#     st.session_state.result_list = []

        
# def _set_ss_text():
#     st.session_state.ss_text = st.session_state.key_ss_text


# st.session_state.ss_text = st.text_input(
#         label="Persistent text_input",
#         value=st.session_state.ss_text,
#         on_change=_set_ss_text,
#         key='key_ss_text'
# )
# st.session_state.result_list.append(st.session_state.ss_text)

# st.write(f"Current ticker array: `{st.session_state.result_list}`")

# st.session_state.first_search = False

    
    






