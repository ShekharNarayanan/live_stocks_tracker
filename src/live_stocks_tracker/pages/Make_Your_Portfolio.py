import streamlit as st
import pandas as pd
from american import load_sp500, load_spmid400, load_spsmall600
from utilities.ticker_info import get_ticker_stats, download_ticker_data
from utilities.adjust_ui import render_company_blocks
import sqlite3
import utilities.auth_utils as auth
from pathlib import Path
from utilities.db_utils import  insert_portfolios_row

# ── FUNCTIONS NEEDED ────────────────────────────────────────────────────────────────

# ── SETTINGS ────────────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_icon="📉📈")
st.title("🏪 Make Your Own Portfolio")
st.info("""
    Create a portfolio of stocks from all three universes.
    """)

# ── PATHS ────────────────────────────────────────────────────────────────
parent_dir = Path(__file__).parents[3]
DB_PATH = parent_dir / "portfolios.db" # need for persisting user data in the database


# ── AUTHORIZATION ────────────────────────────────────────────────────────────────

# initialize with the assumption that user will log in
if "use_without_log_in" not in st.session_state:
    st.session_state.use_without_log_in = False

# Determine if we already have user info (validates tokens)
user = auth.get_user_info() # > if the user is logged in already, this will not be None.

if user is None and not st.session_state.use_without_log_in: # > if we have no user info and we don't what the user wants, give them the option to choose
    st.button("Continue without logging in", on_click=lambda: st.session_state.update(use_without_log_in = True)) # > lets user continue without logging in
    auth.login_button() # > log in button

if user is not None:
    # if user chooses to log in, store email in session state, create log out button and show welcome message
    st.session_state.user_email = user["email"]  
    st.sidebar.button("Log out", on_click=auth.logout)
    st.success(f"Welcome, {user['email']}")
elif st.session_state.use_without_log_in:
    st.success("Welcome, anonymous user!\n Feel free to continue browsing. Refresh the page if you decide to sign up 😃")
else: # stop streamlit until user picks between logging in or continuing anonymously
    st.stop()

#  ── NAIVGATE TO PERSONAL PORTFOLIO IF LOGGED IN ────────────────────────────────────────────────────────────────
if "user_email" in st.session_state:
    if st.button("Look at your existing portfolio! 😎"):
        st.switch_page("pages/Your_Portfolio.py")


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
    "data_loaded": False, # flag to check if data for a universe is loaded
    "watch_list": [], # list of symbols being tracked for the user
    "ticker_input": "", # user search query
    "universe_tickers": [], # list of symbols from a universe
    "current_cap_size": "",  # to track the chosen cap size
    "all_ticker_data": pd.DataFrame(),  # to store all ticker data
    "persisted_tickers": set(),

}

# add session essentials to the session state
for key, value in session_essentials.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ── FETCH DATA AND SEARCH BAR LOGIC ────────────────────────────────────────────────────────────────
fetch_btn = st.button("Fetch Data")

# if fetch btn is pressed and no data has been loaded yet
if fetch_btn and not st.session_state.data_loaded:
    loading_msg.info("🔄 Fetching data… please wait.")
    st.session_state.data_loaded = True # data_loaded is set to true because fetch_btn is pressed
    
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
    all_ticker_data = pd.concat(frames, axis=1)

    # compute tickert stats like change, RSI and average volume
    ticker_stats = get_ticker_stats(data=all_ticker_data, symbols=universe)

    # convert to DataFrame
    ticker_stats_df = pd.DataFrame(ticker_stats)
    
    # save all ticker stats as a session state variable
    st.session_state.all_ticker_data = ticker_stats_df

    loading_msg.empty()

# if cap size changes, change the data loaded flag to false > only make the search bar appear when the user sticks to a cap_size
if st.session_state.current_cap_size != cap_size:
    st.session_state.data_loaded = False
    st.session_state.persisted_tickers = set()


# ── SEARCH BAR AND DATA BASE PERSISTING ────────────────────────────────────────────────────────────────
if st.session_state.data_loaded: # > if data is loaded show example tickers and search bar
    example_list = st.session_state.universe_tickers
    search_inputs = (
        st.text_input(
            "Enter comma seperated ticker symbol",
            placeholder=f"e.g. {str(example_list[:10]).strip("[]")}",
            key="ticker_input",
        )

    )
    search_inputs = search_inputs.split(",") # split comma separated entries of the user

    # initialize a dataframe to store tickers added in a session
    added_tickers = pd.DataFrame()
    
    # loop through all search inputs
    for search_input in search_inputs:
        search_input = search_input.strip().upper()
        if search_input: # provided there is a search input -> 1) check if its in the universe and 2) check if its already added to the watchlist
            if search_input not in st.session_state.universe_tickers:
                st.warning(f"Ticker {search_input} not found in universe.")
            elif search_input in st.session_state.watch_list:
                st.warning(f"Ticker {search_input} already in watch list.")
            else: # add symbol to watchlist

                # Add to watch list and render
                st.session_state.watch_list.append(search_input)

                # filter all ticker data for the users search input
                test_df = st.session_state.all_ticker_data
                test_df = test_df[test_df["Symbol"] == search_input]

                # add ticker data to the dataframe
                added_tickers = pd.concat([added_tickers, test_df], ignore_index=True)
                st.toast(f"Ticker {search_input} added to watch list.")

                # persist data in user DB if not already done in the current session
                if search_input not in st.session_state.persisted_tickers and user is not None: # this only works if user is logged in
                    with sqlite3.connect(DB_PATH) as conn:
                        if insert_portfolios_row( # > function checks if a stock is already present in the user database
                            conn,
                            st.session_state.user_email,
                            st.session_state.current_cap_size,
                            search_input,
                        ):
                            st.success("Portfolio row saved!")
                        else:
                            st.info("That stock is already in your portfolio.")
                    st.session_state.persisted_tickers.add(search_input)

    # display tickers that are added to the watchlist regardless of whether the user is logged in
    if not added_tickers.empty:
        render_company_blocks(ticker_stats_df=added_tickers)           

else: # prompt user to fetch data to begin using this page
    loading_msg.info("Please click 'Fetch Data' to load the data.")
