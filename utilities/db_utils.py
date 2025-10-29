import pandas as pd
import psycopg2
import streamlit as st
from utilities.ticker_info import get_ticker_stats, download_ticker_data

def get_connection():
    cfg = st.secrets["supabase"]
    conn = psycopg2.connect(
        host=cfg["host"],
        database=cfg["database"],
        user=cfg["user"],
        password=cfg["password"],
        port=cfg["port"]
    )
    return conn

def insert_portfolios_row(email: str, cap_size: str, ticker: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM portfolios WHERE email=%s AND ticker=%s", (email, ticker))
    exists = cur.fetchone()
    if exists:
        conn.close()
        return False
    cur.execute(
        "INSERT INTO portfolios (email, cap_size, ticker) VALUES (%s, %s, %s)",
        (email, cap_size, ticker)
    )
    conn.commit()
    conn.close()
    return True

def fetch_portfolio_from_db(email: str, cap_size: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT ticker FROM portfolios WHERE email=%s AND cap_size=%s",
        (email, cap_size)
    )
    symbols = [r[0] for r in cur.fetchall()]
    conn.close()

    if not symbols:
        return [], pd.DataFrame()

    frames = download_ticker_data(symbols=symbols)
    all_ticker_data = pd.concat(frames, axis=1)
    ticker_stats = get_ticker_stats(data=all_ticker_data, symbols=symbols)
    ticker_stats_df = pd.DataFrame(ticker_stats)
    return symbols, ticker_stats_df
