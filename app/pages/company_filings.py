"""
Company Filing Documents Page - Coresight Research
==================================================
SEC filing documents viewer with metric search and document display.
Matches Figma design with Streamlit native components + custom styling.
"""
import streamlit as st
from typing import List, Dict, Optional
from dataclasses import dataclass

from components.styles import hide_sidebar, set_page_layout
hide_sidebar()

from components.styles import render_styles
from components.navigation import render_header, render_coresight_footer


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class FilingMetric:
    """A financial metric from a filing."""
    name: str
    value: str
    category: str  # Income Statement, Balance Sheet, etc.
    document_type: str  # 10-K, 10-Q, etc.
    year: str
    is_viewing: bool = False


@dataclass
class FilingDocument:
    """A SEC filing document."""
    company_name: str
    ticker: str
    document_type: str
    year: str
    quarter: str
    content: str  # Would be actual PDF/binary content


# =============================================================================
# MOCK DATA (Replace with database calls)
# =============================================================================

COMPANIES = [
    ("M", "Macy's Inc."),
    ("ANF", "Abercrombie & Fitch Co."),
    ("JWN", "Nordstrom Inc."),
    ("KSS", "Kohl's Corporation"),
    ("DDS", "Dillard's Inc."),
]

DOCUMENT_TYPES = ["10-K", "10-Q", "8-K", "DEF 14A", "S-1"]

FILING_METRICS = [
    FilingMetric("Revenue", "$416.16B", "Income Statement", "10-K", "2025"),
    FilingMetric("Cost of Goods Sold", "$20.16B", "Income Statement", "10-K", "2025", is_viewing=True),
    FilingMetric("Gross Profit", "$396.00B", "Income Statement", "10-K", "2025"),
    FilingMetric("Operating Income", "$15.4B", "Income Statement", "10-K", "2025"),
    FilingMetric("Net Income", "$12.8B", "Income Statement", "10-K", "2025"),
    FilingMetric("Total Assets", "$520.5B", "Balance Sheet", "10-K", "2025"),
    FilingMetric("Total Liabilities", "$320.2B", "Balance Sheet", "10-K", "2025"),
    FilingMetric("Stockholders Equity", "$200.3B", "Balance Sheet", "10-K", "2025"),
]


# =============================================================================
# CSS STYLES
# =============================================================================

