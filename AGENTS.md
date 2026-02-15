# Research Portal - AI Agent Guide

## Project Overview

The Research Portal is a production-level **Streamlit application** for market research and financial news analysis, developed for **Coresight Research**. It provides real-time financial data visualization, SEC filing access, and curated financial news from a MySQL database.

### Key Features
- **Market Data**: Income statement views, financial metrics, and historical data with company selection
- **Newsroom**: Curated financial news with filtering, categorization, and relative time display
- **State Management**: Persistent user preferences using browser local storage
- **Responsive Design**: Professional UI matching Figma specifications with Coresight branding
- **Database Ready**: MySQL integration with SQLAlchemy ORM and connection pooling

---

## Technology Stack

| Layer | Technology | Version |
|-------|------------|---------|
| **Framework** | Streamlit | >= 1.54.0 |
| **Language** | Python | >= 3.13 |
| **Database** | MySQL | 8.0+ (via SQLAlchemy 2.0+ and PyMySQL) |
| **Visualization** | Plotly | >= 6.5.0 |
| **Data Processing** | Pandas | >= 2.3.0 |
| **Data Processing** | NumPy | >= 2.4.0 |
| **Environment** | python-dotenv | >= 1.2.0 |
| **Security** | cryptography | >= 46.0.0 (for MySQL SSL) |

---

## Project Structure

```
app/
├── main.py                 # Unified entry point - single port for all pages
├── core/                   # Configuration and database layer
│   ├── config.py          # Environment-based configuration
│   └── database.py        # MySQL connector with SQLAlchemy connection pooling
├── components/            # Reusable UI components
│   ├── styles.py         # Design tokens, CSS, and layout utilities
│   ├── layout.py         # Layout primitives
│   ├── charts.py         # Plotly chart components
│   ├── tables.py         # Data table components
│   ├── navigation.py     # Header, footer, and navigation
│   └── toolbar.py        # Tab toolbar for Market Data
├── data/                 # Data layer
│   ├── models.py         # Data models
│   ├── dummy_data.py     # Sample data
│   └── repository.py     # SQLAlchemy repositories
├── pages/                # Page implementations
│   ├── home.py          # Homepage
│   ├── market_data.py   # Market Data with tabs
│   ├── company_profile.py
│   ├── newsroom.py
│   └── earnings_calls.py
└── utils/               # Utilities
    └── local_storage.py # Local storage state management
```

---

## Configuration

### Environment Variables (.env)

```bash
# Application Environment
APP_ENV=local                    # Options: local, staging, production
DEBUG=true

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=secfiling
DB_USER=root
DB_PASSWORD=admin
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Application Settings
SECRET_KEY=your-secret-key-change-in-production
SESSION_TIMEOUT=3600
ENABLE_CACHING=true
CACHE_TTL=300
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### Configuration Architecture

The `app/core/config.py` module uses:
- **Environment Enum**: LOCAL, STAGING, PRODUCTION
- **DatabaseConfig dataclass**: MySQL connection string generation with pooling options
- **AppConfig dataclass**: Global configuration with feature flags and pagination defaults
- **load_config() function**: Loads from environment with sensible defaults

---

## Running the Application

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### Running the Application

All pages now run from a single entry point on port 8502:

```bash
cd app && streamlit run main.py
```

### URL Routing

The application uses query parameter-based routing:

| Page | URL |
|------|-----|
| Homepage | `http://localhost:8502/` |
| Market Data | `http://localhost:8502/?page=market_data&tab=income_statement` |
| Company Profile | `http://localhost:8502/?page=company_profile&ticker=M` |
| Company Documents | `http://localhost:8502/?page=company_filings` |
| Newsroom | `http://localhost:8502/?page=newsroom` |
| Earnings Calls | `http://localhost:8502/?page=earnings_calls` |

Market Data tabs:
- `tab=income_statement`
- `tab=balance_sheet`
- `tab=cash_flow`
- `tab=key_stats`
- `tab=company_profile`

### VS Code Debugging

