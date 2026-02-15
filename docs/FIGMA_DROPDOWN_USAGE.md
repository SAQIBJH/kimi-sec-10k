# Figma-styled Dropdown Component - Usage Guide

## Overview
The `components/dropdown.py` module provides a reusable Figma-styled dropdown that matches the exact design specifications while using Streamlit's selectbox for functionality.

## Quick Start

### 1. Import the Component
```python
from components.dropdown import render_figma_dropdown_css, render_figma_dropdown_dict
```

### 2. Inject CSS Once per Page
```python
# Call this once, typically after render_styles()
render_figma_dropdown_css()
```

### 3. Render the Dropdown

#### Option A: Using a Dictionary (Recommended for display name → value mapping)
```python
companies = {
    "Macy's Inc. (NYSE:M)": "M",
    "Apple Inc. (NASDAQ:AAPL)": "AAPL",
    "Amazon.com Inc. (NASDAQ:AMZN)": "AMZN"
}

selected_ticker = render_figma_dropdown_dict(
    display_text="Macy's Inc. (NYSE:M)",  # What user sees
    options_dict=companies,                # Display → Value mapping
    selected_value="M",                    # Current selected value
    key="company_selector",                # Unique Streamlit key
    label="Company"                        # Accessibility label (hidden)
)

# Returns: "M" (the value, not the display name)
```

#### Option B: Using a List
```python
years = ["2021", "2022", "2023", "2024", "2025"]

selected_year = render_figma_dropdown(
    display_text="2024",
    options=years,
    selected_index=3,  # Index of "2024"
    key="year_selector",
    label="Year"
)

# Returns: "2024"
```

## Design Specifications

The component matches these Figma specs:
- **Font**: Roboto, 600 weight (semibold), 22px
- **Color**: #000000 (black text)
- **Chevron**: 12px, #4F4F4F (dark grey), ▼ character
- **Spacing**: 8px gap between text and chevron
- **Height**: 40px container
- **Margin**: 24px bottom

## Examples

### Company Selector (Market Data)
```python
# In app/pages/market_data.py

from components.dropdown import render_figma_dropdown_css, render_figma_dropdown_dict

# Inject CSS once
render_figma_dropdown_css()

# Get companies from database
companies = CompanyRepository.get_companies_by_source()
company_options = {c.display_name: c.ticker for c in companies}

# Render dropdown
new_ticker = render_figma_dropdown_dict(
    display_text=selected_company.display_name,
    options_dict=company_options,
    selected_value=selected_ticker,
    key="company_sel_marketdata",
    label="Company"
)

# Handle selection change
if new_ticker != selected_ticker:
    set_marketdata_company(new_ticker)
    st.rerun()
```

### Year Selector (Earnings Calls)
```python
# In app/pages/earnings_calls.py

from components.dropdown import render_figma_dropdown_css, render_figma_dropdown

render_figma_dropdown_css()

years = ["2020", "2021", "2022", "2023", "2024", "2025"]
current_year = "2024"

selected_year = render_figma_dropdown(
    display_text=current_year,
    options=years,
    selected_index=years.index(current_year),
    key="year_selector",
    label="Year"
)

if selected_year != current_year:
    # Update state
    st.rerun()
```

### File Type Selector (SEC Filings)
```python
# In app/pages/company_filings.py

from components.dropdown import render_figma_dropdown_css, render_figma_dropdown

render_figma_dropdown_css()

doc_types = ["All", "10-K", "10-Q", "8-K", "DEF 14A"]
 
selected_type = render_figma_dropdown(
    display_text="10-K",
    options=doc_types,
    selected_index=1,
    key="doc_type_selector",
    label="Document Type"
)
```

## Notes

- **CSS Injection**: Call `render_figma_dropdown_css()` only ONCE per page
- **Unique Keys**: Each dropdown needs a unique `key` parameter
- **Reusable**: Import and use in any page (Market Data, Earnings Calls, Company Filings, etc.)
- **Functionality**: Uses native Streamlit selectbox underneath, so all Streamlit features work (on_change callbacks, etc.)
- **Styling**: CSS is scoped to `.figma-dropdown-*` classes to avoid conflicts

## API Reference

### `render_figma_dropdown_css()`
Injects CSS styles for the dropdown component. Call once per page.

**Returns**: None

---

### `render_figma_dropdown_dict()`
Renders a dropdown using a dictionary for options.

**Parameters**:
- `display_text` (str): Text to display (e.g., "Macy's Inc. (NYSE:M)")
- `options_dict` (Dict[str, str]): Mapping of display_name → value
- `selected_value` (str): Current selected value
- `key` (str): Unique Streamlit selectbox key
- `label` (str, optional): Accessibility label (default: "Select")
- `on_change` (callable, optional): Callback function on selection change

**Returns**: str (selected value from dictionary)

---

### `render_figma_dropdown()`
Renders a dropdown using a list for options.

**Parameters**:
- `display_text` (str): Text to display
- `options` (List[str]): List of option labels
- `selected_index` (int): Current selected option index
- `key` (str): Unique Streamlit selectbox key
- `label` (str, optional): Accessibility label (default: "Select")
- `on_change` (callable, optional): Callback function on selection change

**Returns**: str (selected option value)
