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
from core.auth_manager import logout
params = st.query_params
if params.get("action") == "logout":
    logout()
    # Clear all query params and force a rerun so navigation picks up the default page
    st.query_params.clear()
    st.rerun()

# Initialize database
from core.database import init_database
init_database()

# Register all pages with st.navigation()
pg = st.navigation(
    [
        st.Page("pages/login.py",            title="Login",             url_path="login",            default=True),
        st.Page("pages/home.py",            title="Home",             url_path="home"),
        st.Page("pages/market_data.py",     title="Market Data",      url_path="market_data"),
        st.Page("pages/newsroom.py",        title="Newsroom",         url_path="newsroom"),
        st.Page("pages/earnings_calls.py",  title="Earnings Calls",   url_path="earnings_calls"),
        st.Page("pages/company_filings.py", title="Company Filings",  url_path="company_filings"),
    ],
    position="hidden",
)

pg.run()
