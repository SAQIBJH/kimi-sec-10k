# Integrations

## External Services

### Alpha Vantage
- **Purpose**: Financial market data provider
- **Data**: Stock prices, financial statements, news
- **Integration**: Data imported via SQL dumps
- **Tables**: 
  - `coreiq_av_financials_*`
  - `coreiq_av_market_news_sentiment`
  - `coreiq_av_company_overview`
  - `coreiq_av_earnings_call_transcripts`

### MySQL Database
- **Host**: Configurable via `DB_HOST` env var (default: localhost)
- **Port**: 3306
- **Database**: `secfiling`
- **Connection Pooling**: SQLAlchemy QueuePool
- **Pool Size**: 5 (configurable)
- **Max Overflow**: 10 (configurable)

### Currency Conversion
- **Library**: `forex-python`
- **Purpose**: Convert financial data between currencies
- **Usage**: Optional, can be disabled

## Internal Integrations

### MCP Servers (via Kimi Code)
- **Figma**: Design context and wireframe extraction
- **GitHub**: Repository management
- **Context7**: Library documentation
- **Playwright**: Browser automation

### GSD System
- **Location**: `.claude/get-shit-done/`
- **Commands**: `/gsd:*` pattern
- **Purpose**: Spec-driven development workflow

## Data Sources

| Source | Type | Tables | Update Frequency |
|--------|------|--------|------------------|
| Alpha Vantage | Financial API | coreiq_av_* | Manual import |
| SEC EDGAR | Filings | Referenced | Manual import |
| YFinance | Market data | coreiq_companies | Manual import |

## API Patterns

### RESTful API Calls
Currently no external API calls at runtime. All data is:
1. Pre-fetched via Alpha Vantage API
2. Stored in MySQL database
3. Queried by the application

### Database Query Pattern
```python
# Parameterized queries only
query = """
    SELECT * FROM table 
    WHERE ticker = :ticker 
    AND date BETWEEN :start AND :end
"""
results = db_manager.execute_query(query, {
    "ticker": ticker,
    "start": start_date,
    "end": end_date
})
```

## Security Considerations

### Database
- SSL support via `cryptography` library
- Connection string uses environment variables
- Password not logged or exposed

### Environment Variables
```bash
# Required
DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# Optional
SECRET_KEY, DEBUG, APP_ENV
```

### No External API Keys at Runtime
- All Alpha Vantage data pre-imported
- No API keys needed in application code
