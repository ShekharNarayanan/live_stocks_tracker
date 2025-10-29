# import streamlit as st
# from pathlib import Path
# from utilities.db_utils import  fetch_portfolio_from_db
# from utilities.adjust_ui import render_company_blocks
# import os


# #  ── PATHS ────────────────────────────────────────────────────────────────
# parent_dir = Path(__file__).parents[1]
# DB_PATH = parent_dir / "portfolios.db"

# if os.path.exists(DB_PATH) is False:
#     st.warning(f"Database not found. current path. Current path: {DB_PATH}")
#     st.stop()

# #   ── DISPLAY PORTFOLIO ────────────────────────────────────────────────────────────────
# if "user_email" in st.session_state:
#     st.write(f"Welcome back, {st.session_state.user_email}!\n Here is your portfolio")

#     # ── ADD RADIO SETTINGS ──────────────────────────────────────────────────────────────────
#     cap_size = st.radio(
#         "Cap Size universe",
#         [
#             "Large (S&P 500)",
#             "Mid (S&P 400)",
#             "Small (S&P 600)",
#         ],  # categories on the side bar
#         horizontal=True,
#     )

#     symbols, portfolio_df = fetch_portfolio_from_db(
#     st.session_state.user_email,
#     cap_size,  # default cap size for now
#     DB_PATH=DB_PATH
# )
#     if symbols:
#         render_company_blocks(ticker_stats_df=portfolio_df)
#     else:
#         st.warning(f"Whoops! You dont have any tickers from the {cap_size} universe.")
#         if st.button("Add new tickers ➕"):
#             st.switch_page("pages/Make_Your_Portfolio.py")

# else:
#     st.warning("Please log in on the watchlist page to access your saved portfolio")
#     if st.button("Take me there 🥊"):
#         st.switch_page("pages/Make_Your_Portfolio.py")

import streamlit as st
from utilities.db_utils import fetch_portfolio_from_db
from utilities.adjust_ui import render_company_blocks
import utilities.auth_utils as auth

#  ── AUTH CHECK ────────────────────────────────────────────────────────────────
user = auth.get_user_info()

if user is None and "user_email" not in st.session_state:
    st.warning("Please log in on the watchlist page to access your saved portfolio.")
    if st.button("Take me there 🥊"):
        st.switch_page("pages/Make_Your_Portfolio.py")
    st.stop()

# If user logged in, save email for current session
if user is not None:
    st.session_state.user_email = user["email"]
    st.sidebar.button("Log out", on_click=auth.logout)
    st.success(f"Welcome back, {user['email']}!")

#   ── DISPLAY PORTFOLIO ────────────────────────────────────────────────────────────────
if "user_email" in st.session_state:
    st.write(f"Welcome back, {st.session_state.user_email}!\nHere is your portfolio")

    # ── ADD RADIO SETTINGS ────────────────────────────────────────────────────────────────
    cap_size = st.radio(
        "Cap Size universe",
        ["Large (S&P 500)", "Mid (S&P 400)", "Small (S&P 600)"],
        horizontal=True,
    )

    try:
        symbols, portfolio_df = fetch_portfolio_from_db(
            st.session_state.user_email,
            cap_size  # Supabase version of fetch_portfolio_from_db no longer needs DB_PATH
        )
    except Exception as e:
        st.error(f"⚠️ Could not fetch portfolio: {e}")
        st.stop()

    if symbols:
        render_company_blocks(ticker_stats_df=portfolio_df)
    else:
        st.warning(f"Whoops! You don’t have any tickers from the {cap_size} universe.")
        if st.button("Add new tickers ➕"):
            st.switch_page("pages/Make_Your_Portfolio.py")
else:
    st.warning("Please log in on the watchlist page to access your saved portfolio.")
    if st.button("Take me there 🥊"):
        st.switch_page("pages/Make_Your_Portfolio.py")
