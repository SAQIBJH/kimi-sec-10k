"""
Unified Entry Point - Coresight Research Portal
Single port for all pages with URL routing
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

# Initialize
from core.database import init_database
init_database()

from components.styles import hide_sidebar, set_page_layout
hide_sidebar()

from components.styles import render_styles
from components.navigation import render_header, render_coresight_footer

# Get page from query params
query_params = st.query_params
page = query_params.get("page", "home")

# Route to appropriate page
if page == "home":
    # Import and render homepage content
    from pages.home import main as render_home
    render_styles()
    render_home()
    
elif page == "market_data":
    # Import and render market data
    from pages.market_data import render_page
    render_styles()
    
    # Set layout
    set_page_layout(
        header_full_width=True,
        footer_full_width=True,
        body_padding="0 20px",
        max_content_width="1350px",
        remove_top_padding=True,
        footer_at_bottom=True
    )
    
    render_header(full_width=True)
    
    # Handle tab parameter
    tab = query_params.get("tab", "income_statement")
    if tab in ["income_statement", "balance_sheet", "cash_flow", "key_stats", "company_profile"]:
        # Set the tab in session state before rendering
        st.session_state.market_data_tab = tab
    
    render_page()
    render_coresight_footer(full_width=True, stick_to_bottom=True)
    
elif page == "newsroom":
    from pages.newsroom import render_page as render_newsroom
    render_styles()
    
    set_page_layout(
        header_full_width=True,
        footer_full_width=True,
        body_padding="0 20px",
        max_content_width="1350px",
        remove_top_padding=True,
        footer_at_bottom=True
    )
    
    render_header(full_width=True)
    render_newsroom()
    render_coresight_footer(full_width=True, stick_to_bottom=True)
    
elif page == "earnings_calls":
    from pages.earnings_calls import render_earnings_calls
    render_styles()
    
    set_page_layout(
        header_full_width=True,
        footer_full_width=True,
        body_padding="0",
        max_content_width="1440px",
        remove_top_padding=True,
        footer_at_bottom=True
    )
    
    render_header(full_width=True)
    render_earnings_calls()
    render_coresight_footer(full_width=True, stick_to_bottom=True)
    
elif page == "company_profile":
    from pages.company_profile import render_company_profile
    render_styles()
    
    set_page_layout(
        header_full_width=True,
        footer_full_width=True,
        body_padding="0 20px",
        max_content_width="1350px",
        remove_top_padding=True,
        footer_at_bottom=True
    )
    
    render_header(full_width=True)
    ticker = query_params.get("ticker", "M")
    render_company_profile(ticker)
    render_coresight_footer(full_width=True, stick_to_bottom=True)
    
else:
    # Default to home
    from pages.home import main as render_home
    render_styles()
    render_home()