Pre-configured launch profiles in `.vscode/launch.json`:
- `Python Debugger: marketdata.py` - Debug the market data module
- `Streamlit: Market Data` - Run Market Data page with auto-reload
- `Streamlit: Newsroom` - Run Newsroom page
- `Python Debugger: Current File` - Debug any file

---

## Database Schema

### coreiq_companies Table
Stores company information from SEC and YFinance sources.

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| ticker | VARCHAR | Stock ticker symbol |
| name | VARCHAR | Company legal name |
| cik | VARCHAR | SEC CIK number |
| name_coresight | VARCHAR | Display name for Coresight |
| primary_industry_coresight | VARCHAR | Industry classification |
| exchange | VARCHAR | Stock exchange |
| country_of_incorporation | VARCHAR | Country |
| source | VARCHAR | Data source (SEC, YFinance) |

### coreiq_av_financials_income_statement Table
Stores annual income statement data from Alpha Vantage.

| Column | Type | Description |
|--------|------|-------------|
| ticker | VARCHAR | Stock ticker |
| fiscal_date_ending | DATE | Fiscal period end date |
| report_type | VARCHAR | annual/quarterly |
| total_revenue | DECIMAL | Total revenue |
| cost_of_revenue | DECIMAL | COGS |
| gross_profit | DECIMAL | Gross profit |
| operating_income | DECIMAL | Operating income |
| net_income | DECIMAL | Net income |
| selling_general_and_administrative | DECIMAL | SG&A expenses |
| research_and_development | DECIMAL | R&D expenses |
| depreciation_and_amortization | DECIMAL | D&A expenses |
| interest_expense | DECIMAL | Interest expense |
| interest_income | DECIMAL | Interest income |
| ... | ... | Additional financial fields |

### coreiq_av_financials_balance_sheet Table
Stores balance sheet data from Alpha Vantage (using raw_json for flexibility).

| Column | Type | Description |
|--------|------|-------------|
| ticker | VARCHAR | Stock ticker |
| fiscal_date_ending | DATE | Fiscal period end date |
| report_type | VARCHAR | annual/quarterly |
| raw_json | JSON | All balance sheet fields as JSON |
| reported_currency | VARCHAR | Currency code (USD, etc.) |

**JSON Structure**: The `raw_json` column contains camelCase keys like:
- `cashAndCashEquivalentsAtCarryingValue`
- `totalCurrentAssets`
- `totalAssets`
- `currentAccountsPayable`
- `totalLiabilities`
- `commonStock`
- `retainedEarnings`
- `totalShareholderEquity`

---

## Code Organization Patterns

### 1. Repository Pattern

Data access is abstracted through repository classes:

```python
# app/data/repository.py
class CompanyRepository:
    @staticmethod
    def get_all_sources() -> List[str]: ...
    
    @staticmethod
    def get_companies_by_source() -> List[Company]: ...

class IncomeStatementRepository:
    @staticmethod
    def get_income_statement_data(ticker: str, start_date: date, end_date: date) -> IncomeStatementData: ...

class BalanceSheetRepository:
    LINE_ITEMS = [...]  # Maps UI labels to JSON keys
    
    @staticmethod
    def get_balance_sheet_data(ticker: str, start_date: date, end_date: date) -> BalanceSheetData: ...
```

### 2. Component Architecture

UI components follow a hierarchical structure:

```python
# High-level navigation components (app/components/navigation.py)
- render_header(full_width=True)          # Coresight branded header
- render_coresight_footer(...)            # Full footer with widgets

# Layout components (app/components/layout.py)
- render_card(content, title, ...)
- render_metric_card(label, value, change, ...)
- render_badge(text, variant)

# Chart components (app/components/charts.py)
- create_candlestick_chart(metrics, ...)
- create_line_chart(data, x_column, y_columns, ...)
- render_chart(fig, ...)
```

### 3. State Management

Local storage utilities provide persistence:

