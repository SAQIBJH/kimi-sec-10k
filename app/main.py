# app/main.py
"""
Coresight Research Portal - Main Entry Point
Initializes SSL certificates and database connections
"""

import streamlit as st

st.set_page_config(
    page_title="Market Data Portal",
    page_icon="https://coresight.com/wp-content/uploads/2019/03/cropped-CoreSightTransparent_Logo_favico-32x32.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Download SSL CA certificate before database init (required for secure MySQL connections)
from core.ssl_setup import ensure_ca_cert
ensure_ca_cert()

# Register navigation first — required before any st.switch_page() calls
pg = st.navigation(
    [
        st.Page("pages/login.py",            title="Login",             url_path="login",            default=True),
        st.Page("pages/home.py",             title="Home",              url_path="home"),
        st.Page("pages/market_data.py",      title="Market Data",       url_path="market_data"),
        st.Page("pages/newsroom.py",         title="Newsroom",          url_path="newsroom"),
        st.Page("pages/earnings_calls.py",   title="Earnings Calls",    url_path="earnings_calls"),
        st.Page("pages/company_filings.py",  title="Company Filings",   url_path="company_filings"),
    ],
    position="hidden",
)

from core.auth_manager import get_current_domain
import streamlit.components.v1 as _components
from time import sleep as _sleep

params = st.query_params
if params.get("action") == "logout":
    # Clear session state immediately
    for _k in ["auth_data", "authenticated"]:
        if _k in st.session_state:
            del st.session_state[_k]
    st.query_params.clear()

    # Clear cookie via JS — domain comes from get_current_domain(), never hardcoded
    _domain = get_current_domain()
    _exp = "expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"
    _clears = f"document.cookie='auth_session=; {_exp}';"
    if _domain:
        _clears += f"document.cookie='auth_session=; {_exp} domain={_domain};';"
    _components.html(f"<script>(function(){{{_clears}}})()</script>", height=0)
    _sleep(0.8)  # Wait for same-origin iframe to load and JS to run

    st.switch_page("pages/login.py")
    st.stop()

# Initialize database
from core.database import init_database
init_database()

pg.run()
