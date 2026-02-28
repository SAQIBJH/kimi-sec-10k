"""
Newsroom Page - Coresight Research
==================================
Financial news feed with filtering and sentiment analysis.
"""
import streamlit as st
from datetime import date, datetime, timedelta
from typing import List, Optional
import re

from components.styles import hide_sidebar, set_page_layout
from core.auth_manager import require_auth
require_auth()
hide_sidebar()

from components.styles import render_styles, COLORS, TYPOGRAPHY, SPACING
from components.navigation import render_header, render_coresight_footer
from data.models import NewsArticle, TickerSentiment
from data.repository import NewsRepository
from core.database import init_database

# Initialize
def initialize_app():
    """Initialize application state and dependencies."""
    init_database()


def get_company_name_map() -> dict:
    """Get mapping of ticker to company name."""
    if 'company_name_map' not in st.session_state:
        companies = NewsRepository.get_companies()
        st.session_state.company_name_map = {
            c['ticker']: c['name'] for c in companies
        }
    return st.session_state.company_name_map


def _get_ticker_sector(ticker: str) -> Optional[str]:
    """Look up the sector (primary_industry_coresight) for a given ticker."""
    from core.database import db_manager
    query = """
        SELECT primary_industry_coresight as sector
        FROM coreiq_companies
        WHERE ticker = :ticker
        LIMIT 1
    """
    results = db_manager.execute_query(query, {'ticker': ticker})
    if results and results[0].get('sector'):
        return results[0]['sector']
    return None


def format_company_display(ticker: str, company_map: dict) -> str:
    """Get company display name for ticker."""
    return company_map.get(ticker, ticker)


def calculate_relative_time(published_time: datetime) -> str:
    """Calculate relative time string on server side."""
    try:
        now = datetime.now(published_time.tzinfo) if published_time.tzinfo else datetime.now()
        if not published_time.tzinfo:
            published_time = published_time.replace(tzinfo=None)
            now = now.replace(tzinfo=None)

        diff = now - published_time
        diff_seconds = diff.total_seconds()

        if diff_seconds < 0:
            return '(just now)'

        diff_mins = int(diff_seconds / 60)
        diff_hours = int(diff_seconds / 3600)
        diff_days = int(diff_seconds / 86400)

        if diff_mins < 1:
            return '(just now)'
        elif diff_mins < 60:
            return f'({diff_mins} minute{"s" if diff_mins != 1 else ""} ago)'
        elif diff_hours < 24:
            remaining_mins = diff_mins % 60
            if remaining_mins == 0:
                return f'({diff_hours} hour{"s" if diff_hours != 1 else ""} ago)'
            else:
                return f'({diff_hours} hour{"s" if diff_hours != 1 else ""}, {remaining_mins} minute{"s" if remaining_mins != 1 else ""} ago)'
        elif diff_days == 1:
            return '(1 day ago)'
        else:
            return f'({diff_days} days ago)'
    except Exception:
        return ''


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


def render_news_card(article: NewsArticle, company_map: dict, keyword: str = None):
    """
    Render a single news article card using custom HTML/CSS.
    Matches Figma wireframe exactly.
    """
    # Format the date
    formatted_date = article.formatted_date

    # Calculate relative time server-side
    relative_time = calculate_relative_time(article.time_published)

    # Build tagged companies HTML with tooltips
    tagged_companies_html = ""
    if article.ticker_sentiment:
        companies_parts = []
        for ts in article.ticker_sentiment:
            company_name = format_company_display(ts.ticker, company_map)
            # Create tooltip content
            tooltip_text = f"Relevance: {float(ts.relevance_score)*100:.1f}% | Sentiment: {ts.ticker_sentiment_label} ({float(ts.ticker_sentiment_score):.2f})"
            # Company link with custom tooltip - links to company profile page
            company_html = f'<a href="/market_data?ticker={ts.ticker}" class="company-link" title="{tooltip_text}">{company_name}</a>'
            companies_parts.append(company_html)

        tagged_companies_html = "<span class='tagged-label'>Tagged Companies: </span>" + " | ".join(companies_parts)

    # Build the card HTML - Title is a link but styled as black text without underline
    display_title = _highlight_keyword(article.title, keyword) if keyword else article.title
    display_summary = _highlight_keyword(article.summary, keyword) if keyword else article.summary

    card_html = f"""
    <div class="news-card">
        <div class="news-header">
            <div class="news-source">{article.source}</div>
            <div class="news-date">
                {formatted_date} <span class="relative-time">{relative_time}</span>
            </div>
        </div>
        <a href="{article.url}" target="_blank" class="news-title-link">{display_title}</a>
        <div class="news-summary">{display_summary}</div>
        {f'<div class="tagged-companies">{tagged_companies_html}</div>' if tagged_companies_html else ''}
    </div>
    <div class="divider"></div>
    """

    return card_html