```python
# app/utils/local_storage.py
local_storage = LocalStorageManager()

# Get/Set operations
local_storage.get(StorageKey.SEC_FILING, default=None)
local_storage.set(StorageKey.SEC_FILING, value)

# Convenience functions for Market Data
get_marketdata_source() -> Optional[str]
set_marketdata_source(source: str) -> bool
get_marketdata_company() -> Optional[str]
set_marketdata_company(ticker: str) -> bool
get_marketdata_tab() -> Optional[str]
set_marketdata_tab(tab: str) -> bool
get_marketdata_date_range() -> tuple[Optional[str], Optional[str]]
set_marketdata_date_range(start: str, end: str) -> bool
```

---

## Design System

### Design Tokens (app/components/styles.py)

```python
# Color Palette
COLORS = {
    "primary": "#0066CC",
    "primary_hover": "#0052A3",
    "success": "#28A745",
    "danger": "#DC3545",
    "warning": "#FFC107",
    # ... grayscale palette
}

# Typography (Inter font family)
TYPOGRAPHY = {
    "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "text_xs": "0.75rem",      # 12px
    "text_sm": "0.875rem",     # 14px
    "text_base": "1rem",       # 16px
    "text_2xl": "1.5rem",      # 24px
    # ... font weights and line heights
}

# Spacing (8px base grid)
SPACING = {
    "space_1": "0.25rem",   # 4px
    "space_2": "0.5rem",    # 8px
    "space_4": "1rem",      # 16px
    # ...
}
```

### Coresight Brand Colors

The UI uses Coresight Research brand colors:
- **Primary Red**: `#d62e2f` - Logo, active nav, contact button
- **Dark Text**: `#323232` - Body text
- **Border Gray**: `#cbcaca` - Header/footer borders

---

## Page Development Guidelines

### Adding a New Page

1. Create a new file in `app/pages/`
2. Implement a `render_page()` function for the content
3. Create an entry point file (similar to `app/marketdata.py`)
4. Add to `Page` enum in `components/navigation.py` if using internal navigation

### Adding a New Page to main.py

To add a new page to the unified navigation:

```python
# In app/main.py, add a new elif clause:

elif page == "your_page":
    from pages.your_page import render_page as render_your_page
    render_styles()
    set_page_layout(
        header_full_width=True,
        footer_full_width=True,
        body_padding="0 20px",
        max_content_width="1350px",
    )
    render_header(full_width=True)
    render_your_page()
    render_coresight_footer(full_width=True, stick_to_bottom=True)
```

### Page Implementation Template

Create a new file in `app/pages/your_page.py`:

```python
"""Your page module."""
import streamlit as st

def render_page():
    """Render the page content."""
    # Your page implementation here
    st.title("Your Page")
```

---

## Key Implementation Details

### Database Connection

The `DatabaseManager` class in `app/core/database.py` uses:
- **Singleton pattern**: Single connection pool across the application
- **Thread-local storage**: Session isolation per thread
- **Context managers**: Automatic transaction handling with commit/rollback
- **Connection pooling**: SQLAlchemy QueuePool with configurable size

```python
# Usage pattern
db_manager = DatabaseManager()
db_manager.connect()  # Initialize pool

with db_manager.get_session() as session:
    result = session.execute(query)
    
# Or use decorator
@with_db_session
def my_function(session: Session, ...):
    ...
```

### Income Statement Table Rendering

The Market Data page renders custom HTML tables:
- Custom CSS in `render_income_statement_table()` 
- Subtotal rows get bold styling + light background
- Section-start rows have heavier top border
- Values formatted in millions with comma separators

---

## Build and Test Commands

### Manual Testing

```bash
# Test Market Data page
cd app && streamlit run marketdata.py

# Test Newsroom page
cd app && streamlit run pages/newsroom.py
```

### Database Import

```bash
# Import company data
mysql -u root -p secfiling < coreiq_companies_202602110336.sql

# Import financial data
mysql -u root -p secfiling < coreiq_av_financials_income_statement_202602110149.sql
mysql -u root -p secfiling < coreiq_av_financials_balance_sheet_202602110149.sql
mysql -u root -p secfiling < coreiq_av_financials_cash_flow_202602110149.sql

# Import news data
mysql -u root -p secfiling < coreiq_av_market_news_sentiment_202602110147.sql
```

