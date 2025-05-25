import streamlit as st



def get_logo_from_symbol(symbol, size=30):
    """
    Get the logo URL for a given stock symbol from Parqet. Check it out here:
    https://www.parqet.com/api/logos

    Args:
        symbol (str): Stock symbol to get the logo for, e.g. 'AAPL' for Apple Inc.
        size (int, optional): Size of the logo in pixels. Defaults to 30 x30.

    Returns:
        _type_: _description_
    """
    img_url = f"https://assets.parqet.com/logos/symbol/{symbol}?format=jpg&size={size}"
    
    return img_url
def render_company_blocks(df,days):
    """
    Render a Streamlit block for each row in the given DataFrame.
    
    Every block is a bordered div with a header (stock symbol) and 4 rows of text:
    - sector (if available)
    - change (with arrow and color)
    - current price
    - price 30 days ago
    - RSI-14
    - average 30-day volume
    
    The blocks are arranged in columns of 4, wrapping to the next line if there are more than 4 entries.
    """
    
    """"""
    cols = st.columns(4)
    for idx, row in df.reset_index(drop=True).iterrows():
        with cols[idx % 4]:
            # every block wrapped in a bordered div
            st.markdown(
                f"""
                <div style="
                    border:6px solid #004080;
                    border-radius:6px;
                    padding:5px 12px;
                    margin-bottom:12px;
                    ">
                    <h3 style="margin:0">{row.Symbol}</h3>
                    <span style="font-size:25px;color:#aaaaaa;">{row.Sector if row.Sector!='-' else ''}</span><br>
                    <span style="font-size:25px; color:{'red' if row.Change<0 else 'green'};">
                        {'↓' if row.Change<0 else '↑'} {row.Change:+.2f}%
                    </span><br>
                    <span style="font-size:25px;color:green;">Now €{row.Today:.2f}</span><br>
                    <span style="font-size:25px;color:red;">{days} d ago €{row.Ago:.2f}</span><br>
                    <span style="font-size:20px;">RSI-14: {row.RSI:.1f}</span><br>
                    <span style="font-size:20px;">Avg Vol (30 d): {row.AvgVol:,.0f}</span>
                </div>
                """,
                unsafe_allow_html=True
            )