def get_news_css() -> str:
    """Get custom CSS for newsroom styling - matches Figma exactly."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Montserrat:wght@400;500;600;700&display=swap');

    /* Keyword highlight — brand red theme */
    mark {
        background: rgba(214, 46, 47, 0.15);
        color: #D62E2F;
        padding: 2px 4px;
        border-radius: 2px;
        font-weight: 600;
    }

    .news-container {
        max-width: 1238px;
        margin: 0 auto;
        padding: 16px 0;
    }

    .news-card {
        padding: 16px 0;
        font-family: 'Roboto', sans-serif;
    }

    .news-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
    }

    .news-source {
        font-family: 'Roboto', sans-serif;
        font-weight: 700;
        font-size: 18px;
        line-height: 21px;
        color: #888888;
    }

    .news-date {
        font-family: 'Roboto', sans-serif;
        font-weight: 700;
        font-size: 16px;
        line-height: 22px;
        color: #888888;
        text-align: right;
    }

    .relative-time {
        color: #888888;
        font-weight: 700;
    }

    .news-title-link {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 20px;
        line-height: 24px;
        letter-spacing: -0.28px;
        color: #000000 !important;
        text-decoration: none !important;
        margin-bottom: 12px;
        display: block;
    }

    /* Ensure title link is black and not underlined */
    .news-title-link,
    .news-title-link:hover,
    .news-title-link:active,
    .news-title-link:visited {
        color: #000000 !important;
        text-decoration: none !important;
    }

    .news-summary {
        font-family: 'Roboto', sans-serif;
        font-weight: 400;
        font-size: 18px;
        line-height: 21px;
        color: #4F4F4F;
        margin-bottom: 12px;
        padding-left: 24px;
    }

    .tagged-companies {
        font-family: 'Roboto', sans-serif;
        font-weight: 700;
        font-size: 18px;
        line-height: 21px;
        color: #4F4F4F;
        padding-left: 24px;
    }

    .tagged-label {
        font-weight: 700;
        color: #4F4F4F;
    }

    .company-link {
        color: #d62e2f !important;
        text-decoration: none;
        cursor: pointer;
    }

    .company-link:hover {
        color: #d62e2f !important;
        text-decoration: underline;
    }

    /* Override Streamlit's default link colors */
    a.company-link,
    a.company-link:visited,
    a.company-link:hover,
    a.company-link:active {
        color: #d62e2f !important;
    }

    .divider {
        height: 1px;
        background: #CBCACA;
        margin: 8px 0;
        width: 100%;
    }

    /* Filter section styles */
    .filter-container {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 24px;
    }

    .filter-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 18px;
        color: #323232;
        margin-bottom: 16px;
    }

    /* ===== NEWS SEARCH SIDEBAR ===== */
    .news-search-sidebar {
        background: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 12px;
        padding: 16px;
        height: calc(100vh - 340px);
        min-height: 480px;
        overflow-y: auto;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.05);
    }

    .news-search-sidebar::-webkit-scrollbar {
        width: 6px;
    }
    .news-search-sidebar::-webkit-scrollbar-track {
        background: #F2F2F2;
        border-radius: 3px;
    }
    .news-search-sidebar::-webkit-scrollbar-thumb {
        background: #CBCACA;
        border-radius: 3px;
    }

    .news-search-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #F2F2F2;
    }

    .news-search-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 16px;
        color: #2D2A29;
    }

    .news-search-count {
        font-family: 'Roboto', sans-serif;
        font-size: 12px;
        color: #888888;
        margin: 4px 0 12px 4px;
    }

    .news-search-result-card {
        background: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .news-search-result-card:hover {
        border-color: #CBCACA;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.10), 0 2px 6px rgba(0, 0, 0, 0.06);
    }
    .news-search-result-title {
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        font-size: 13px;
        color: #2D2A29;
        margin-bottom: 4px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .news-search-result-snippet {
        font-family: 'Roboto', sans-serif;
        font-size: 12px;
        color: #6B6B6B;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .news-search-result-meta {
        display: flex;
        align-items: center;
        gap: 6px;
        font-family: 'Roboto', sans-serif;
        font-size: 11px;
        color: #888888;
        margin-top: 6px;
    }
    .news-search-result-meta-dot {
        width: 3px;
        height: 3px;
        background: #888888;
        border-radius: 50%;
    }
    .news-search-placeholder {
        text-align: center;
        color: #888;
        padding: 40px 0;
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
    }

    /* =======================================================================
       SCROLLBARS — Left search panel (Streamlit container)
       ======================================================================= */
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

    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #E5E5E5 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.07), 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    }
    </style>
    """


