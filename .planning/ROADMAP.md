# Roadmap - Coresight Research Portal v3.0

**Last Updated**: 2026-02-14

---

## Phase 1: Foundation (COMPLETE) ✅
**Goal**: Core application structure and Income Statement view

**Deliverables**:
- ✅ Project setup with Streamlit
- ✅ MySQL database connection pooling
- ✅ Repository pattern implementation
- ✅ Component architecture (styles, layout, charts, tables)
- ✅ Income Statement view with company/date selection
- ✅ State management with local storage
- ✅ Coresight brand styling

**Success Criteria**:
- ✅ Income Statement displays real data from database
- ✅ Company selector populates from database
- ✅ Date range selection works
- ✅ Values formatted correctly in millions

---

## Phase 2: Balance Sheet (COMPLETE) ✅
**Goal**: Add Balance Sheet financial statement view

**Deliverables**:
- ✅ BalanceSheetRepository with raw JSON parsing
- ✅ Balance Sheet table with proper formatting
- ✅ Visual hierarchy (indents, underlines, separators)
- ✅ Sort filter integration
- ✅ Tab navigation

**Success Criteria**:
- ✅ Balance Sheet displays correctly
- ✅ All formatting rules applied
- ✅ Works with sort and date filters

---

## Phase 3: Cash Flow Statement (v3.0) 🔄 IN PROGRESS
**Goal**: Complete the 3-statement financial view

**Description**:
Implement Cash Flow Statement showing operating, investing, and financing activities. Follow established patterns from Balance Sheet.

**Key Tasks**:
1. Create CashFlow models (dataclasses)
2. Create CashFlowRepository with raw JSON parsing
3. Add Cash Flow table component with 3 sections
4. Integrate with tab navigation in Market Data
5. Apply formatting (indents, underlines, separators)

**Depends On**: Phase 2

**Estimated Effort**: 1-2 days

---

## Phase 4: Unified Navigation (v3.0) 🔄 IN PROGRESS
**Goal**: Seamless navigation between all pages

**Description**:
Create unified entry point with URL-based routing. Users select a company on homepage and it persists across all pages.

**Key Tasks**:
1. ✅ Create `app/main.py` as unified entry point
2. ✅ Implement URL-based routing: `/?page=market_data&tab=balance_sheet&ticker=M`
3. ✅ Update header navigation links with dynamic URLs
4. ✅ Ensure state persistence across pages (localStorage)
5. ✅ Single entry point for all pages
6. ✅ Add NAVIGATION_MODE env variable (new/same tab)
7. ✅ Company switcher dropdown on all pages
8. 🔄 Testing and verification

**Manager Requirements Addressed**:
- Homepage is the entry point for company selection
- Selected company auto-populates in News and Earnings Calls
- "View" button opens Company Profile in new tab (configurable)
- Company switcher available without going back to home
- Navigation supports both new-tab and same-tab modes

**Depends On**: Phase 3

**Estimated Effort**: 2-3 days

---

## Phase 5: Document Search Integration (v3.0) 📋
**Goal**: Integrate RAG search from `sec-rag-demo` repository

**Description**:
Add intelligent document search on SEC filings (10-K, 10-Q) with semantic understanding and view-in-document highlighting.

**Key Tasks**:
1. Copy `search/` module from `sec-rag-demo`
   - SmartEmbedder (OpenAI + caching)
   - Semantic search engine
   - Synonym mapper
2. Create new page: `app/pages/doc_search.py`
3. Integrate EdgarTools standardization
4. Add navigation link to Document Search
5. Test with AAPL, AMZN, MSFT data

**Features**:
- Natural language queries
- Synonym expansion (Revenue = Net Sales = Total Revenue)
- View-in-document with highlighting
- 23 calculated ratios

**Depends On**: Phase 4

**Estimated Effort**: 5-7 days

---

## Phase 6: EdgarTools Standardization (v3.0) 📋
**Goal**: Robust synonym handling for all financial metrics

**Description**:
Implement EdgarTools standardization to handle metric variations across companies.

**Key Tasks**:
1. Install edgartools: `pip install edgartools`
2. Create `app/search/synonym_mapper.py`
3. Implement 59+ synonym groups
4. Add calculated metrics (23 ratios)
5. Add exclusions system (prevent false matches)

**Synonym Groups**:
- Revenue (Revenue, Net Sales, Total Revenue, etc.)
- COGS (Cost of Revenue, Cost of Sales, etc.)
- Net Income (Net Income, Net Profit, Earnings, etc.)
- ... 56 more groups

**Depends On**: Phase 5

**Estimated Effort**: 3-4 days

---

## Phase 7: Key Stats & Visualization (v3.0) 📊
**Goal**: Financial ratios and trend charts

**Description**:
Add Key Stats tab with calculated ratios and interactive charts.

**Key Tasks**:
1. Implement calculated metrics (23 ratios)
   - Profitability: Gross Margin, Operating Margin, Net Margin
   - Returns: ROE, ROA, ROIC
   - Liquidity: Current Ratio, Quick Ratio
   - Leverage: Debt/Equity, Debt/Assets
2. Add Key Stats tab to Market Data
3. Create visualization components (Plotly)
4. Add trend charts (revenue over time, etc.)

**Depends On**: Phase 3

**Estimated Effort**: 4-5 days

---

## Phase 8: Testing & Quality (v3.0) ✅
**Goal**: Comprehensive testing and bug fixes

**Description**:
Add automated tests, fix known issues, and improve error handling.

**Key Tasks**:
1. Set up pytest framework
2. Write repository unit tests
3. Add integration tests for search
4. Implement error boundaries
5. Performance profiling and optimization

**Depends On**: Phases 1-7

**Estimated Effort**: 4-5 days

---

## Phase 9: Documentation & Polish (v3.0) 📚
**Goal**: Complete documentation and UI polish

**Description**:
Final documentation updates, code cleanup, and minor UI improvements.

**Key Tasks**:
1. Update AGENTS.md with final patterns
2. Add inline code documentation
3. Create user guide
4. UI consistency audit
5. Accessibility improvements

**Depends On**: Phases 1-8

**Estimated Effort**: 2 days

---

## Milestone: v3.0 Release
**Target**: End of development cycle
**Includes**: Phases 3-9
**Definition of Done**:
- All v3.0 requirements implemented
- Document search working with semantic understanding
- All 3 financial statements complete
- Tests passing
- Documentation complete
- UI matches Figma specifications
- No critical bugs

---

## Integration: sec-rag-demo

### What to Port
| Component | Source | Destination |
|-----------|--------|-------------|
| SmartEmbedder | `sec_fintelligence/search/smart_embedder.py` | `app/search/smart_embedder.py` |
| Semantic Search | `sec_fintelligence/search/enhanced_semantic_search.py` | `app/search/semantic_search.py` |
| XBRL Extractor | `sec_fintelligence/extractors/comprehensive_10k_extractor.py` | `app/extractors/xbrl_extractor.py` |
| Calculated Metrics | `sec_fintelligence/metrics/calculated_metrics.py` | `app/metrics/calculated_metrics.py` |
| Dashboard v2 | `sec_fintelligence/dashboard/v2_app.py` | Reference for `app/pages/doc_search.py` |

### Database Additions
```sql
-- New tables for document search
sec_metrics_cache (metric embeddings)
sec_filing_documents (10-K/10-Q content)
sec_metric_synonyms (synonym mappings)
```

---

## Future Milestones

### v4.0 Ideas (Not Planned)
- Real-time data integration
- Advanced analytics dashboard
- Machine learning insights
- Mobile app
- API for external access
- Multi-user collaboration

---

**End of Roadmap**
