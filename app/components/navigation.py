"""
Navigation components for the application.
"""
import streamlit as st
from typing import List, Dict, Callable, Optional
from enum import Enum
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.styles import COLORS, TYPOGRAPHY, SPACING, BORDER_RADIUS
import streamlit as st

# Import auth functions
from core.auth_manager import is_authenticated, get_current_user, logout, get_auth_manager

def render_header(full_width: bool = True, current_page: str = "market_data",ticker: str = "M"):
    """
    Render Coresight header based on Figma design - EXACT MATCH.

    Figma Reference: Header (Node ID: 20895:206587)
    - Container: 1440x80px, background #f2f2f2
    - Logo: 132x60px at x=390 (106px from left edge)
    - Nav: Frame at x=568 with 48px gaps between items
    - Nav items: Roboto 18px weight 500
    - Nav text color: #2d2a29

    Parameters:
    -----------
    full_width : bool
        If True, header takes full width
    current_page : str
        Current page identifier for active nav highlighting
    """
    is_newsroom = current_page == "newsroom"
    is_company_profile = current_page == "company_profile"
    is_earnings_calls = current_page == "earnings_calls"

    # Priority: session state active_ticker > URL query param > function argument
    actual_ticker = st.session_state.get("active_ticker") or st.query_params.get("ticker", ticker) or ticker
    
    # Build header HTML - EXACT Figma specifications
    header_html = '''<style>
    /* Header full-width wrapper - background #f2f2f2 */
    .coresight-header-exact {
      background-color: #f2f2f2;
      width: 100vw;
      margin-left: calc(-50vw + 50%);
      margin-right: calc(-50vw + 50%);
      box-sizing: border-box;
      position: sticky;
      top: 0;
      z-index: 1000;
    }

    /* Header container - 1440px max width, centered, flex layout */
    .coresight-header-container {
      max-width: 1440px;
      margin: 0 auto;
      height: 80px;
      display: flex;
      align-items: center;
      gap: 46px; /* Gap from logo to nav: 568 - 390 - 132 = 46px */
      padding-left: 106px; /* Logo at x=390 which is 106px from left edge of 1440px container */
    }

    /* Logo - 132x60px */
    .coresight-header-logo {
      flex-shrink: 0;
      width: 132px;
      height: 60px;
    }
    .coresight-header-logo img {
      width: 132px;
      height: 60px;
      object-fit: contain;
      display: block;
    }

    /* Navigation - horizontal layout with 48px gaps */
    .coresight-header-nav {
      display: flex;
      align-items: center;
      gap: 48px;
      height: 26px;
    }

    /* Nav links - Roboto 18px weight 500, color #2d2a29 */
    .coresight-header-nav a {
      font-family: 'Roboto', sans-serif;
      font-size: 18px;
      font-weight: 500;
      color: #2d2a29;
      text-decoration: none;
      white-space: nowrap;
      transition: color 0.2s ease;
      line-height: 26px;
    }
    .coresight-header-nav a:hover {
      color: #d62e2f;
    }
    .coresight-header-nav a.active {
      color: #d62e2f;
    }

    /* Logout button - styled as nav link with red color */
    .logout-btn {
    font-family: 'Roboto', sans-serif;
    font-size: 16px;
    font-weight: 500;
    color: #d62e2f;
    text-decoration: none;
    white-space: nowrap;
    line-height: 1;
    padding: 8px 18px;
    border-radius: 6px;
    border: 1px solid #d62e2f;
    background-color: white !important;
    transition: all 0.18s ease;
    margin-right: 40px;
    cursor: pointer;
  }

  .logout-btn:hover {
    background-color: #d62e2f !important;
    color: #ffffff;
    border-color: transparent;
    box-shadow: 0 2px 6px rgba(214, 46, 47, 0.25);
  }

    /* Remove default Streamlit padding */
    .stApp > header {
      display: none !important;
    }
    .main > div:first-child {
      padding-top: 0 !important;
    }

    /* Prevent horizontal scroll */
    html, body {
      overflow-x: hidden !important;
      max-width: 100% !important;
    }
    .stApp {
      overflow-x: hidden !important;
    }

    /* Responsive adjustments */
    @media (max-width: 1024px) {
      .coresight-header-container {
        padding-left: 20px;
        gap: 30px;
      }
      .coresight-header-nav {
        gap: 24px;
      }
      .coresight-header-nav a {
        font-size: 14px;
      }
    }

    @media (max-width: 768px) {
      .coresight-header-nav {
        display: none;
      }
    }
    </style>

    <div class="coresight-header-exact">
      <div class="coresight-header-container">
        <!-- Logo: 132x60 at x=390 (106px from left edge) -->
        <div class="coresight-header-logo">
          <a href="https://coresight.com/">
            <img src="https://production-wordpress-cdn-dpa0g9bzd7b3h7gy.z03.azurefd.net/wp-content/uploads/2023/12/coresight-logo-1.png" 
                alt="Coresight Research" width="132" height="60">
          </a>
        </div>
        
        <!-- Navigation: at x=568, 48px gaps between items, Roboto 18px weight 500 -->
        <nav class="coresight-header-nav">
          <a href="/market_data?ticker=''' + actual_ticker + '''" target="_self" class="''' + ('active' if not is_newsroom and not is_company_profile and not is_earnings_calls else '') + '''">Market Data Dashboard</a>
          <a href="/earnings_calls?ticker=''' + actual_ticker + '''" target="_self" class="''' + ('active' if is_earnings_calls else '') + '''">Earnings Calls</a>
          <a href="/newsroom?ticker=''' + actual_ticker + '''" target="_self" class="''' + ('active' if is_newsroom else '') + '''">News</a>
        </nav>
        
        <!-- Spacer to push logout to right -->
        <div style="flex: 1;"></div>
        <a href="?action=logout" class="logout-btn">Logout</a>
        <!-- Logout placeholder - Streamlit button will be injected here -->
        <div id="logout-container" style="margin-right: 40px;"></div>
      </div> 
      
    </div>'''
    
    # Use st.html for proper rendering
    try:
        st.html(header_html)
    except AttributeError:
        st.markdown(header_html, unsafe_allow_html=True)


