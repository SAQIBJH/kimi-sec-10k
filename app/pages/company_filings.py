"""
Company Filing Documents Page - Coresight Research
==================================================
SEC filing documents viewer with metric search and document display.
Matches Figma design with Streamlit native components + custom styling.
"""
import os
import json
import logging
import streamlit as st
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from components.styles import hide_sidebar, set_page_layout
from core.auth_manager import require_auth
require_auth()
hide_sidebar()

from components.styles import render_styles
from components.navigation import render_header, render_coresight_footer

# =============================================================================
# FILINGS DIRECTORY SCANNER
# =============================================================================
FILINGS_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "filings")

# ── DB-based company names (replaces hardcoded dict) ─────────────────────────
def _load_company_names_from_db():
    """Load ticker→display_name map from coreiq_companies for all DB companies."""
    try:
        from data.repository import FilingMetricRepository
        repo = FilingMetricRepository()
        with repo.engine.connect() as conn:
            from sqlalchemy import text
            rows = conn.execute(text("""
                SELECT c.ticker, COALESCE(c.name_coresight, c.name) AS display_name
                FROM coreiq_companies c
                WHERE c.ticker IS NOT NULL AND c.ticker != ''
                ORDER BY c.ticker
            """)).fetchall()
            return {row[0].strip(): row[1] for row in rows if row[0].strip()}
    except Exception as e:
        logger.warning(f"[DB] Failed to load company names: {e}")
        return {"AAPL": "Apple Inc.", "AMZN": "Amazon.com Inc.", "M": "Macy's Inc."}

COMPANY_NAMES = _load_company_names_from_db()
logger.info(f"[INIT] Loaded {len(COMPANY_NAMES)} company names from DB")

# Map directory names to display names for document types
# Map directory names to display names (handles both old "10K" and new "10-K" folders)
DOC_TYPE_MAP = {
    "10K": "10-K",
    "10-K": "10-K",
    "10Q": "10-Q",
    "10-Q": "10-Q",
    "8K": "8-K",
    "8-K": "8-K",
    "DEF14A": "DEF 14A",
    "S1": "S-1",
    "S-1": "S-1",
}
# Reverse map: display name → DB doc_type (uses new hyphenated folder names)
DOC_TYPE_REVERSE = {
    "10-K": "10-K",
    "10-Q": "10-Q",
    "8-K": "8-K",
    "DEF 14A": "DEF14A",
    "S-1": "S-1",
}

# Annual document types (no quarter filter needed)
ANNUAL_DOC_TYPES = {"10-K", "DEF 14A", "S-1"}


def scan_filings_directory():
    """Scan the filings directory to discover available companies, years, and doc types.

    Expected structure: data/filings/{TICKER}/{YEAR}/{DOC_TYPE}/*.html or *.htm
    Prefers *-clean.html > *.html > *.htm when multiple files exist.
    """
    filings_data = {}  # {ticker: {year: {doc_type: html_path}}}

    if not os.path.isdir(FILINGS_BASE_DIR):
        logger.warning(f"[SCAN] Filings directory not found: {FILINGS_BASE_DIR}")
        return filings_data

    for ticker in sorted(os.listdir(FILINGS_BASE_DIR)):
        ticker_dir = os.path.join(FILINGS_BASE_DIR, ticker)
        if not os.path.isdir(ticker_dir) or ticker.startswith(('.', '_')):
            continue

        for year_name in sorted(os.listdir(ticker_dir), reverse=True):
            year_dir = os.path.join(ticker_dir, year_name)
            if not os.path.isdir(year_dir) or not year_name.isdigit():
                continue

            for doc_type_dir_name in sorted(os.listdir(year_dir)):
                doc_dir = os.path.join(year_dir, doc_type_dir_name)
                if not os.path.isdir(doc_dir):
                    continue

                # Find best HTML file: prefer filing.html (has iXBRL IDs),
                # then other .html, then .htm. Avoid -clean.html (strips iXBRL).
                filing_html = None
                html_files = []
                htm_files = []
                for f in os.listdir(doc_dir):
                    full = os.path.join(doc_dir, f)
                    if f == 'filing.html':
                        filing_html = full
                    elif f.endswith('.html') and not f.endswith('-clean.html'):
                        html_files.append(full)
                    elif f.endswith('.htm'):
                        htm_files.append(full)

                html_file = filing_html or (html_files or htm_files or [None])[0]

                if html_file:
                    display_type = DOC_TYPE_MAP.get(doc_type_dir_name, doc_type_dir_name)
                    filings_data.setdefault(ticker, {}).setdefault(year_name, {})[display_type] = html_file
                    logger.debug(f"[SCAN] {ticker}/{year_name}/{display_type} -> {os.path.basename(html_file)}")

    logger.info(f"[SCAN] Found filings: {[(t, list(y.keys())) for t, y in filings_data.items()]}")
    return filings_data


