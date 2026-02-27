"""
Homepage - Coresight Research
"""
import streamlit as st
from components.styles import hide_sidebar, render_styles
from components.navigation import render_header, render_coresight_footer
from core.auth_manager import require_auth
from data.repository import CompanyRepository
from utils.local_storage_manager import set_persistent_state, save_market_data_state
require_auth()
hide_sidebar()

@st.cache_data(ttl=300)
def _load_companies():
    """Fetch companies from database, returns list of (ticker, name) tuples."""
    rows = CompanyRepository.get_companies()
    return [(r['ticker'], r['name']) for r in rows]

COMPANIES = _load_companies()
SECTORS = ["Apparel & Footwear", "Department Stores", "Discount Stores", "Luxury Goods"]

def main():
    if 'home_company' not in st.session_state:
        st.session_state.home_company = COMPANIES[0][0] if COMPANIES else ""
    if 'home_sector' not in st.session_state:
        st.session_state.home_sector = SECTORS[0]

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&family=Montserrat:wght@400;500;600;700&display=swap');

    .block-container { padding: 0 !important; max-width: 100% !important; }
    .appview-container .main .block-container { padding-top: 0 !important; }
    [data-testid="stSidebar"] { display: none !important; }

    .main-title {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        font-size: 39px !important;
        color: #D62E2F !important;
        text-align: center !important;
        letter-spacing: -0.5px !important;
        margin: 96px 0 32px 0 !important;
    }

    /* Card wrapper - gray background for columns */
    [data-testid="stColumn"]:nth-of-type(2) > div,
    [data-testid="stColumn"]:nth-of-type(3) > div {
        background-color: #EBEBEB !important;
        border-radius: 8px !important;
        padding: 8px 16px 28px 16px !important;
        width: 357px !important;
        margin: 0 auto !important;
    }

    /* Streamlit Selectbox Styling - White background */
    div[data-testid="stSelectbox"] {
        margin-bottom: 8px !important;
    }

    div[data-testid="stSelectbox"] > label { display: none !important; }

    /* Force white background on selectbox */
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
    }

    /* The actual input/control */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        min-height: 40px !important;
        height: 40px !important;
        padding-bottom: 40px !important;
    }

    /* Hover and focus states */
    div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover,
    div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within {
        border-color: #D62E2F !important;
        box-shadow: 0 0 0 1px #D62E2F !important;
    }

    /* Text styling */
    div[data-testid="stSelectbox"] span {
        font-family: 'Roboto', sans-serif !important;
        font-weight: 400 !important;
        font-size: 14px !important;
        color: #000000 !important;
    }

    /* Dropdown icon */
    div[data-testid="stSelectbox"] svg { color: #666666 !important; }
    </style>
    """, unsafe_allow_html=True)

    render_styles()
    render_header(full_width=True, current_page="home")

    # Main title
    st.markdown('<h1 class="main-title">CORESIGHT MARKET DATA</h1>', unsafe_allow_html=True)

    # Two cards side by side
    col_spacer1, col1, col2, col_spacer2 = st.columns([1, 2, 2, 1])

    # Card 1: View by Company
    with col1:
        st.markdown('<p style="font-family: Roboto, sans-serif; font-weight: 600; font-size: 18px; color: #2D2A29; text-align: center; margin: 0 0 8px 0;">View by Company</p>', unsafe_allow_html=True)

        company = st.selectbox("Company", options=[c[0] for c in COMPANIES],
            format_func=lambda x: next((c[1] for c in COMPANIES if c[0] == x), x),
            index=[c[0] for c in COMPANIES].index(st.session_state.home_company),
            key="company_select", label_visibility="collapsed")
        st.session_state.home_company = company
        # No need to save ticker to local storage - it will be passed via query params
        save_market_data_state()
        st.markdown(f'''
            <a href="/market_data?ticker={company}" target="_self" style="background-color: #D62E2F; color: white; font-family: Montserrat, sans-serif; font-weight: 700; font-size: 16px; border-radius: 8px; padding: 8px 16px; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 8px; width: 100%; height: 41px; box-sizing: border-box;">
                View
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                    <path d="M10 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"/>
                    <path d="M14 4h6v6"/>
                    <path d="M21 3 12 12"/>
                </svg>
            </a>
        ''', unsafe_allow_html=True)

    # Card 2: View by Sector
    with col2:
        st.markdown('<p style="font-family: Roboto, sans-serif; font-weight: 600; font-size: 18px; color: #2D2A29; text-align: center; margin: 0 0 8px 0;">View by Sector</p>', unsafe_allow_html=True)

        sector = st.selectbox("Sector", options=SECTORS,
            index=SECTORS.index(st.session_state.home_sector) if st.session_state.home_sector in SECTORS else 0,
            key="sector_select", label_visibility="collapsed")
        st.session_state.home_sector = sector
        set_persistent_state('selected_sector_home', sector)
        save_market_data_state()
        st.markdown('''
            <a href="/market_data" style="background-color: #D62E2F; color: white; font-family: Montserrat, sans-serif; font-weight: 700; font-size: 16px; border-radius: 8px; padding: 8px 16px; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 8px; width: 100%; height: 41px; box-sizing: border-box;">
                View
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                    <path d="M10 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"/>
                    <path d="M14 4h6v6"/>
                    <path d="M21 3 12 12"/>
                </svg>
            </a>
        ''', unsafe_allow_html=True)

    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    render_coresight_footer(full_width=True, stick_to_bottom=True)

main()

if __name__ == "__main__":
    pass