---

## Code Style Guidelines

### Python Style

- **Type hints**: Use type hints for function signatures and return types
- **Docstrings**: Use Google-style docstrings for all public functions
- **Dataclasses**: Use `@dataclass` for data models
- **Static methods**: Repository methods should be `@staticmethod`

### File Organization

```python
"""
Module docstring describing purpose.
"""
# 1. Standard library imports
import os
from typing import List, Optional

# 2. Third-party imports
import streamlit as st
import pandas as pd

# 3. Local imports
from components.styles import COLORS
from data.models import Company
```

### Naming Conventions

- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private**: `_leading_underscore`

---

## Testing Strategy

Currently, the project does not have automated tests. Recommended approach:

```bash
# Manual testing via Streamlit
cd app && streamlit run marketdata.py

# Add pytest for unit tests
pip install pytest pytest-asyncio

# Test structure (recommended)
tests/
├── __init__.py
├── test_models.py
├── test_repositories.py
└── test_components.py
```

---

## Security Considerations

1. **Environment Variables**: All secrets stored in `.env` (not committed)
2. **SQL Injection**: Repository layer uses parameterized queries with SQLAlchemy `text()`
3. **Secret Key**: Used for session management (change in production)
4. **Debug Mode**: Disabled automatically in production environment

---

## Deployment Notes

### Production Checklist

1. Set `APP_ENV=production` and `DEBUG=false`
2. Change `SECRET_KEY` to a secure random value
3. Configure production database credentials
4. Verify database connection pooling settings
5. Ensure all SQL files are imported to MySQL

---

## Current Implementation Status

### Completed Features

| Feature | Status | Location | Notes |
|---------|--------|----------|-------|
| Unified Navigation | ✅ Complete | `app/main.py` | Single port 8502 for all pages |
| Homepage | ✅ Complete | `app/pages/home.py` | Company/sector selection cards |
| Market Data | ✅ Complete | `app/pages/market_data.py` | All tabs working with URL routing |
| Balance Sheet | ✅ Complete | `app/data/repository.py` | Raw JSON parsing with visual hierarchy |
| Income Statement | ✅ Complete | `app/pages/market_data.py` | Full implementation |
| Company Profile | ✅ Complete | `app/pages/company_profile.py` | Company overview page |
| Company Documents | ✅ Complete | `app/pages/company_filings.py` | SEC filing documents with metric search |
| Newsroom | ✅ Complete | `app/pages/newsroom.py` | Financial news with filtering |
| Earnings Calls | ✅ Complete | `app/pages/earnings_calls.py` | Earnings calls page |
| Tab Navigation | ✅ Complete | `app/components/toolbar.py` | Red underline active tab indicator |
| Sort Filter | ✅ Complete | `app/pages/market_data.py` | Earliest/Latest dropdown |
| Date Filters | ✅ Complete | `app/pages/market_data.py` | Start Date, End Date dropdowns |

### Pending Features

| Feature | Status | Priority | Notes |
|---------|--------|----------|-------|
| Company Documents | 🔴 Pending | Medium | Document search page not built yet |
| Sector Selection | 🔴 Pending | Low | "Coming Soon" popup needed |
| Company Persistence | 🔴 Pending | Medium | localStorage for selected company |

### Unified Navigation Details

**Entry Point**: `app/main.py`

All pages now run from a single entry point with URL-based routing:

```python
# URL Routing in main.py
page = st.query_params.get("page", "home")

if page == "home":
    from pages.home import main as render_home
    render_home()
elif page == "market_data":
    from pages.market_data import render_page
    tab = st.query_params.get("tab", "income_statement")
    # ...
elif page == "company_profile":
    ticker = st.query_params.get("ticker", "M")
    render_company_profile(ticker)
```

**Header Navigation** (`app/components/navigation.py`):
- Market Data Dashboard → `/?page=market_data`
- Earnings Calls → `/?page=earnings_calls`
- News → `/?page=newsroom`

