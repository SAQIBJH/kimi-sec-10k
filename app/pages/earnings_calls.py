"""
Earnings Calls Page - Coresight Research
========================================
Earnings call transcripts page using native Streamlit components with custom styling.
"""
import streamlit as st
import re
from typing import List, Optional, Tuple, Dict

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
       HIDE STREAMLIT CHROME
       ======================================================================= */
    [data-testid="stHeaderActionElements"] {
        display: none !important;
        visibility: hidden !important;
    }
    /* Also hide stHeader if styles.py didn't already catch it */
    header[data-testid="stHeader"] {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        overflow: hidden !important;
    }

    /* =======================================================================
       FIX: REMOVE EXTRA TOP PADDING ABOVE NAV
       Streamlit adds default top padding to block-container; remove it so
       the nav bar starts at the top of the viewport.
       ======================================================================= */
    div.block-container > div[data-testid="stVerticalBlock"],
    [data-testid="block-container"] > div[data-testid="stVerticalBlock"] {
        padding-top: 0 !important;
    }

    /* =======================================================================
       SCROLLBARS — Left panel (Streamlit container) + Right panel (transcript)
       Matches company_filings.py scrollbar style exactly.
       ======================================================================= */

    /* Left search panel scrollbar — target inner scrollable div of st.container */
    [data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"]::-webkit-scrollbar,
    [data-testid="stVerticalBlockBorderWrapper"] div::-webkit-scrollbar {
        width: 6px;
    }
    [data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"]::-webkit-scrollbar-track,
    [data-testid="stVerticalBlockBorderWrapper"] div::-webkit-scrollbar-track {
        background: #F2F2F2;
        border-radius: 3px;
    }
    [data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"]::-webkit-scrollbar-thumb,
    [data-testid="stVerticalBlockBorderWrapper"] div::-webkit-scrollbar-thumb {
        background: #CBCACA;
        border-radius: 3px;
    }

    /* Left panel border/shadow — matches company_filings style */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #E5E5E5 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    }

    /* Right transcript body scrollbar */
    .transcript-body::-webkit-scrollbar {
        width: 6px;
    }
    .transcript-body::-webkit-scrollbar-track {
        background: #F2F2F2;
        border-radius: 3px;
    }
    .transcript-body::-webkit-scrollbar-thumb {
        background: #CBCACA;
        border-radius: 3px;
    }

    /* =======================================================================
       FILTER BAR - Styled Streamlit Selectboxes
       ======================================================================= */

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
       Fixed at 520px to match the left search panel height exactly.
       Uses flex so the body fills remaining space after the header.
       ======================================================================= */
    .transcript-card {
        width: 100%;
        height: 520px;
        display: flex;
        flex-direction: column;
        background: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 12px;
        overflow: hidden;
        margin-top: 0;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.05);
    }

    /* Card Header */
    .transcript-card-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        padding: 16px 20px;
        border-bottom: 1px solid #E5E5E5;
        background: #FFFFFF;
        gap: 12px;
    }

    .transcript-title-section {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        flex-wrap: wrap;
        flex: 1;
        min-width: 0;
        margin-right: 16px;
    }

    .transcript-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 18px;
        color: #2D2A29;
        word-break: break-word;
        overflow-wrap: anywhere;
        min-width: 0;
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
        flex-shrink: 0;
        white-space: nowrap;
    }

    .download-btn:hover {
        background: #0066CC;
        color: #FFFFFF;
    }

    /* =======================================================================
       TRANSCRIPT BODY
       flex: 1 so it fills whatever height remains after the card header.
       This ensures the total card height stays at exactly 520px.
       ======================================================================= */
    .transcript-body {
        flex: 1;
        max-height: none;
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

    /* ===== SEARCH RESULT VIEW BUTTON & META ===== */
    .transcript-result-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 8px;
        padding-top: 6px;
        border-top: 1px solid #F0F0F0;
    }
    .transcript-result-meta {
        font-family: 'Roboto', sans-serif;
        font-size: 11px;
        color: #999;
        font-weight: 500;
        letter-spacing: 0.3px;
    }
    .transcript-view-btn {
        font-family: 'Roboto', sans-serif;
        font-size: 11px;
        font-weight: 600;
        color: #D62E2F;
        text-decoration: none;
        border: 1px solid #D62E2F;
        border-radius: 4px;
        padding: 3px 10px;
        transition: all 0.15s;
        background: transparent;
        white-space: nowrap;
        display: inline-block;
    }
    .transcript-view-btn:hover {
        background: #D62E2F;
        color: #fff !important;
        text-decoration: none !important;
    }

    /* Highlight the targeted segment when navigated via anchor */
    .speaker-section:target {
        background: rgba(214, 46, 47, 0.06);
        border-radius: 6px;
        outline: 1px solid rgba(214, 46, 47, 0.2);
        padding: 8px;
        margin: -8px;
    }

    </style>
    """


# =============================================================================
# TRANSCRIPT PARSING
# =============================================================================

@st.cache_data(ttl=600, show_spinner=False)
def parse_transcript(transcript_text: str) -> List[Dict]:
    """
    Parse transcript text into speaker segments.

    Returns List[Dict] with keys 'speaker' and 'text' — plain dicts are
    picklable so st.cache_data works correctly across Streamlit reruns.
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

        match = speaker_pattern.match(para)

        if match:
            if current_speaker and current_text:
                segments.append({'speaker': current_speaker, 'text': ' '.join(current_text)})
            current_speaker = match.group(1).strip()
            current_text = [match.group(2).strip()] if match.group(2) else []
        else:
            current_text.append(para)

    if current_speaker and current_text:
        segments.append({'speaker': current_speaker, 'text': ' '.join(current_text)})

    if not segments and transcript_text.strip():
        segments.append({'speaker': 'Transcript', 'text': transcript_text.strip()})

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