def get_filings_css() -> str:
    """Get custom CSS for filings page."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&family=Montserrat:wght@400;500;600;700&display=swap');
    
    /* =======================================================================
       PAGE CONTAINER
       ======================================================================= */
    .filings-page-container {
        max-width: 1440px;
        margin: 0 auto;
        padding: 0;
        font-family: 'Roboto', sans-serif;
        background: #FFFFFF;
    }
    
    .filings-content-wrapper {
        max-width: 1220px;
        margin: 0 auto;
        padding: 0 110px;
    }
    
    /* =======================================================================
       HEADER SECTION WITH FILTERS
       ======================================================================= */
    .filings-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 24px 0;
        border-bottom: 1px solid #E5E5E5;
        margin-bottom: 24px;
    }
    
    .filings-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 24px;
        color: #2D2A29;
        margin: 0;
    }
    
    /* Filter row styling */
    .filter-row {
        display: flex;
        gap: 16px;
        align-items: flex-end;
    }
    
    /* =======================================================================
       STREAMLIT SELECTBOX STYLING
       ======================================================================= */
    
    /* Selectbox label styling */
    div[data-testid="stSelectbox"] label {
        font-family: 'Roboto', sans-serif !important;
        font-size: 12px !important;
        font-weight: 400 !important;
        color: #6B6B6B !important;
        margin-bottom: 4px !important;
    }
    
    /* Selectbox input container */
    div[data-testid="stSelectbox"] > div[data-baseweb="select"] {
        border: 1px solid #CBCACA !important;
        border-radius: 4px !important;
        background: #FFFFFF !important;
        min-height: 36px !important;
    }
    
    /* Selectbox hover state */
    div[data-testid="stSelectbox"] > div[data-baseweb="select"]:hover {
        border-color: #0066CC !important;
    }
    
    /* Selectbox text */
    div[data-testid="stSelectbox"] > div[data-baseweb="select"] span {
        font-family: 'Roboto', sans-serif !important;
        font-size: 14px !important;
        color: #2D2A29 !important;
    }
    
    /* =======================================================================
       SEARCH METRICS SIDEBAR
       ======================================================================= */
    .search-sidebar {
        background: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 8px;
        padding: 16px;
        height: calc(100vh - 340px);
        min-height: 480px;
        overflow-y: auto;
    }
    
    .search-sidebar::-webkit-scrollbar {
        width: 6px;
    }
    
    .search-sidebar::-webkit-scrollbar-track {
        background: #F2F2F2;
        border-radius: 3px;
    }
    
    .search-sidebar::-webkit-scrollbar-thumb {
        background: #CBCACA;
        border-radius: 3px;
    }
    
    .search-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #F2F2F2;
    }
    
    .search-header svg {
        color: #D62E2F;
    }
    
    .search-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 16px;
        color: #2D2A29;
    }
    
    /* Search input styling - integrated with sidebar */
    div[data-testid="stTextInput"] {
        margin-bottom: 0 !important;
    }
    
    div[data-testid="stTextInput"] > div > div > input {
        border: 1px solid #CBCACA !important;
        border-radius: 4px !important;
        font-family: 'Roboto', sans-serif !important;
        font-size: 14px !important;
        background: #FFFFFF !important;
        height: 36px !important;
    }
    
    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: #0066CC !important;
        box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.2) !important;
    }
    
    .metrics-count {
        font-family: 'Roboto', sans-serif;
        font-size: 12px;
        color: #888888;
        margin: 4px 0 12px 4px;
    }
    
    /* =======================================================================
       METRIC CARDS
       ======================================================================= */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: #CBCACA;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .metric-card.active {
        border-color: #D62E2F;
        background: #FDF5F5;
    }
    
    .metric-info {
        flex: 1;
    }
    
    .metric-name {
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        font-size: 14px;
        color: #2D2A29;
        margin-bottom: 4px;
    }
    
    .metric-value {
        font-family: 'Roboto', sans-serif;
        font-weight: 600;
        font-size: 16px;
        color: #2D2A29;
        margin-bottom: 4px;
    }
    
    .metric-meta {
        display: flex;
        align-items: center;
        gap: 6px;
        font-family: 'Roboto', sans-serif;
        font-size: 11px;
        color: #888888;
    }
    
    .metric-meta-dot {
        width: 3px;
        height: 3px;
        background: #888888;
        border-radius: 50%;
    }
    
    .metric-action-btn {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 6px 12px;
        border-radius: 4px;
        font-family: 'Roboto', sans-serif;
        font-size: 12px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        border: none;
        background: transparent;
    }
    
    .metric-action-btn.view {
        color: #0066CC;
        background: #F0F7FF;
    }
    
    .metric-action-btn.view:hover {
        background: #E0EFFF;
    }
    
    .metric-action-btn.viewing {
        color: #D62E2F;
        background: #FDF5F5;
    }
    
    /* =======================================================================
       DOCUMENT VIEWER
       ======================================================================= */
    .document-viewer {
        background: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 8px;
        height: calc(100vh - 280px);
        min-height: 540px;
        display: flex;
        flex-direction: column;
    }
    
    .document-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        border-bottom: 1px solid #E5E5E5;
    }
    
    .document-title-section {
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
    }
    
    .document-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 16px;
        color: #2D2A29;
    }
    
    .document-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        color: #6B6B6B;
    }
    
    .document-meta-dot {
        width: 4px;
        height: 4px;
        background: #6B6B6B;
        border-radius: 50%;
    }
    
    .document-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        background: #F2F2F2;
        border-radius: 4px;
        font-family: 'Roboto', sans-serif;
        font-size: 13px;
        color: #4F4F4F;
    }
    
    .download-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 16px;
        background: #FFFFFF;
        border: 1px solid #CBCACA;
        border-radius: 4px;
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        color: #2D2A29;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        white-space: nowrap;
    }
    
    .download-btn:hover {
        background: #F9F9F9;
        border-color: #888888;
    }
    
    .document-content {
        flex: 1;
        padding: 40px;
        background: #F9F9F9;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        overflow: auto;
        border-radius: 0 0 8px 8px;
    }
    
    .document-placeholder {
        text-align: center;
        color: #888888;
    }
    
    .document-placeholder svg {
        margin-bottom: 16px;
        color: #CBCACA;
    }
    
    .document-placeholder-text {
        font-family: 'Roboto', sans-serif;
        font-size: 18px;
        color: #888888;
        margin-bottom: 8px;
    }
    
    .document-placeholder-subtext {
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        color: #888888;
    }
    
    /* =======================================================================
       RESPONSIVE ADJUSTMENTS
       ======================================================================= */
    @media (max-width: 1024px) {
        .filings-content-wrapper {
            padding: 0 24px;
        }
        
        .filings-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 16px;
        }
    }
    </style>
    """


