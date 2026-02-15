# Testing

## Current State

**Minimal automated testing** is currently in place. Testing is primarily manual via Streamlit.

## Manual Testing

### Running Pages
```bash
# Market Data page
cd app && streamlit run marketdata.py

# Newsroom page
cd app && streamlit run pages/newsroom.py

# Company Filings
cd app && streamlit run companyfilings.py

# Earnings Calls
cd app && streamlit run earningscalls.py

# Home Page
cd app && streamlit run homepage.py
```

### VS Code Debugging
Pre-configured launch profiles in `.vscode/launch.json`:
- `Python Debugger: marketdata.py`
- `Streamlit: Market Data`
- `Streamlit: Newsroom`
- `Python Debugger: Current File`

## Recommended Testing Strategy

### Unit Tests
```bash
pip install pytest pytest-asyncio
```

Recommended test structure:
```
tests/
├── __init__.py
├── test_models.py          # Data model tests
├── test_repositories.py    # Repository layer tests
├── test_components.py      # UI component tests
└── conftest.py            # Pytest fixtures
```

### Integration Tests
- Database connectivity
- Query execution
- Data transformation

### UI Tests
- Streamlit component rendering
- User interaction flows
- State management

## Testing Checklist

### Data Layer
- [ ] CompanyRepository queries return correct data
- [ ] IncomeStatementRepository handles date ranges
- [ ] NewsRepository filters work correctly
- [ ] Database connection pooling works under load

### UI Layer
- [ ] All pages load without errors
- [ ] Charts render correctly
- [ ] Tables display data properly
- [ ] Filters and search work
- [ ] Responsive design works

### Integration
- [ ] Database connection on startup
- [ ] State persistence across sessions
- [ ] Error handling for missing data
- [ ] Currency conversion (if enabled)

## GSD Verification

Use `/gsd:verify-work <phase>` after building features to validate:
- Features work as expected
- Data is displayed correctly
- UI matches specifications
- No regressions introduced
