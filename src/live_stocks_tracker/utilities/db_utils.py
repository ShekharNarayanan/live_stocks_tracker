import sqlite3, pathlib
import pandas as pd
from pathlib import Path
from utilities.ticker_info import get_ticker_stats, download_ticker_data


def insert_portfolios_row(conn: sqlite3.Connection,
                 email:str,
                 cap_size:str,
                 ticker:str) -> bool:
    """
    Guarantee that a (email, cap_size, ticker) row exists.

    Returns
    -------
    bool
        True  → a NEW row was inserted
        False → the identical row was already present
    """
    # 1️⃣ See if the exact row already exists
    cur = conn.execute(
        "SELECT 1 FROM portfolios "
        "WHERE email=? AND ticker=?",
        (email, ticker),
    )
    if cur.fetchone():            # already there
        return False

    # 2️⃣ Otherwise insert it
    conn.execute(
        "INSERT INTO portfolios (email, cap_size, ticker) "
        "VALUES (?,?,?)",
        (email, cap_size, ticker),
    )
    conn.commit()
    return True


def fetch_portfolio_from_db(email: str, cap_size: str, DB_PATH: pathlib.Path) -> tuple[list[str], pd.DataFrame]:
    """
    Return (symbols_list, ticker_stats_df) for the user's saved portfolio.
    If no rows, returns ([], empty_df).
    """
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM portfolios
            WHERE email = ? AND cap_size = ?
            """,
            (email, cap_size),
        )
        rows = cur.fetchall()

    # assuming schema: (id, email, cap_size, symbol)
    symbols = [row[2] for row in rows]

    if not symbols:
        return [], pd.DataFrame(columns=["Symbol", "Change", "RSI14", "AvgVol30d", "Price", "Price_30d_ago"])

    # Pull fresh stats just for these symbols (independent of “Fetch Data”)
    frames = download_ticker_data(symbols=symbols)
    all_ticker_data = pd.concat(frames, axis=1)
    ticker_stats = get_ticker_stats(data=all_ticker_data, symbols=symbols)
    ticker_stats_df = pd.DataFrame(ticker_stats)
    return symbols, ticker_stats_df

if __name__ == "__main__":
    # Create Table if it doesn't exist
    DB_PATH = Path(__file__).parents[3] / "portfolios.db"
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolios (
                email     TEXT NOT NULL,
                cap_size  TEXT NOT NULL,   -- e.g. 'large', 'mid', 'small'
                ticker    TEXT NOT NULL,
                PRIMARY KEY (email, ticker)   -- one row per user–stock pair
            );
            """
        )