# =============================================================================
# COMPONENT RENDERING
# =============================================================================

def render_metric_card(metric: FilingMetric, index: int) -> str:
    """Render a metric card with View/Viewing button."""
    btn_class = "viewing" if metric.is_viewing else "view"
    btn_text = "Viewing" if metric.is_viewing else "View"
    card_class = "metric-card active" if metric.is_viewing else "metric-card"
    
    # Use inline SVG without newlines to avoid escaping issues
    if metric.is_viewing:
        eye_icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>'
    else:
        eye_icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/><line x1="1" y1="1" x2="23" y2="23"/></svg>'
    
    return f'<div class="{card_class}"><div class="metric-info"><div class="metric-name">{metric.name}</div><div class="metric-value">{metric.value}</div><div class="metric-meta"><span>{metric.category}</span><span class="metric-meta-dot"></span><span>{metric.document_type}</span><span class="metric-meta-dot"></span><span>{metric.year}</span></div></div><button class="metric-action-btn {btn_class}">{eye_icon}<span>{btn_text}</span></button></div>'


def render_search_sidebar(metrics: List[FilingMetric], search_term: str, show_count: int = 8) -> str:
    """Render the search metrics sidebar."""
    # Filter metrics based on search term
    filtered_metrics = [
        m for m in metrics 
        if search_term.lower() in m.name.lower() or not search_term
    ]
    
    # Render metric cards
    metrics_html = "".join([
        render_metric_card(m, i) for i, m in enumerate(filtered_metrics[:show_count])
    ])
    
    # Inline SVG for search icon
    search_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D62E2F" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
    
    return f'<div class="search-sidebar"><div class="search-header">{search_icon}<span class="search-title">Search Metrics</span></div><div class="metrics-list">{metrics_html}</div></div>'


def render_document_viewer(document: Optional[FilingDocument]) -> str:
    """Render the document viewer area."""
    # Download icon SVG (inline)
    download_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'
    
    if not document:
        return f'<div class="document-viewer"><div class="document-content"><div class="document-placeholder"><div class="document-placeholder-text">Select a metric to view document</div><div class="document-placeholder-subtext">Choose a financial metric from the list to view details</div></div></div></div>'
    
    return f'<div class="document-viewer"><div class="document-header"><div class="document-title-section"><span class="document-title">{document.company_name} ({document.ticker}) {document.document_type}</span><span class="document-badge">{document.year}</span><span class="document-meta"><span class="document-meta-dot"></span><span>{document.quarter}</span></span></div><a href="#" class="download-btn" onclick="alert(\'Download functionality coming soon!\'); return false;">{download_icon}<span>Download</span></a></div><div class="document-content"><div class="document-placeholder"><div class="document-placeholder-text">FILING DOCUMENT</div><div class="document-placeholder-subtext">{document.company_name} {document.document_type} for {document.year} {document.quarter}</div></div></div></div>'


# =============================================================================
# MAIN PAGE
# =============================================================================

