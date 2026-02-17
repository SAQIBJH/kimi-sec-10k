"""
Earnings Calls Page - Coresight Research
========================================
Earnings call transcripts page using native Streamlit components with custom styling.
"""
import streamlit as st
import re
from typing import List, Optional, Tuple
from dataclasses import dataclass

from components.styles import hide_sidebar, set_page_layout
hide_sidebar()

from components.styles import render_styles, COLORS, TYPOGRAPHY, SPACING
from components.navigation import render_header, render_coresight_footer
from data.repository import EarningsCallRepository
from core.database import init_database


# =============================================================================
# CSS - Styled Streamlit Components
# =============================================================================

def get_earnings_css() -> str:
    """Get custom CSS for earnings calls page - styles native Streamlit components."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&family=Montserrat:wght@400;500;600;700&display=swap');
    
    /* =======================================================================
       PAGE CONTAINER
       ======================================================================= */
    .earnings-page-container {
        max-width: 1440px;
        margin: 0 auto;
        padding: 0;
        font-family: 'Roboto', sans-serif;
        background: #FFFFFF;
    }
    
    .earnings-content-wrapper {
        max-width: 1220px;
        margin: 0 auto;
        padding: 0 110px;
    }
    
    /* =======================================================================
       HEADER SECTION
       ======================================================================= */
    .earnings-header-section {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 32px 0 24px 0;
        border-bottom: 1px solid #E5E5E5;
        margin-bottom: 24px;
    }
    
    .earnings-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 24px;
        color: #2D2A29;
        margin: 0;
    }
    
    /* =======================================================================
       FILTER BAR - Styled Streamlit Selectboxes
       ======================================================================= */
    
    /* Style the filter row */
    .filter-bar {
        display: flex;
        align-items: flex-end;
        gap: 16px;
    }
    
    /* Target Streamlit selectboxes in the filter area */
    div[data-testid="stSelectbox"] {
        min-height: auto !important;
    }
    
    /* Style the selectbox labels (helper text) */
    div[data-testid="stSelectbox"] label {
        font-family: 'Roboto', sans-serif !important;
        font-size: 12px !important;
        font-weight: 400 !important;
        color: #6B6B6B !important;
        margin-bottom: 4px !important;
    }
    
    /* Style the selectbox input container */
    div[data-testid="stSelectbox"] > div[data-baseweb="select"] {
        border: 1px solid #CBCACA !important;
        border-radius: 4px !important;
        background: #FFFFFF !important;
        min-height: 36px !important;
    }
    
    /* Style the selectbox input value text */
    div[data-testid="stSelectbox"] > div[data-baseweb="select"] span {
        font-family: 'Roboto', sans-serif !important;
        font-size: 14px !important;
        color: #2D2A29 !important;
    }
    
    /* Hover state */
    div[data-testid="stSelectbox"] > div[data-baseweb="select"]:hover {
        border-color: #0066CC !important;
    }
    
    /* Focus state */
    div[data-testid="stSelectbox"] > div[data-baseweb="select"][aria-expanded="true"] {
        border-color: #0066CC !important;
        box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.2) !important;
    }
    
    /* Dropdown menu styling */
    div[data-baseweb="popover"] div[data-baseweb="menu"] {
        border: 1px solid #E5E5E5 !important;
        border-radius: 4px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Dropdown options */
    div[data-baseweb="popover"] div[data-baseweb="menu"] li {
        font-family: 'Roboto', sans-serif !important;
        font-size: 14px !important;
    }
    
    /* =======================================================================
       TRANSCRIPT CARD
       ======================================================================= */
    .transcript-card {
        width: 90%;
        background: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 8px;
        overflow: hidden;
        margin-top: 32px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Card Header */
    .transcript-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        border-bottom: 1px solid #E5E5E5;
        background: #FFFFFF;
    }
    
    .transcript-title-section {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .transcript-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 18px;
        color: #2D2A29;
    }
    
    .transcript-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        font-size: 14px;
        color: #6B6B6B;
    }
    
    .meta-dot {
        width: 4px;
        height: 4px;
        background: #6B6B6B;
        border-radius: 50%;
    }
    
    /* Download Button */
    .download-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 12px;
        background: transparent;
        border: 1px solid #0066CC;
        border-radius: 4px;
        cursor: pointer;
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        color: #0066CC;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    
    .download-btn:hover {
        background: #0066CC;
        color: #FFFFFF;
    }
    
    /* =======================================================================
       TRANSCRIPT BODY
       ======================================================================= */
    .transcript-body {
        max-height: 600px;
        overflow-y: auto;
        padding: 20px;
        background: #F9F9F9;
    }
    
    .transcript-content {
        padding: 20px;
        background: #FFFFFF;
        border-radius: 8px;
    }
    
    /* Speaker Section */
    .speaker-section {
        margin-bottom: 24px;
    }
    
    .speaker-section:last-child {
        margin-bottom: 0;
    }
    
    .speaker-name {
        font-family: 'Roboto', sans-serif;
        font-weight: 700;
        font-size: 16px;
        color: #D62E2F;
        margin-bottom: 8px;
    }
    
    .speaker-text {
        font-family: 'Roboto', sans-serif;
        font-weight: 400;
        font-size: 15px;
        color: #2D2A29;
        line-height: 1.7;
    }
    
    /* =======================================================================
       EMPTY STATE
       ======================================================================= */
    .empty-state {
        padding: 60px 40px;
        text-align: center;
        background: #F9F9F9;
        border-radius: 8px;
        margin-top: 32px;
    }
    
    .empty-state-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 18px;
        color: #2D2A29;
        margin-bottom: 8px;
    }
    
    .empty-state-text {
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
        color: #6B6B6B;
    }
    
    /* =======================================================================
       SCROLLBAR STYLING
       ======================================================================= */
    .transcript-body::-webkit-scrollbar {
        width: 8px;
    }
    
    .transcript-body::-webkit-scrollbar-track {
        background: #F2F2F2;
        border-radius: 4px;
    }
    
    .transcript-body::-webkit-scrollbar-thumb {
        background: #CBCACA;
        border-radius: 4px;
    }
    
    .transcript-body::-webkit-scrollbar-thumb:hover {
        background: #999999;
    }
    
    /* =======================================================================
       RESPONSIVE ADJUSTMENTS
       ======================================================================= */
    @media (max-width: 1024px) {
        .earnings-content-wrapper {
            padding: 0 24px;
        }
        
        .earnings-header-section {
            flex-direction: column;
            align-items: flex-start;
            gap: 16px;
        }
    }
    </style>
    """