**Market Data Toolbar** (`app/components/toolbar.py`):
- Company Profile → `/?page=company_profile`
- Key Stats → `/?page=market_data&tab=key_stats`
- Income Statement → `/?page=market_data&tab=income_statement`
- Balance Sheet → `/?page=market_data&tab=balance_sheet`
- Cash Flow → `/?page=market_data&tab=cash_flow`

All links use `target="_self"` to ensure same-tab navigation.

### Balance Sheet Implementation Details

**Files**:
- `app/data/repository.py` - `BalanceSheetRepository` class
- `app/pages/market_data.py` - `render_balance_sheet()` function

**Key Features**:
1. **Data Source**: Uses `raw_json` column from MySQL table `coreiq_av_financials_balance_sheet`
2. **JSON Parsing**: Maps camelCase JSON keys to UI labels
3. **Visual Hierarchy**:
   - Line items: 0px indent
   - Subtotals: 20px indent
   - Totals: 40px indent
4. **Underlines**: Black 90% width underline on row BEFORE each total/subtotal
5. **Separators**: 4px grey border after major totals

---

## Agent Handoff Guide

### If You Are a New Agent Taking Over

**STEP 1: Read Documentation**
1. Read `STATUS.md` - Current project status and what's been implemented
2. Read `AGENTS.md` - This file for architecture details
3. Read `README.md` - High-level project overview

**STEP 2: Check Database Connection**
```bash
# Verify MySQL is running
mysql -u root -p -e "SHOW DATABASES;"

# Check tables exist
mysql -u root -p chainxydata_stg -e "SHOW TABLES;"
```

**STEP 3: Run the Application**
```bash
cd /Users/mohdsaeedafri/Documents/Documents/Code-Base/kimi-sec-10k-1/app
streamlit run main.py
```

Access pages via:
- Homepage: `http://localhost:8502/`
- Market Data: `http://localhost:8502/?page=market_data&tab=income_statement`
- Company Profile: `http://localhost:8502/?page=company_profile&ticker=M`
- Newsroom: `http://localhost:8502/?page=newsroom`
- Earnings Calls: `http://localhost:8502/?page=earnings_calls`

**STEP 4: Test Current Features**
1. Navigate through all pages via header
2. Test Market Data tab navigation (red underlines)
3. Verify Company Profile loads from homepage
4. Check database connectivity on all pages

**STEP 5: Continue Development**
- Next priorities in `STATUS.md`
- Common patterns documented in this file

### Token Expiration Plan

If your tokens expire mid-task:

1. **Current Status Is Documented**:
   - `STATUS.md` always reflects the latest state
   - `AGENTS.md` contains architecture details
   - Git commits preserve code changes

2. **Resume Workflow**:
   ```bash
   # New agent should:
   git status                    # Check what files were modified
   git diff                      # Review changes
   cat STATUS.md                 # Read current status
   cat AGENTS.md | grep -A 20 "Agent Handoff"  # Read handoff guide
   ```

3. **Key Files to Check**:
   - `app/main.py` - Unified entry point
   - `app/pages/*.py` - Page implementations
   - `app/components/*.py` - Shared components
   - `app/data/repository.py` - Data access layer
   - `STATUS.md` - Current implementation status

---

## Common Tasks

### Adjusting Page Layout

Modify `set_page_layout()` call in the entry point:

```python
set_page_layout(
    body_padding="0 20px",      # "top_bottom left_right"
    max_content_width="1350px",  # Max content width
)
```

### Adding a New Chart Type

1. Add function to `app/components/charts.py`
2. Return a Plotly `go.Figure` object
3. Use `CHART_LAYOUT` for consistent styling
4. Use design tokens from `COLORS` and `TYPOGRAPHY`

### Adding New Database Tables

1. Define dataclass in `app/data/models.py`
2. Create repository class in `app/data/repository.py`
3. Add SQL queries using parameterized statements
4. Update entry points to call `init_database()`

---

## License

Proprietary - Market Intelligence Platform (Coresight Research)
