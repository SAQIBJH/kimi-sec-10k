"""
Unified Entry Point - Coresight Research Portal v3.0
====================================================
Single entry point for all pages with URL-based routing.
Uses existing page implementations without modification.

URL Patterns:
- /?page=home                      -> Homepage (default)
- /?page=company_profile&ticker=M  -> Company Profile
- /?page=market_data&tab=income_statement&ticker=M -> Market Data
- /?page=newsroom&ticker=M         -> Newsroom
- /?page=earnings_calls&ticker=M   -> Earnings Calls
"""
import streamlit as st

# Configure page settings - MUST be first Streamlit command
st.set_page_config(
    page_title="Coresight Research Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Import page modules
from pages.home import main as render_home
from pages.company_profile import render_company_profile
from pages.market_data import render_page as render_market_data
from pages.newsroom import render_page as render_newsroom
from pages.earnings_calls import render_earnings_calls


def main():
    """Main entry point with URL routing."""
    # Initialize database
    from core.database import init_database
    init_database()
    
    # Get query parameters
    query_params = st.query_params
    page = query_params.get("page", "home")
    
    # Route to appropriate page
    if page == "home":
        # Homepage - uses existing homepage.py implementation
        render_home()
        
    elif page == "company_profile":
        # Company Profile page
        ticker = query_params.get("ticker", "M")
        render_company_profile(ticker)
        
    elif page == "market_data":
        # Market Data page
        ticker = query_params.get("ticker", None)
        render_market_data(ticker)
        
    elif page == "newsroom":
        # Newsroom page
        ticker = query_params.get("ticker", None)
        render_newsroom(ticker)
        
    elif page == "earnings_calls":
        # Earnings Calls page
        ticker = query_params.get("ticker", None)
        render_earnings_calls(ticker)
        
    else:
        # Default to home
        render_home()


if __name__ == "__main__":
    main()