# =============================================================================
# TRANSCRIPT PARSING
# =============================================================================

@dataclass
class SpeakerSegment:
    """A segment of transcript from a single speaker."""
    speaker: str
    text: str


def parse_transcript(transcript_text: str) -> List[SpeakerSegment]:
    """
    Parse transcript text into speaker segments.
    
    Detects speakers by pattern: "Name:" at the beginning of a paragraph.
    """
    if not transcript_text:
        return []
    
    # Split into paragraphs
    paragraphs = re.split(r'\n\s*\n', transcript_text.strip())
    
    segments = []
    current_speaker = None
    current_text = []
    
    # Pattern to detect speaker names (Name: or Name Title:)
    speaker_pattern = re.compile(r'^([A-Z][a-zA-Z\s\.]+(?:\s+[A-Z][a-zA-Z]+)*):\s*(.*)$')
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # Check if this paragraph starts with a speaker name
        match = speaker_pattern.match(para)
        
        if match:
            # Save previous segment if exists
            if current_speaker and current_text:
                segments.append(SpeakerSegment(
                    speaker=current_speaker,
                    text=' '.join(current_text)
                ))
            
            # Start new segment
            current_speaker = match.group(1).strip()
            current_text = [match.group(2).strip()] if match.group(2) else []
        else:
            # Continue current segment
            current_text.append(para)
    
    # Save last segment
    if current_speaker and current_text:
        segments.append(SpeakerSegment(
            speaker=current_speaker,
            text=' '.join(current_text)
        ))
    
    # If no speakers detected, treat entire text as one segment
    if not segments and transcript_text.strip():
        segments.append(SpeakerSegment(
            speaker="Transcript",
            text=transcript_text.strip()
        ))
    
    return segments


def render_speaker_section(segment: SpeakerSegment) -> str:
    """Render a single speaker section."""
    # Format text with paragraphs
    paragraphs = segment.text.split('\n')
    paragraphs_html = ''.join([f'<p style="margin: 0 0 12px 0;">{p.strip()}</p>' for p in paragraphs if p.strip()])
    
    return f"""
    <div class="speaker-section">
        <div class="speaker-name">{segment.speaker}</div>
        <div class="speaker-text">{paragraphs_html}</div>
    </div>
    """


def render_transcript_card(
    company_name: str,
    ticker: str,
    year: str,
    quarter: str,
    transcript_text: str
) -> str:
    """Render the transcript card with header and content."""
    # Parse transcript into speaker segments
    segments = parse_transcript(transcript_text)
    
    # Render speaker sections
    speaker_html = ''.join([render_speaker_section(s) for s in segments])
    
    html = f"""
    <div class="transcript-card">
        <div class="transcript-card-header">
            <div class="transcript-title-section">
                <span class="transcript-title">{company_name} ({ticker}) Earnings Call</span>
                <span class="transcript-meta">
                    {year}
                    <span class="meta-dot"></span>
                    {quarter}
                </span>
            </div>
            <a href="#" class="download-btn" onclick="alert('Download functionality coming soon!'); return false;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 15V3m0 12l-4-4m4 4l4-4M2 17l.621 2.485A2 2 0 0 0 4.561 21h14.878a2 2 0 0 0 1.94-1.515L22 17" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>Download Transcript</span>
            </a>
        </div>
        <div class="transcript-body">
            <div class="transcript-content">
                {speaker_html}
            </div>
        </div>
    </div>
    """
    return html


