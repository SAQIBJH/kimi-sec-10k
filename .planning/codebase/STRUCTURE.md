# Project Structure

## Directory Tree

```
kimi-sec-10k-1/
├── app/                           # Main application code
│   ├── core/                      # Core infrastructure
│   │   ├── __init__.py
│   │   ├── config.py              # Environment configuration
│   │   └── database.py            # MySQL connection pooling
│   ├── components/                # Reusable UI components
│   │   ├── __init__.py
│   │   ├── charts.py              # Plotly chart components
│   │   ├── layout.py              # Layout primitives
│   │   ├── navigation.py          # Header, footer, nav
│   │   ├── styles.py              # Design tokens & CSS
│   │   ├── tables.py              # Data table components
│   │   └── toolbar.py             # Toolbar components
│   ├── data/                      # Data layer
│   │   ├── __init__.py
│   │   ├── dummy_data.py          # News repository with dummy data
│   │   ├── models.py              # Dataclass models
│   │   └── repository.py          # SQLAlchemy repositories
│   ├── pages/                     # Page implementations
│   │   ├── __init__.py
│   │   ├── company_filings.py     # SEC filings page
│   │   ├── company_profile.py     # Company profile page
│   │   ├── earnings_calls.py      # Earnings calls page
│   │   ├── home.py                # Home page
│   │   ├── market_data.py         # Market data page
│   │   ├── newsroom.py            # Newsroom page
│   │   └── sec_filing.py          # Individual SEC filing view
│   ├── utils/                     # Utilities
│   │   ├── __init__.py
│   │   └── local_storage.py       # Browser localStorage sync
│   ├── __init__.py
│   ├── companyfilings.py          # Company Filings entry point
│   ├── earningscalls.py           # Earnings Calls entry point
│   ├── homepage.py                # Home page entry point
│   ├── marketdata.py              # Market Data entry point
│   └── sec_filing.py              # SEC Filing entry point
├── sql/                           # SQL dump files
│   ├── coreiq_av_financials_balance_sheet_*.sql
│   ├── coreiq_av_financials_cash_flow_*.sql
│   ├── coreiq_av_financials_income_statement_*.sql
│   ├── coreiq_av_market_news_sentiment_*.sql
│   └── coreiq_companies_*.sql
├── wireframes/                    # Figma wireframes/designs
├── docs/                          # Documentation
├── .claude/                       # GSD configuration
│   └── get-shit-done/            # GSD system files
├── .planning/                     # GSD planning documents
│   └── codebase/                  # Codebase analysis
├── .env                           # Environment variables
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── AGENTS.md                      # Project guidelines for agents
├── README.md                      # Project documentation
└── requirements.txt               # Python dependencies
```

## Key Files

| File | Purpose |
|------|---------|
| `app/marketdata.py` | Market Data page entry point |
| `app/companyfilings.py` | Company Filings entry point |
| `app/earningscalls.py` | Earnings Calls entry point |
| `app/homepage.py` | Home page entry point |
| `app/pages/market_data.py` | Market Data implementation |
| `app/pages/newsroom.py` | Newsroom implementation |
| `app/data/repository.py` | All data access patterns |
| `app/data/models.py` | Data models (dataclasses) |
| `app/core/database.py` | Database connection management |
| `app/components/styles.py` | Design system tokens |
| `AGENTS.md` | Coding guidelines and conventions |

## Entry Points

Each entry point follows the same pattern:
1. `st.set_page_config()`
2. Hide sidebar
3. Initialize local storage & database
4. Render styles
5. Set page layout
6. Render header
7. Render page content
8. Render footer

## SQL Schema Files

| File | Size | Content |
|------|------|---------|
| coreiq_companies_*.sql | ~17KB | Company master data |
| coreiq_av_financials_income_statement_*.sql | ~7.9MB | Income statements |
| coreiq_av_financials_balance_sheet_*.sql | ~12MB | Balance sheets |
| coreiq_av_financials_cash_flow_*.sql | ~9.7MB | Cash flow statements |
| coreiq_av_market_news_sentiment_*.sql | ~6.2MB | News & sentiment |

## Assets

- **wireframes/**: Figma design files for UI reference
- **docs/**: Additional documentation
