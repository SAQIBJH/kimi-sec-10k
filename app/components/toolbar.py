"""
Navigation Toolbar Component
Based on Figma design node 20862-187662
"""
import streamlit as st


def inject_toolbar(active_page: str = "Company Profile") -> None:
    """
    Inject a sticky navigation toolbar for the Market Data section.
    
    Args:
        active_page: The currently active page name. 
                     Options: "Company Profile", "Key Stats", "Income Statement", "Balance Sheet", "Cash Flow"
    """
    
    # Define pages and their corresponding URLs
    # Unified navigation - all on single port
    pages = [
        ("Company Profile", "/?page=company_profile"),
        ("Key Stats", "/?page=market_data&tab=key_stats"),
        ("Income Statement", "/?page=market_data&tab=income_statement"),
        ("Balance Sheet", "/?page=market_data&tab=balance_sheet"),
        ("Cash Flow", "/?page=market_data&tab=cash_flow"),
    ]
    
    # Generate toolbar HTML
    toolbar_html = f"""
    <style>
        /* Toolbar Container - Sticky, full width with 110px side padding */
        .toolbar-container {{
            background-color: #FFFFFF;
            padding: 32px 110px 1px 110px;
            position: sticky;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid #CBCACA;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
            width: 100%;
            box-sizing: border-box;
        }}
        
        /* Links Container - left aligned, matches Figma spec */
        .toolbar-links {{
            display: flex;
            gap: 105px;
            align-items: flex-start;
            width: 100%;
            max-width: 1220px;
        }}
        
        /* Individual Link */
        .toolbar-link {{
            font-family: 'Roboto', sans-serif;
            font-weight: 600;
            font-size: 18px;
            color: #2D2A29 !important;
            text-decoration: none !important;
            position: relative;
            padding-bottom: 2px;
            white-space: nowrap;
        }}
        
        /* Active Link - Red color */
        .toolbar-link.active {{
            color: #D62E2F !important;
        }}
        
        /* Active Link - Red underline */
        .toolbar-link.active::after {{
            content: '';
            position: absolute;
            bottom: -8px;
            left: 0;
            width: 100%;
            height: 4px;
            background-color: #D62E2F;
        }}
        
        /* Hover effect */
        .toolbar-link:hover {{
            color: #D62E2F !important;
            text-decoration: none !important;
        }}
        
        /* Bottom border line (gray for inactive) */
        .toolbar-border {{
            height: 4px;
            width: 100%;
            max-width: 1220px;
            background-color: transparent;
            margin-top: -4px;
        }}
    </style>
    
    <div class="toolbar-container">
        <div class="toolbar-links">
            {''.join([
                f'<a href="{url}" target="_self" class="toolbar-link {"active" if name == active_page else ""}">{name}</a>'
                for name, url in pages
            ])}
        </div>
        <div class="toolbar-border"></div>
    </div>
    """
    
    st.markdown(toolbar_html, unsafe_allow_html=True)


# Example usage
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    
    # Test the toolbar with different active pages
    inject_toolbar(active_page="Key Stats")
    
    # Add some content to demonstrate sticky behavior
    for i in range(50):
        st.write(f"Content line {i + 1}")
