import streamlit as st
import pandas as pd
from american import load_sp500, load_spmid400, load_spsmall600
from utilities.ticker_info import get_ticker_stats, download_ticker_data
from utilities.adjust_ui import render_company_blocks
import utilities.auth_utils as auth
from utilities.db_utils import insert_portfolios_row

# ─────────────────────────────────────────────────────────────
# PAGE SETTINGS
# ─────────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_icon="📉📈")
st.title("🏪 Make Your Own Portfolio")
st.info("Create a portfolio of stocks from all three universes.")

# ─────────────────────────────────────────────────────────────
# AUTHENTICATION LOGIC
# ─────────────────────────────────────────────────────────────
if "use_without_log_in" not in st.session_state:
    st.session_state.use_without_log_in = False

user = auth.get_user_info()  # returns user info dict or None

if user is None and not st.session_state.use_without_log_in:
    st.button("Continue without logging in", on_click=lambda: st.session_state.update(use_without_log_in=True))
    auth.login_button()
    st.stop()

elif user is not None:
    st.session_state.user_email = user["email"]
    st.sidebar.button("Log out", on_click=auth.logout)
    st.success(f"Welcome, {user['email']}")

elif st.session_state.use_without_log_in:
    st.success("Welcome, anonymous user! Feel free to browse freely. Refresh to sign in later 😃")

# ─────────────────────────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────────────────────────
if "user_email" in st.session_state:
    if st.button("Look at your existing portfolio! 😎"):
        st.switch_page("pages/Your_Portfolio.py")

# ─────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────
session_defaults = {
    "data_loaded": False,
    "watch_list": [],
    "ticker_input": "",
    "universe_tickers": [],
    "current_cap_size": "",
    "all_ticker_data": pd.DataFrame(),
    "persisted_tickers": set(),
}

for key, val in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────────────────────────
# MAIN APP CONTENT (ONLY AFTER LOGIN DECISION)
# ─────────────────────────────────────────────────────────────
loading_msg = st.empty()

cap_size = st.radio(
    "Cap Size universe",
    ["Large (S&P 500)", "Mid (S&P 400)", "Small (S&P 600)"],
    horizontal=True,
)

fetch_btn = st.button("Fetch Data")

# ─────────────────────────────────────────────────────────────
# FETCH DATA LOGIC
# ─────────────────────────────────────────────────────────────
if fetch_btn and not st.session_state.data_loaded:
    loading_msg.info("🔄 Fetching data… please wait.")
    st.session_state.data_loaded = True

    if cap_size.startswith("Large"):
        universe = load_sp500()
    elif cap_size.startswith("Mid"):
        universe = load_spmid400()
    else:
        universe = load_spsmall600()

    st.session_state.universe_tickers = universe
    st.session_state.current_cap_size = cap_size

    frames = download_ticker_data(symbols=universe)
    all_ticker_data = pd.concat(frames, axis=1)
    ticker_stats = get_ticker_stats(data=all_ticker_data, symbols=universe)
    ticker_stats_df = pd.DataFrame(ticker_stats)
    st.session_state.all_ticker_data = ticker_stats_df
    loading_msg.empty()

# reset data_loaded if user changes cap size
if st.session_state.current_cap_size != cap_size:
    st.session_state.data_loaded = False
    st.session_state.persisted_tickers = set()

# ─────────────────────────────────────────────────────────────
# SEARCH + PORTFOLIO PERSISTENCE
# ─────────────────────────────────────────────────────────────
if st.session_state.data_loaded:
    example_list = st.session_state.universe_tickers
    search_inputs = st.text_input(
        "Enter comma-separated ticker symbols",
        placeholder=f"e.g. {str(example_list[:10]).strip('[]')}",
        key="ticker_input",
    )
    search_inputs = search_inputs.split(",")
    added_tickers = pd.DataFrame()

    for search_input in search_inputs:
        search_input = search_input.strip().upper()
        if not search_input:
            continue

        if search_input not in st.session_state.universe_tickers:
            st.warning(f"Ticker {search_input} not found in universe.")
        elif search_input in st.session_state.watch_list:
            st.info(f"Ticker {search_input} already in watch list.")
        else:
            st.session_state.watch_list.append(search_input)
            test_df = st.session_state.all_ticker_data
            filtered = test_df[test_df["Symbol"] == search_input]
            added_tickers = pd.concat([added_tickers, filtered], ignore_index=True)
            st.toast(f"Ticker {search_input} added to watch list.")

            # persist in Supabase
            if user is not None and search_input not in st.session_state.persisted_tickers:
                try:
                    if insert_portfolios_row(
                        st.session_state.user_email,
                        st.session_state.current_cap_size,
                        search_input,
                    ):
                        st.success(f"✅ {search_input} saved to your portfolio!")
                    else:
                        st.info(f"ℹ️ {search_input} is already saved.")
                    st.session_state.persisted_tickers.add(search_input)
                except Exception as e:
                    st.error(f"⚠️ Failed to save {search_input}: {e}")

    if not added_tickers.empty:
        render_company_blocks(ticker_stats_df=added_tickers)
else:
    loading_msg.info("Please click 'Fetch Data' to load data.")