def main():
    """Company Filing Documents page entry point."""
    render_styles()

    # Initialize session state
    if 'cf_search' not in st.session_state:
        st.session_state.cf_search = ""
    if 'cf_company' not in st.session_state:
        st.session_state.cf_company = "M"
    if 'cf_doc_type' not in st.session_state:
        st.session_state.cf_doc_type = "10-K"
    if 'cf_year' not in st.session_state:
        st.session_state.cf_year = "2025"
    if 'cf_quarter' not in st.session_state:
        st.session_state.cf_quarter = "Q1"
    
    # Set layout
    set_page_layout(
        header_full_width=True,
        footer_full_width=True,
        body_padding="0",
        max_content_width="1440px",
        remove_top_padding=True,
        footer_at_bottom=True
    )
    
    # Render Header
    render_header(full_width=True, current_page="company_filings",ticker=st.query_params.get("ticker", "M"))

    # Inject custom CSS
    st.markdown(get_filings_css(), unsafe_allow_html=True)
    
    # Page container
    st.markdown('<div class="filings-page-container">', unsafe_allow_html=True)
    st.markdown('<div class="filings-content-wrapper">', unsafe_allow_html=True)
    
    # =======================================================================
    # HEADER WITH TITLE AND FILTERS
    # =======================================================================
    
    header_col1, header_col2 = st.columns([1, 2])
    
    with header_col1:
        st.markdown('<h1 class="filings-title">Company Filing Documents</h1>', unsafe_allow_html=True)
    
    with header_col2:
        # Filter row
        f1, f2, f3, f4 = st.columns([2.5, 1.2, 1.2, 1.2])
        
        with f1:
            company = st.selectbox(
                "Company",
                options=[c[0] for c in COMPANIES],
                format_func=lambda x: next((c[1] for c in COMPANIES if c[0] == x), x),
                index=[c[0] for c in COMPANIES].index(st.session_state.cf_company),
                key="cf_company_select"
            )
        
        with f2:
            doc_type = st.selectbox(
                "Document Type",
                options=DOCUMENT_TYPES,
                index=DOCUMENT_TYPES.index(st.session_state.cf_doc_type),
                key="cf_doc_type_select"
            )
        
        with f3:
            year = st.selectbox(
                "Year",
                options=["2025", "2024", "2023", "2022", "2021"],
                index=0,
                key="cf_year_select"
            )
        
        with f4:
            quarter = st.selectbox(
                "Quarter",
                options=["Q1", "Q2", "Q3", "Q4"],
                index=0,
                key="cf_quarter_select"
            )
    
    # Update session state
    st.session_state.cf_company = company
    st.session_state.cf_doc_type = doc_type
    st.session_state.cf_year = year
    st.session_state.cf_quarter = quarter
    
    # =======================================================================
    # MAIN CONTENT - TWO COLUMN LAYOUT
    # =======================================================================
    
    left_col, right_col = st.columns([0.3, 0.7])
    
    with left_col:
        # Search input at the top
        search_term = st.text_input(
            "Search",
            placeholder="eg., Revenue",
            value=st.session_state.cf_search,
            key="cf_search_input",
            label_visibility="collapsed"
        )
        st.session_state.cf_search = search_term
        
        # Show count text
        filtered_count = len([m for m in FILING_METRICS if search_term.lower() in m.name.lower() or not search_term])
        st.markdown(f'<div style="font-family: Roboto, sans-serif; font-size: 12px; color: #888888; margin: 4px 0 12px 4px;">Showing {filtered_count} metrics</div>', unsafe_allow_html=True)
        
        # Render search sidebar with metrics - includes Search Metrics header
        sidebar_html = render_search_sidebar(FILING_METRICS, search_term)
        st.markdown(sidebar_html, unsafe_allow_html=True)
    
    with right_col:
        # Create document object
        company_name = next((c[1] for c in COMPANIES if c[0] == company), company)
        document = FilingDocument(
            company_name=company_name,
            ticker=company,
            document_type=doc_type,
            year=year,
            quarter=quarter,
            content=""
        )
        
        # Render document viewer
        viewer_html = render_document_viewer(document)
        st.markdown(viewer_html, unsafe_allow_html=True)
    
    # Close containers
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Render Footer
    render_coresight_footer(full_width=True, stick_to_bottom=True)


