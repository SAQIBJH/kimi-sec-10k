# Coresight Research Portal - MASTER PLAN

**Version**: 3.0  
**Last Updated**: 2026-02-14  
**Status**: IN PROGRESS

---

## TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Vision & Goals](#vision--goals)
4. [System Architecture](#system-architecture)
5. [Phase-by-Phase Roadmap](#phase-by-phase-roadmap)
6. [Integration Strategy](#integration-strategy)
7. [Token Expiration Contingency](#token-expiration-contingency)
8. [Appendices](#appendices)

---

## EXECUTIVE SUMMARY

### What We're Building
A **unified financial intelligence platform** that combines:
- Traditional financial statements (Income, Balance Sheet, Cash Flow)
- AI-powered document search on SEC filings (10-K, 10-Q)
- Semantic understanding of financial metrics
- Intelligent synonym handling (Revenue = Net Sales = Total Revenue)

### Current Repositories

| Repository | Purpose | Status |
|------------|---------|--------|
| `kimi-sec-10k-1` | Main Research Portal | Active - Balance Sheet Complete |
| `sec-rag-demo` | RAG Search Prototype | Ready for Integration |

### Key Challenge to Solve
**The "Revenue" Search Problem:**
- Amazon uses "Total net sales"
- Apple uses "Net sales"
- Microsoft uses "Revenue"
- Tesla uses "Total revenues"

**Solution**: EdgarTools standardization + OpenAI semantic search

---

## CURRENT STATE ANALYSIS

### kimi-sec-10k-1 (Main Portal)

#### ✅ COMPLETED
| Feature | File | Notes |
|---------|------|-------|
| Income Statement | `app/pages/market_data.py` | Full implementation |
| Balance Sheet | `app/pages/market_data.py` | Raw JSON parsing, proper formatting |
| Sort Filter | `app/pages/market_data.py` | Earliest/Latest dropdown |
| Date Filters | `app/pages/market_data.py` | Start/End date selection |
| Newsroom | `app/pages/newsroom.py` | Cards, filtering, sentiment |
| Company Profile | `app/pages/company_profile.py` | Basic info, metrics |
| Earnings Calls | `app/pages/earnings_calls.py` | Transcripts, speaker parsing |
| SEC Filing List | `app/pages/sec_filing.py` | Form types, links to EDGAR |

#### ❌ MISSING / INCOMPLETE
| Feature | Priority | Blocker |
|---------|----------|---------|
| Cash Flow Statement | HIGH | None - follow Balance Sheet pattern |
| Navigation Flow | HIGH | URLs not fully linked between pages |
| Document Search | HIGH | Need to integrate from sec-rag-demo |
| Key Stats Tab | MEDIUM | Waiting for all 3 statements |
| Data Visualization | MEDIUM | Charts for trends |

### sec-rag-demo (RAG Prototype)

#### ✅ COMPLETED & READY TO INTEGRATE
| Feature | Description | Files |
|---------|-------------|-------|
| Smart Embedder | OpenAI embeddings with caching | `search/smart_embedder.py` |
| Semantic Search | Search metrics with AI understanding | `search/enhanced_semantic_search.py` |
| Calculated Metrics | 23 auto-computed ratios | `metrics/calculated_metrics.py` |
| XBRL Extraction | Multi-method extraction (5 methods) | `extractors/comprehensive_10k_extractor.py` |
| Dashboard v2 | Working search UI with highlighting | `dashboard/v2_app.py` |
| MySQL Schema | Database for metrics storage | `database/schema_mysql.sql` |

#### EdgarTools Integration
- 59+ synonym groups for metric standardization
- Handles Revenue ↔ Net Sales ↔ Total Revenue
- 2,067+ GAAP taxonomy mappings
- 276 excluded tags (prevents false matches)

---

## VISION & GOALS

### Primary Goals

1. **Unified Financial View**
   - All 3 statements (Income, Balance Sheet, Cash Flow)
   - Year-over-year comparison
   - Cross-company metric comparison

2. **Intelligent Document Search**
   - Natural language queries: "Show me revenue growth"
   - Semantic understanding: "Revenue" finds all variations
   - View-in-document with highlighting

3. **Synonym Intelligence**
   - Revenue = Net Sales = Total Revenue = Operating Revenue
   - COGS = Cost of Revenue = Cost of Sales
   - Automated via EdgarTools standardization

4. **Professional UX**
   - Seamless navigation between pages
   - Consistent Coresight branding
   - Fast, responsive interface

### Success Metrics

| Metric | Target |
|--------|--------|
| Search Accuracy | >95% for synonym queries |
| Page Load Time | <2 seconds |
| Document Highlight | <500ms to locate metric |
| User Satisfaction | Complete tasks without help |

---

## SYSTEM ARCHITECTURE

### Integrated System Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CORESIGHT RESEARCH PORTAL v3.0                       │
│                         (kimi-sec-10k-1 + sec-rag-demo)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     STREAMLIT UI LAYER                               │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────────┐ │   │
│  │  │   Market    │ │  Company    │ │  Earnings   │ │    Document    │ │   │
│  │  │    Data     │ │   Profile   │ │    Calls    │ │    Search      │ │   │
│  │  │  (3 tabs)   │ │             │ │             │ │   (NEW v3.0)   │ │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   INTELLIGENCE LAYER (NEW)                           │   │
│  │                                                                      │   │
│  │   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   │   │
│  │   │  EdgarTools     │   │  Smart Embedder │   │  Semantic       │   │   │
│  │   │  Standardization│   │  (OpenAI +      │   │  Search Engine  │   │   │
│  │   │  (59+ synonyms) │   │   Cache)        │   │                 │   │   │
│  │   └─────────────────┘   └─────────────────┘   └─────────────────┘   │   │
│  │            │                       │                       │         │   │
│  │            └───────────────────────┼───────────────────────┘         │   │
│  │                                    │                                  │   │
│  │   Search: "Revenue" → Synonym Expansion → Embedding → MySQL Results │   │
│  │                                    │                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    REPOSITORY LAYER                                  │   │
│  │                                                                      │   │
│  │   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────┐  │   │
│  │   │   Company    │ │   Income     │ │   Balance    │ │  Cash     │  │   │
│  │   │  Repository  │ │  Statement   │ │    Sheet     │ │   Flow    │  │   │
│  │   └──────────────┘ └──────────────┘ └──────────────┘ └───────────┘  │   │
│  │                                                                      │   │
│  │   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                 │   │
│  │   │     News     │ │  Earnings    │ │   Document   │                 │   │
│  │   │  Repository  │ │    Call      │ │   Search     │                 │   │
│  │   │              │ │ Repository   │ │ Repository   │                 │   │
│  │   └──────────────┘ └──────────────┘ └──────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     DATA LAYER                                       │   │
│  │                                                                      │   │
│  │   ┌──────────────────────────────────────────────────────────────┐  │   │
│  │   │                    MySQL Database                             │  │   │
│  │   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │  │   │
│  │   │  │  Companies  │ │ Financials  │ │    News     │ │ Metrics │ │  │   │
│  │   │  │             │ │(3 statements│ │             │ │  Cache  │ │  │   │
│  │   │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │  │   │
│  │   │  ┌─────────────┐ ┌─────────────┐                            │  │   │
│  │   │  │  Earnings   │ │  Document   │                            │  │   │
│  │   │  │    Calls    │ │   Search    │                            │  │   │
│  │   │  └─────────────┘ └─────────────┘                            │  │   │
│  │   └──────────────────────────────────────────────────────────────┘  │   │
│  │                                                                      │   │
│  │   ┌──────────────────────────────────────────────────────────────┐  │   │
│  │   │              SEC EDGAR (via edgartools)                       │  │   │
│  │   │  - 10-K filings                                               │  │   │
│  │   │  - 10-Q filings                                               │  │   │
│  │   │  - Real-time document access                                  │  │   │
│  │   └──────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Integration Map

```
kimi-sec-10k-1/                          sec-rag-demo/
├── app/                                 ├── sec_fintelligence/
│   ├── pages/                           │   ├── search/
│   │   ├── market_data.py      ←───────→│   │   ├── smart_embedder.py
│   │   ├── company_profile.py           │   │   └── enhanced_semantic_search.py
│   │   ├── newsroom.py                  │   ├── extractors/
│   │   ├── earnings_calls.py            │   │   └── comprehensive_10k_extractor.py
│   │   ├── sec_filing.py                │   ├── metrics/
│   │   └── (NEW) doc_search.py ←───────→│   │   └── calculated_metrics.py
│   ├── data/                            │   └── db/
│   │   └── repository.py                │       └── connection.py
│   └── components/
└── docs/                                └── database/
    ├── MASTER_PLAN.md (this file)           └── schema_mysql.sql
    ├── ARCHITECTURE.md
    └── HANDOFF.md
```

---

## PHASE-BY-PHASE ROADMAP

### PHASE 1: Cash Flow Statement (HIGH PRIORITY)
**Goal**: Complete the 3-statement financial view

**Tasks**:
1. Create `CashFlowRepository` in `app/data/repository.py`
   - Follow BalanceSheetRepository pattern
   - Use raw_json from `coreiq_av_financials_cash_flow` table
   - Define LINE_ITEMS for Operating/Investing/Financing sections

2. Add `render_cash_flow()` in `app/pages/market_data.py`
   - Copy Balance Sheet structure
   - 3 sections: Operating, Investing, Financing
   - Same formatting (indents, underlines, grey separators)

3. Add "Cash Flow" tab to navigation
   - Already exists but needs implementation
   - Update `render_page()` to call `render_cash_flow()`

**Deliverables**:
- [ ] Cash Flow table displays correctly
- [ ] All 3 statements accessible via tabs
- [ ] Sort filter works on Cash Flow
- [ ] Date filters work on Cash Flow

**Estimated Effort**: 1-2 days

---

### PHASE 2: Navigation Flow (HIGH PRIORITY)
**Goal**: Seamless navigation between all pages

**Current State Analysis**:
```
Current Entry Points:
- app/marketdata.py → Market Data (port 8502)
- app/homepage.py → Home (port ?)
- app/companyfilings.py → Company Filings (port ?)
- app/earningscalls.py → Earnings Calls (port ?)
- app/sec_filing.py → SEC Filing (port ?)
- app/newsroom.py → Newsroom (port ?)

Problems:
1. Different ports for each page
2. No unified navigation
3. URL parameters not consistent
4. State doesn't persist across pages
```

**Tasks**:
1. Create unified navigation system
   - All pages should use same port (8502)
   - URL-based routing: `/?page=market_data&tab=balance_sheet`
   - State persistence across navigation

2. Update header navigation links
   - Link Market Data → Home
   - Link Earnings Calls → Earnings Calls page
   - Link News → Newsroom page

3. Create main entry point
   - `app/main.py` as single entry
   - Route to appropriate page based on URL params
   - Maintain state in session

**Deliverables**:
- [ ] Single port (8502) for all pages
- [ ] Working navigation links in header
- [ ] URL parameters work correctly
- [ ] State persists across page navigation

**Estimated Effort**: 2-3 days

---

### PHASE 3: Document Search Integration (HIGH PRIORITY)
**Goal**: Integrate RAG search from sec-rag-demo

**Architecture**:
```
User Query: "What was Amazon's revenue in 2024?"
    │
    ▼
┌─────────────────────────────────────┐
│ 1. SYNONYM EXPANSION                │
│    "revenue" → ["revenue", "sales", │
│     "net sales", "total revenue"]    │
│    (via EdgarTools synonym_groups)  │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 2. SEMANTIC EMBEDDING               │
│    Query → OpenAI Embedding         │
│    (cached via SmartEmbedder)       │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 3. VECTOR SEARCH                    │
│    Find similar metric embeddings   │
│    in MySQL vector store            │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 4. RESULT RANKING                   │
│    Score by:                        │
│    - Semantic similarity            │
│    - Exact label match              │
│    - Year relevance                 │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 5. VIEW IN DOCUMENT                 │
│    User clicks "View" →             │
│    Highlight metric in 10-K HTML    │
│    Scroll to location               │
└─────────────────────────────────────┘
```

**Files to Create/Move**:
```
app/
├── search/                          # NEW MODULE
│   ├── __init__.py
│   ├── smart_embedder.py           # From sec-rag-demo
│   ├── synonym_mapper.py           # EdgarTools integration
│   ├── semantic_search.py          # Search engine
│   └── document_highlighter.py     # HTML highlighting
│
├── pages/
│   └── doc_search.py               # NEW PAGE
│
└── data/
    └── document_repository.py      # NEW - SEC filing access
```

**Tasks**:
1. Copy `smart_embedder.py` to `app/search/`
2. Create `synonym_mapper.py` using EdgarTools patterns
3. Create `semantic_search.py` for metric search
4. Create `document_highlighter.py` for HTML highlighting
5. Create `doc_search.py` page with UI
6. Add navigation link to Document Search

**Deliverables**:
- [ ] Search box accepts natural language
- [ ] Synonym expansion works (revenue → net sales)
- [ ] Results show metric value + context
- [ ] "View in Document" highlights text in 10-K
- [ ] Works for all 3 companies (AAPL, AMZN, MSFT initially)

**Estimated Effort**: 5-7 days

---

### PHASE 4: EdgarTools Standardization (MEDIUM PRIORITY)
**Goal**: Robust synonym handling for all financial metrics

**Synonym Groups to Implement**:
```python
# From EdgarTools - 59+ groups
REVENUE_SYNONYMS = [
    'revenue', 'revenues', 'total revenue', 'total revenues',
    'sales', 'net sales', 'total net sales', 'gross sales',
    'operating revenue', 'contract revenue',
    'RevenueFromContractWithCustomerExcludingAssessedTax',
    'RevenueFromContractWithCustomerIncludingAssessedTax',
    'Revenues', 'Revenue', 'SalesRevenueNet',
    'SalesRevenueGoodsNet', 'TotalRevenues', 'NetSales',
    'OperatingRevenue'
]

COGS_SYNONYMS = [
    'cost of revenue', 'cost of goods sold', 'cogs',
    'cost of sales', 'cost of goods and services sold',
    'direct costs', 'cost of products sold',
    'CostOfRevenue', 'CostOfSales', 'CostOfGoodsSold'
]

NET_INCOME_SYNONYMS = [
    'net income', 'net profit', 'profit', 'earnings',
    'net earnings', 'income', 'bottom line',
    'net income attributable', 'profit attributable',
    'NetIncomeLoss', 'ProfitLoss', 'NetIncome'
]
# ... 56 more groups
```

**Implementation Strategy**:
```python
# Option A: Full edgartools library (recommended)
from edgar.standardization import SynonymGroups

synonyms = SynonymGroups()
group = synonyms.get_group('revenue')
matching_concepts = group.get_all_tags()

# Option B: Extract JSON mappings (if edgartools too heavy)
import json
with open('concept_mappings.json') as f:
    mappings = json.load(f)
```

**Tasks**:
1. Install edgartools: `pip install edgartools`
2. Create `app/search/synonym_mapper.py`
3. Integrate into search pipeline
4. Add calculated metrics (23 ratios)

**Deliverables**:
- [ ] Revenue search finds all variations
- [ ] COGS search finds all variations
- [ ] Net Income search finds all variations
- [ ] 23 calculated ratios working
- [ ] Exclusions system prevents false matches

**Estimated Effort**: 3-4 days

---

### PHASE 5: Key Stats & Visualization (MEDIUM PRIORITY)
**Goal**: Financial ratios and trend charts

**Key Stats to Display**:
```
Profitability:
- Gross Margin = Gross Profit / Revenue
- Operating Margin = Operating Income / Revenue
- Net Margin = Net Income / Revenue
- EBITDA Margin = EBITDA / Revenue

Returns:
- ROE = Net Income / Shareholders' Equity
- ROA = Net Income / Total Assets
- ROIC = NOPAT / Invested Capital

Liquidity:
- Current Ratio = Current Assets / Current Liabilities
- Quick Ratio = (Current Assets - Inventory) / Current Liabilities

Leverage:
- Debt/Equity = Total Debt / Shareholders' Equity
- Debt/Assets = Total Debt / Total Assets
```

**Tasks**:
1. Implement calculated metrics in `app/metrics/calculated_metrics.py`
2. Add Key Stats tab to Market Data page
3. Create visualization components using Plotly
4. Add trend charts (revenue over time, etc.)

**Deliverables**:
- [ ] Key Stats tab displays 23 ratios
- [ ] Ratios calculated from raw data
- [ ] Revenue trend chart
- [ ] Profit margin visualization

**Estimated Effort**: 4-5 days

---

### PHASE 6: Testing & Polish (MEDIUM PRIORITY)
**Goal**: Production-ready quality

**Tasks**:
1. Unit tests for repositories
2. Integration tests for search
3. Error handling for all database calls
4. Performance optimization
5. UI consistency audit

**Deliverables**:
- [ ] pytest suite running
- [ ] >80% code coverage
- [ ] All error cases handled
- [ ] Performance <2s for all operations

**Estimated Effort**: 4-5 days

---

## INTEGRATION STRATEGY

### Step-by-Step Integration

#### Step 1: Merge Repositories (Don't duplicate code)
```bash
# Option A: Keep sec-rag-demo as submodule
cd kimi-sec-10k-1
git submodule add /Users/mohdsaeedafri/Documents/Documents/Code-Base/sec-rag-demo sec_rag

# Option B: Copy files selectively (recommended)
cp -r /Users/mohdsaeedafri/Documents/Documents/Code-Base/sec-rag-demo/sec_fintelligence/search app/
cp -r /Users/mohdsaeedafri/Documents/Documents/Code-Base/sec-rag-demo/sec_fintelligence/metrics app/
```

#### Step 2: Database Integration
```sql
-- Add to existing secfiling database
-- New tables for document search:
- sec_metrics_cache (metric embeddings)
- sec_filing_documents (10-K/10-Q content)
- sec_metric_synonyms (synonym mappings)
```

#### Step 3: Configuration
```python
# app/core/config.py
# Add new settings:
- OPENAI_API_KEY (for embeddings)
- EDGAR_EMAIL (for SEC access)
- ENABLE_SEMANTIC_SEARCH (feature flag)
```

#### Step 4: Dependency Management
```txt
# requirements.txt additions:
edgartools>=0.4.0
openai>=1.0.0
sentence-transformers>=2.2.0
```

---

## TOKEN EXPIRATION CONTINGENCY

### Critical Information for Next Agent

If tokens expire, the next agent MUST:

#### 1. Read These Files (In Order)
```bash
cat docs/MASTER_PLAN.md      # This file - overall plan
cat STATUS.md                # Current implementation status
cat docs/HANDOFF.md          # Quick start guide
cat AGENTS.md                # Architecture details
```

#### 2. Check Current State
```bash
# What's been completed
git log --oneline -20

# What's pending
git status

# Current branch
git branch
```

#### 3. Resume From Correct Phase

| If This Is Done | Resume From |
|-----------------|-------------|
| Balance Sheet only | Phase 1: Cash Flow |
| Cash Flow done | Phase 2: Navigation |
| Navigation done | Phase 3: Document Search |
| Document Search done | Phase 4: EdgarTools |
| EdgarTools done | Phase 5: Key Stats |

#### 4. Testing Checklist Before Continuing
- [ ] Balance Sheet loads correctly
- [ ] Sort filter works
- [ ] Date filters work
- [ ] Can switch between tabs

#### 5. Common Issues & Solutions

**Issue**: Database connection fails
```bash
# Check MySQL running
mysql -u root -p -e "SHOW DATABASES;"

# Check tables exist
mysql -u root -p secfiling -e "SHOW TABLES;"
```

**Issue**: OpenAI API errors
```bash
# Check API key
export OPENAI_API_KEY="sk-..."
echo $OPENAI_API_KEY
```

**Issue**: Import errors from sec-rag-demo
```bash
# Ensure path is correct
cd /Users/mohdsaeedafri/Documents/Documents/Code-Base/kimi-sec-10k-1/app
python -c "from search.smart_embedder import SmartEmbedder; print('OK')"
```

---

## APPENDICES

### Appendix A: File Inventory

#### Critical Files (Must Maintain)
| File | Purpose | Lines |
|------|---------|-------|
| `app/pages/market_data.py` | Main financial statements | ~900 |
| `app/data/repository.py` | All data access | ~350 |
| `app/components/navigation.py` | Header/footer | ~200 |
| `app/utils/local_storage.py` | State management | ~150 |

#### New Files (To Create)
| File | Purpose |
|------|---------|
| `app/search/smart_embedder.py` | OpenAI embeddings |
| `app/search/synonym_mapper.py` | EdgarTools synonyms |
| `app/search/semantic_search.py` | Search engine |
| `app/pages/doc_search.py` | Document search UI |
| `app/metrics/calculated_metrics.py` | 23 ratios |

### Appendix B: Database Schema

```sql
-- Existing Tables
coreiq_companies
coreiq_av_financials_income_statement
coreiq_av_financials_balance_sheet
coreiq_av_financials_cash_flow
coreiq_av_market_news_sentiment
coreiq_earnings_calls

-- New Tables (from sec-rag-demo)
sec_metrics_cache (
    id, ticker, concept, label, value, year,
    embedding_json, filing_url, created_at
)

sec_filing_documents (
    id, ticker, form_type, year, quarter,
    html_content, xbrl_data, accessed_at
)

sec_metric_synonyms (
    id, canonical_name, synonyms_json, category
)
```

### Appendix C: API Keys & Environment

```bash
# .env file
db_host=localhost
db_port=3306
db_name=secfiling
db_user=root
db_password=admin

# For Document Search
OPENAI_API_KEY=sk-...
EDGAR_EMAIL=your.email@example.com
```

### Appendix D: Testing Commands

```bash
# Run main app
cd app && streamlit run marketdata.py --server.port=8502

# Test database
mysql -u root -p secfiling -e "SELECT COUNT(*) FROM coreiq_companies;"

# Test OpenAI
python -c "import openai; print(openai.__version__)"

# Run tests (when implemented)
pytest tests/ -v
```

### Appendix E: Glossary

| Term | Definition |
|------|------------|
| **10-K** | Annual SEC filing |
| **10-Q** | Quarterly SEC filing |
| **XBRL** | eXtensible Business Reporting Language |
| **EdgarTools** | Python library for SEC data |
| **RAG** | Retrieval-Augmented Generation |
| **Embedding** | Vector representation of text |
| **Synonym Group** | Set of terms with same meaning |

---

**END OF MASTER PLAN**

*This document is the single source of truth for the project. Keep it updated as work progresses.*