def render_page():
    """Render newsroom content (for unified entry point)."""
    # Page Title
    st.markdown("""
    <div style="margin: 24px 0;">
        <div style="font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 24px; color: #d62e2f; letter-spacing: 1px;">CORESIGHT MARKET DATA</div>
        <div style="font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 28px; color: #323232;">News Results</div>
    </div>
    """, unsafe_allow_html=True)

    # Get URL ticker parameter (e.g. /newsroom?ticker=UA)
    url_ticker = st.query_params.get("ticker", None)

    # Get date bounds from news table
    date_bounds = NewsRepository.get_news_date_range()
    news_min_date = date_bounds['min_date']
    news_max_date = date_bounds['max_date']

    # Initialize session state for filters within valid bounds
    if 'date_from' not in st.session_state:
        st.session_state.date_from = max(news_min_date, news_max_date - timedelta(days=7))
    if 'date_to' not in st.session_state:
        st.session_state.date_to = news_max_date

    # Initialize sort order
    if 'news_sort_order' not in st.session_state:
        st.session_state.news_sort_order = "Latest"

    # Render custom CSS
    st.markdown(get_news_css(), unsafe_allow_html=True)

    # =======================================================================
    # FILTER ROW: Search + Date + Sort + Sector + Company
    # =======================================================================
    search_col,frre_space, col_from, col_to, col_sort, col_sector, col_company = st.columns(
        [2.7, 0.5, 1, 1, 1, 1.3, 1.5]
    )

    with search_col:
        search_term = st.text_input(
            "Search",
            placeholder="eg., inflation, earnings, retail...",
            value=st.session_state.get('news_search', ''),
            key="news_search_input",
        )
        st.session_state.news_search = search_term

    with col_from:
        date_from = st.date_input(
            "From",
            value=st.session_state.date_from,
            min_value=news_min_date,
            max_value=news_max_date,
        )
        st.session_state.date_from = date_from

    with col_to:
        date_to = st.date_input(
            "To",
            value=st.session_state.date_to,
            min_value=news_min_date,
            max_value=news_max_date,
        )
        st.session_state.date_to = date_to

    # Sort filter (Earliest = ASC, Latest = DESC)
    with col_sort:
        sort_order = st.selectbox(
            "Sort",
            options=["Latest", "Earliest"],
            index=0 if st.session_state.news_sort_order == "Latest" else 1,
            key="news_sort_select",
        )
        st.session_state.news_sort_order = sort_order
    sort_ascending = sort_order == "Earliest"

    # Cascading: sectors based on selected date range
    sectors = ['All'] + NewsRepository.get_sectors(date_from=date_from, date_to=date_to)

    # Sector always defaults to "All" — preserve user's manual selection if valid
    default_sector_idx = 0
    if st.session_state.get('news_selected_sector') and st.session_state['news_selected_sector'] in sectors:
        default_sector_idx = sectors.index(st.session_state['news_selected_sector'])

    with col_sector:
        selected_sector = st.selectbox(
            "Sector",
            options=sectors,
            index=default_sector_idx,
            key="news_sector_select",
        )
    st.session_state.news_selected_sector = selected_sector

    # Cascading: companies based on selected date range + sector
    query_sector = None if selected_sector == 'All' else selected_sector
    companies = [{'ticker': 'All', 'name': 'All Companies'}] + NewsRepository.get_companies(
        date_from=date_from,
        date_to=date_to,
        sector=query_sector
    )
    company_tickers = [c['ticker'] for c in companies]

    # Pre-set the widget key ONLY on initial load (key doesn't exist yet).
    # After that, let the user's selectbox changes drive the state.
    if 'news_company_select' not in st.session_state:
        # First visit: use URL ticker if valid, else "All"
        if url_ticker and url_ticker in company_tickers:
            st.session_state['news_company_select'] = url_ticker
        else:
            st.session_state['news_company_select'] = 'All'
    elif st.session_state.get('news_company_select') not in company_tickers:
        # Current selection no longer valid (e.g., date range or sector changed)
        st.session_state['news_company_select'] = 'All'

    # Build display label map: ticker → "Company Name (TICKER)" or "All Companies"
    company_display_map = {}
    for c in companies:
        if c['ticker'] == 'All':
            company_display_map['All'] = 'All Companies'
        else:
            company_display_map[c['ticker']] = f"{c['name']} ({c['ticker']})"

    with col_company:
        selected_company = st.selectbox(
            "Company",
            options=company_tickers,
            format_func=lambda t: company_display_map.get(t, t),
            key="news_company_select",
        )

    # Prepare filters for query
    query_company = None if selected_company == 'All' else selected_company

    # Fetch articles (with keyword filter if provided)
    active_keyword = search_term.strip() if search_term and search_term.strip() else None
    try:
        articles = NewsRepository.get_articles(
            date_from=date_from,
            date_to=date_to,
            sector=query_sector,
            company_ticker=query_company,
            keyword=active_keyword,
            limit=50,
            sort_ascending=sort_ascending,
        )
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        articles = []

    # Get company name mapping
    company_map = get_company_name_map()

    # =======================================================================
    # TWO-COLUMN LAYOUT: Search Results (Left) + News Cards (Right)
    # =======================================================================
    left_col, right_col = st.columns([0.3, 0.7])

    # ── LEFT COLUMN: Search Results Panel ──
    with left_col:
        search_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D62E2F" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'

        with st.container(border=True, height=560):
            st.markdown(f'<div class="news-search-header">{search_icon}<span class="news-search-title">Search News</span></div>', unsafe_allow_html=True)

            if active_keyword:
                if articles:
                    st.markdown(f'<div class="news-search-count">Found {len(articles)} article{"s" if len(articles) != 1 else ""} matching "<b>{active_keyword}</b>"</div>', unsafe_allow_html=True)
                    for article in articles[:20]:
                        # Truncate title and summary for compact display
                        title_short = (article.title[:80] + '...') if len(article.title) > 80 else article.title
                        summary_short = (article.summary[:100] + '...') if article.summary and len(article.summary) > 100 else (article.summary or '')
                        # Highlight keywords in left panel snippets
                        title_short = _highlight_keyword(title_short, active_keyword)
                        summary_short = _highlight_keyword(summary_short, active_keyword)
                        source = article.source_domain or article.source or ''
                        pub_date = article.time_published.strftime('%b %d, %Y') if article.time_published else ''

                        card_html = f'''
                        <div class="news-search-result-card">
                            <div class="news-search-result-title">{title_short}</div>
                            <div class="news-search-result-snippet">{summary_short}</div>
                            <div class="news-search-result-meta">
                                <span>{source}</span>
                                <span class="news-search-result-meta-dot"></span>
                                <span>{pub_date}</span>
                            </div>
                        </div>
                        '''
                        st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="news-search-placeholder">No articles found matching "<b>{active_keyword}</b>"</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="news-search-placeholder">Type a keyword above to search across news headlines and summaries</div>', unsafe_allow_html=True)

    # ── RIGHT COLUMN: News Cards (scrollable container) ──
    with right_col:
        with st.container(border=False, height=560):
            if articles:
                for article in articles:
                    card_html = render_news_card(article, company_map, keyword=active_keyword)
                    st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.info("No news articles found for the selected filters.")


def main():
    """Newsroom page entry point (standalone)."""
    # Initialize
    initialize_app()

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
    render_header(full_width=True, current_page="newsroom",ticker=st.query_params.get("ticker", "M"))

    # Render content
    render_page()

    # Render Footer
    render_coresight_footer(full_width=True, stick_to_bottom=True)


main()

if __name__ == "__main__":
    pass
