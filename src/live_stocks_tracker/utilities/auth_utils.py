# auth.py
import streamlit as st
import requests
from streamlit_oauth import OAuth2Component

# --- internal ---------------------------------------------------------------
def _oauth2() -> OAuth2Component:
    cfg = st.secrets["google_oauth"]
    return OAuth2Component(
        cfg["client_id"],
        cfg["client_secret"],
        cfg["authorize_url"],
        cfg["token_url"],
        cfg["token_url"],          # refresh uses same endpoint for Google
        cfg["revoke_token_url"],
    )

def _get_token():
    return st.session_state.get("token")

def _save_token(tok: dict):
    st.session_state.token = tok

# --- public API -------------------------------------------------------------
def login_button(label_sign_in: str = "Continue with Google"):
    """
    Renders a Google-sign-in button.
    • If the user authorizes, the access token is cached in st.session_state.
    • If already signed in, nothing is shown.
    """
    if _get_token() is not None:
        return  # already signed in

    cfg = st.secrets["google_oauth"]
    result = _oauth2().authorize_button(
        label_sign_in,
        cfg["redirect_uri"],
        cfg["scope"],
    )
    if result and "token" in result:
        _save_token(result["token"])
        st.rerun()

def get_user_info():
    """
    Returns the Google /userinfo JSON for the signed-in user,
    or None if not authenticated / token expired.
    """
    tok = _get_token()
    if tok is None:
        return None

    resp = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {tok['access_token']}"},
        timeout=10,
    )
    if resp.status_code == 200:
        return resp.json()

    # token expired or revoked → wipe it
    st.session_state.pop("token", None)
    return None

def logout():
    """Revokes the token (best-effort) and clears session state."""
    tok = st.session_state.pop("token", None)
    if tok:
        try:
            _oauth2().revoke_token(tok)
        except Exception:
            pass