# Scan on module load (cached by Streamlit reruns within same session)
FILINGS_DATA = scan_filings_directory()
logger.info(f"[INIT] Filings data: {[(t, {y: list(d.keys()) for y, d in years.items()}) for t, years in FILINGS_DATA.items()]}")


# =============================================================================
# DATA MODELS
# =============================================================================

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

# ── DB-based company/year/doctype lists (replaces folder scan) ────────────────
from data.repository import FilingMetricRepository

def _load_companies_from_db():
    """Get (ticker, display_label) for companies that have data in filing_metrics.
    Display label uses the format: 'Company Name (TICKER)'.
    """
    try:
        from core.database import db_manager
        rows = db_manager.execute_query("""
            SELECT fm.ticker, MIN(fm.company_name) AS company_name
            FROM filing_metrics fm
            WHERE fm.ticker IS NOT NULL AND fm.ticker != ''
            GROUP BY fm.ticker
            ORDER BY fm.ticker
        """)
        results = []
        for row in rows:
            ticker = row["ticker"]
            name = row["company_name"] or COMPANY_NAMES.get(ticker, ticker)
            display = f"{name} ({ticker})"
            results.append((ticker, display))
        return results
    except Exception as e:
        logger.warning(f"[DB] Failed to load companies: {e}")
        return [(t, f"{COMPANY_NAMES.get(t, t)} ({t})") for t in sorted(FILINGS_DATA.keys())] if FILINGS_DATA else [("AAPL", "Apple Inc. (AAPL)")]

def _get_available_years_from_db(ticker: str):
    """Get available fiscal years for a ticker from filing_metrics DB."""
    try:
        from core.database import db_manager
        rows = db_manager.execute_query("""
            SELECT DISTINCT fiscal_year FROM filing_metrics
            WHERE ticker = :ticker ORDER BY fiscal_year DESC
        """, {"ticker": ticker})
        return [str(row["fiscal_year"]) for row in rows if row["fiscal_year"]]
    except Exception:
        return sorted(FILINGS_DATA.get(ticker, {}).keys(), reverse=True)

def _get_available_doc_types_from_db(ticker: str):
    """Get available doc types for a ticker from filing_metrics DB."""
    try:
        from core.database import db_manager
        rows = db_manager.execute_query("""
            SELECT DISTINCT doc_type FROM filing_metrics
            WHERE ticker = :ticker ORDER BY doc_type
        """, {"ticker": ticker})
        return [row["doc_type"] for row in rows if row["doc_type"]]
    except Exception:
        company_data = FILINGS_DATA.get(ticker, {})
        return sorted(set(dt for yd in company_data.values() for dt in yd.keys())) if company_data else ["10-K"]

COMPANIES = _load_companies_from_db()
logger.info(f"[INIT] DB companies with data: {len(COMPANIES)}")