def render_page():
    """Render company filings page (callable from main.py)."""
    # Initialize session state
    if 'cf_search' not in st.session_state:
        st.session_state.cf_search = ""
    if 'cf_company' not in st.session_state:
        st.session_state.cf_company = "M"
    if 'cf_doc_type' not in st.session_state:
        st.session_state.cf_doc_type = "10-K"
    if 'cf_year' not in st.session_state:
        st.session_state.cf_year = "2025"
    if 'cf_quarter' not in st.session_state:
        st.session_state.cf_quarter = "Q1"
    
    # Inject custom CSS
    st.markdown(get_filings_css(), unsafe_allow_html=True)
    
    # Page container
    st.markdown('<div class="filings-page-container">', unsafe_allow_html=True)
    st.markdown('<div class="filings-content-wrapper">', unsafe_allow_html=True)
    
    # =======================================================================
    # HEADER WITH TITLE AND FILTERS
    # =======================================================================
    
    header_col1, header_col2 = st.columns([1, 2])
    
    with header_col1:
        st.markdown('<h1 class="filings-title">Company Filing Documents</h1>', unsafe_allow_html=True)
    
    with header_col2:
        # Filter row
        f1, f2, f3, f4 = st.columns([2.5, 1.2, 1.2, 1.2])
        
        with f1:
            company = st.selectbox(
                "Company",
                options=[c[0] for c in COMPANIES],
                format_func=lambda x: next((c[1] for c in COMPANIES if c[0] == x), x),
                index=[c[0] for c in COMPANIES].index(st.session_state.cf_company),
                key="cf_company_select"
            )
        
        with f2:
            doc_type = st.selectbox(
                "Document Type",
                options=DOCUMENT_TYPES,
                index=DOCUMENT_TYPES.index(st.session_state.cf_doc_type),
                key="cf_doc_type_select"
            )
        
        with f3:
            year = st.selectbox(
                "Year",
                options=["2025", "2024", "2023", "2022", "2021"],
                index=0,
                key="cf_year_select"
            )
        
        with f4:
            quarter = st.selectbox(
                "Quarter",
                options=["Q1", "Q2", "Q3", "Q4"],
                index=0,
                key="cf_quarter_select"
            )
    
    # Update session state
    st.session_state.cf_company = company
    st.session_state.cf_doc_type = doc_type
    st.session_state.cf_year = year
    st.session_state.cf_quarter = quarter
    
    # =======================================================================
    # MAIN CONTENT - TWO COLUMN LAYOUT
    # =======================================================================
    
    left_col, right_col = st.columns([0.3, 0.7])
    
    with left_col:
        # Search input at the top
        search_term = st.text_input(
            "Search",
            placeholder="eg., Revenue",
            value=st.session_state.cf_search,
            key="cf_search_input",
            label_visibility="collapsed"
        )
        st.session_state.cf_search = search_term
        
        # Show count text
        filtered_count = len([m for m in FILING_METRICS if search_term.lower() in m.name.lower() or not search_term])
        st.markdown(f'<div style="font-family: Roboto, sans-serif; font-size: 12px; color: #888888; margin: 4px 0 12px 4px;">Showing {filtered_count} metrics</div>', unsafe_allow_html=True)
        
        # Render search sidebar with metrics - includes Search Metrics header
        sidebar_html = render_search_sidebar(FILING_METRICS, search_term)
        st.markdown(sidebar_html, unsafe_allow_html=True)
    
    with right_col:
        # Create document object
        company_name = next((c[1] for c in COMPANIES if c[0] == company), company)
        document = FilingDocument(
            company_name=company_name,
            ticker=company,
            document_type=doc_type,
            year=year,
            quarter=quarter,
            content=""
        )
        
        # Render document viewer
        viewer_html = render_document_viewer(document)
        st.markdown(viewer_html, unsafe_allow_html=True)
    
    # Close containers
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


main()

if __name__ == "__main__":
    pass
