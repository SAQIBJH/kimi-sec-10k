"""
Unified Entry Point - Coresight Research Portal
Uses Streamlit's built-in multipage navigation for hot-reload support.
"""
import streamlit as st

# MUST be first Streamlit command
st.set_page_config(
    page_title="Coresight Research Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Handle logout action (must be AFTER set_page_config)
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