# Fallback doc types list (used only if DB query fails)
DOCUMENT_TYPES = ["10-K"]


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
        border-radius: 12px;
        padding: 16px;
        height: calc(100vh - 340px);
        min-height: 480px;
        overflow-y: auto;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.05);
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
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04);
    }

    .metric-card:hover {
        border-color: #CBCACA;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.10), 0 2px 6px rgba(0, 0, 0, 0.06);
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
        margin-bottom: 2px;
    }

    .metric-formula {
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-size: 11px;
        color: #888;
        margin-bottom: 4px;
        white-space: normal;
        overflow-wrap: break-word;
        word-break: break-word;
    }

    .metric-dimension {
        font-size: 11px;
        color: #777;
        font-style: italic;
        margin: 1px 0 4px 0;
        line-height: 1.3;
        overflow-wrap: break-word;
        word-break: break-word;
    }

    .metric-meta {
        display: flex;
        align-items: center;
        flex-wrap: nowrap;
        gap: 6px;
        font-family: 'Roboto', sans-serif;
        font-size: 11px;
        color: #888888;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .metric-meta span {
        white-space: nowrap;
        flex-shrink: 0;
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
       COMPACT VIEW BUTTONS IN SEARCH SIDEBAR
       ======================================================================= */
    [data-testid="stColumn"]:first-child button {
        height: 30px !important;
        min-height: 30px !important;
        padding: 2px 12px !important;
        font-size: 12px !important;
        background: #F0F7FF !important;
        color: #0066CC !important;
        border: 1px solid #E0EFFF !important;
        border-radius: 4px !important;
        font-family: 'Roboto', sans-serif !important;
    }

    [data-testid="stColumn"]:first-child button:hover {
        background: #E0EFFF !important;
        border-color: #0066CC !important;
    }

    /* =======================================================================
       DOCUMENT VIEWER
       ======================================================================= */
    .document-viewer {
        background: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 12px;
        height: calc(100vh - 280px);
        min-height: 540px;
        display: flex;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.05);
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

def render_document_viewer(document: Optional[FilingDocument]) -> str:
    """Render the document viewer area."""
    # Download icon SVG (inline)
    download_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'
    
    if not document:
        return f'<div class="document-viewer"><div class="document-content"><div class="document-placeholder"><div class="document-placeholder-text">Select a metric to view document</div><div class="document-placeholder-subtext">Choose a financial metric from the list to view details</div></div></div></div>'
    
    return f'<div class="document-viewer"><div class="document-header"><div class="document-title-section"><span class="document-title">{document.company_name} ({document.ticker}) {document.document_type}</span><span class="document-badge">{document.year}</span><span class="document-meta"><span class="document-meta-dot"></span><span>{document.quarter}</span></span></div><a href="#" class="download-btn" onclick="alert(\'Download functionality coming soon!\'); return false;">{download_icon}<span>Download</span></a></div><div class="document-content"><div class="document-placeholder"><div class="document-placeholder-text">FILING DOCUMENT</div><div class="document-placeholder-subtext">{document.company_name} {document.document_type} for {document.year} {document.quarter}</div></div></div></div>'


def _convert_ixbrl_to_spans(html: str) -> str:
    """Convert iXBRL namespace elements (ix:nonFraction, ix:nonNumeric, etc.)
    to regular <span> elements so their id attributes are accessible via
    document.getElementById() in the browser.

    The HTML5 parser does not create proper DOM nodes for namespace-prefixed
    elements like <ix:nonFraction>, so id attributes on them are invisible
    to JavaScript. Converting to <span> fixes this.
    """
    import re
    # Convert opening ix: tags → <span> while keeping id and other attrs
    # Matches <ix:nonFraction ...>, <ix:nonNumeric ...>, <ix:continuation ...>, etc.
    html = re.sub(
        r'<ix:(\w+)(\s[^>]*)?>',
        lambda m: f'<span data-ix="{m.group(1)}"{m.group(2) or ""}>',
        html,
    )
    # Convert closing tags
    html = re.sub(r'</ix:\w+>', '</span>', html)
    return html


def render_sec_html_viewer(html_path: str, highlight_fact_id: Optional[str] = None) -> None:
    """
    Render SEC HTML document using components.html for iframe isolation.
    """
    import streamlit.components.v1 as components

    logger.info(f"[RENDER HTML] html_path: {html_path}")
    logger.info(f"[RENDER HTML] highlight_fact_id: {highlight_fact_id}")

    # Read HTML content
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            clean_html = f.read()
        logger.info(f"[RENDER HTML] File read success, size: {len(clean_html)} bytes")
    except Exception as e:
        logger.error(f"[RENDER HTML] Error loading document: {e}")
        st.error(f"Error loading document: {e}")
        return

    # Convert iXBRL namespace tags to spans so IDs are in the DOM
    clean_html = _convert_ixbrl_to_spans(clean_html)

    # Inject highlight script if fact_id provided
    if highlight_fact_id:
        highlight_script = f"""
        <script>
        (function() {{
            let attempts = 0;
            const factId = '{highlight_fact_id}';
            const isTextSearch = factId.startsWith('TEXT:');
            const searchText = isTextSearch ? factId.substring(5) : '';

            function highlightElement(el) {{
                el.style.backgroundColor = '#FDF5F5';
                el.style.boxShadow = '0 0 10px rgba(214, 46, 47, 0.3)';
                el.style.border = '2px solid #D62E2F';
                el.style.borderRadius = '4px';
                el.style.padding = '4px';
                el.scrollIntoView({{behavior: 'smooth', block: 'center'}});
            }}

            function findAndHighlightText(text) {{
                /*
                 * Robust text search for non-XBRL metrics.
                 *
                 * WHY NOT TreeWalker: SEC filings wrap numbers in iXBRL <span> tags,
                 * e.g. "operated <span>680</span> store locations".
                 * TreeWalker visits individual text nodes, so it never sees the full
                 * sentence in one node.
                 *
                 * FIX: Use element.textContent (concatenates ALL child text) to find
                 * the DEEPEST element containing the search text, then highlight it
                 * exactly like getElementById does for XBRL.
                 */
                /*
                 * Normalize ALL whitespace including non-breaking spaces (U+00A0 / &#160;)
                 * SEC filings heavily use &#160; which becomes U+00A0 in textContent
                 * but search text has regular U+0020 spaces — must normalize both.
                 */
                const WS = /[\u00A0\s]+/g;
                const normalizedSearch = text.replace(WS, ' ').trim();


                /* Try full text first, then progressively shorter prefixes */
                const searchVariants = [
                    normalizedSearch,
                    normalizedSearch.substring(0, 80),
                    normalizedSearch.substring(0, 50),
                    normalizedSearch.substring(0, 30),
                ];

                for (const searchStr of searchVariants) {{
                    if (searchStr.length < 15) continue;

                    const allElements = document.body.querySelectorAll('p, td, li, div, span, section, article');
                    let bestMatch = null;
                    let bestSize = Infinity;

                    for (const el of allElements) {{
                        const elText = (el.textContent || '').replace(WS, ' ');
                        if (elText.includes(searchStr)) {{
                            /* Prefer the smallest (most specific) element */
                            if (elText.length < bestSize) {{
                                bestSize = elText.length;
                                bestMatch = el;
                            }}
                        }}
                    }}

                    if (bestMatch) {{
                        highlightElement(bestMatch);
                        return true;
                    }}
                }}
                return false;
            }}

            function tryScroll() {{
                if (isTextSearch) {{
                    /* Text-search fallback for non-XBRL (store_count, credit_rating) */
                    if (!findAndHighlightText(searchText) && attempts < 30) {{
                        attempts++;
                        setTimeout(tryScroll, 300);
                    }}
                }} else {{
                    /* Standard getElementById for XBRL */
                    const el = document.getElementById(factId);
                    if (el) {{
                        highlightElement(el);
                    }} else if (attempts < 30) {{
                        attempts++;
                        setTimeout(tryScroll, 300);
                    }}
                }}
            }}
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', tryScroll);
            }} else {{
                tryScroll();
            }}
        }})();
        </script>
        """
        if '</body>' in clean_html:
            clean_html = clean_html.replace('</body>', highlight_script + '</body>')
        else:
            clean_html = clean_html + highlight_script

    # Render HTML via components.html (creates sandboxed iframe)
    logger.info("[RENDER HTML] Calling components.html...")
    try:
        components.html(clean_html, height=800, scrolling=True)
        logger.info("[RENDER HTML] components.html completed")
    except Exception as e:
        logger.error(f"[RENDER HTML] components.html error: {e}")
        st.error(f"Error rendering HTML: {e}")


# =============================================================================
# MAIN PAGE
# =============================================================================

def main():
    """Company Filing Documents page entry point."""
    render_styles()

    # Initialize session state with defaults from available data
    available_tickers = [c[0] for c in COMPANIES]
    if 'cf_search' not in st.session_state:
        st.session_state.cf_search = ""
    if 'cf_company' not in st.session_state:
        st.session_state.cf_company = available_tickers[0] if available_tickers else "AAPL"
    if st.session_state.cf_company not in available_tickers:
        st.session_state.cf_company = available_tickers[0] if available_tickers else "AAPL"
    if 'cf_doc_type' not in st.session_state:
        st.session_state.cf_doc_type = DOCUMENT_TYPES[0] if DOCUMENT_TYPES else "10-K"
    if 'cf_year' not in st.session_state:
        # Default to the latest available year for this company
        company_years = _get_available_years_from_db(st.session_state.cf_company)
        st.session_state.cf_year = company_years[0] if company_years else "2025"
    if 'cf_quarter' not in st.session_state:
        st.session_state.cf_quarter = "Q1"
    if 'cf_highlight_fact_id' not in st.session_state:
        st.session_state.cf_highlight_fact_id = None
    if 'cf_view_metric' not in st.session_state:
        st.session_state.cf_view_metric = None
    
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
    render_header(full_width=True, current_page="company_filings")

    # Inject custom CSS
    st.markdown(get_filings_css(), unsafe_allow_html=True)
    
    # =======================================================================
    # HEADER WITH TITLE AND FILTERS
    # =======================================================================

    header_col1, header_col2 = st.columns([1, 2])

    with header_col1:
        st.markdown('<h3 class="filings-title">Company Filing Documents</h3>', unsafe_allow_html=True)

    with header_col2:
        # Dynamic filter values based on selected company
        # DB-based filter values (no folder dependency)
        available_years = _get_available_years_from_db(st.session_state.cf_company) or ["2025"]
        available_doc_types = _get_available_doc_types_from_db(st.session_state.cf_company) or DOCUMENT_TYPES

        # Hide quarter filter for annual filings (10-K, DEF 14A, S-1)
        show_quarter = st.session_state.cf_doc_type not in ANNUAL_DOC_TYPES

        if show_quarter:
            f1, f2, f3, f4 = st.columns([2.5, 1.2, 1.2, 1.2])
        else:
            f1, f2, f3 = st.columns([2.5, 1.2, 1.2])

        with f1:
            company = st.selectbox(
                "Company",
                options=[c[0] for c in COMPANIES],
                format_func=lambda x: next((c[1] for c in COMPANIES if c[0] == x), x),
                index=min([c[0] for c in COMPANIES].index(st.session_state.cf_company), len(COMPANIES) - 1),
                key="cf_company_select"
            )

        with f2:
            safe_doc_idx = available_doc_types.index(st.session_state.cf_doc_type) if st.session_state.cf_doc_type in available_doc_types else 0
            doc_type = st.selectbox(
                "Document Type",
                options=available_doc_types,
                index=safe_doc_idx,
                key="cf_doc_type_select"
            )

        with f3:
            safe_year_idx = available_years.index(st.session_state.cf_year) if st.session_state.cf_year in available_years else 0
            year = st.selectbox(
                "Year",
                options=available_years,
                index=safe_year_idx,
                key="cf_year_select"
            )

        quarter = "Annual"
        if show_quarter:
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

        # DB Search — matches on original_label OR standard_concept (with synonym expansion)
        # Falls back to LLM extraction on miss (spinner shown only during LLM call).
        search_results = []
        used_llm = False
        if search_term.strip():
            doc_type_dir = DOC_TYPE_REVERSE.get(doc_type, doc_type)

            # Step 1: fast DB search (no spinner needed)
            try:
                search_results = FilingMetricRepository.search(
                    ticker=company,
                    fiscal_year=int(year),
                    doc_type=doc_type_dir,
                    query=search_term,
                    limit=50,
                )
            except Exception as e:
                logger.error(f"[SEARCH] DB search error: {e}", exc_info=True)

            # Step 2: DB miss → try LLM extraction (spinner only here)
            if not search_results:
                import os as _os
                if _os.getenv("OPENAI_API_KEY", "").strip():
                    try:
                        with st.spinner("Searching document with AI..."):
                            from core.llm_extractor import LLMExtractor
                            from core.database import db_manager as _dbm
                            engine = _dbm._engine
                            if engine:
                                with engine.begin() as conn:
                                    llm_res = LLMExtractor.extract(
                                        conn=conn,
                                        ticker=company,
                                        fiscal_year=int(year),
                                        doc_type=doc_type_dir,
                                        query=search_term,
                                    )
                                if llm_res:
                                    search_results = llm_res
                                    used_llm = True
                    except Exception as e:
                        logger.error(f"[LLM] extraction error: {e}", exc_info=True)

        # Source badge HTML helpers
        def _source_badge(source: Optional[str]) -> str:
            if source == "calculated":
                return '<span style="background:#E8F4FD;color:#0066CC;font-size:10px;font-weight:600;padding:2px 6px;border-radius:3px;margin-left:6px;vertical-align:middle;">CALC</span>'
            if source == "llm":
                return '<span style="background:#F0F7EE;color:#2E7D32;font-size:10px;font-weight:600;padding:2px 6px;border-radius:3px;margin-left:6px;vertical-align:middle;">AI</span>'
            if source == "edgartools":
                return '<span style="background:#FFF3E0;color:#E65100;font-size:10px;font-weight:600;padding:2px 6px;border-radius:3px;margin-left:6px;vertical-align:middle;">EDGAR</span>'
            return ""  # xbrl = no badge (default, most common)

        def _format_calc_note(note: str) -> str:
            """Format raw calculation note: replace (123456789) with ($123.5B)."""
            import re
            if not note:
                return ""
            def _fmt(m):
                try:
                    val = abs(float(m.group(1).replace(",", "")))
                    if val >= 1e12:
                        return f"(${val/1e12:.1f} T)"
                    elif val >= 1e9:
                        return f"(${val/1e9:.1f} B)"
                    elif val >= 1e6:
                        return f"(${val/1e6:.0f} M)"
                    else:
                        return f"(${val:,.0f})"
                except Exception:
                    return m.group(0)
            result = re.sub(r'\(([\d,]+(?:\.\d+)?)\)', _fmt, note)
            return "= " + result

        # Search Metrics box — bordered container with styled cards
        search_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D62E2F" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
        eye_icon_svg = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>'

        with st.container(border=True):
            st.markdown(f'<div class="search-header">{search_icon}<span class="search-title">Search Metrics</span></div>', unsafe_allow_html=True)

            if search_results:
                source_note = " · AI extracted" if used_llm else ""
                st.markdown(f'<div class="metrics-count">Showing {len(search_results)} metrics{source_note}</div>', unsafe_allow_html=True)
                def _fmt_period_date(d_str: str) -> str:
                    """Format "2023-01-29" → "Jan '23"."""
                    if not d_str:
                        return ""
                    try:
                        from datetime import datetime as _dt
                        return _dt.strptime(str(d_str)[:10], "%Y-%m-%d").strftime("%b '%y")
                    except Exception:
                        return str(d_str)[:7]

                for i, metric in enumerate(search_results):
                    is_viewing = (st.session_state.cf_highlight_fact_id == metric.ixbrl_id and metric.ixbrl_id)
                    card_class = "metric-card active" if is_viewing else "metric-card"
                    btn_class = "viewing" if is_viewing else "view"
                    btn_text = "Viewing" if is_viewing else "View"
                    badge_html = _source_badge(metric.source)
                    label_html = f'{metric.display_label}{badge_html}'
                    # Dimension subtitle: show full_dimension_label on its own line in parens
                    dim_html = ""
                    if metric.is_dimensioned and metric.full_dimension_label:
                        dim_html = f'<div class="metric-dimension">( {metric.full_dimension_label} )</div>'
                    formula_html = ""
                    if metric.source == "calculated" and metric.calculation_note:
                        formula_html = f'<div class="metric-formula">{_format_calc_note(metric.calculation_note)}</div>'
                    # ── Period label: show actual data period, not filing year ──
                    pt = metric.period_type or ""
                    if pt == "duration" and metric.period_start and metric.period_end:
                        period_meta = f"{_fmt_period_date(metric.period_start)} → {_fmt_period_date(metric.period_end)}"
                    elif pt == "instant" and metric.period_instant:
                        period_meta = _fmt_period_date(metric.period_instant)
                    else:
                        period_meta = str(metric.fiscal_year)
                    st.markdown(f'<div class="{card_class}"><div class="metric-info"><div class="metric-name">{label_html}</div>{dim_html}<div class="metric-value">{metric.formatted_value}</div>{formula_html}<div class="metric-meta"><span>{metric.display_statement_type}</span><span class="metric-meta-dot"></span><span>{doc_type}</span><span class="metric-meta-dot"></span><span>{period_meta}</span></div></div><div class="metric-action-btn {btn_class}">{eye_icon_svg}<span>{btn_text}</span></div></div>', unsafe_allow_html=True)
                    # Enable "View in Document" for ixbrl_id OR text-searchable sources
                    source_sentence = None
                    if not metric.ixbrl_id and metric.source in ('store_count', 'credit_rating') and getattr(metric, 'llm_query', None):
                        try:
                            detail = json.loads(getattr(metric, 'llm_query', '{}'))
                            source_sentence = detail.get('source_sentence', '')
                        except Exception:
                            source_sentence = None
                    
                    view_id = metric.ixbrl_id  # Normal XBRL ID
                    if not view_id and source_sentence:
                        # Use TEXT: prefix for text-search fallback
                        view_id = f"TEXT:{source_sentence[:120]}"
                    
                    if view_id:
                        btn_key = f"view_{i}_{metric.original_label.replace(' ', '_')}_{hash(view_id) % 10000}"
                        if st.button(f"View in Document", key=btn_key, use_container_width=True):
                            st.session_state.cf_highlight_fact_id = view_id
                            st.session_state.cf_view_metric = metric.display_label
                            st.rerun()
            elif search_term.strip():
                st.markdown(f'<div style="text-align:center;color:#888;padding:40px 0;font-size:14px;">Not disclosed in this filing for &quot;{search_term}&quot;</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="text-align:center;color:#888;padding:40px 0;font-size:14px;">Search for a metric to see results</div>', unsafe_allow_html=True)

    with right_col:
        # HTML VIEWER - Dynamic path based on selected filters
        company_name = next((c[1] for c in COMPANIES if c[0] == company), company)

        # Look up HTML path from scanned filings data
        html_path = FILINGS_DATA.get(company, {}).get(year, {}).get(doc_type, "")

        logger.info(f"[HTML VIEWER] Company: {company}, Year: {year}, DocType: {doc_type}")
        logger.info(f"[HTML VIEWER] HTML path: {html_path}")
        logger.info(f"[HTML VIEWER] File exists: {os.path.exists(html_path) if html_path else False}")

        if html_path and os.path.exists(html_path):
            logger.info("[HTML VIEWER] ✅ File found, rendering HTML")
            
            # Show document header
            highlight_text = ""
            if st.session_state.cf_highlight_fact_id:
                highlight_text = f"🔍 Auto-scrolled to {st.session_state.cf_view_metric or 'metric'} ({st.session_state.cf_highlight_fact_id})"
                logger.info(f"[HTML VIEWER] Highlight: {highlight_text}")
            
            header_html = f'<div style="display:flex;align-items:center;justify-content:space-between;padding:16px 20px;border-bottom:1px solid #E5E5E5;background:#fff;border-radius:8px 8px 0 0;"><div><span style="font-weight:600;font-size:16px;color:#2D2A29;">{company_name} ({company}) {doc_type}</span><span style="background:#F2F2F2;padding:4px 10px;border-radius:4px;font-size:13px;color:#4F4F4F;margin-left:12px;">{year}</span></div><div style="color:#0066CC;font-size:14px;">{highlight_text}</div></div>'
            st.markdown(header_html, unsafe_allow_html=True)
            
            # Render SEC HTML with highlighting
            logger.info(f"[HTML VIEWER] Calling render_sec_html_viewer with path: {html_path}")
            render_sec_html_viewer(html_path, st.session_state.cf_highlight_fact_id)
            logger.info("[HTML VIEWER] ✅ render_sec_html_viewer completed")
        else:
            logger.error(f"[HTML VIEWER] ❌ File NOT found: {html_path}")
            # Show placeholder
            document = FilingDocument(
                company_name=company_name,
                ticker=company,
                document_type=doc_type,
                year=year,
                quarter=quarter,
                content=""
            )
            viewer_html = render_document_viewer(document)
            st.markdown(viewer_html, unsafe_allow_html=True)
    
    # Render Footer
    render_coresight_footer(full_width=True, stick_to_bottom=True)


main()
