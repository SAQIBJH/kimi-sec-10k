# Architecture Overview

## System Design
The Research Portal is a **Streamlit-based single-page application (SPA)** with multiple entry points for different views. It follows a layered architecture with clear separation of concerns.

## Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Entry Points                             │
│  (marketdata.py, companyfilings.py, earningscalls.py, ...) │
├─────────────────────────────────────────────────────────────┤
│                    Page Layer                               │
│         (pages/market_data.py, pages/newsroom.py)          │
├─────────────────────────────────────────────────────────────┤
│                  Component Layer                            │
│    (components/charts.py, tables.py, layout.py, ...)       │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                               │
│      (data/models.py, data/repository.py, dummy_data.py)   │
├─────────────────────────────────────────────────────────────┤
│                   Core Infrastructure                       │
│         (core/config.py, core/database.py)                 │
├─────────────────────────────────────────────────────────────┤
│                   Utilities                                 │
│              (utils/local_storage.py)                      │
└─────────────────────────────────────────────────────────────┘
```

## Key Patterns

### 1. Repository Pattern
- **CompanyRepository** - Company data access
- **IncomeStatementRepository** - Income statement financials
- **NewsRepository** - News articles and sentiment
- **CompanyOverviewRepository** - Company profile data
- **EarningsCallRepository** - Earnings call transcripts

### 2. Component-Based UI
Reusable UI components in `app/components/`:
- `styles.py` - Design tokens and CSS
- `layout.py` - Layout primitives (cards, badges)
- `charts.py` - Plotly chart components
- `tables.py` - Data table components
- `navigation.py` - Header, footer, navigation
- `toolbar.py` - Toolbar components

### 3. Dataclass Models
Pydantic-style dataclasses in `data/models.py`:
- `Company` - Company information
- `IncomeStatementData` - Financial data container
- `NewsArticle` - News article with sentiment
- `CompanyOverview` - Extended company data
- `EarningsCall` - Earnings call transcripts

### 4. State Management
- **Session State** - Streamlit's built-in session state
- **Local Storage** - Browser localStorage via `utils/local_storage.py`
- **Persistent Preferences** - User selections saved across sessions

### 5. Configuration Management
- **Environment-based** - `.env` file support
- **Dataclass-based** - Type-safe configuration in `core/config.py`
- **Feature Flags** - Enable/disable features via config

## Data Flow

```
User Input → Page Handler → Repository → Database
                                               ↓
User View ← Component ← Data Model ← Repository
```

## Database Schema

### Core Tables
1. **coreiq_companies** - Company master data
2. **coreiq_av_financials_income_statement** - Income statements
3. **coreiq_av_financials_balance_sheet** - Balance sheets
4. **coreiq_av_financials_cash_flow** - Cash flow statements
5. **coreiq_av_market_news_sentiment** - News with sentiment
6. **coreiq_av_company_overview** - Company profiles
7. **coreiq_av_earnings_call_transcripts** - Earnings transcripts

## Module Dependencies

```
marketdata.py → pages/market_data.py → components/* → data/repository.py → core/database.py
                                            ↓
                                     data/models.py
```
