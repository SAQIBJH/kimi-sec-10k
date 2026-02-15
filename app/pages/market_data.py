"""
Market Data Page - PIXEL PERFECT FIGMA MATCH
============================================
Based on detailed wireframe analysis
"""
import streamlit as st
from datetime import date
from typing import Optional, List

from components.styles import render_styles, COLORS
from components.toolbar import inject_toolbar
from data.repository import CompanyRepository, IncomeStatementRepository, BalanceSheetRepository
from data.models import IncomeStatementData, Company, BalanceSheetData
from utils.local_storage import (
    get_marketdata_company, set_marketdata_company,
    get_marketdata_tab, set_marketdata_tab,
    get_marketdata_date_range, set_marketdata_date_range
)


def format_value(value: Optional[float], conversion_rate: float = 1.0) -> str:
    """Format value in millions with comma separator and currency conversion."""
    if value is None:
        return "-"
    converted = value * conversion_rate
    return f"{converted:,.1f}"


def is_bold_row(label: str) -> bool:
    """Check if row should be bold (subtotal rows) per Figma."""
    bold_labels = {"Total Revenue", "Gross Profit", "Other Operating Exp., Total",
                   "Operating Income", "Net Interest Exp."}
    return label in bold_labels


def has_underline(label: str) -> bool:
    """Check if row should have 2px dark grey underline per Figma."""
    underline_labels = {"Total Revenue", "Gross Profit", "Other Operating Exp., Total",
                        "Operating Income", "Net Interest Exp."}
    return label in underline_labels


def has_grey_separator(label: str) -> bool:
    """Check if row should have 4px grey separator line below it per Figma."""
    separator_labels = {"Total Revenue", "Gross Profit", "Operating Income"}
    return label in separator_labels


def get_indent_level(label: str) -> int:
    """Get indentation level based on row type - 0=normal (12px), 1=indented (24px)."""
    # Level 1: SUBTOTAL/SUMMARY rows - INDENTED (24px left padding)
    level_1 = {"Total Revenue", "Gross Profit", "Other Operating Exp., Total",
               "Operating Income", "Net Interest Exp."}
    
    # Level 0: Regular line items - NOT INDENTED (12px left padding)
    # Revenue, Other Revenue, Cost Of Goods Sold, Selling General & Admin Exp.,
    # R&D Exp., Depreciation & Amort., Other Operating Expense/(Income),
    # Interest Expense, Interest and Invest. Income
    
    if label in level_1:
        return 1  # Subtotals are indented
    else:
        return 0  # Everything else is NOT indented


def get_conversion_rate(from_currency: str, to_currency: str) -> float:
    """Get conversion rate between currencies from the forex table."""
    from data.repository import ForexRepository
    
    if from_currency == to_currency:
        return 1.0
    
    return ForexRepository.get_conversion_rate(from_currency, to_currency)


def is_balance_sheet_bold_row(label: str) -> bool:
    """Check if balance sheet row should be bold (subtotal/total rows)."""
    bold_labels = {
        "Total Assets", "Total Liabilities", "Total Shareholder Equity",
        "Total Current Assets", "Total Non-Current Assets",
        "Total Current Liabilities", "Total Non-Current Liabilities"
    }
    return label.strip() in bold_labels


def has_balance_sheet_grey_separator(label: str) -> bool:
    """Check if row should have grey separator after it (major totals)."""
    separator_after = {
        "Total Assets", "Total Liabilities", "Total Shareholder Equity"
    }
    return label.strip() in separator_after


def get_balance_sheet_indent_level(label: str) -> int:
    """Get indentation level for balance sheet rows.
    0 = no indent (line items like Cash, Inventory)
    1 = one indent (subtotals like Total Current Assets)
    2 = two indents (major totals like Total Assets)
    """
    stripped = label.strip()
    # Major totals - most indented
    if stripped in {"Total Assets", "Total Liabilities", "Total Shareholder Equity"}:
        return 2
    # Subtotals - one indent  
    elif stripped.startswith("Total "):
        return 1
    # Line items - no indent
    else:
        return 0


