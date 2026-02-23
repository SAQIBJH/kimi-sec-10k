"""Stock Quote Table Demo - Figma Design Implementation

This module demonstrates how to extract data from raw_json field
and display it in a table matching the Figma design.

Figma URL: https://www.figma.com/design/CiMfOW2lULkY8p613AuNkX/Marketing---Research-Website?node-id=20660-223833
"""

import json
import streamlit as st
from typing import Dict, Any, Optional
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class StockQuoteData:
    """Stock quote data structure matching Figma design."""
    # From raw_json (available)
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: int
    
    # Calculated from raw_json (available)
    change_on_day: Decimal
    change_percent: Decimal
    
    # From other sources (not in raw_json)
    market_cap: Optional[Decimal] = None
    shares_outstanding: Optional[Decimal] = None
    float_percent: Optional[Decimal] = None
    shares_sold_short: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    diluted_eps: Optional[Decimal] = None
    pe_ratio: Optional[Decimal] = None
    week_52_high: Optional[Decimal] = None
    week_52_low: Optional[Decimal] = None


def parse_raw_json(raw_json_str: str) -> Dict[str, Any]:
    """Parse raw_json string from database.
    
    Example raw_json:
    {
        "bar": {
            "3. low": "16.5000",
            "1. open": "16.5200",
            "2. high": "16.7050",
            "4. close": "16.6500",
            "5. volume": "6097152"
        },
        "date": "2026-01-30"
    }
    """
    try:
        return json.loads(raw_json_str)
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse raw_json: {e}")
        return {}


def extract_stock_data(raw_json_str: str) -> StockQuoteData:
    """Extract stock quote data from raw_json field.
    
    This is the MAIN function that your manager is talking about!
    Sirf raw_json se ye sab data nikalta hai:
    - Open, High, Low, Close, Volume
    - Change on Day (calculated)
    - Change % on Day (calculated)
    """
    data = parse_raw_json(raw_json_str)
    bar_data = data.get("bar", {})
    
    # Extract raw values from JSON
    open_price = Decimal(bar_data.get("1. open", "0"))
    high_price = Decimal(bar_data.get("2. high", "0"))
    low_price = Decimal(bar_data.get("3. low", "0"))
    close_price = Decimal(bar_data.get("4. close", "0"))
    volume = int(bar_data.get("5. volume", "0"))
    
    # Calculate change values
    change_on_day = close_price - open_price
    change_percent = (change_on_day / open_price * 100) if open_price else Decimal("0")
    
    return StockQuoteData(
        open_price=open_price,
        high_price=high_price,
        low_price=low_price,
        close_price=close_price,
        volume=volume,
        change_on_day=change_on_day,
        change_percent=change_percent
    )


def format_decimal(value: Decimal, decimal_places: int = 2) -> str:
    """Format decimal value with specified decimal places."""
    quantize_str = "0." + "0" * decimal_places
    return str(value.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP))


def format_number_mm(value: Optional[Decimal]) -> str:
    """Format number in millions (mm)."""
    if value is None:
        return "-"
    millions = value / Decimal("1000000")
    return f"{millions:,.1f}"


def format_percent(value: Decimal) -> str:
    """Format percentage value."""
    return f"{value:.2f}%"


