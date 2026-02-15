# Project: Coresight Research Portal

## Vision
A professional-grade market research and financial analysis platform for Coresight Research analysts. The portal provides real-time access to SEC filings, financial statements, market news sentiment, and earnings call transcripts — all unified in a cohesive, branded interface matching Coresight's corporate identity.

## Goals

### Primary Goals
1. **Centralized Financial Data**: Single interface for income statements, balance sheets, cash flows
2. **News Intelligence**: Curated financial news with sentiment analysis and sector filtering
3. **SEC Filing Access**: Direct access to company SEC filings
4. **Earnings Call Transcripts**: Searchable, speaker-parsed earnings call data
5. **Professional UI**: Match Coresight brand (colors, typography, layout)

### Secondary Goals
1. **State Persistence**: User preferences saved across sessions
2. **Responsive Design**: Works on desktop and tablet
3. **Fast Performance**: Sub-second page loads, efficient data queries
4. **Extensible Architecture**: Easy to add new data sources/views

## Constraints

### Technical Constraints
- **Framework**: Streamlit (chosen for rapid development)
- **Database**: MySQL 8.0+ (existing infrastructure)
- **Data Source**: Alpha Vantage (pre-imported, no live API)
- **Deployment**: Internal use initially

### Design Constraints
- **Brand Colors**: Must use Coresight palette (#d62e2f primary red)
- **Typography**: Inter font family
- **Layout**: Match provided Figma wireframes
- **Max Width**: 1350px content area

### Business Constraints
- **Users**: Coresight Research analysts (internal)
- **Data Lag**: Alpha Vantage data is daily, not real-time
- **Coverage**: S&P 500 and major retailers only

## Context

### Current State
- Streamlit application with 6 entry points
- MySQL database with 5 core tables (~35MB data)
- Income Statement view fully implemented
- Newsroom with filtering implemented
- Company Profile page implemented
- Earnings Calls page implemented
- SEC Filing viewer implemented

### Data Available
- 2,000+ companies (SEC + YFinance sources)
- 5 years of financial statements
- 50,000+ news articles with sentiment
- Earnings call transcripts (select companies)

### Architecture
- Repository pattern for data access
- Component-based UI architecture
- Dataclass models for type safety
- Connection pooling for database efficiency

## Success Criteria

### User Experience
- [ ] All pages load in < 2 seconds
- [ ] User selections persist across sessions
- [ ] UI matches Figma specifications
- [ ] No raw errors shown to users

### Functional
- [ ] Income Statement displays correctly with all line items
- [ ] Balance Sheet displays correctly
- [ ] Cash Flow displays correctly
- [ ] News filters work (date, sector, company)
- [ ] SEC filings accessible and readable
- [ ] Earnings calls searchable by speaker

### Technical
- [ ] 100% database queries use connection pooling
- [ ] All data access through repositories
- [ ] Type hints on all public functions
- [ ] Error handling on all database calls