def render_balance_sheet(ticker: str, start_date: date, end_date: date, conversion_rate: float, reported_currency: str, sort_ascending: bool = True):
    """Render the balance sheet table."""
    try:
        data = BalanceSheetRepository.get_balance_sheet_data(ticker, start_date, end_date)
        
        # Apply sorting based on user selection
        if not sort_ascending:
            # Reverse the periods and corresponding values
            data.periods = list(reversed(data.periods))
            for item in data.line_items:
                item.values = list(reversed(item.values))
        
        if data.periods and data.line_items:
            # Build table HTML
            html = '<div class="table-container"><div class="table-scroll"><table class="data-table"><thead>'
            
            # Header row
            html += '<tr class="row-grey-separator"><th>For Fiscal Period Ending<span class="header-subtext">Millions of trading currency, except per share items.</span></th>'
            for period in data.periods:
                lines = period.label.split('\n')
                if len(lines) >= 2:
                    period_text = lines[0]
                    date_text = lines[1]
                else:
                    period_text = ""
                    date_text = period.label
                
                html += f'<th class="data-col"><span class="period-label">{period_text}</span><span class="period-date">{date_text}</span></th>'
            html += '</tr></thead><tbody>'
            
            # Data rows with currency conversion applied
            for i, item in enumerate(data.line_items):
                indent = get_balance_sheet_indent_level(item.label)
                is_bold = is_balance_sheet_bold_row(item.label)
                has_grey_sep = has_balance_sheet_grey_separator(item.label)
                
                # Check if NEXT row is a total/subtotal - if so, add underline to THIS row
                next_item = data.line_items[i + 1] if i + 1 < len(data.line_items) else None
                needs_underline = next_item and is_balance_sheet_bold_row(next_item.label)
                
                # Build row classes
                row_classes = []
                if is_bold:
                    row_classes.append("row-bold")
                if needs_underline:
                    row_classes.append("row-underline-black")
                if has_grey_sep:
                    row_classes.append("row-grey-separator")
                
                row_class_str = ' '.join(row_classes) if row_classes else ''
                
                html += f'<tr class="{row_class_str}">'
                
                # First column - label with proper indentation
                # indent-0: no indent (line items)
                # indent-1: one indent (subtotals like Total Current Assets)
                # indent-2: two indents (major totals like Total Assets)
                display_label = item.label.strip()
                html += f'<td class="indent-{indent}">{display_label}</td>'
                
                # Data columns with converted values
                for val in item.values:
                    formatted = format_value(val, conversion_rate)
                    html += f'<td class="data-cell">{formatted}</td>'
                
                html += '</tr>'
            
            html += '</tbody></table></div></div>'
            st.html(html)
            
            # ==================== CURRENCY CONVERSION - LEFT SIDE ONLY ====================
            st.html('<div class="currency-section"><div class="currency-label">Currency Conversion</div>')
            
            c1, c2, c3, c4 = st.columns([1.5, 0.3, 1.5, 6])
            
            with c1:
                st.html(f'<div class="currency-box">{reported_currency}</div>')
            
            with c2:
                st.html('<div class="currency-arrow">→</div>')
            
            with c3:
                currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR"]
                default_index = currencies.index(st.session_state.target_currency)
                
                target = st.selectbox(
                    "To",
                    options=currencies,
                    index=default_index,
                    label_visibility="collapsed",
                    key="currency_to_balance"
                )
                
                if target != st.session_state.target_currency:
                    st.session_state.target_currency = target
                    st.rerun()
            
            st.html('</div>')
            
            if st.session_state.target_currency != reported_currency:
                rate = get_conversion_rate(reported_currency, st.session_state.target_currency)
                st.caption(f"Converted at 1 {reported_currency} = {rate:.4f} {st.session_state.target_currency}")
                
        else:
            st.info("No balance sheet data available for the selected date range")
            
    except Exception as e:
        st.error(f"Error loading balance sheet: {e}")


def get_cash_flow_indent_level(label: str) -> int:
    """Get indentation level for cash flow rows.
    0 = no indent (line items)
    1 = one indent (section totals like Operating Cash Flow)
    2 = two indents (major totals like Net Change in Cash)
    """
    stripped = label.strip()
    # Major totals - most indented
    if stripped in {"Net Change in Cash", "Cash at End of Period"}:
        return 2
    # Section totals - one indent
    elif stripped in {"Operating Cash Flow", "Investing Cash Flow", "Financing Cash Flow"}:
        return 1
    # Line items - no indent
    else:
        return 0


def is_cash_flow_bold_row(label: str) -> bool:
    """Check if row should be bold (totals and subtotals)."""
    bold_labels = {
        "Operating Cash Flow", "Investing Cash Flow", "Financing Cash Flow",
        "Net Change in Cash", "Cash at Beginning of Period", "Cash at End of Period"
    }
    return label.strip() in bold_labels


def has_cash_flow_grey_separator(label: str) -> bool:
    """Check if row should have grey separator after it."""
    grey_after = {
        "Operating Cash Flow", "Investing Cash Flow", "Financing Cash Flow",
        "Cash at End of Period"
    }
    return label.strip() in grey_after