def render_coresight_footer(full_width: bool = True, stick_to_bottom: bool = True):
    """
    Render Coresight footer based on Figma design - EXACT MATCH.
    
    Figma Reference: Advisory/Footer (Node ID: 20881:205174)
    - Background: #f2f2f2
    - Layout: 4 columns with 152px gap, horizontal
    - Column Order: Logo/Socials | LEARN MORE | GET IN TOUCH | QUICK LINKS
    - Link spacing: 16px vertical
    - Terms/Privacy gap: 25px horizontal
    - Copyright: centered with separator line above
    """
    # Full width styles
    if full_width:
        outer_style = "width: 100vw; margin-left: calc(-50vw + 50%); margin-right: calc(-50vw + 50%); box-sizing: border-box;"
    else:
        outer_style = ""
    
    # Bottom margin styles
    if stick_to_bottom:
        bottom_style = "margin-bottom: -100px !important; padding-bottom: 0 !important;"
    else:
        bottom_style = ""
    
    footer_html = f'''<style>
.coresight-footer-exact {{
  background-color: #f2f2f2;
  {outer_style}
  {bottom_style}
}}
.coresight-footer-container {{
  max-width: 1350px;
  margin: 0 auto;
  padding: 72px 20px 40px;
}}
/* Main content wrapper - 1249px width, horizontal layout with 152px gaps */
.coresight-footer-main {{
  display: flex;
  flex-direction: row;
  gap: 152px;
  margin-bottom: 40px;
  align-items: flex-start;
}}
/* Column 1: Logo section - 247px width */
.footer-col-logo {{
  width: 247px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}}
.footer-logo-img {{
  width: 247px;
  height: 112px;
}}
/* Social icons - 36px circles with 12px gap */
.footer-socials-row {{
  display: flex;
  flex-direction: row;
  gap: 12px;
}}
.footer-social-icon {{
  width: 36px;
  height: 36px;
  background-color: #d62e2f;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.footer-social-icon svg {{
  width: 17px;
  height: 17px;
  fill: #ffffff;
}}
/* Legal links - 25px gap */
.footer-legal-row {{
  display: flex;
  flex-direction: row;
  gap: 25px;
}}
.footer-legal-row a {{
  font-family: 'Roboto', sans-serif;
  font-size: 16px;
  color: #333333;
  text-decoration: none;
}}
.footer-legal-row a:hover {{
  color: #d62e2f;
}}
/* Columns 2-4: Navigation columns */
.footer-col-nav {{
  display: flex;
  flex-direction: column;
  gap: 0;
}}
/* Headers - Montserrat 25px, uppercase */
.footer-nav-header {{
  font-family: 'Montserrat', sans-serif;
  font-size: 25px;
  font-weight: 600;
  color: #333333;
  text-transform: uppercase;
  margin: 0 0 30px 0;
  line-height: 1.2;
}}
/* Links - vertical layout with 16px gap */
.footer-nav-links {{
  display: flex;
  flex-direction: column;
  gap: 16px;
}}
.footer-nav-links a {{
  font-family: 'Roboto', sans-serif;
  font-size: 16px;
  color: #333333;
  text-decoration: none;
  line-height: 22px;
}}
.footer-nav-links a:hover {{
  color: #d62e2f;
}}
/* Separator line */
.footer-separator-line {{
  width: 100%;
  height: 1px;
  background-color: #cbcaca;
  margin: 0 0 20px 0;
}}
/* Copyright - centered */
.footer-copyright-centered {{
  text-align: center;
  padding: 0;
}}
.footer-copyright-centered p {{
  font-family: 'Montserrat', sans-serif;
  font-size: 14px;
  color: #454545;
  margin: 0;
}}
/* Responsive */
@media (max-width: 1200px) {{
  .coresight-footer-main {{
    gap: 60px;
  }}
}}
@media (max-width: 900px) {{
  .coresight-footer-main {{
    flex-wrap: wrap;
    gap: 40px;
  }}
  .footer-col-logo {{
    width: 100%;
  }}
}}
@media (max-width: 640px) {{
  .coresight-footer-main {{
    flex-direction: column;
    gap: 30px;
  }}
  .footer-nav-header {{
    font-size: 20px;
  }}
}}
.main .block-container {{
  padding-bottom: 0 !important;
}}
</style>

<div class="coresight-footer-exact">
  <div class="coresight-footer-container">
    <!-- Main Footer Content - 4 Columns -->
    <div class="coresight-footer-main">
      
      <!-- Column 1: Logo & Socials -->
      <div class="footer-col-logo">
        <img src="https://production-wordpress-cdn-dpa0g9bzd7b3h7gy.z03.azurefd.net/wp-content/uploads/2023/12/coresight-logo.png" 
             alt="Coresight Research" class="footer-logo-img" width="247" height="112">
        
        <div class="footer-socials-row">
          <a href="https://www.facebook.com/coresightresearch" target="_blank" class="footer-social-icon" aria-label="Facebook">
            <svg viewBox="0 0 320 512" xmlns="http://www.w3.org/2000/svg"><path d="M279.14 288l14.22-92.66h-88.91v-60.13c0-25.35 12.42-50.06 52.24-50.06h40.42V6.26S260.43 0 225.36 0c-73.22 0-121.08 44.38-121.08 124.72v70.62H22.89V288h81.39v224h100.17V288z"/></svg>
          </a>
          <a href="https://twitter.com/coresightnews" target="_blank" class="footer-social-icon" aria-label="Twitter">
            <svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg"><path d="M459.37 151.716c.325 4.548.325 9.097.325 13.645 0 138.72-105.583 298.558-298.558 298.558-59.452 0-114.68-17.219-161.137-47.106 8.447.974 16.568 1.299 25.34 1.299 49.055 0 94.213-16.568 130.274-44.832-46.132-.975-84.792-31.188-98.112-72.772 6.498.974 12.995 1.624 19.818 1.624 9.421 0 18.843-1.3 27.614-3.573-48.081-9.747-84.143-51.98-84.143-102.985v-1.299c13.969 7.797 30.214 12.67 47.431 13.319-28.264-18.843-46.781-51.005-46.781-87.391 0-19.492 5.197-37.36 14.294-52.954 51.655 63.675 129.3 105.258 216.365 109.807-1.624-7.797-2.599-15.918-2.599-24.04 0-57.828 46.782-104.934 104.934-104.934 30.213 0 57.502 12.67 76.67 33.137 23.715-4.548 46.456-13.32 66.599-25.34-7.798 24.366-24.366 44.833-46.132 57.827 21.117-2.273 41.584-8.122 60.426-16.243-14.292 20.791-32.161 39.308-52.628 54.253z"/></svg>
          </a>
          <a href="#" target="_blank" class="footer-social-icon" aria-label="WeChat">
            <svg viewBox="0 0 576 512" xmlns="http://www.w3.org/2000/svg"><path d="M385.2 167.6c6.4 0 12.6.3 18.8 1.1C387.4 90.3 303.3 32 207.7 32 100.5 32 13 104.8 13 197.4c0 53.4 29.3 97.5 77.9 131.6l-19.3 58.6 68-34.1c24.4 4.8 43.8 9.7 68.2 9.7 6.2 0 12.1-.3 18.3-.8-4-12.9-6.2-26.6-6.2-40.8-.1-84.9 72.9-154 165.3-154zm-104.5-52.9c14.5 0 24.2 9.7 24.2 24.4 0 14.5-9.7 24.2-24.2 24.2-14.8 0-29.3-9.7-29.3-24.2.1-14.7 14.6-24.4 29.3-24.4zm-136.4 48.6c-14.5 0-29.3-9.7-29.3-24.2 0-14.8 14.8-24.4 29.3-24.4 14.8 0 24.4 9.7 24.4 24.4 0 14.6-9.6 24.2-24.4 24.2zM563 319.4c0-77.9-77.9-141.3-165.4-141.3-92.7 0-165.4 63.4-165.4 141.3S305 460.7 397.6 460.7c19.3 0 38.9-5.1 58.6-9.9l53.4 29.3-14.8-48.6C534 402.1 563 363.2 563 319.4zm-219.1-24.5c-9.7 0-19.3-9.7-19.3-19.6 0-9.7 9.7-19.3 19.3-19.3 14.8 0 24.4 9.7 24.4 19.3 0 10-9.7 19.6-24.4 19.6zm107.1 0c-9.7 0-19.3-9.7-19.3-19.6 0-9.7 9.7-19.3 19.3-19.3 14.5 0 24.4 9.7 24.4 19.3.1 10-9.9 19.6-24.4 19.6z"/></svg>
          </a>
          <a href="https://www.linkedin.com/company/coresight-research/" target="_blank" class="footer-social-icon" aria-label="LinkedIn">
            <svg viewBox="0 0 448 512" xmlns="http://www.w3.org/2000/svg"><path d="M100.28 448H7.4V148.9h92.88zM53.79 108.1C24.09 108.1 0 83.5 0 53.8a53.79 53.79 0 0 1 107.58 0c0 29.7-24.1 54.3-53.79 54.3zM447.9 448h-92.68V302.4c0-34.7-.7-79.2-48.29-79.2-48.29 0-55.69 37.7-55.69 76.7V448h-92.78V148.9h89.08v40.8h1.3c12.4-23.5 42.69-48.3 87.88-48.3 94 0 111.28 61.9 111.28 142.3V448z"/></svg>
          </a>
        </div>
        
        <div class="footer-legal-row">
          <a href="https://coresight.com/terms-of-service/" target="_blank">Terms of Use</a>
          <a href="https://coresight.com/privacy-policy/" target="_blank">Privacy Policy</a>
        </div>
      </div>
      
      <!-- Column 2: LEARN MORE -->
      <div class="footer-col-nav">
        <h3 class="footer-nav-header">Learn<br>More</h3>
        <div class="footer-nav-links">
          <a href="https://coresight.com/subscriptions/" target="_blank">Research Subscriptions</a>
          <a href="https://coresight.com/events/" target="_blank">Our Events</a>
          <a href="https://coresight.com/about-us/" target="_blank">About Us</a>
        </div>
      </div>
      
      <!-- Column 3: GET IN TOUCH -->
      <div class="footer-col-nav">
        <h3 class="footer-nav-header">Get In<br>Touch</h3>
        <div class="footer-nav-links">
          <a href="https://coresight.com/become-a-client/" target="_blank">Become a Client</a>
          <a href="https://coresight.com/about/contact/" target="_blank">Contact Us</a>
        </div>
      </div>
      
      <!-- Column 4: QUICK LINKS -->
      <div class="footer-col-nav">
        <h3 class="footer-nav-header">Quick<br>Links</h3>
        <div class="footer-nav-links">
          <a href="https://coresight.com/research/" target="_blank">Research Portal</a>
          <a href="https://coresight.com/retailistic-podcast/" target="_blank">The Retaili$tic Podcast</a>
          <a href="https://coresight.com/coresight-ai-council/" target="_blank">AI Council</a>
        </div>
      </div>
      
    </div>
    
    <!-- Separator Line -->
    <div class="footer-separator-line"></div>
    
    <!-- Copyright - Centered -->
    <div class="footer-copyright-centered">
      <p>2025 Coresight Research. All rights reserved.</p>
    </div>
  </div>
</div>'''
    
    # Use st.html for raw HTML rendering (Streamlit 1.54+)
    try:
        st.html(footer_html)
    except AttributeError:
        # Fallback for older Streamlit versions
        st.markdown(footer_html, unsafe_allow_html=True)


