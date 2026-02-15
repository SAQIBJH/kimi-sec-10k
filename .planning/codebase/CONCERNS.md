# Concerns & Technical Debt

## Current Limitations

### 1. Testing Coverage
- **Issue**: No automated unit tests
- **Impact**: Manual testing required for all changes
- **Mitigation**: Use `/gsd:verify-work` for feature validation

### 2. Hardcoded Data Sources
- **Issue**: SQL queries have hardcoded table names and schemas
- **Impact**: Schema changes require code updates
- **Mitigation**: Document schema in AGENTS.md

### 3. Mock Data Still Present
- **Issue**: Some components may still reference dummy_data.py
- **Impact**: Confusion about data source
- **Mitigation**: Audit and remove unused mock data

### 4. No Caching Layer
- **Issue**: Database queries run on every interaction
- **Impact**: Performance degradation with many users
- **Mitigation**: Implement Streamlit caching decorators

### 5. Limited Error Handling
- **Issue**: Some edge cases not handled gracefully
- **Impact**: Streamlit stack traces shown to users
- **Mitigation**: Add try/except wrappers with user-friendly messages

## Performance Considerations

### Database
- **Connection Pool**: 5 connections, 10 overflow
- **Query Optimization**: Large tables (10MB+ SQL dumps)
- **Recommendation**: Add indexes on frequently queried columns

### Frontend
- **Chart Rendering**: Plotly charts can be slow with large datasets
- **Table Rendering**: Large tables need pagination
- **Recommendation**: Implement virtual scrolling for large datasets

## Security Considerations

### Database Credentials
- **Current**: Stored in `.env` file
- **Risk**: Accidental commit of credentials
- **Mitigation**: `.env` in `.gitignore`, use `.env.example` template

### SQL Injection
- **Current**: Parameterized queries used
- **Status**: Safe from injection attacks
- **Audit**: Review all raw SQL for safety

### Session Management
- **Current**: Basic Streamlit session state
- **Risk**: No user authentication
- **Mitigation**: Document as internal tool, add auth if externalizing

## Scalability Concerns

### Single User Design
- **Current**: Streamlit apps are single-user by default
- **Limitation**: Concurrent users may experience issues
- **Mitigation**: Consider migration to proper web framework if scaling needed

### Data Volume
- **Current**: ~35MB of SQL data
- **Growth**: Will increase with more companies/years
- **Mitigation**: Archive old data, implement data retention policy

## Future Improvements

### Phase 1 (Immediate)
- Add automated tests for repositories
- Remove unused mock data
- Add error boundaries to pages

### Phase 2 (Short-term)
- Implement caching layer
- Add data export functionality
- Improve mobile responsiveness

### Phase 3 (Long-term)
- Add user authentication
- Implement real-time data updates
- Migrate to production web framework (FastAPI + React)