def render_cash_flow(ticker: str, start_date: date, end_date: date, conversion_rate: float, reported_currency: str, sort_ascending: bool = True):
    """Render the cash flow statement table."""
    try:
        from data.repository import CashFlowRepository
        
        data = CashFlowRepository.get_cash_flow_data(ticker, start_date, end_date)
        
        # Apply sorting based on user selection
        if not sort_ascending:
            # Reverse the periods and corresponding values
            data.periods = list(reversed(data.periods))
            for item in data.line_items:
                item.values = list(reversed(item.values))
        
        if data.periods and data.line_items:
            # Build table HTML
            html = '<div class="table-container"><div class="table-scroll"><table class="data-table"><thead>'
            
            # Header row
            html += '<tr class="row-grey-separator"><th>For Fiscal Period Ending<span class="header-subtext">Millions of trading currency, except per share items.</span></th>'
            for period in data.periods:
                lines = period.label.split('\n')
                if len(lines) >= 2:
                    period_text = lines[0]
                    date_text = lines[1]
                else:
                    period_text = ""
                    date_text = period.label
                
                html += f'<th class="data-col"><span class="period-label">{period_text}</span><span class="period-date">{date_text}</span></th>'
            html += '</tr></thead><tbody>'
            
            # Data rows with currency conversion applied
            for i, item in enumerate(data.line_items):
                indent = get_cash_flow_indent_level(item.label)
                is_bold = is_cash_flow_bold_row(item.label)
                has_grey_sep = has_cash_flow_grey_separator(item.label)
                
                # Check if NEXT row is a total/subtotal - if so, add underline to THIS row
                next_item = data.line_items[i + 1] if i + 1 < len(data.line_items) else None
                needs_underline = next_item and is_cash_flow_bold_row(next_item.label)
                
                # Build row classes
                row_classes = []
                if is_bold:
                    row_classes.append("row-bold")
                if needs_underline:
                    row_classes.append("row-underline-black")
                if has_grey_sep:
                    row_classes.append("row-grey-separator")
                
                row_class_str = ' '.join(row_classes) if row_classes else ''
                
                html += f'<tr class="{row_class_str}">'
                
                # First column - label with proper indentation
                display_label = item.label.strip()
                html += f'<td class="indent-{indent}">{display_label}</td>'
                
                # Data columns with converted values
                for val in item.values:
                    formatted = format_value(val, conversion_rate)
                    html += f'<td class="data-cell">{formatted}</td>'
                
                html += '</tr>'
            
            html += '</tbody></table></div></div>'
            st.html(html)
            
            # ==================== CURRENCY CONVERSION - LEFT SIDE ONLY ====================
            st.html('<div class="currency-section"><div class="currency-label">Currency Conversion</div>')
            
            c1, c2, c3, c4 = st.columns([1.5, 0.3, 1.5, 6])
            
            with c1:
                st.html(f'<div class="currency-box">{reported_currency}</div>')
            
            with c2:
                st.html('<div class="currency-arrow">→</div>')
            
            with c3:
                currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR"]
                default_index = currencies.index(st.session_state.target_currency)
                
                target = st.selectbox(
                    "To",
                    options=currencies,
                    index=default_index,
                    label_visibility="collapsed",
                    key="currency_to_cashflow"
                )
                
                if target != st.session_state.target_currency:
                    st.session_state.target_currency = target
                    st.rerun()
            
            st.html('</div>')
            
            if st.session_state.target_currency != reported_currency:
                rate = get_conversion_rate(reported_currency, st.session_state.target_currency)
                st.caption(f"Converted at 1 {reported_currency} = {rate:.4f} {st.session_state.target_currency}")
                
        else:
            st.info("No cash flow data available for the selected date range")
            
    except Exception as e:
        st.error(f"Error loading cash flow statement: {e}")