def render_company_header(company_name: str, ticker: str, exchange: str = "NYSE"):
    """
    Render reusable company header section with dropdown - matches Figma exactly.
    
    This is a centralized component that can be used on any page that needs
    the company header with:
    - "CORESIGHT MARKET DATA" red title
    - Company name with dropdown
    - Company Documents button
    
    Parameters:
    -----------
    company_name : str
        The company display name (e.g., "Macy's Inc")
    ticker : str
        The stock ticker symbol (e.g., "M")
    exchange : str, optional
        The stock exchange (default: "NYSE")
    
    Usage:
    ------
    from components.navigation import render_company_header
    from data.repository import CompanyRepository
    
    # Get company data
    companies = CompanyRepository.get_companies()
    
    # Render header
    render_company_header(
        company_name=company.name,
        ticker=company.ticker,
        exchange=company.exchange or "NYSE"
    )
    """
    from data.repository import CompanyRepository
    
    # CSS for the company header component
    header_css = """
    <style>
    /* Company Header Section - reusable component */
    .company-header-section {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 24px;
        padding: 24px 0;
    }
    
    .company-header-left {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .section-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 20px;
        color: #d62e2f;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin: 0;
        padding: 0;
    }
    
    .company-name-dropdown {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 20px;
        color: #2d2a29;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .dropdown-arrow {
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .dropdown-arrow svg {
        width: 16px;
        height: 16px;
        stroke: #2d2a29;
    }
    
    .company-documents-btn {
        background-color: #d62e2f;
        color: #ffffff !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 14px;
        padding: 10px 26px;
        border-radius: 4px;
        border: none;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        transition: background-color 0.2s ease;
        text-decoration: none !important;
    }
    .company-documents-btn .text {
      display: flex;
      flex-direction: column;
      line-height: 1.1;    /* tighter two-line look */
    }

    .company-documents-btn .text span {
      margin: 0;
    }
    
    .company-documents-btn:hover {
        background-color: #b52627;
    }
    
    .company-documents-btn svg {
        width: 20px;
        height: 20px;
    }
    
    /* Streamlit Selectbox Styling - positioned over the company name */
    div[data-testid="stSelectbox"]:has(> div > div > input[aria-label*="Select Company"]) {
        margin-top: -40px !important;
        margin-bottom: 20px !important;
        width: 400px !important;
        opacity: 0;
    }
    
    div[data-testid="stSelectbox"]:has(> div > div > input[aria-label*="Select Company"]) > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stSelectbox"]:has(> div > div > input[aria-label*="Select Company"]) label {
        display: none !important;
    }
    
    div[data-testid="stSelectbox"]:has(> div > div > input[aria-label*="Select Company"]) > div > div {
        height: 30px;
        cursor: pointer;
    }
    </style>
    """
    
    # HTML for the header display (company name + button)
    header_html = f'''
    {header_css}
    <div class="company-header-section">
        <div class="company-header-left">
            <div class="section-title">CORESIGHT MARKET DATA</div>
            <div class="company-name-dropdown">
                <span>{company_name} ({exchange}:{ticker})</span>
                <span class="dropdown-arrow">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </span>
            </div>
        </div>
        <a href="/company_filings?ticker={ticker}" target="_self" class="company-documents-btn">
            <span class="text">
              <span>Company</span>
              <span>Documents</span>
            </span>
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M7 1H3C2.46957 1 1.96086 1.21071 1.58579 1.58579C1.21071 1.96086 1 2.46957 1 3V15C1 15.5304 1.21071 16.0391 1.58579 16.4142C1.96086 16.7893 2.46957 17 3 17H15C15.5304 17 16.0391 16.7893 16.4142 16.4142C16.7893 16.0391 17 15.5304 17 15V11M9 9L17 1M17 1V6M17 1H12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </a>
    </div>
    '''
    
    # Render the HTML header
    st.markdown(header_html, unsafe_allow_html=True)
    
    # Get all companies for the dropdown
    companies = CompanyRepository.get_companies()
    company_options = {f"{c['name']} ({c['ticker']})": c['ticker'].strip() for c in companies}
    current_display = f"{company_name} ({ticker})"
    
    # Find current index
    option_list = list(company_options.keys())
    current_index = option_list.index(current_display) if current_display in option_list else 0
    
    # Hidden Streamlit selectbox for functionality
    # Use a callback to handle selection change
    def on_company_change():
        selected = st.session_state.company_selector_header
        selected_ticker = company_options[selected]
        # Update URL with new ticker - this automatically triggers a rerun
        st.query_params["ticker"] = selected_ticker
        # Also update active_ticker so the cross-page sync logic doesn't
        # override the new selection with the stale old ticker
        st.session_state.active_ticker = selected_ticker
    
    # The selectbox is positioned via CSS to align with the header
    st.selectbox(
        "Select Company",
        options=option_list,
        index=current_index,
        key="company_selector_header",
        on_change=on_company_change,
        label_visibility="collapsed"
    )