def render_speaker_section(segment: Dict, keyword: str = None, index: int = 0) -> str:
    """Render a single speaker section with optional keyword highlighting."""
    paragraphs = segment['text'].split('\n')
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
        <div class="speaker-name">{segment['speaker']}</div>
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
                <span class="transcript-title">{company_name} ({ticker})</span>
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


@st.cache_data(ttl=120, show_spinner=False)
def _get_cross_search_results(keyword: str, company: str, year: str, quarter: str) -> List[Dict]:
    """
    Cross-transcript search: FULLTEXT DB lookup (~15ms) + cached segment extraction.

    Returns up to 50 results — one best-matching segment per transcript.
    Cached 2 min: subsequent searches for same keyword+filters are instant.
    """
    raw_rows = EarningsCallRepository.search_transcripts_fulltext(
        keyword=keyword,
        ticker=company if company != 'ALL' else None,
        year=year if str(year) != 'ALL' else None,
        quarter=quarter if quarter != 'ALL' else None,
        limit=50,
    )

    results = []
    kw_lower = keyword.lower()
    for row in raw_rows:
        transcript_text = row.get('transcript_text', '') or ''
        if not transcript_text:
            continue

        segments = parse_transcript(transcript_text)

        for i, seg in enumerate(segments):
            if kw_lower in seg['text'].lower():
                idx = seg['text'].lower().find(kw_lower)
                start = max(0, idx - 40)
                end = min(len(seg['text']), idx + len(keyword) + 40)
                snippet = seg['text'][start:end]
                if start > 0:
                    snippet = '...' + snippet
                if end < len(seg['text']):
                    snippet = snippet + '...'

                q_val = row.get('q')
                q_str = f"Q{q_val}" if q_val else ''
                results.append({
                    'ticker': row.get('ticker', ''),
                    'year': str(row.get('year', '')),
                    'quarter': q_str,
                    'speaker': seg['speaker'],
                    'snippet': snippet,
                    'seg_index': i,
                })
                break  # first match per transcript only

    return results


def render_cross_search_panel(company: str, year: str, quarter: str) -> str:
    """Right panel shown when any filter is ALL (cross-transcript search mode)."""
    parts = []
    parts.append('All Companies' if company == 'ALL' else company)
    parts.append('All Years' if str(year) == 'ALL' else str(year))
    parts.append('All Quarters' if quarter == 'ALL' else quarter)
    scope = ' &bull; '.join(parts)

    return f"""
    <div class="empty-state" style="margin-top: 32px;">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#D62E2F" stroke-width="1.5" style="margin-bottom: 16px; opacity: 0.7;">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <div class="empty-state-title">Search Across Transcripts</div>
        <div class="empty-state-text" style="margin-top: 10px;">
            <span style="font-weight: 600; color: #2D2A29; font-size: 13px;">{scope}</span><br><br>
            Type a keyword on the left to search all matching transcripts.<br>
            Click <strong>View &#8594;</strong> on any result to open the full transcript.
        </div>
    </div>
    """

