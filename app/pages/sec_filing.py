"""
SEC Filing Documents Page - Coresight Research
==============================================
Company filing documents page with document list and viewer.
Matches Figma design exactly.
"""
import streamlit as st
from typing import Optional, List, Dict
from datetime import datetime

# MUST be first Streamlit command
st.set_page_config(
    page_title="Company Filing Documents - Coresight Research",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Hide sidebar immediately
from components.styles import hide_sidebar, set_page_layout
hide_sidebar()

from components.styles import render_styles, COLORS, TYPOGRAPHY, SPACING
from components.navigation import render_header, render_coresight_footer, render_company_header
from data.repository import CompanyRepository
from core.database import init_database


# Mock data for filing documents
MOCK_FILINGS = [
    {
        "id": 1,
        "title": "10-K Annual Report",
        "date": "2025-01-15",
        "type": "10-K",
        "status": "Available",
        "url": "#"
    },
    {
        "id": 2,
        "title": "10-Q Quarterly Report",
        "date": "2024-11-30",
        "type": "10-Q",
        "status": "Available",
        "url": "#"
    },
    {
        "id": 3,
        "title": "8-K Current Report",
        "date": "2024-10-12",
        "type": "8-K",
        "status": "Processing",
        "url": "#"
    },
    {
        "id": 4,
        "title": "DEF 14A Proxy Statement",
        "date": "2024-04-20",
        "type": "DEF 14A",
        "status": "Available",
        "url": "#"
    },
    {
        "id": 5,
        "title": "10-Q Quarterly Report",
        "date": "2024-08-30",
        "type": "10-Q",
        "status": "Available",
        "url": "#"
    },
]

MOCK_DOCUMENT_CONTENT = """
UNITED STATES
SECURITIES AND EXCHANGE COMMISSION
WASHINGTON, D.C. 20549

FORM 10-K

☒ ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934

For the fiscal year ended January 31, 2025

OR

☐ TRANSITION REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934

For the transition period from __________ to __________

Commission File Number: 1-13536

MACY'S, INC.
(Exact name of registrant as specified in its charter)

Delaware                                                        13-3324058
(State or other jurisdiction of incorporation or organization)  (I.R.S. Employer Identification No.)

7 West Seventh Street, Cincinnati, Ohio                          45202
(Address of principal executive offices)                         (Zip Code)

Registrant's telephone number, including area code: (513) 579-7000

Securities registered pursuant to Section 12(b) of the Act:

Title of each class              Trading Symbol(s)   Name of each exchange on which registered
Common Stock, par value $0.01    M                   New York Stock Exchange

Securities registered pursuant to Section 12(g) of the Act: None

Indicate by check mark if the registrant is a well-known seasoned issuer, as defined in Rule 405 of the Securities Act. Yes ☒ No ☐

Indicate by check mark if the registrant is not required to file reports pursuant to Section 13 or Section 15(d) of the Act. Yes ☐ No ☒

Indicate by check mark whether the registrant (1) has filed all reports required to be filed by Section 13 or 15(d) of the Securities Exchange Act 
of 1934 during the preceding 12 months (or for such shorter period that the registrant was required to file such reports), and (2) has been 
subject to such filing requirements for the past 90 days. Yes ☒ No ☐

Indicate by check mark whether the registrant has submitted electronically every Interactive Data File required to be submitted pursuant to 
Rule 405 of Regulation S-T during the preceding 12 months (or for such shorter period that the registrant was required to submit such files). 
Yes ☒ No ☐

Indicate by check mark whether the registrant is a large accelerated filer, an accelerated filer, a non-accelerated filer, a smaller reporting 
company, or an emerging growth company. See the definitions of "large accelerated filer," "accelerated filer," "smaller reporting company," 
and "emerging growth company" in Rule 12b-2 of the Exchange Act.

Large accelerated filer ☒    Accelerated filer ☐    Non-accelerated filer ☐    Smaller reporting company ☐    Emerging growth company ☐

If an emerging growth company, indicate by check mark if the registrant has elected not to use the extended transition period for complying 
with any new or revised financial accounting standards provided pursuant to Section 13(a) of the Exchange Act. ☐

Indicate by check mark whether the registrant has filed a report on and attestation to its management's assessment of the effectiveness of 
its internal control over financial reporting under Section 404(b) of the Sarbanes-Oxley Act (15 U.S.C. 7262(b)) by the registered public 
accounting firm that prepared or issued its audit report. ☒

If securities are registered pursuant to Section 12(b) of the Act, indicate by check mark whether the financial statements of the registrant 
included in the filing reflect the correction of an error to previously issued financial statements. ☐

Indicate by check mark whether any of those error corrections are restatements that required a recovery analysis of incentive-based 
compensation received by any of the registrant's executive officers during the relevant recovery period pursuant to §240.10D-1(b). ☐

Indicate by check mark whether the registrant is a shell company (as defined in Rule 12b-2 of the Act). Yes ☐ No ☒

The aggregate market value of the voting and non-voting common equity held by non-affiliates of the registrant as of July 31, 2024 
(the last business day of the registrant's most recently completed second fiscal quarter): $4.3 billion.

The number of shares outstanding of the registrant's common stock as of March 14, 2025: 275,000,000 shares.

DOCUMENTS INCORPORATED BY REFERENCE

Portions of the registrant's definitive proxy statement for the 2025 Annual Meeting of Shareholders are incorporated by reference 
into Part III of this Form 10-K.
"""


def get_sec_filing_css() -> str:
    """Get custom CSS for SEC filing page - matches Figma exactly."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&family=Montserrat:wght@400;500;600;700&display=swap');
    
    /* Page Container */
    .sec-filing-container {
        max-width: 1350px;
        margin: 0 auto;
        padding: 24px 0;
        font-family: 'Roboto', sans-serif;
    }
    
    /* Page Title */
    .sec-filing-page-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 20px;
        color: #2d2a29;
        margin: 0 0 24px 0;
        padding: 0;
    }
    
    /* Main Layout - Two Column */
    .sec-filing-layout {
        display: flex;
        gap: 24px;
        min-height: 600px;
    }
    
    /* Left Sidebar - Document List */
    .document-sidebar {
        width: 380px;
        flex-shrink: 0;
        border: 1px solid #CBCACA;
        border-radius: 8px;
        overflow: hidden;
        background: #FFFFFF;
    }
    
    .sidebar-header {
        padding: 16px 20px;
        background: #F2F2F2;
        border-bottom: 1px solid #CBCACA;
    }
    
    .sidebar-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 16px;
        color: #2d2a29;
        margin: 0 0 12px 0;
    }
    
    .sidebar-subtitle {
        font-family: 'Roboto', sans-serif;
        font-weight: 400;
        font-size: 12px;
        color: #666666;
        margin: 0;
    }
    
    /* Search Box */
    .search-container {
        padding: 12px 20px;
        border-bottom: 1px solid #CBCACA;
    }
    
    .search-box {
        width: 100%;
        padding: 10px 14px;
        border: 1px solid #CBCACA;
        border-radius: 6px;
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        color: #333333;
        background: #FFFFFF;
    }
    
    .search-box::placeholder {
        color: #999999;
    }
    
    /* Document List */
    .document-list {
        max-height: 500px;
        overflow-y: auto;
    }
    
    .document-item {
        padding: 16px 20px;
        border-bottom: 1px solid #E5E5E5;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }
    
    .document-item:hover {
        background-color: #F8F8F8;
    }
    
    .document-item.active {
        background-color: #FFF5F5;
        border-left: 3px solid #d62e2f;
    }
    
    .document-item-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 6px;
    }
    
    .document-title {
        font-family: 'Roboto', sans-serif;
        font-weight: 600;
        font-size: 14px;
        color: #2d2a29;
        margin: 0;
    }
    
    .document-date {
        font-family: 'Roboto', sans-serif;
        font-weight: 400;
        font-size: 12px;
        color: #888888;
        white-space: nowrap;
    }
    
    .document-type {
        display: inline-block;
        padding: 2px 8px;
        background: #F2F2F2;
        border-radius: 4px;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        font-size: 11px;
        color: #666666;
        margin-right: 8px;
    }
    
    .document-status {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        font-size: 11px;
    }
    
    .status-available {
        background: #E8F5E9;
        color: #2E7D32;
    }
    
    .status-processing {
        background: #FFF3E0;
        color: #EF6C00;
    }
    
    /* Right Content - Document Viewer */
    .document-viewer {
        flex: 1;
        border: 1px solid #CBCACA;
        border-radius: 8px;
        overflow: hidden;
        background: #FFFFFF;
        display: flex;
        flex-direction: column;
    }
    
    .viewer-header {
        padding: 16px 24px;
        background: #F2F2F2;
        border-bottom: 1px solid #CBCACA;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .viewer-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 16px;
        color: #2d2a29;
        margin: 0;
    }
    
    .download-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: #d62e2f;
        color: #FFFFFF;
        border: none;
        border-radius: 4px;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        font-size: 13px;
        cursor: pointer;
        text-decoration: none;
        transition: background-color 0.2s ease;
    }
    
    .download-btn:hover {
        background: #b52627;
    }
    
    .viewer-content {
        flex: 1;
        padding: 32px 40px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.6;
        color: #333333;
        white-space: pre-wrap;
        background: #FFFFFF;
    }
    
    /* Empty State */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 80px 40px;
        text-align: center;
    }
    
    .empty-state-icon {
        font-size: 48px;
        margin-bottom: 16px;
    }
    
    .empty-state-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 18px;
        color: #2d2a29;
        margin: 0 0 8px 0;
    }
    
    .empty-state-text {
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        color: #666666;
        margin: 0;
    }
    
    /* Tab Navigation */
    .tab-navigation {
        display: flex;
        border-bottom: 1px solid #CBCACA;
        margin-bottom: 24px;
        gap: 48px;
    }
    
    .tab-item {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 16px;
        padding: 12px 0;
        cursor: pointer;
        color: #666666;
        border-bottom: 3px solid transparent;
        margin-bottom: -2px;
        transition: all 0.2s ease;
    }
    
    .tab-item:hover {
        color: #d62e2f;
    }
    
    .tab-item.active {
        color: #d62e2f;
        border-bottom-color: #d62e2f;
    }
    </style>
    """


def render_document_list(documents: List[Dict], selected_id: Optional[int]) -> str:
    """Render the document list sidebar."""
    html = '<div class="document-sidebar">'
    
    # Header
    html += '''
    <div class="sidebar-header">
        <div class="sidebar-title">Company Filing Documents</div>
        <div class="sidebar-subtitle">Macy's Inc. (NYSE: M) • 2025 - 01</div>
    </div>
    '''
    
    # Search
    html += '''
    <div class="search-container">
        <input type="text" class="search-box" placeholder="Search documents...">
    </div>
    '''
    
    # Document list
    html += '<div class="document-list">'
    for doc in documents:
        active_class = "active" if doc["id"] == selected_id else ""
        status_class = "status-available" if doc["status"] == "Available" else "status-processing"
        
        html += f'''
        <div class="document-item {active_class}" data-id="{doc['id']}">
            <div class="document-item-header">
                <div class="document-title">{doc['title']}</div>
                <div class="document-date">{doc['date']}</div>
            </div>
            <div>
                <span class="document-type">{doc['type']}</span>
                <span class="document-status {status_class}">{doc['status']}</span>
            </div>
        </div>
        '''
    html += '</div>'
    
    html += '</div>'
    return html


def render_document_viewer(document: Optional[Dict], content: str) -> str:
    """Render the document viewer."""
    html = '<div class="document-viewer">'
    
    if document:
        html += f'''
        <div class="viewer-header">
            <div class="viewer-title">{document['title']}</div>
            <a href="{document['url']}" class="download-btn" download>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 15V3M12 15L8 11M12 15L16 11M3 15V19C3 20.1046 3.89543 21 5 21H19C20.1046 21 21 20.1046 21 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Download PDF
            </a>
        </div>
        <div class="viewer-content">{content}</div>
        '''
    else:
        html += '''
        <div class="empty-state">
            <div class="empty-state-icon">📄</div>
            <div class="empty-state-title">No document selected</div>
            <div class="empty-state-text">Select a document from the list to view its contents</div>
        </div>
        '''
    
    html += '</div>'
    return html


def render_tabs(active_tab: str = "documents") -> str:
    """Render the tab navigation - matches Figma exactly."""
    tabs = [
        ("profile", "Company Profile"),
        ("stats", "Key Stats"),
        ("income", "Income Statement"),
        ("documents", "Documents")
    ]
    
    html = '<div class="tab-navigation">'
    for tab_id, tab_label in tabs:
        active_class = "active" if tab_id == active_tab else ""
        html += f'<div class="tab-item {active_class}">{tab_label}</div>'
    html += '</div>'
    
    return html


def main():
    """SEC Filing page entry point."""
    # Initialize
    init_database()
    
    # Render global styles
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
    
    # Render Header
    render_header(full_width=True)
    
    # Inject custom CSS
    st.markdown(get_sec_filing_css(), unsafe_allow_html=True)
    
    # Page content container
    st.markdown('<div class="sec-filing-container">', unsafe_allow_html=True)
    
    # Page title
    st.markdown('<h1 class="sec-filing-page-title">Company Filing Documents</h1>', unsafe_allow_html=True)
    
    # Tab navigation
    st.markdown(render_tabs(active_tab="documents"), unsafe_allow_html=True)
    
    # Get selected document from session state
    if 'selected_document_id' not in st.session_state:
        st.session_state.selected_document_id = 1
    
    # Find selected document
    selected_doc = next(
        (d for d in MOCK_FILINGS if d["id"] == st.session_state.selected_document_id),
        None
    )
    
    # Main layout - sidebar and viewer
    st.markdown('<div class="sec-filing-layout">', unsafe_allow_html=True)
    
    # Document list sidebar
    st.markdown(render_document_list(MOCK_FILINGS, st.session_state.selected_document_id), unsafe_allow_html=True)
    
    # Document viewer
    st.markdown(render_document_viewer(selected_doc, MOCK_DOCUMENT_CONTENT), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close layout
    
    # Close container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Render Footer
    render_coresight_footer(full_width=True, stick_to_bottom=True)


if __name__ == "__main__":
    main()