def render_stock_quote_table(stock_data: StockQuoteData, currency: str = "USD"):
    """Render stock quote table matching Figma design.
    
    Figma Design Structure:
    - 7 rows x 4 columns (Label-Value | Label-Value)
    - Gray labels on left, white values on right
    - Title: "Stock Quote and Chart (Currency: USD)"
    """
    
    # Table title
    st.markdown(f"**Stock Quote and Chart (Currency: {currency})**")
    
    # Prepare data rows matching Figma design
    # Format: (Left Label, Left Value, Right Label, Right Value)
    
    rows = [
        # Row 1
        (
            "Last (Delayed)",
            format_decimal(stock_data.close_price),
            "Market Cap (mm)",
            format_number_mm(stock_data.market_cap) if stock_data.market_cap else "-"
        ),
        # Row 2
        (
            "Open",
            format_decimal(stock_data.open_price),
            "Shares Out. (mm)",
            format_number_mm(stock_data.shares_outstanding)
        ),
        # Row 3
        (
            "Previous Close",
            format_decimal(stock_data.close_price),  # Same as Last
            "Float %",
            format_percent(stock_data.float_percent) if stock_data.float_percent else "-"
        ),
        # Row 4
        (
            "Change on Day",
            format_decimal(stock_data.change_on_day),
            "Shares Sold Short (mm)",
            format_number_mm(stock_data.shares_sold_short)
        ),
        # Row 5
        (
            "Change % on Day",
            format_percent(stock_data.change_percent),
            "Dividend Yield %",
            format_percent(stock_data.dividend_yield) if stock_data.dividend_yield else "-"
        ),
        # Row 6
        (
            "Day High/Low",
            f"{format_decimal(stock_data.high_price)}/ {format_decimal(stock_data.low_price)}",
            "Diluted EPS Excl. Extra Items",
            format_decimal(stock_data.diluted_eps) if stock_data.diluted_eps else "-"
        ),
        # Row 7
        (
            "52 wk High/Low",
            f"{format_decimal(stock_data.week_52_high) if stock_data.week_52_high else '-'}/ {format_decimal(stock_data.week_52_low) if stock_data.week_52_low else '-'}",
            "P/Diluted EPS Before Extra",
            f"{format_decimal(stock_data.pe_ratio)}x" if stock_data.pe_ratio else "-"
        ),
    ]
    
    # Custom CSS for Figma-style table
    st.markdown("""
    <style>
    .stock-quote-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Roboto', sans-serif;
        font-size: 14px;
    }
    .stock-quote-table td {
        padding: 4px 12px;
        height: 24px;
    }
    .stock-quote-table .label {
        background-color: #f9f9f9;
        color: #4f4f4f;
        font-weight: 600;
        width: 200px;
    }
    .stock-quote-table .value {
        background-color: #ffffff;
        color: #000000;
        text-align: right;
        width: 100px;
        border-bottom: 1px solid #cfcfcf;
    }
    .stock-quote-container {
        border: 1px solid #cfcfcf;
        border-radius: 8px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Build HTML table
    html = '<div class="stock-quote-container"><table class="stock-quote-table">'
    for left_label, left_value, right_label, right_value in rows:
        html += f"""
        <tr>
            <td class="label">{left_label}</td>
            <td class="value">{left_value}</td>
            <td class="label">{right_label}</td>
            <td class="value">{right_value}</td>
        </tr>
        """
    html += "</table></div>"
    
    st.markdown(html, unsafe_allow_html=True)


def render_page():
    """Main page function."""
    st.title("📊 Stock Quote Table Demo")
    
    # Your sample database row
    sample_raw_json = '''{"bar": {"3. low": "16.5000", "1. open": "16.5200", "2. high": "16.7050", "4. close": "16.6500", "5. volume": "6097152"}, "date": "2026-01-30"}'''
    
    st.subheader("Raw JSON from Database:")
    st.code(sample_raw_json, language="json")
    
    # Extract data
    stock_data = extract_stock_data(sample_raw_json)
    
    st.subheader("Extracted Values:")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Open:** {stock_data.open_price}")
        st.write(f"**High:** {stock_data.high_price}")
        st.write(f"**Low:** {stock_data.low_price}")
        st.write(f"**Close:** {stock_data.close_price}")
    with col2:
        st.write(f"**Volume:** {stock_data.volume:,}")
        st.write(f"**Change:** {stock_data.change_on_day}")
        st.write(f"**Change %:** {stock_data.change_percent:.2f}%")
    
    st.divider()
    
    # Render Figma-style table
    st.subheader("Figma Design Table:")
    render_stock_quote_table(stock_data, currency="USD")
    
    st.divider()
    
    # Explanation
    with st.expander("ℹ️ Samajhna hai? Yeh padho!"):
        st.markdown("""
        ### Raw JSON se kya kya nikal sakte hain:
        
        **Direct Values (JSON se milega):**
        | Field | JSON Key |
        |-------|----------|
        | Open | `bar["1. open"]` |
        | High | `bar["2. high"]` |
        | Low | `bar["3. low"]` |
        | Close/Last | `bar["4. close"]` |
        | Volume | `bar["5. volume"]` |
        
        **Calculated Values (Formula se banega):**
        | Field | Formula |
        |-------|---------|
        | Change on Day | `Close - Open` |
        | Change % on Day | `((Close - Open) / Open) * 100` |
        | Day High/Low | `High / Low` (concatenate) |
        
        **Dusri Tables se aayega:**
        - Market Cap → Company info table
        - Shares Outstanding → Company info table  
        - 52 Week High/Low → Historical data table
        - EPS → Financial statements table
        - P/E Ratio → Calculate from Price/EPS
        
        **Sirf raw_json se ye fields NAHIN ban sakte:**
        - Market Cap (mm)
        - Shares Out. (mm)
        - Float %
        - Shares Sold Short (mm)
        - Dividend Yield %
        - Diluted EPS
        - 52 wk High/Low
        - P/Diluted EPS
        """)


if __name__ == "__main__":
    st.set_page_config(page_title="Stock Quote Demo", layout="wide")
    render_page()