def render_earnings_calls(active_ticker: str = None):
    """Render earnings calls content (for unified entry point)."""
    # Inject custom CSS
    st.markdown(get_earnings_css(), unsafe_allow_html=True)

    # (title is rendered inline in the filter header row below — matches Figma layout)

    # Get data for dropdowns
    companies = EarningsCallRepository.get_companies_with_earnings()
    company_options = [('ALL', 'All Companies')] + [(c['ticker'], f"{c['name']} ({c['ticker']})") for c in companies]

    if len(company_options) <= 1:
        st.error("No earnings call data available.")
        st.stop()

    tickers = [opt[0] for opt in company_options]

    # ---------------------------------
    # Restore persisted state from local storage (before initializing defaults)
    # ---------------------------------
    load_earnings_calls_state()

    # ---------------------------------
    # Handle View → navigation from cross-search results
    # Uses a nav_id to consume params ONCE per navigation, not on every rerun.
    # URL: /earnings_calls?ticker=NKE&year=2024&quarter=Q2&highlight=revenue
    # ---------------------------------
    _qp_ticker = st.query_params.get("ticker", "")
    _qp_year = st.query_params.get("year", "")
    _qp_quarter = st.query_params.get("quarter", "")
    _qp_highlight = st.query_params.get("highlight", "")
    _nav_id = f"nav_{_qp_ticker}_{_qp_year}_{_qp_quarter}_{_qp_highlight}"

    if _qp_highlight and st.session_state.get("_ec_nav_id") != _nav_id:
        # Fresh cross-search navigation — consume params into session state
        st.session_state._ec_nav_id = _nav_id
        st.session_state.ec_search = _qp_highlight
        if _qp_ticker and _qp_ticker in tickers:
            st.session_state.ec_company = _qp_ticker
        if _qp_year and _qp_year != 'ALL':
            st.session_state.ec_year = _qp_year
        if _qp_quarter and _qp_quarter != 'ALL':
            st.session_state.ec_quarter = _qp_quarter

    # ---------------------------------
    # Initialize company state (default to first real company, not ALL)
    # ---------------------------------
    if "ec_company" not in st.session_state:
        if active_ticker and active_ticker in tickers:
            st.session_state.ec_company = active_ticker
        else:
            st.session_state.ec_company = tickers[1] if len(tickers) > 1 else tickers[0]
    # Validate persisted company still exists in available tickers
    elif st.session_state.ec_company not in tickers:
        st.session_state.ec_company = tickers[1] if len(tickers) > 1 else tickers[0]

    # Get available years based on selected company
    if st.session_state.ec_company == 'ALL':
        _all_yrs = EarningsCallRepository.get_all_available_years()
        year_options = ['ALL'] + [str(y) for y in _all_yrs]
    else:
        available_years = get_years(st.session_state.ec_company)
        year_options = ['ALL'] + ([str(y) for y in sorted(available_years, reverse=True)] if available_years else ["2025", "2024"])

    if "ec_year" not in st.session_state or st.session_state.ec_year not in year_options:
        # Default to first real year (skip 'ALL')
        st.session_state.ec_year = year_options[1] if len(year_options) > 1 else year_options[0]

    # Get available quarters based on company + year
    if st.session_state.ec_company != 'ALL' and str(st.session_state.ec_year) != 'ALL':
        available_quarters = get_quarters(st.session_state.ec_company, st.session_state.ec_year)
        quarter_options = ['ALL'] + (sorted(available_quarters) if available_quarters else ["Q1", "Q2", "Q3", "Q4"])
    else:
        quarter_options = ['ALL', 'Q1', 'Q2', 'Q3', 'Q4']

    if "ec_quarter" not in st.session_state or st.session_state.ec_quarter not in quarter_options:
        # Default to first real quarter (skip 'ALL')
        st.session_state.ec_quarter = quarter_options[1] if len(quarter_options) > 1 else quarter_options[0]

    # =======================================================================
    # HEADER WITH TITLE AND FILTERS
    # =======================================================================
    def on_company_change():
        ticker = st.session_state.ec_company_select
        # Only push a specific ticker to URL — never push "ALL" (breaks nav links)
        if ticker == 'ALL':
            if "ticker" in st.query_params:
                del st.query_params["ticker"]
        else:
            st.query_params["ticker"] = ticker
        st.session_state.ec_company = ticker

        if ticker == 'ALL':
            _yrs = EarningsCallRepository.get_all_available_years()
            year_opts = ['ALL'] + [str(y) for y in _yrs]
        else:
            years = get_years(ticker)
            year_opts = ['ALL'] + ([str(y) for y in sorted(years, reverse=True)] if years else ["2025", "2024"])

        # Default to first real year when changing company
        st.session_state.ec_year = year_opts[1] if len(year_opts) > 1 else year_opts[0]

        if ticker != 'ALL' and str(st.session_state.ec_year) != 'ALL':
            quarters = get_quarters(ticker, st.session_state.ec_year)
            q_opts = ['ALL'] + (sorted(quarters) if quarters else ["Q1", "Q2", "Q3", "Q4"])
        else:
            q_opts = ['ALL', 'Q1', 'Q2', 'Q3', 'Q4']

        st.session_state.ec_quarter = q_opts[1] if len(q_opts) > 1 else q_opts[0]

        save_earnings_calls_state()

    def on_year_change():
        ticker = st.session_state.ec_company_select
        year = st.session_state.ec_year_select
        st.session_state.ec_year = year

        if ticker != 'ALL' and str(year) != 'ALL':
            quarters = get_quarters(ticker, year)
            q_opts = ['ALL'] + (sorted(quarters) if quarters else ["Q1", "Q2", "Q3", "Q4"])
        else:
            q_opts = ['ALL', 'Q1', 'Q2', 'Q3', 'Q4']

        st.session_state.ec_quarter = q_opts[1] if len(q_opts) > 1 else q_opts[0]

        save_earnings_calls_state()

    def on_quarter_change():
        st.session_state.ec_quarter = st.session_state.ec_quarter_select
        save_earnings_calls_state()

    # =======================================================================
    # PAGE TITLE — Same pattern as newsroom
    # =======================================================================
    st.markdown("""
    <div style="margin: 24px 0 8px 0;">
        <div style="font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 24px; color: #d62e2f; letter-spacing: 1px;">CORESIGHT MARKET DATA</div>
        <div style="font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 28px; color: #323232;">Earnings Calls</div>
    </div>
    """, unsafe_allow_html=True)

    # =======================================================================
    # FILTER ROW — Same pattern as newsroom:
    # Search | (gap) | Company | Year | Quarter
    # =======================================================================
    search_col, _gap, company_col, year_col, quarter_col = st.columns([2.5, 0.3, 2.2, 0.8, 0.8])

    with search_col:
        search_term = st.text_input(
            "Search",
            placeholder="eg., revenue, AWS, guidance...",
            value=st.session_state.get('ec_search', ''),
            key="ec_search_input",
        )
        st.session_state.ec_search = search_term

    with company_col:
        company = st.selectbox(
            "Company",
            options=tickers,
            format_func=lambda x: next((opt[1] if opt[0] == 'ALL' else opt[1].split("(")[0].strip() for opt in company_options if opt[0] == x), x),
            index=tickers.index(st.session_state.ec_company),
            key="ec_company_select",
            on_change=on_company_change,
        )

    with year_col:
        year = st.selectbox(
            "Year",
            options=year_options,
            index=year_options.index(st.session_state.ec_year),
            key="ec_year_select",
            on_change=on_year_change,
        )

    with quarter_col:
        quarter = st.selectbox(
            "Quarter",
            options=quarter_options,
            index=quarter_options.index(st.session_state.ec_quarter),
            key="ec_quarter_select",
            on_change=on_quarter_change,
        )


    # =======================================================================
    # DETECT MODE: cross-transcript search vs single-transcript view
    # =======================================================================
    is_cross_search = (company == 'ALL' or str(year) == 'ALL' or quarter == 'ALL')

    # =======================================================================
    # FETCH TRANSCRIPT DATA (single-transcript mode only)
    # =======================================================================
    earnings_calls = []
    if not is_cross_search:
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

    # ── Parse transcript for single-transcript search ──
    transcript_text = None
    segments = []
    if not is_cross_search and earnings_calls and len(earnings_calls) > 0:
        transcript = earnings_calls[0]
        transcript_text = transcript.transcript_text
        if transcript_text:
            segments = parse_transcript(transcript_text)

    # active_keyword comes from the search input in the filter row above
    active_keyword = search_term.strip() if search_term and search_term.strip() else None

    # ── LEFT COLUMN: Search Results Panel ──
    with left_col:
        search_label = "Search All Transcripts" if is_cross_search else "Search Transcript"
        search_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D62E2F" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'

        with st.container(border=True, height=520):
            st.markdown(f'<div class="transcript-search-header">{search_icon}<span class="transcript-search-title">{search_label}</span></div>', unsafe_allow_html=True)

            if is_cross_search:
                # ── CROSS-TRANSCRIPT SEARCH MODE ──
                if active_keyword:
                    cross_results = _get_cross_search_results(active_keyword, company, str(year), quarter)
                    if cross_results:
                        st.markdown(
                            f'<div class="transcript-search-count">Found <b>{len(cross_results)}</b> '
                            f'match{"es" if len(cross_results) != 1 else ""} for "<b>{active_keyword}</b>"</div>',
                            unsafe_allow_html=True
                        )
                        for r in cross_results:
                            highlighted_snippet = _highlight_keyword(r['snippet'], active_keyword)
                            view_url = (
                                f"/earnings_calls?ticker={r['ticker']}"
                                f"&year={r['year']}&quarter={r['quarter']}"
                                f"&highlight={active_keyword}"
                            )
                            card_html = f'''
                            <div class="transcript-search-result-card">
                                <div class="transcript-search-speaker">{r['speaker']}</div>
                                <div class="transcript-search-snippet">{highlighted_snippet}</div>
                                <div class="transcript-result-footer">
                                    <span class="transcript-result-meta">{r['ticker']} &bull; {r['year']} &bull; {r['quarter']}</span>
                                    <a href="{view_url}" target="_self" class="transcript-view-btn">View &#8594;</a>
                                </div>
                            </div>
                            '''
                            st.markdown(card_html, unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f'<div class="transcript-search-placeholder">No matches found for "<b>{active_keyword}</b>"</div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        '<div class="transcript-search-placeholder">Enter a keyword to search across all matching transcripts</div>',
                        unsafe_allow_html=True
                    )

            elif active_keyword and segments:
                # ── SINGLE-TRANSCRIPT SEARCH MODE ──
                matches = []
                for i, seg in enumerate(segments):
                    if active_keyword.lower() in seg['text'].lower():
                        idx = seg['text'].lower().find(active_keyword.lower())
                        start = max(0, idx - 40)
                        end = min(len(seg['text']), idx + len(active_keyword) + 40)
                        snippet = seg['text'][start:end]
                        if start > 0:
                            snippet = '...' + snippet
                        if end < len(seg['text']):
                            snippet = snippet + '...'
                        matches.append({'speaker': seg['speaker'], 'snippet': snippet, 'index': i})

                if matches:
                    st.markdown(f'<div class="transcript-search-count">Found {len(matches)} match{"es" if len(matches) != 1 else ""} for "<b>{active_keyword}</b>"</div>', unsafe_allow_html=True)
                    for m in matches[:30]:
                        highlighted_snippet = _highlight_keyword(m['snippet'], active_keyword)
                        card_html = f'''
                        <div class="transcript-search-result-card">
                            <div class="transcript-search-speaker">{m['speaker']}</div>
                            <div class="transcript-search-snippet">{highlighted_snippet}</div>
                            <div class="transcript-result-footer">
                                <span class="transcript-result-meta">{company} &bull; {year} &bull; {quarter}</span>
                                <a href="#seg-{m['index']}" class="transcript-view-btn">View &#8594;</a>
                            </div>
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
        if is_cross_search:
            card_html = render_cross_search_panel(company, str(year), quarter)
        elif transcript_text:
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

    # (no wrapper divs to close — using newsroom's flat layout pattern)


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
        body_padding="0 20px",
        max_content_width="1350px",
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
