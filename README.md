# Research Portal

A production-level Streamlit application for market research and financial news.

## Features

- **Market Data**: Real-time price charts, financial metrics, and historical data
- **Newsroom**: Curated financial news with filtering and categorization
- **State Management**: Persistent user preferences using local storage
- **Responsive Design**: Professional UI matching Figma specifications
- **Database Ready**: Architecture prepared for MySQL integration (Phase 2)

## Architecture

```
app/
├── core/               # Configuration and database layer
│   ├── config.py      # Environment-based configuration
│   └── database.py    # MySQL connector (Phase 2 ready)
├── components/         # Reusable UI components
│   ├── styles.py      # Design tokens and CSS
│   ├── layout.py      # Layout primitives
│   ├── charts.py      # Chart components
│   ├── tables.py      # Data table components
│   └── navigation.py  # Navigation components
├── data/              # Data layer
│   ├── models.py      # Pydantic-style data models
│   └── dummy_data.py  # Dummy data and repositories
├── pages/             # Page implementations
│   ├── market_data.py # Market Data page
│   └── newsroom.py    # Newsroom page
├── utils/             # Utilities
│   └── local_storage.py # Local storage state management
└── main.py            # Application entry point
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run the Application

```bash
cd app
streamlit run main.py
```

## Phase 2: Database Integration

To connect to a MySQL database:

1. Uncomment database dependencies in `requirements.txt`
2. Configure database credentials in `.env`
3. Uncomment the SQLAlchemy implementation in `core/database.py`
4. The repository pattern in `data/dummy_data.py` will automatically use the database

## Design System

The application uses a consistent design system defined in `components/styles.py`:

- **Colors**: Professional color palette with semantic variants
- **Typography**: Inter font family with consistent sizing
- **Spacing**: 8px base grid system
- **Components**: Cards, badges, metrics, and form elements

## State Management

User selections are persisted across sessions using local storage:

- Selected SEC filing/ticker
- Date range (start and end dates)
- Filter preferences

See `utils/local_storage.py` for the implementation.

## Development

### Adding a New Page

1. Create a new file in `app/pages/`
2. Implement a `render_page()` function
3. Add the page to `Page` enum in `components/navigation.py`
4. Update `main.py` to route to the new page

### Adding a New Component

1. Create reusable components in `app/components/`
2. Use design tokens from `styles.py`
3. Document component props and usage

## License

Proprietary - Market Intelligence Platfor
