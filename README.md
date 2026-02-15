# Research Portal v3.0

A production-level Streamlit application for market research and financial news analysis.

## Features

- **Market Data Dashboard**: Income Statement, Balance Sheet, Cash Flow with tab navigation
- **Company Profile**: Company information with visual data tables
- **Newsroom**: Curated financial news with filtering
- **Earnings Calls**: Transcript viewing with speaker sections
- **Unified Navigation**: Single entry point, all pages on one port
- **State Management**: Persistent user preferences using local storage
- **Responsive Design**: Professional UI matching Figma specifications
- **Database**: MySQL integration with SQLAlchemy ORM

## Architecture

```
app/
├── main.py              # Unified entry point (single port)
├── core/                # Configuration and database layer
│   ├── config.py       # Environment-based configuration
│   └── database.py     # MySQL connector with connection pooling
├── components/          # Reusable UI components
│   ├── styles.py       # Design tokens and CSS
│   ├── layout.py       # Layout primitives
│   ├── charts.py       # Chart components
│   ├── tables.py       # Data table components
│   ├── navigation.py   # Navigation components
│   └── toolbar.py      # Tab toolbar for Market Data
├── data/               # Data layer
│   ├── models.py       # Data models
│   ├── repository.py   # Repository pattern with SQLAlchemy
│   └── dummy_data.py   # Sample data
├── pages/              # Page implementations
│   ├── home.py         # Homepage
│   ├── market_data.py  # Market Data with tabs
│   ├── company_profile.py
│   ├── newsroom.py
│   └── earnings_calls.py
└── utils/              # Utilities
    └── local_storage.py # Local storage state management
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database settings
```

### 3. Run the Application

```bash
cd app
streamlit run main.py
```

Access at: **http://localhost:8502**

## URL Routes

| Page | URL |
|------|-----|
| Homepage | `http://localhost:8502/` |
| Market Data | `http://localhost:8502/?page=market_data` |
| Company Profile | `http://localhost:8502/?page=company_profile&ticker=M` |
| Newsroom | `http://localhost:8502/?page=newsroom` |
| Earnings Calls | `http://localhost:8502/?page=earnings_calls` |

## Market Data Tabs

| Tab | URL Parameter |
|-----|---------------|
| Income Statement | `?page=market_data&tab=income_statement` |
| Balance Sheet | `?page=market_data&tab=balance_sheet` |
| Cash Flow | `?page=market_data&tab=cash_flow` |
| Key Stats | `?page=market_data&tab=key_stats` |
| Company Profile | `?page=market_data&tab=company_profile` |

## Design System

The application uses Coresight Research brand colors and design tokens:

- **Primary Red**: `#D62E2F`
- **Dark Text**: `#323232`
- **Border Gray**: `#CBCACA`
- **Background**: `#F2F2F2`

## State Management

User selections are persisted across sessions:

- Selected company ticker
- Date ranges
- Tab selections
- Filter preferences

## Development

### Adding a New Page

1. Create a new file in `app/pages/`
2. Implement a `render_page()` function
3. Add route in `main.py`
4. Update navigation in `components/navigation.py`

### Navigation Mode

By default, all links open in the same tab. To change this behavior, modify the `target` attribute in:
- `components/navigation.py` (header links)
- `components/toolbar.py` (tab links)

## License

Proprietary - Coresight Research
