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
from core.auth_manager import require_auth
require_auth()
hide_sidebar()

from components.styles import render_styles, COLORS, TYPOGRAPHY, SPACING
from components.navigation import render_header, render_coresight_footer
from data.repository import EarningsCallRepository
from core.database import init_database
from utils.local_storage_manager import load_earnings_calls_state, save_earnings_calls_state


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
    [data-testid="stHeaderActionElements"] {
                display: none !important;
                visibility: hidden !important;
    }
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
        border-radius: 12px;
        overflow: hidden;
        margin-top: 32px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.05);
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

    /* ===== KEYWORD HIGHLIGHT — BRAND RED THEME ===== */
    mark {
        background: rgba(214, 46, 47, 0.15);
        color: #D62E2F;
        padding: 2px 4px;
        border-radius: 2px;
        font-weight: 600;
    }
    .transcript-content mark {
        background: rgba(214, 46, 47, 0.15);
        color: #D62E2F;
        padding: 2px 4px;
        border-radius: 2px;
        font-weight: 600;
    }
    
    /* ===== TRANSCRIPT SEARCH SIDEBAR ===== */
    .transcript-search-sidebar {
        background: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 12px;
        padding: 16px;
        height: calc(100vh - 340px);
        min-height: 480px;
        overflow-y: auto;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .transcript-search-sidebar::-webkit-scrollbar {
        width: 6px;
    }
    .transcript-search-sidebar::-webkit-scrollbar-track {
        background: #F2F2F2;
        border-radius: 3px;
    }
    .transcript-search-sidebar::-webkit-scrollbar-thumb {
        background: #CBCACA;
        border-radius: 3px;
    }

    .transcript-search-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #F2F2F2;
    }
    .transcript-search-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 16px;
        color: #2D2A29;
    }

    .transcript-search-count {
        font-family: 'Roboto', sans-serif;
        font-size: 12px;
        color: #888888;
        margin: 4px 0 12px 4px;
    }

    .transcript-search-result-card {
        background: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .transcript-search-result-card:hover {
        border-color: #CBCACA;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .transcript-search-speaker {
        font-family: 'Roboto', sans-serif;
        font-weight: 600;
        font-size: 13px;
        color: #D62E2F;
        margin-bottom: 4px;
    }
    .transcript-search-snippet {
        font-family: 'Roboto', sans-serif;
        font-size: 12px;
        color: #6B6B6B;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .transcript-search-placeholder {
        text-align: center;
        color: #888;
        padding: 40px 0;
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
    }
    /* Relevance score badges */
    .relevance-badge {
        font-family: 'Roboto', sans-serif;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 10px;
        white-space: nowrap;
    }
    .relevance-high {
        background: #D4EDDA;
        color: #155724;
    }
    .relevance-mid {
        background: #FFF3CD;
        color: #856404;
    }
    .relevance-low {
        background: #F0F0F0;
        color: #6B6B6B;
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


def _highlight_keyword(text: str, keyword: str) -> str:
    """Wrap keyword matches with <mark> tags — highlights each word individually for multi-word queries."""
    if not keyword or not keyword.strip():
        return text
    # Split into individual words and highlight each
    words = keyword.strip().split()
    result = text
    for word in words:
        if word.strip():
            pattern = re.compile(re.escape(word.strip()), re.IGNORECASE)
            result = pattern.sub(lambda m: f'<mark>{m.group()}</mark>', result)
    return result


def render_speaker_section(segment: SpeakerSegment, keyword: str = None, index: int = 0) -> str:
    """Render a single speaker section with optional keyword highlighting."""
    # Format text with paragraphs
    paragraphs = segment.text.split('\n')
    processed = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if keyword:
            p = _highlight_keyword(p, keyword)
        processed.append(f'<p style="margin: 0 0 12px 0;">{p}</p>')
    paragraphs_html = ''.join(processed)
    
    return f"""
    <div class="speaker-section" id="seg-{index}">
        <div class="speaker-name">{segment.speaker}</div>
        <div class="speaker-text">{paragraphs_html}</div>
    </div>
    """


def render_transcript_card(
    company_name: str,
    ticker: str,
    year: str,
    quarter: str,
    transcript_text: str,
    keyword: str = None
) -> str:
    """Render the transcript card with header and content."""
    # Parse transcript into speaker segments
    segments = parse_transcript(transcript_text)
    
    # Render speaker sections with optional keyword highlighting
    speaker_html = ''.join([
        render_speaker_section(s, keyword=keyword, index=i)
        for i, s in enumerate(segments)
    ])
    
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

@st.cache_data
def get_years(company):
    return EarningsCallRepository.get_available_years(company)

@st.cache_data
def get_quarters(company, year):
    return EarningsCallRepository.get_available_quarters(company, year)

def render_earnings_calls(active_ticker: str = None):
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

    tickers = [opt[0] for opt in company_options]

    # ---------------------------------
    # Restore persisted state from local storage (before initializing defaults)
    # ---------------------------------
    load_earnings_calls_state()

    # ---------------------------------
    # Initialize company state
    # ---------------------------------
    if "ec_company" not in st.session_state:
        if active_ticker and active_ticker in tickers:
            st.session_state.ec_company = active_ticker
        else:
            st.session_state.ec_company = tickers[0]
    # Validate persisted company still exists in available tickers
    elif st.session_state.ec_company not in tickers:
        st.session_state.ec_company = tickers[0]

    # Get available years and quarters based on selected company
    available_years = get_years(st.session_state.ec_company)
    year_options = [str(y) for y in sorted(available_years, reverse=True)] if available_years else ["2025", "2024"]

    if "ec_year" not in st.session_state or st.session_state.ec_year not in year_options:
        st.session_state.ec_year = year_options[0]

    available_quarters = get_quarters(st.session_state.ec_company, st.session_state.ec_year)
    quarter_options = sorted(available_quarters) if available_quarters else ["Q4", "Q3", "Q2", "Q1"]

    if "ec_quarter" not in st.session_state or st.session_state.ec_quarter not in quarter_options:
        st.session_state.ec_quarter = quarter_options[0]

    # =======================================================================
    # HEADER WITH TITLE AND FILTERS
    # =======================================================================
    def on_company_change():
        ticker = st.session_state.ec_company_select
        st.query_params["ticker"] = ticker
        st.session_state.ec_company = ticker

        years = get_years(ticker)
        year_opts = [str(y) for y in sorted(years, reverse=True)] if years else ["2025", "2024"]

        st.session_state.ec_year = year_opts[0]
        st.session_state.ec_year_select = st.session_state.ec_year

        quarters = get_quarters(ticker, st.session_state.ec_year)
        q_opts = sorted(quarters) if quarters else ["Q4", "Q3", "Q2", "Q1"]

        st.session_state.ec_quarter = q_opts[0]
        st.session_state.ec_quarter_select = st.session_state.ec_quarter

        save_earnings_calls_state()

    def on_year_change():
        ticker = st.session_state.ec_company_select
        year = st.session_state.ec_year_select
        st.session_state.ec_year = year

        quarters = get_quarters(ticker, year)
        q_opts = sorted(quarters) if quarters else ["Q4", "Q3", "Q2", "Q1"]

        st.session_state.ec_quarter = q_opts[0]
        st.session_state.ec_quarter_select = st.session_state.ec_quarter

        save_earnings_calls_state()

    def on_quarter_change():
        st.session_state.ec_quarter = st.session_state.ec_quarter_select
        save_earnings_calls_state()

    spacer1, header_col1, header_col2, spacer2 = st.columns([0.1, 1, 1, 0.1])

    with header_col1:
        st.markdown('<h1 class="earnings-title">Earnings Calls</h1>', unsafe_allow_html=True)

    with header_col2:
        filter_col1, filter_col2, filter_col3 = st.columns([1.5, 0.5, 0.5])

        with filter_col1:
            company = st.selectbox(
                "Select a company and date range to view transcripts.",
                options=tickers,
                format_func=lambda x: next((opt[1].split("(")[0].strip() for opt in company_options if opt[0] == x), x),
                index=tickers.index(st.session_state.ec_company),
                key="ec_company_select",
                on_change=on_company_change,
            )

        with filter_col2:
            year = st.selectbox(
                "Year",
                options=year_options,
                index=year_options.index(st.session_state.ec_year),
                key="ec_year_select",
                on_change=on_year_change,
            )

        with filter_col3:
            quarter = st.selectbox(
                "Quarter",
                options=quarter_options,
                index=quarter_options.index(st.session_state.ec_quarter),
                key="ec_quarter_select",
                on_change=on_quarter_change,
            )

    
    # Sync session state with widget values
    st.session_state.ec_company = company
    st.session_state.ec_year = year
    st.session_state.ec_quarter = quarter
    save_earnings_calls_state()
    
    # =======================================================================
    # FETCH TRANSCRIPT DATA
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

    # =======================================================================
    # TWO-COLUMN LAYOUT: Search (Left) + Transcript (Right)
    # =======================================================================
    left_col, right_col = st.columns([0.3, 0.7])

    # ── Parse transcript for search ──
    transcript_text = None
    segments = []
    if earnings_calls and len(earnings_calls) > 0:
        transcript = earnings_calls[0]
        transcript_text = transcript.transcript_text
        if transcript_text:
            segments = parse_transcript(transcript_text)

    # ── LEFT COLUMN: Search Input + Results Panel ──
    with left_col:
        search_term = st.text_input(
            "Search Transcript",
            placeholder="eg., revenue, AWS, guidance...",
            value=st.session_state.get('ec_search', ''),
            key="ec_search_input",
        )
        st.session_state.ec_search = search_term
        active_keyword = search_term.strip() if search_term and search_term.strip() else None

        search_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D62E2F" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'

        with st.container(border=True):
            st.markdown(f'<div class="transcript-search-header">{search_icon}<span class="transcript-search-title">Search Transcript</span></div>', unsafe_allow_html=True)

            if active_keyword and segments:
                # Find matching segments
                matches = []
                for i, seg in enumerate(segments):
                    if active_keyword.lower() in seg.text.lower():
                        # Extract snippet around first occurrence
                        idx = seg.text.lower().find(active_keyword.lower())
                        start = max(0, idx - 40)
                        end = min(len(seg.text), idx + len(active_keyword) + 40)
                        snippet = seg.text[start:end]
                        if start > 0:
                            snippet = '...' + snippet
                        if end < len(seg.text):
                            snippet = snippet + '...'
                        matches.append({'speaker': seg.speaker, 'snippet': snippet, 'index': i})

                if matches:
                    st.markdown(f'<div class="transcript-search-count">Found {len(matches)} match{"es" if len(matches) != 1 else ""} for "<b>{active_keyword}</b>"</div>', unsafe_allow_html=True)
                    for m in matches[:30]:
                        highlighted_snippet = _highlight_keyword(m['snippet'], active_keyword)
                        card_html = f'''
                        <div class="transcript-search-result-card">
                            <div class="transcript-search-speaker">{m['speaker']}</div>
                            <div class="transcript-search-snippet">{highlighted_snippet}</div>
                        </div>
                        '''
                        st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="transcript-search-placeholder">No matches found for "<b>{active_keyword}</b>"</div>', unsafe_allow_html=True)
            elif active_keyword and not segments:
                st.markdown('<div class="transcript-search-placeholder">No transcript loaded to search</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="transcript-search-placeholder">Type a keyword above to search within the transcript</div>', unsafe_allow_html=True)

    # ── RIGHT COLUMN: Transcript Content ──
    with right_col:
        if transcript_text:
            card_html = render_transcript_card(
                company_name=company_name,
                ticker=company,
                year=year,
                quarter=quarter,
                transcript_text=transcript_text,
                keyword=active_keyword
            )
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
    active_ticker = st.query_params.get("ticker", "M")
    # Render Header
    render_header(full_width=True, current_page="earnings_calls",ticker=active_ticker)

    # Render content
    render_earnings_calls(active_ticker)
    
    # Render Footer
    render_coresight_footer(full_width=True, stick_to_bottom=True)


main()

if __name__ == "__main__":
    pass