class Page(Enum):
    """Application pages."""
    MARKET_DATA = "market_data"
    NEWSROOM = "newsroom"


PAGE_CONFIG = {
    Page.MARKET_DATA: {
        "label": "Market Data",
        "icon": "📈",
        "description": "Real-time market data and analytics"
    },
    Page.NEWSROOM: {
        "label": "Newsroom",
        "icon": "📰",
        "description": "Latest news and market updates"
    },
}


def render_logo():
    """Render application logo."""
    st.markdown(f"""
    <div style="
        padding: {SPACING['space_6']} {SPACING['space_4']};
        margin-bottom: {SPACING['space_4']};
        border-bottom: 1px solid {COLORS['gray_200']};
    ">
        <div style="
            font-size: {TYPOGRAPHY['text_xl']};
            font-weight: {TYPOGRAPHY['font_bold']};
            color: {COLORS['primary']};
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="font-size: 1.5rem;">📊</span>
            <span>Research Portal</span>
        </div>
        <div style="
            font-size: {TYPOGRAPHY['text_sm']};
            color: {COLORS['gray_500']};
            margin-top: 4px;
        ">Market Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)



def render_user_state():
    """Render current user selections from local storage."""
    st.markdown(f"""
    <div style="
        font-size: {TYPOGRAPHY['text_xs']};
        font-weight: {TYPOGRAPHY['font_semibold']};
        color: {COLORS['gray_500']};
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 0 {SPACING['space_4']};
        margin-bottom: {SPACING['space_3']};
    ">Current Selection</div>
    """, unsafe_allow_html=True)
    
    # Get values from session state (synced from local storage)
    ticker = st.session_state.get("sec_filing", "-")
    start_date = st.session_state.get("start_date", "-")
    end_date = st.session_state.get("end_date", "-")
    
    st.markdown(f"""
    <div style="
        background: {COLORS['gray_100']};
        border-radius: {BORDER_RADIUS['rounded_lg']};
        padding: {SPACING['space_4']};
        margin: 0 {SPACING['space_2']};
    ">
        <div style="margin-bottom: {SPACING['space_3']};">
            <div style="
                font-size: {TYPOGRAPHY['text_xs']};
                color: {COLORS['gray_500']};
                margin-bottom: 2px;
            ">Ticker/Filing</div>
            <div style="
                font-size: {TYPOGRAPHY['text_sm']};
                font-weight: {TYPOGRAPHY['font_semibold']};
                color: {COLORS['gray_900']};
            ">{ticker}</div>
        </div>
        <div>
            <div style="
                font-size: {TYPOGRAPHY['text_xs']};
                color: {COLORS['gray_500']};
                margin-bottom: 2px;
            ">Date Range</div>
            <div style="
                font-size: {TYPOGRAPHY['text_sm']};
                color: {COLORS['gray_700']};
            ">{start_date} to {end_date}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_divider():
    """Render a divider line."""
    st.markdown(f"""
    <div style="
        height: 1px;
        background: {COLORS['gray_200']};
        margin: {SPACING['space_6']} {SPACING['space_4']};
    "></div>
    """, unsafe_allow_html=True)


def render_footer():
    """Render sidebar footer."""
    st.markdown(f"""
    <div style="
        padding: 0 {SPACING['space_4']};
        text-align: center;
    ">
        <div style="
            font-size: {TYPOGRAPHY['text_xs']};
            color: {COLORS['gray_500']};
            margin-bottom: 4px;
        ">Research Portal v1.0</div>
        <div style="
            font-size: {TYPOGRAPHY['text_xs']};
            color: {COLORS['gray_400']};
        ">© 2024 Market Intelligence</div>
    </div>
    """, unsafe_allow_html=True)


def render_top_bar():
    """Render top navigation bar with actions."""
    col1, col2, col3 = st.columns([6, 2, 2])
    
    with col2:
        st.button("🔔 Notifications", use_container_width=True)
    
    with col3:
        st.button("👤 Profile", use_container_width=True)


def get_page_title(page: Page) -> str:
    """Get the title for a page."""
    config = PAGE_CONFIG[page]
    return f"{config['icon']} {config['label']}"