def render_page():
    """Main render function - PIXEL PERFECT FIGMA MATCH."""
    
    # Get data first
    companies = CompanyRepository.get_companies_by_source()
    if not companies:
        st.error("No companies found")
        return
    
    stored_ticker = get_marketdata_company()
    selected_ticker = stored_ticker if stored_ticker and any(
        c.ticker == stored_ticker for c in companies
    ) else companies[0].ticker
    
    selected_company = next(
        (c for c in companies if c.ticker == selected_ticker),
        companies[0]
    )
    
    # Check for URL query param tab first, then fall back to stored tab
    query_tab = st.query_params.get("tab")
    stored_tab = get_marketdata_tab()
    
    selected_tab = query_tab if query_tab in [
        "income_statement", "balance_sheet", "cash_flow", "key_stats", "company_profile"
    ] else (stored_tab if stored_tab in [
        "income_statement", "balance_sheet", "cash_flow", "key_stats", "company_profile"
    ] else "income_statement")
    
    # Get dates based on selected tab
    if selected_tab == "balance_sheet":
        min_date, max_date = BalanceSheetRepository.get_date_range(selected_ticker)
        available_dates = BalanceSheetRepository.get_available_dates(selected_ticker)
    elif selected_tab == "cash_flow":
        from data.repository import CashFlowRepository
        min_date, max_date = CashFlowRepository.get_date_range(selected_ticker)
        available_dates = CashFlowRepository.get_available_dates(selected_ticker)
    else:
        min_date, max_date = IncomeStatementRepository.get_date_range(selected_ticker)
        available_dates = IncomeStatementRepository.get_available_dates(selected_ticker)
    
    stored_start, stored_end = get_marketdata_date_range()
    start_date = date.fromisoformat(stored_start) if stored_start else min_date
    end_date = date.fromisoformat(stored_end) if stored_end else max_date
    
    # Get currency from database based on tab
    if selected_tab == "balance_sheet":
        reported_currency = BalanceSheetRepository.get_reported_currency(
            selected_ticker, end_date
        ) or "USD"
    elif selected_tab == "cash_flow":
        from data.repository import CashFlowRepository
        reported_currency = CashFlowRepository.get_reported_currency(
            selected_ticker, end_date
        ) or "USD"
    else:
        reported_currency = IncomeStatementRepository.get_reported_currency(
            selected_ticker, end_date
        ) or "USD"
    
    # Initialize session state for target currency if not exists
    if 'target_currency' not in st.session_state:
        st.session_state.target_currency = "USD"
    
    # Get conversion rate
    conversion_rate = get_conversion_rate(reported_currency, st.session_state.target_currency)
    
    # ==================== GLOBAL CSS - PIXEL PERFECT FIGMA SPECS ====================
    st.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,400;0,600;0,700;1,400&display=swap');
    
    :root {
        /* Figma Colors - Exact Match */
        --white: #FFFFFF;
        --light-grey: #F9F9F9;
        --black: #000000;
        --dark-grey: #4F4F4F;
        --border-light: #CFCFCF;
        --border-medium: #C1CFCF;
        
        /* Accent Colors */
        --primary-red: #D62E2F;
        
        /* Typography - Figma Specs */
        --font-family: 'Roboto', sans-serif;
        --font-size-base: 16px;
        --font-size-small: 12px;
        --line-height-base: 19px;
        --line-height-compact: 100%;
        
        /* Font Weights */
        --font-weight-regular: 400;
        --font-weight-semibold: 600;
        --font-weight-bold: 700;
        
        /* Spacing */
        --padding-normal: 12px;
        --padding-indented: 24px;
        --padding-top: 4px;
        --gap-small: 2px;
        --gap-medium: 6px;
        
        /* Dimensions */
        --header-height: 48px;
        --row-height: 24px;
        --border-width: 1px;
        --underline-width: 2px;
        
        /* Column Widths */
        --first-column-width: 400px;
        --date-column-width: 164px;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    
    /* Main content container - 110px left/right padding per Figma */
    .block-container {
        padding-left: 110px !important; 
        padding-right: 110px !important; 
        max-width: 1440px !important;
        margin: 0 auto !important;
    }
    
    /* Ensure main container has proper padding */
    .main .block-container {
        padding-left: 110px !important;
        padding-right: 110px !important;
    }
    
    /* Hide duplicate Streamlit button tabs (we use styled HTML tabs instead) */
    div[data-testid="stElementContainer"].st-key-tabbtn_income_statement,
    div[data-testid="stElementContainer"].st-key-tabbtn_key_stats,
    div[data-testid="stElementContainer"].st-key-tabbtn_company_profile {
        display: none !important;
    }
    
    /* Page title - aligned to 110px left margin */
    .page-title {
        font-family: var(--font-family);
        font-weight: var(--font-weight-bold);
        font-size: var(--font-size-small);
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: var(--primary-red);
        margin: 32px 0 4px 0;
        padding-left: 0;
    }
    
    /* Company selector */
    .company-selector {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 24px;
        padding-left: 0;
    }
    
    .company-name {
        font-family: var(--font-family);
        font-weight: var(--font-weight-semibold);
        font-size: 22px;
        color: var(--black);
    }
    
    .dropdown-chevron {
        font-size: var(--font-size-small);
        color: var(--dark-grey);
    }
    
    /* ==================== NAVIGATION TABS - FIGMA EXACT SPECS ==================== */
    .tabs-container {
        display: flex;
        gap: 48px;  /* Figma spec: 48px gap between tabs */
        border-bottom: var(--border-width) solid var(--border-light);
        margin-bottom: 30px;
        padding-top: 8px;  /* Align with Figma 80px header height */
    }
    
    .tab {
        font-family: var(--font-family);
        font-size: var(--font-size-base);  /* 16px Body 1 */
        font-weight: 500;  /* Medium weight from Figma */
        line-height: 26px;  /* Figma height spec */
        padding: 12px 0;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        margin-bottom: -1px;
        transition: all 0.2s ease;
        white-space: nowrap;
    }
    
    .tab-active {
        color: var(--primary-red);  /* #D62E2F */
        font-weight: 500;  /* Medium */
        border-bottom-color: var(--primary-red);
    }
    
    .tab-inactive {
        color: rgba(0, 0, 0, 0.6);  /* 60% opacity for inactive */
        font-weight: 400;  /* Regular */
    }
    
    .tab-inactive:hover {
        color: rgba(0, 0, 0, 0.8);  /* Slight hover effect */
    }
    
    /* Filter row - Figma Design Match */
    .filter-label {
        font-family: var(--font-family);
        font-size: 12px;
        font-weight: 400;
        color: #4F4F4F;
        margin-bottom: 6px;
        margin-top: 0;
        line-height: normal;
        display: block;
        padding-top: 12px;
    }
    
    /* Streamlit selectbox styling to match Figma */
    div[data-testid="stSelectbox"] {
        margin-top: 0 !important;
    }
    
    /* Override the selectbox container */
    div[data-testid="stSelectbox"] > div[data-baseweb="select"] {
        background-color: #F2F2F2 !important;
        border-radius: 4px !important;
        border: none !important;
        height: 36px !important;
        min-height: 36px !important;
    }
    
    /* Override the inner control */
    div[data-testid="stSelectbox"] > div[data-baseweb="select"] > div {
        background-color: #F2F2F2 !important;
        border-radius: 4px !important;
        border: none !important;
        min-height: 36px !important;
        height: 36px !important;
        padding: 0 10px !important;
    }
    
    /* Override the input text - prevent truncation */
    div[data-testid="stSelectbox"] > div[data-baseweb="select"] input {
        font-family: 'Roboto', sans-serif !important;
        font-size: 14px !important;
        color: #000000 !important;
        text-overflow: clip !important;
        overflow: visible !important;
    }
    
    /* Override the value container - ensure full text is shown */
    div[data-testid="stSelectbox"] > div[data-baseweb="select"] > div > div:nth-child(2) {
        padding: 0 !important;
        text-overflow: clip !important;
        overflow: visible !important;
        white-space: nowrap !important;
    }
    
    /* Ensure selectbox value text is not truncated */
    div[data-testid="stSelectbox"] [data-baseweb="select"] span {
        text-overflow: clip !important;
        overflow: visible !important;
    }
    
    /* Override the dropdown indicator */
    div[data-testid="stSelectbox"] > div[data-baseweb="select"] svg {
        color: #4F4F4F !important;
    }
    
    /* Streamlit selectbox styling */
    div[data-testid="stSelectbox"] > div > div {
        background-color: var(--white) !important;
        border: var(--border-width) solid var(--border-light) !important;
        border-radius: 6px !important;
    }
    
    div[data-testid="stSelectbox"] > div > div > div {
        padding: 10px 14px !important;
        font-family: var(--font-family) !important;
        font-size: 14px !important;
        color: var(--black) !important;
    }
    
    /* ==================== TABLE STYLING - PIXEL PERFECT FROM FIGMA ==================== */
    
    .table-container {
        border: var(--border-width) solid var(--border-light);
        border-radius: 8px;
        overflow: hidden;
        background: var(--white);
        margin-bottom: 30px;
    }
    
    .table-scroll {
        max-height: 600px;
        overflow-x: auto;
        overflow-y: auto;
    }
    
    .data-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-family: var(--font-family);
        font-size: var(--font-size-base);
    }
    
    /* ========== HEADER ROW - 48px height, grey background ========== */
    .data-table thead {
        background-color: var(--light-grey);
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .data-table th {
        height: var(--header-height);
        padding: var(--padding-top) var(--padding-normal);
        text-align: left;
        font-weight: var(--font-weight-bold);
        font-size: var(--font-size-base);
        line-height: var(--line-height-base);
        color: var(--black);
        border-bottom: var(--border-width) solid var(--border-light);
        background-color: var(--light-grey);
        vertical-align: top;
    }
    
    /* STICKY FIRST COLUMN */
    .data-table th:first-child,
    .data-table td:first-child {
        position: sticky;
        left: 0;
        z-index: 5;
        background-color: var(--light-grey);
    }
    
    .data-table th:first-child {
        min-width: var(--first-column-width);
        max-width: var(--first-column-width);
    }
    
    .data-table td:first-child {
        min-width: var(--first-column-width);
        max-width: var(--first-column-width);
    }
    
    /* Date column headers - right aligned */
    .data-table th.data-col {
        text-align: right;
        min-width: var(--date-column-width);
        padding: var(--padding-top) var(--padding-top) var(--padding-top) var(--padding-normal);
    }
    
    /* Header subtext */
    .header-subtext {
        display: block;
        font-size: var(--font-size-small);
        font-weight: var(--font-weight-regular);
        font-style: italic;
        color: var(--dark-grey);
        margin-top: var(--gap-small);
        line-height: var(--line-height-compact);
    }
    
    /* Period labels in header */
    .period-label {
        display: block;
        font-size: var(--font-size-base);
        font-weight: var(--font-weight-bold);
        color: var(--black);
        line-height: var(--line-height-compact);
        text-align: right;
    }
    
    .period-date {
        display: block;
        font-size: var(--font-size-base);
        font-weight: var(--font-weight-bold);
        color: var(--black);
        line-height: var(--line-height-compact);
        text-align: right;
        margin-top: var(--gap-small);
    }
    
    /* ========== DATA ROWS - 24px height ========== */
    .data-table tbody tr {
        height: var(--row-height);
    }
    
    .data-table td {
        height: var(--row-height);
        padding: var(--padding-top) var(--padding-normal);
        border-bottom: var(--border-width) solid var(--border-light);
        vertical-align: bottom;
        font-size: var(--font-size-base);
        line-height: var(--line-height-base);
    }
    
    /* First column - label column */
    .data-table td:first-child {
        text-align: left;
        background-color: var(--light-grey);
        color: var(--black);
        font-weight: var(--font-weight-regular);
        vertical-align: middle;
    }
    
    /* Data cells - numbers */
    .data-table td.data-cell {
        text-align: right;
        font-variant-numeric: tabular-nums;
        background-color: var(--white);
        color: var(--black);
        font-weight: var(--font-weight-regular);
        padding: var(--padding-top) 8px var(--padding-top) var(--padding-normal);
    }
    
    /* ========== ROW INDENTATION ========== */
    /* Reversed: Line items = no indent, Totals = indented */
    .indent-0 { 
        padding-left: 8px !important; 
    }
    
    .indent-1 { 
        padding-left: 40px !important; 
    }
    
    .indent-2 { 
        padding-left: 80px !important; 
    }
    
    /* ========== BOLD ROWS (Subtotals) ========== */
    .row-bold td:first-child {
        font-weight: var(--font-weight-bold) !important;
        color: var(--dark-grey) !important;
    }
    
    .row-bold td.data-cell {
        font-weight: var(--font-weight-semibold) !important;
        color: var(--dark-grey) !important;
    }
    
    /* ========== UNDERLINES - 2px thick, dark grey ========== */
    .row-underline-black td.data-cell {
        position: relative;
    }
    
    .row-underline-black td.data-cell::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 5%;
        right: 5%;
        height: var(--underline-width);
        background-color: var(--dark-grey);
    }
    
    /* ========== INDENTED ROW BACKGROUNDS ========== */
    .row-indent-grey {
        background-color: var(--light-grey) !important;
    }
    
    /* ========== GREY SEPARATOR - 4px thick ========== */
    .row-grey-separator td {
        border-bottom: 4px solid #9CA3AF !important;
    }
    
    /* ========== CURRENCY CONVERSION - LEFT SIDE ONLY ========== */
    .currency-section {
        margin-top: 30px;
        max-width: 500px;
    }
    
    .currency-label {
        font-family: var(--font-family);
        font-size: var(--font-size-small);
        font-weight: var(--font-weight-regular);
        color: var(--dark-grey);
        margin-bottom: 12px;
    }
    
    .currency-row {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    
    .currency-box {
        background: var(--white);
        border: var(--border-width) solid var(--border-light);
        border-radius: 6px;
        padding: 12px 16px;
        font-family: var(--font-family);
        font-size: 14px;
        color: var(--black);
        min-width: 160px;
    }
    
    .currency-arrow {
        color: var(--dark-grey);
        font-size: 18px;
        font-weight: 300;
    }
    </style>
    """)
    
    # ==================== TITLE SECTION ====================
    st.html(f'<div class="page-title">CORESIGHT MARKET DATA</div>')
    
    # Company selector - custom HTML with Streamlit selectbox overlay
    company_options = {c.display_name: c.ticker for c in companies}
    current_display = selected_company.display_name
    
    # Custom HTML display
    st.html(f"""
        <style>
        .company-selector-container {{
            position: relative;
            height: 40px;
            margin-bottom: 24px;
        }}
        .company-selector-display {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: 'Roboto', sans-serif;
            font-weight: 600;
            font-size: 22px;
            color: #000;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 1;
            pointer-events: none;
        }}
        .dropdown-chevron {{
            font-size: 12px;
            color: #4F4F4F;
        }}
        /* Hide the Streamlit selectbox but keep it clickable */
        .company-select-overlay div[data-testid="stSelectbox"] {{
            opacity: 0;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            max-width: 500px;
            height: 40px;
            z-index: 2;
            cursor: pointer;
        }}
        .company-select-overlay div[data-testid="stSelectbox"] > div {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            height: 40px !important;
            min-height: 40px !important;
        }}
        .company-select-overlay div[data-testid="stSelectbox"] label {{
            display: none !important;
        }}
        </style>
        <div class="company-selector-container">
            <div class="company-selector-display">
                <span>{selected_company.display_name}</span>
                <span class="dropdown-chevron">▼</span>
            </div>
            <div class="company-select-wrapper"></div>
        </div>
    """)
    
    # Streamlit selectbox positioned over the custom display (invisible but functional)
    new_display = st.selectbox(
        "Company",
        options=list(company_options.keys()),
        index=list(company_options.keys()).index(current_display),
        label_visibility="collapsed",
        key="company_sel_marketdata"
    )
    
    new_ticker = company_options[new_display]
    
    if new_ticker != selected_ticker:
        set_marketdata_company(new_ticker)
        new_min, new_max = IncomeStatementRepository.get_date_range(new_ticker)
        if new_min and new_max:
            set_marketdata_date_range(new_min.isoformat(), new_max.isoformat())
        st.rerun()
    
    # ==================== TOOLBAR ====================
    # Map tab keys to page names for the toolbar
    tab_to_page = {
        "company_profile": "Company Profile",
        "key_stats": "Key Stats",
        "income_statement": "Income Statement",
        "balance_sheet": "Balance Sheet",
        "cash_flow": "Cash Flow"
    }
    active_page = tab_to_page.get(selected_tab, "Income Statement")
    inject_toolbar(active_page=active_page)
    
    # Hidden tab buttons (COMMENTED OUT - using HTML tabs instead)
    # tab_cols = st.columns([1, 1, 1, 6])
    # for i, (tab_key, label) in enumerate([
    #     ("income_statement", "Income Statement"),
    #     ("key_stats", "Key Stats"),
    #     ("company_profile", "Company Profile")
    # ]):
    #     with tab_cols[i]:
    #         if st.button(label, key=f"tabbtn_{tab_key}", type="tertiary", use_container_width=True):
    #             set_marketdata_tab(tab_key)
    #             st.rerun()
    
    # ==================== FILTER ROW - DATES & SORT ====================
    # Initialize sort state
    if 'sort_order' not in st.session_state:
        st.session_state.sort_order = "Earliest"
    
    date_options = [d.strftime("%B %Y") for d in available_dates]
    date_values = {d.strftime("%B %Y"): d for d in available_dates}
    
    curr_start = start_date.strftime("%B %Y")
    start_idx = date_options.index(curr_start) if curr_start in date_options else 0
    
    curr_end = end_date.strftime("%B %Y")
    end_idx = date_options.index(curr_end) if curr_end in date_options else len(date_options) - 1
    
    # Create columns: [spacer, Start Date, End Date, Sort]
    # Wider columns to prevent text truncation - adjusted ratios for proper display
    f1, f2, f3, f4 = st.columns([4, 2, 2, 1.5])
    
    with f2:
        st.html('<div class="filter-label">Start Date</div>')
        new_start_label = st.selectbox(
            "Start",
            options=date_options,
            index=start_idx,
            label_visibility="collapsed",
            key="start_dt"
        )
        new_start_date = date_values.get(new_start_label, start_date)
    
    with f3:
        st.html('<div class="filter-label">End Date</div>')
        new_end_label = st.selectbox(
            "End",
            options=date_options,
            index=end_idx,
            label_visibility="collapsed",
            key="end_dt"
        )
        new_end_date = date_values.get(new_end_label, end_date)
    
    with f4:
        st.html('<div class="filter-label">Sort</div>')
        new_sort_order = st.selectbox(
            "Sort",
            options=["Earliest", "Latest"],
            index=0 if st.session_state.sort_order == "Earliest" else 1,
            label_visibility="collapsed",
            key="sort_order_select"
        )
    
    # Update states if changed
    date_changed = new_start_date != start_date or new_end_date != end_date
    sort_changed = new_sort_order != st.session_state.sort_order
    
    if date_changed:
        if new_start_date > new_end_date:
            st.error("Start date must be before end date")
        else:
            set_marketdata_date_range(new_start_date.isoformat(), new_end_date.isoformat())
            if sort_changed:
                st.session_state.sort_order = new_sort_order
            st.rerun()
    elif sort_changed:
        st.session_state.sort_order = new_sort_order
        st.rerun()
    
    # ==================== TABLE WITH CURRENCY CONVERSION ====================
    # Apply sort order to data
    sort_ascending = st.session_state.sort_order == "Earliest"
    
    if selected_tab == "balance_sheet":
        render_balance_sheet(selected_ticker, start_date, end_date, conversion_rate, reported_currency, sort_ascending)
    elif selected_tab == "cash_flow":
        render_cash_flow(selected_ticker, start_date, end_date, conversion_rate, reported_currency, sort_ascending)
    elif selected_tab in ["income_statement", "key_stats"]:
        try:
            data = IncomeStatementRepository.get_income_statement_data(
                selected_ticker, start_date, end_date
            )
            
            # Apply sorting based on user selection
            if not sort_ascending:
                # Reverse the periods and corresponding values
                data.periods = list(reversed(data.periods))
                for item in data.line_items:
                    item.values = list(reversed(item.values))
            
            if data.periods and data.line_items:
                # Build table HTML
                html = '<div class="table-container"><div class="table-scroll"><table class="data-table"><thead>'
                
                # Header row - with grey separator
                html += '<tr class="row-grey-separator"><th>For Fiscal Period Ending<span class="header-subtext">Millions of trading currency, except per share items.</span></th>'
                for period in data.periods:
                    lines = period.label.split('\n')
                    if len(lines) >= 2:
                        period_text = lines[0]
                        date_text = lines[1]
                    else:
                        period_text = ""
                        date_text = period.label
                    
                    html += f'<th class="data-col"><span class="period-label">{period_text}</span><span class="period-date">{date_text}</span></th>'
                html += '</tr></thead><tbody>'
                
                # Data rows with currency conversion applied
                prev_item_label = None
                for i, item in enumerate(data.line_items):
                    indent = get_indent_level(item.label)
                    is_bold = is_bold_row(item.label)
                    needs_grey_sep = has_grey_separator(item.label)
                    
                    # Check if NEXT row needs underline, if so add it to THIS row
                    next_item = data.line_items[i + 1] if i + 1 < len(data.line_items) else None
                    needs_underline = has_underline(next_item.label) if next_item else False
                    
                    # Build row classes
                    row_classes = []
                    if is_bold:
                        row_classes.append("row-bold")
                    if needs_underline:
                        row_classes.append("row-underline-black")
                    if needs_grey_sep:
                        row_classes.append("row-grey-separator")
                    
                    row_class_str = ' '.join(row_classes) if row_classes else ''
                    
                    html += f'<tr class="{row_class_str}">'
                    
                    # First column - label with proper indentation
                    html += f'<td class="indent-{indent}">{item.label}</td>'
                    
                    # Data columns with converted values
                    for val in item.values:
                        formatted = format_value(val, conversion_rate)
                        html += f'<td class="data-cell">{formatted}</td>'
                    
                    html += '</tr>'
                
                html += '</tbody></table></div></div>'
                st.html(html)
                
                # ==================== CURRENCY CONVERSION - LEFT SIDE ONLY ====================
                st.html('<div class="currency-section"><div class="currency-label">Currency Conversion</div>')
                
                c1, c2, c3, c4 = st.columns([1.5, 0.3, 1.5, 6])
                
                with c1:
                    st.html(f'<div class="currency-box">{reported_currency}</div>')
                
                with c2:
                    st.html('<div class="currency-arrow">→</div>')
                
                with c3:
                    currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR"]
                    default_index = currencies.index("USD")
                    
                    target = st.selectbox(
                        "To",
                        options=currencies,
                        index=default_index,
                        label_visibility="collapsed",
                        key="currency_to"
                    )
                    
                    if target != st.session_state.target_currency:
                        st.session_state.target_currency = target
                        st.rerun()
                
                st.html('</div>')
                
                if st.session_state.target_currency != reported_currency:
                    rate = get_conversion_rate(reported_currency, st.session_state.target_currency)
                    st.caption(f"Converted at 1 {reported_currency} = {rate:.4f} {st.session_state.target_currency}")
                
            else:
                st.info("No data available")
                
        except Exception as e:
            st.error(f"Error: {e}")
    
    elif selected_tab == "company_profile":
        st.info("Company Profile")
        st.markdown(f'<a href="http://localhost:8504/company_profile?ticker={selected_ticker}" target="_blank">View Profile</a>', unsafe_allow_html=True)