def render_empty_state() -> str:
    """Render empty state when no transcript is available."""
    return """
    <div class="empty-state">
        <div class="empty-state-title">Select a Company, Year, and Quarter</div>
        <div class="empty-state-text">Choose filters above to view earnings call transcripts</div>
    </div>
    """


# =============================================================================
# MAIN PAGE
# =============================================================================

def render_earnings_calls():
    """Render earnings calls content (for unified entry point)."""
    # Inject custom CSS
    st.markdown(get_earnings_css(), unsafe_allow_html=True)
    
    # Page container
    st.markdown('<div class="earnings-page-container">', unsafe_allow_html=True)
    st.markdown('<div class="earnings-content-wrapper">', unsafe_allow_html=True)
    
    # Get data for dropdowns
    companies = EarningsCallRepository.get_companies_with_earnings()
    company_options = [(c['ticker'], f"{c['name']} ({c['ticker']})") for c in companies]
    
    if not company_options:
        st.error("No earnings call data available.")
        st.stop()
    
    # Initialize session state for filters
    if 'ec_company' not in st.session_state:
        st.session_state.ec_company = company_options[0][0]
    if 'ec_year' not in st.session_state:
        st.session_state.ec_year = "2025"
    if 'ec_quarter' not in st.session_state:
        st.session_state.ec_quarter = "Q1"
    
    # Get available years and quarters based on selected company
    available_years = EarningsCallRepository.get_available_years(st.session_state.ec_company)
    year_options = [str(y) for y in sorted(available_years, reverse=True)] if available_years else ["2025", "2024"]
    
    available_quarters = EarningsCallRepository.get_available_quarters(st.session_state.ec_company, st.session_state.ec_year)
    quarter_options = sorted(available_quarters) if available_quarters else ["Q4", "Q3", "Q2", "Q1"]
    
    # =======================================================================
    # HEADER WITH TITLE AND FILTERS
    # =======================================================================
    
    # Create header row with title on left and filters on right
    spacer1,header_col1, header_col2,spacer2 = st.columns([0.1,1, 1,0.1])
    
    with header_col1:
        st.markdown('<h1 class="earnings-title">Earnings Calls</h1>', unsafe_allow_html=True)
    
    with header_col2:
        # Filter row with proper labels
        filter_col1, filter_col2, filter_col3 = st.columns([1.5, 0.5, 0.5])
        
        with filter_col1:
            company = st.selectbox(
                "Select a company and date range to view transcripts.",
                options=[opt[0] for opt in company_options],
                format_func=lambda x: next((opt[1].split('(')[0].strip() for opt in company_options if opt[0] == x), x),
                index=[opt[0] for opt in company_options].index(st.session_state.ec_company) if st.session_state.ec_company in [opt[0] for opt in company_options] else 0,
                key="ec_company_select"
            )
        
        with filter_col2:
            year = st.selectbox(
                "Year",
                options=year_options,
                index=year_options.index(st.session_state.ec_year) if st.session_state.ec_year in year_options else 0,
                key="ec_year_select"
            )
        
        with filter_col3:
            quarter = st.selectbox(
                "Quarter",
                options=quarter_options,
                index=quarter_options.index(st.session_state.ec_quarter) if st.session_state.ec_quarter in quarter_options else 0,
                key="ec_quarter_select"
            )
    
    # Sync session state with widget values
    st.session_state.ec_company = company
    st.session_state.ec_year = year
    st.session_state.ec_quarter = quarter
    
    # =======================================================================
    # FETCH AND DISPLAY TRANSCRIPT
    # =======================================================================
    
    # Fetch transcript data
    earnings_calls = EarningsCallRepository.get_earnings_calls(
        ticker=company,
        year=year,
        quarter=quarter
    )
    
    # Get company display name
    company_display = next((opt[1] for opt in company_options if opt[0] == company), company)
    company_name = company_display.split('(')[0].strip() if '(' in company_display else company_display
    
    # Render transcript card or empty state
    if earnings_calls and len(earnings_calls) > 0:
        transcript = earnings_calls[0]
        if transcript.transcript_text:
            card_html = render_transcript_card(
                company_name=company_name,
                ticker=company,
                year=year,
                quarter=quarter,
                transcript_text=transcript.transcript_text
            )
        else:
            card_html = render_empty_state()
    else:
        card_html = render_empty_state()
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Close containers
    st.markdown('</div>', unsafe_allow_html=True)  # content-wrapper
    st.markdown('</div>', unsafe_allow_html=True)  # page-container


def main():
    """Earnings calls page entry point (standalone)."""
    # Initialize
    init_database()
    
    # Render global styles
    render_styles()
    
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
    render_header(full_width=True, current_page="earnings_calls")

    # Render content
    render_earnings_calls()
    
    # Render Footer
    render_coresight_footer(full_width=True, stick_to_bottom=True)


main()

if __name__ == "__main__":
    pass
