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
├── core/                    # Configuration and database layer
│   ├── config.py           # Environment-based configuration (dataclass-based)
│   └── database.py         # MySQL connector with SQLAlchemy connection pooling
├── components/             # Reusable UI components
│   ├── styles.py          # Design tokens, CSS, and layout utilities
│   ├── layout.py          # Layout primitives (cards, badges, etc.)
│   ├── charts.py          # Plotly chart components
│   ├── tables.py          # Data table components with formatting
│   └── navigation.py      # Header, footer, and navigation components
├── data/                   # Data layer
│   ├── models.py          # Pydantic-style dataclasses for Market Data
│   ├── dummy_data.py      # News repository with dummy data and repositories
│   └── repository.py      # SQLAlchemy repositories for companies and income statements
├── pages/                  # Page implementations
│   ├── market_data.py     # Income Statement view implementation
│   └── newsroom.py        # Newsroom page (standalone entry point)
├── utils/                  # Utilities
│   └── local_storage.py   # Local storage state management with session state sync
├── marketdata.py          # Market Data entry point (standalone page)
└── __init__.py

.vscode/                   # VS Code configuration
└── launch.json           # Debug configurations for Streamlit

SQL Files (MySQL dump files):
├── coreiq_av_financials_balance_sheet_*.sql
├── coreiq_av_financials_cash_flow_*.sql
├── coreiq_av_financials_income_statement_*.sql
├── coreiq_av_market_news_sentiment_*.sql
└── coreiq_companies_*.sql
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

### Running Pages

```bash
# Market Data page (standalone)
cd app
streamlit run marketdata.py

# Newsroom page (standalone)
cd app
streamlit run pages/newsroom.py
```

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

### Page Entry Point Template

```python
import streamlit as st

# MUST be first Streamlit command
st.set_page_config(
    page_title="Page Title",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Immediately hide sidebar
from components.styles import hide_sidebar, set_page_layout
hide_sidebar()

# Initialize
from utils.local_storage import init_local_storage
from core.database import init_database
init_local_storage()
init_database()

# Render styles
from components.styles import render_styles
render_styles()

# Set layout
set_page_layout(
    header_full_width=True,
    footer_full_width=True,
    body_padding="0 20px",
    max_content_width="1350px",
)

# Render shared header
from components.navigation import render_header, render_coresight_footer
render_header(full_width=True)

# Render page content
from pages.your_page import render_page
render_page()

# Render footer
render_coresight_footer(full_width=True, stick_to_bottom=True)
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
