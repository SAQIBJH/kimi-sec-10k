"""
Newsroom Page - Coresight Research
==================================
Financial news feed with filtering and sentiment analysis.
"""
import streamlit as st
from datetime import date, datetime, timedelta
from typing import List, Optional

# MUST be first Streamlit command
st.set_page_config(
    page_title="Coresight Newsroom",
    page_icon="📰",
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


def render_news_card(article: NewsArticle, company_map: dict):
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
            # Company link with custom tooltip
            company_html = f'<a href="/company/{ts.ticker}" class="company-link" title="{tooltip_text}">{company_name}</a>'
            companies_parts.append(company_html)
        
        tagged_companies_html = "<span class='tagged-label'>Tagged Companies: </span>" + " | ".join(companies_parts)
    
    # Build the card HTML - Title is a link but styled as black text without underline
    card_html = f"""
    <div class="news-card">
        <div class="news-header">
            <div class="news-source">{article.source}</div>
            <div class="news-date">
                {formatted_date} <span class="relative-time">{relative_time}</span>
            </div>
        </div>
        <a href="{article.url}" target="_blank" class="news-title-link">{article.title}</a>
        <div class="news-summary">{article.summary}</div>
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
    </style>
    """


def main():
    """Newsroom page entry point."""
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
    render_header(full_width=True)
    
    # Page Title
    st.markdown("""
    <div style="margin: 24px 0;">
        <div style="font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 24px; color: #d62e2f; letter-spacing: 1px;">CORESIGHT MARKET DATA</div>
        <div style="font-family: 'Montserrat', sans-serif; font-weight: 700; font-size: 28px; color: #323232;">News Results</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for filters
    if 'date_from' not in st.session_state:
        st.session_state.date_from = date.today() - timedelta(days=7)
    if 'date_to' not in st.session_state:
        st.session_state.date_to = date.today()
    
    # Get filter options
    sectors = ['All'] + NewsRepository.get_sectors()
    companies = [{'ticker': 'All', 'name': 'All Companies'}] + NewsRepository.get_companies()
    
    # Filters row at the top
    st.markdown("""
    <style>
    .filter-container {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 24px;
    }
    .filter-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 16px;
        color: #323232;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        # Date range filter
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.markdown("**From**")
            date_from = st.date_input(
                "From date",
                value=st.session_state.date_from,
                max_value=date.today(),
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("**To**")
            date_to = st.date_input(
                "To date",
                value=st.session_state.date_to,
                max_value=date.today(),
                label_visibility="collapsed"
            )
        
        with col3:
            st.markdown("**Sector**")
            selected_sector = st.selectbox(
                "Sector",
                options=sectors,
                index=0,
                label_visibility="collapsed"
            )
        
        # Company filter row
        col4, col5 = st.columns([3, 1])
        
        with col4:
            st.markdown("**Company**")
            company_options = [f"{c['name']} ({c['ticker']})" for c in companies]
            company_tickers = [c['ticker'] for c in companies]
            selected_company_idx = st.selectbox(
                "Select company",
                options=range(len(company_options)),
                format_func=lambda i: company_options[i],
                index=0,
                label_visibility="collapsed"
            )
            selected_company = company_tickers[selected_company_idx]
        
        with col5:
            st.markdown("&nbsp;")
            if st.button("Apply Filters", type="primary", use_container_width=True):
                st.session_state.date_from = date_from
                st.session_state.date_to = date_to
                st.rerun()
    
    # Prepare filters for query
    query_sector = None if selected_sector == 'All' else selected_sector
    query_company = None if selected_company == 'All' else selected_company
    
    # Fetch articles
    try:
        articles = NewsRepository.get_articles(
            date_from=date_from,
            date_to=date_to,
            sector=query_sector,
            company_ticker=query_company,
            limit=50
        )
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        articles = []
    
    # Get company name mapping
    company_map = get_company_name_map()
    
    # Render articles
    if articles:
        # Render custom CSS first
        st.markdown(get_news_css(), unsafe_allow_html=True)
        
        # Render each article card
        for article in articles:
            card_html = render_news_card(article, company_map)
            st.markdown(card_html, unsafe_allow_html=True)
        
    else:
        st.info("No news articles found for the selected filters.")
    
    # Render Footer
    render_coresight_footer(full_width=True, stick_to_bottom=True)


if __name__ == "__main__":
    main()
