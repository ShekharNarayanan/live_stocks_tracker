import streamlit as st
import pandas as pd
import requests, io, yfinance as yf, numpy as np, random
from american import load_sp500, load_spmid400, load_spsmall600
from utilities.ticker_info import get_ticker_stats, download_ticker_data
from utilities.adjust_ui import render_company_blocks
import sqlite3
import streamlit as st
import streamlit as st
import utilities.auth_utils as auth
from utilities.db_utils import DB_PATH, insert_portfolios_row


# ── AUTHORIZATION ────────────────────────────────────────────────────────────────
user = auth.get_user_info() # check if user wants to log in

# add part where user can continue without logging in too
if "no_login" not in st.session_state:
    st.session_state.no_login = False

def no_login():
    st.session_state.no_login = True

if user is None and not st.session_state.no_login:
    # st.title("🛂 Sign in")
    st.button("Continue without logging in", on_click=lambda: no_login())
    auth.login_button()

if user is not None:
    st.session_state.user_email = user["email"]  
    st.sidebar.button("Log out", on_click=auth.logout)
    st.success(f"Welcome, {user['email']}")
elif st.session_state.no_login:
    st.success("Welcome, anonymous user!\n Feel free to continue browsing")
else:
    st.warning("Please log in or continue as an anonymous user.")
    st.stop()



# ── SETTINGS ────────────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_icon="📉📈")
st.title("🏪 Watchlist")
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
loading_msg = st.empty()

# ── INITIALIZE SESSION STATE VARIABLES ────────────────────────────────────────────────────────────────
# we need to track if the data has been loaded,
# whether the entered tickers are being stored in a watch list, and
# the ticker inputs being entered by the user


session_essentials = {
    "data_loaded": False,
    "watch_list": [],
    "ticker_input": "",
    "universe_tickers": [],
    "current_cap_size": "",  # to track the chosen cap size
    "all_ticker_data": pd.DataFrame(),  # to store all ticker data
    "saved": False
}

for key, value in session_essentials.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ── FETCH DATA AND SEARCH BAR LOGIC ────────────────────────────────────────────────────────────────
fetch_btn = st.button("Fetch Data")


if fetch_btn and not st.session_state.data_loaded:
    loading_msg.info("🔄 Fetching data… please wait.")
    st.session_state.data_loaded = True
    # load universe
    if cap_size.startswith("Large"):
        universe = load_sp500()
        st.session_state.current_cap_size = cap_size
    elif cap_size.startswith("Mid"):
        universe = load_spmid400()
        st.session_state.current_cap_size = cap_size
    elif cap_size.startswith("Small"):
        universe = load_spsmall600()
        st.session_state.current_cap_size = cap_size

    # add ticker data to session state
    st.session_state.universe_tickers = universe

    # download dataframes of all tickers in the chosen universe
    frames = download_ticker_data(symbols=universe)

    # concatenate all frames into a single DataFrame
    all_ticker_data = pd.concat(frames, axis=1)

    # compute tickert stats like change, RSI and average volume
    ticker_stats = get_ticker_stats(data=all_ticker_data, symbols=universe)

    # convert to DataFrame
    ticker_stats_df = pd.DataFrame(ticker_stats)


    st.session_state.all_ticker_data = ticker_stats_df

    loading_msg.empty()


if st.session_state.current_cap_size != cap_size:
    st.session_state.data_loaded = False
    st.session_state.saved = False

if st.session_state.data_loaded:
    
    search_inputs = (
        st.text_input(
            "Enter comma seperated ticker symbol",
            placeholder="e.g. AAPL, MSFT, TSLA",
            key="ticker_input",
        )

    )
    search_inputs = search_inputs.split(",") 
    added_tickers = pd.DataFrame()
    
    for search_input in search_inputs:
        search_input = search_input.strip().upper()

        if search_input:
            if search_input not in st.session_state.universe_tickers:
                st.warning(f"Ticker {search_input} not found in universe.")
            elif search_input in st.session_state.watch_list:
                st.warning(f"Ticker {search_input} already in watch list.")
            else:
                #TODO: add ticker to sql database
                st.session_state.watch_list.append(search_input)
                test_df = st.session_state.all_ticker_data 
                test_df = test_df[test_df["Symbol"] == search_input] 
                added_tickers = pd.concat([added_tickers, test_df], ignore_index=True)                

                st.toast(f"Ticker {search_input} added to watch list.")
    
    render_company_blocks(ticker_stats_df=added_tickers)
    # add everything to sql database

    for ticker in st.session_state.watch_list:
        with sqlite3.connect(DB_PATH) as conn:
            if insert_portfolios_row(
            conn,
            st.session_state.user_email,
            st.session_state.current_cap_size,
            ticker
            ):
                st.success("Portfolio row saved!")
            else:
                st.info("That stock is already in your portfolio.")
            

else:
    loading_msg.info("Please click 'Fetch Data' to load the data.")
