# Architecture Documentation - Research Portal

**Project**: Coresight Research Portal  
**Last Updated**: 2026-02-14

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Data Flow](#data-flow)
3. [Module Details](#module-details)
4. [Balance Sheet Implementation](#balance-sheet-implementation)
5. [Sort Filter Implementation](#sort-filter-implementation)
6. [CSS Architecture](#css-architecture)
7. [State Management](#state-management)
8. [Testing Strategy](#testing-strategy)

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Header     │  │  Navigation  │  │     Filter Bar       │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Main Content Area                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │  │
│  │  │   Income    │  │   Balance   │  │    Key Stats    │  │  │
│  │  │  Statement  │  │    Sheet    │  │                 │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      Footer                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Repository Layer                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ CompanyRepository│  │ IncomeStatement  │  │BalanceSheet │  │
│  │                  │  │   Repository     │  │ Repository  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MySQL Database                              │
│  ┌────────────────────┐  ┌────────────────────────────────────┐ │
│  │  coreiq_companies  │  │ coreiq_av_financials_balance_sheet │ │
│  └────────────────────┘  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │     coreiq_av_financials_income_statement                  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Balance Sheet Data Flow

```
User Request (Balance Sheet Tab)
    │
    ▼
┌─────────────────────────────────────┐
│  render_balance_sheet()             │  ← app/pages/market_data.py
│  - Get date range from session      │
│  - Get sort order from session      │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  BalanceSheetRepository             │  ← app/data/repository.py
│  .get_balance_sheet_data()          │
│  - Query MySQL                      │
│  - Parse raw_json                   │
│  - Map to LINE_ITEMS                │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  MySQL                              │
│  SELECT raw_json FROM               │
│  coreiq_av_financials_balance_sheet │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Data Processing                    │
│  - Extract JSON values              │
│  - Convert to millions              │
│  - Apply sorting                    │
│  - Return BalanceSheetData          │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  HTML Generation                    │
│  - Generate table HTML              │
│  - Apply CSS classes                │
│  - Add underlines/separators        │
└─────────────────────────────────────┘
    │
    ▼
User Sees Rendered Table
```

---

## Module Details

### 1. `app/data/repository.py`

#### `BalanceSheetRepository`

**Purpose**: Fetches and parses balance sheet data from MySQL.

**Key Method**: `get_balance_sheet_data(ticker, start_date, end_date)`

**LINE_ITEMS Structure**:
```python
LINE_ITEMS = [
    # Format: ("UI Label", "JSON Key", "Section")
    
    # ASSETS - Line Items
    ("Cash & Cash Equivalents", "cashAndCashEquivalentsAtCarryingValue", "assets"),
    ("Cash & Short Term Investments", "cashAndShortTermInvestments", "assets"),
    ("Inventory", "inventory", "assets"),
    ("Current Net Receivables", "currentNetReceivables", "assets"),
    ("Other Current Assets", "otherCurrentAssets", "assets"),
    
    # ASSETS - Subtotals
    ("Total Current Assets", "totalCurrentAssets", "assets"),
    
    # ASSETS - Non-Current
    ("Property Plant & Equipment", "propertyPlantEquipment", "assets"),
    ("Intangible Assets", "intangibleAssets", "assets"),
    ("Intangible Assets Excl. Goodwill", "intangibleAssetsExcludingGoodwill", "assets"),
    ("Long Term Investments", "longTermInvestments", "assets"),
    
    # ASSETS - Totals
    ("Total Non-Current Assets", "totalNonCurrentAssets", "assets"),
    ("Total Assets", "totalAssets", "assets"),
    
    # LIABILITIES - Line Items
    ("Current Accounts Payable", "currentAccountsPayable", "liabilities"),
    ("Short Term Debt", "shortTermDebt", "liabilities"),
    ("Other Current Liabilities", "otherCurrentLiabilities", "liabilities"),
    
    # LIABILITIES - Subtotals
    ("Total Current Liabilities", "totalCurrentLiabilities", "liabilities"),
    
    # LIABILITIES - Non-Current
    ("Long Term Debt", "longTermDebt", "liabilities"),
    ("Capital Lease Obligations", "capitalLeaseObligations", "liabilities"),
    ("Other Non-Current Liabilities", "otherNonCurrentLiabilities", "liabilities"),
    
    # LIABILITIES - Totals
    ("Total Non-Current Liabilities", "totalNonCurrentLiabilities", "liabilities"),
    ("Total Liabilities", "totalLiabilities", "liabilities"),
    
    # EQUITY
    ("Common Stock", "commonStock", "equity"),
    ("Retained Earnings", "retainedEarnings", "equity"),
    ("Treasury Stock", "treasuryStock", "equity"),
    ("Total Shareholder Equity", "totalShareholderEquity", "equity"),
]
```

**Data Flow**:
1. Query MySQL for rows matching ticker and date range
2. Parse `raw_json` column for each row
3. Extract values using JSON keys from LINE_ITEMS
4. Return `BalanceSheetData` with periods and line_items

---

### 2. `app/pages/market_data.py`

#### `render_balance_sheet()`

**Purpose**: Renders the balance sheet table with proper formatting.

**Key CSS Classes Applied**:

| Class | Applied To | Purpose |
|-------|-----------|---------|
| `indent-level-0` | Line items | No indentation |
| `indent-level-1` | Subtotals | 20px left padding |
| `indent-level-2` | Totals | 40px left padding |
| `row-bold` | Totals/Subtotals | Bold text |
| `row-with-underline` | Rows before totals | Full black underline |
| `row-underline-partial` | Data cells only | Black underline on data |
| `row-grey-separator` | After major totals | 4px grey border |

**Underline Logic**:
```python
def has_balance_sheet_underline(label: str) -> bool:
    """Check if row should have underline (row BEFORE a total/subtotal)."""
    underline_before = {
        "Total Current Assets", "Total Non-Current Assets",
        "Total Current Liabilities", "Total Non-Current Liabilities",
        "Common Stock", "Retained Earnings", "Treasury Stock"
    }
    return label.strip() in underline_before
```

---

## Balance Sheet Implementation

### Visual Hierarchy

```
Cash & Cash Equivalents                    [0px indent]
Inventory                                  [0px indent]
Other Current Assets                       [0px indent]
─────────────────────────────────────────── [underline]
    Total Current Assets                   [20px indent, bold]
═══════════════════════════════════════════ [grey separator]
Property Plant & Equipment                 [0px indent]
Intangible Assets                          [0px indent]
─────────────────────────────────────────── [underline]
    Total Non-Current Assets               [20px indent, bold]
═══════════════════════════════════════════ [grey separator]
        Total Assets                       [40px indent, bold]
═══════════════════════════════════════════ [grey separator]
```

### CSS Implementation

```css
/* Indentation */
.indent-level-0 { padding-left: 0; }
.indent-level-1 { padding-left: 20px; }
.indent-level-2 { padding-left: 40px; }

/* Underlines - 90% width */
.row-with-underline td {
    border-bottom: 2px solid #000000 !important;
}
.row-underline-partial td:not(:first-child) {
    border-bottom: 2px solid #000000 !important;
}

/* Grey Separators - 4px after major totals */
.row-grey-separator td {
    border-bottom: 4px solid #DDDDDD !important;
}
```

---

## Sort Filter Implementation

### Location
`app/pages/market_data.py` (lines ~785-850)

### Session State
```python
st.session_state.sort_order = "Earliest"  # or "Latest"
```

### Implementation Logic

```python
# Get sort preference
sort_ascending = st.session_state.sort_order == "Earliest"

# Apply sorting
if not sort_ascending:
    # Reverse the periods and corresponding values
    data.periods = list(reversed(data.periods))
    for item in data.line_items:
        item.values = list(reversed(item.values))
```

### UI Components

```python
# Filter Section
f1, f2, f3, f4 = st.columns([6, 1.2, 1.2, 0.9])

with f2:
    st.html('<div class="filter-label">Start Date</div>')
    new_start_label = st.selectbox(...)

with f3:
    st.html('<div class="filter-label">End Date</div>')
    new_end_label = st.selectbox(...)

with f4:
    st.html('<div class="filter-label">Sort</div>')
    new_sort_order = st.selectbox(
        "Sort",
        options=["Earliest", "Latest"],
        ...
    )
```

---

## CSS Architecture

### Custom CSS Location
All custom CSS is embedded in `app/pages/market_data.py` within `<style>` tags.

### CSS Structure

```css
/* 1. CSS Variables */
:root {
    --primary-red: #D62E2F;
    --black: #000000;
    --dark-grey: #4F4F4F;
    --border-light: #cbcaca;
    --bg-light: #F2F2F2;
    --font-family: 'Inter', sans-serif;
    --row-height: 24px;
    --first-column-width: 400px;
    --date-column-width: 164px;
}

/* 2. Layout */
.block-container { padding: 0 40px !important; }

/* 3. Navigation Tabs */
.tabs-container {
    display: flex;
    gap: 48px;
    border-bottom: 1px solid var(--border-light);
}

/* 4. Filter Section */
.filter-label {
    font-size: 12px;
    color: #4F4F4F;
    padding-top: 12px;  /* Space from tab border */
    margin-bottom: 6px;
}

/* 5. Table Styling */
.data-table {
    border-collapse: collapse;
    width: 100%;
}
.data-table th, .data-table td {
    height: 24px;
    padding: 0 8px;
    border-bottom: 1px solid #E0E0E0;
}

/* 6. Indentation */
.indent-level-0 { padding-left: 0; }
.indent-level-1 { padding-left: 20px; }
.indent-level-2 { padding-left: 40px; }

/* 7. Visual Hierarchy */
.row-bold { font-weight: 600; }
.row-with-underline td { border-bottom: 2px solid #000 !important; }
.row-grey-separator td { border-bottom: 4px solid #DDD !important; }
```

---

## State Management

### Session State Keys

| Key | Type | Purpose | Set By |
|-----|------|---------|--------|
| `marketdata_company` | str | Selected ticker | Company dropdown |
| `marketdata_tab` | str | Current tab | Tab navigation |
| `marketdata_date_range` | tuple | (start, end) dates | Date filters |
| `sort_order` | str | "Earliest" or "Latest" | Sort dropdown |
| `marketdata_source` | str | Data source filter | Source dropdown |

### Local Storage Integration

```python
# Reading from local storage
from utils.local_storage import get_marketdata_company, get_marketdata_tab

ticker = get_marketdata_company() or "AAPL"
tab = get_marketdata_tab() or "income_statement"

# Writing to local storage
from utils.local_storage import set_marketdata_company, set_marketdata_tab

set_marketdata_company("MSFT")
set_marketdata_tab("balance_sheet")
```

---

## Testing Strategy

### Manual Testing Checklist

#### Balance Sheet
- [ ] Data loads correctly for any ticker
- [ ] All expected line items appear
- [ ] Indentation is correct (0px, 20px, 40px)
- [ ] Underlines appear before totals/subtotals
- [ ] Grey separators appear after major totals
- [ ] Values are in millions with comma separators
- [ ] Missing data shows as "-"

#### Sort Filter
- [ ] "Earliest" sorts 2006 → 2025
- [ ] "Latest" sorts 2025 → 2006
- [ ] Works on both Income Statement and Balance Sheet
- [ ] Persists across tab switches

#### Date Filters
- [ ] Start Date dropdown works
- [ ] End Date dropdown works
- [ ] Date range filters data correctly
- [ ] Error shown if start > end

#### Tab Navigation
- [ ] All tabs accessible via URL (?tab=...)
- [ ] Active tab highlighted correctly
- [ ] Tab state persists

### Test Commands

```bash
# Run application
cd app && streamlit run marketdata.py --server.port=8502

# Check database connection
mysql -u root -p secfiling -e "SELECT COUNT(*) FROM coreiq_av_financials_balance_sheet;"
```

---

## Future Enhancements

### 1. Cash Flow Statement
**Pattern**: Follow Balance Sheet implementation

**Steps**:
1. Create `CashFlowRepository` in `repository.py`
2. Define `LINE_ITEMS` for cash flow sections (Operating, Investing, Financing)
3. Add `render_cash_flow()` in `market_data.py`
4. Add tab to navigation

### 2. Automated Testing
```python
# Recommended test structure
tests/
├── __init__.py
├── test_repositories.py    # Test BalanceSheetRepository
├── test_components.py      # Test UI components
└── test_integration.py     # End-to-end tests
```

### 3. Data Export
```python
# Add to market_data.py
def export_to_csv(data):
    df = pd.DataFrame(...)
    st.download_button("Download CSV", df.to_csv(), "data.csv")
```

---

**End of Architecture Documentation**
