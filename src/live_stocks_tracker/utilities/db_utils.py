import sqlite3, pathlib

DB_PATH = pathlib.Path("portfolios.db")

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

with sqlite3.connect(DB_PATH) as conn:
    for row in conn.execute("SELECT email, cap_size, ticker FROM portfolios"):
        print(row) 