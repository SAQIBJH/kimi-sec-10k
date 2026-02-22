# EdgarTools API Documentation

> **Common documentation for all EdgarTools methods - Updated regularly**
> 
> **Company:** Apple Inc. (AAPL)  
> **CIK:** 0000320193  
> **Fiscal Year:** 2025  
> **Filing:** 10-K (2025-10-31)

---

## Table of Contents

1. [FactsView Methods](#factsview-methods) - XBRL Facts Access
2. [Financials Methods](#financials-methods) - Financial Statements
3. [Statement Methods](#statement-methods) - Individual Statement Access
4. [Company Methods](#company-methods) - High-level Access
5. [Data Storage Scripts](#data-storage-scripts) - Complete Scripts

---

## FactsView Methods

Access via: `filing.xbrl().facts`

### Core Methods

#### `get_facts()` → List[Dict]
Returns all raw XBRL facts as a list of dictionaries.

```python
from edgar import Company, set_identity
set_identity("your@email.com")

apple = Company("AAPL")
filing = apple.get_filings(form="10-K").latest()
facts = filing.xbrl().facts

# Get all facts
all_facts = facts.get_facts()
print(f"Total facts: {len(all_facts)}")  # 1131

# Each fact contains:
# - concept: XBRL concept name (e.g., "us-gaap:Revenue")
# - value: String value
# - numeric_value: Numeric value (if applicable)
# - unit_ref: Unit (usd, shares, etc.)
# - period_start, period_end: Date range
# - fiscal_year, fiscal_period: FY2025, Q1, etc.
# - statement_type: IncomeStatement, BalanceSheet, etc.
# - dimensions: Breakdown data (Product, Geography, etc.)
```

**Storage Script:**
```python
import json

# Save all facts
with open("all_facts.json", "w") as f:
    json.dump(all_facts, f, indent=2, default=str)
```

---

#### `to_dataframe()` → pd.DataFrame
Converts all facts to a pandas DataFrame (53 columns).

```python
df = facts.to_dataframe()
print(df.shape)  # (1131, 53)

# Key columns:
# - concept, label, value, numeric_value
# - period_start, period_end, period_type (instant/duration)
# - fiscal_year, fiscal_period
# - statement_type, statement_name
# - dimension, member (for breakdowns)
# - unit_ref, decimals
```

**Storage Script:**
```python
# Save as CSV
df.to_csv("all_facts.csv", index=False)

# Save as JSON
df.to_json("all_facts_dataframe.json", orient="records", indent=2)

# Save as Parquet (efficient)
df.to_parquet("all_facts.parquet")
```

---

#### `get_facts_by_concept(pattern, exact=False)` → pd.DataFrame
Filter facts by XBRL concept name.

```python
# Wildcard search (default)
revenue = facts.get_facts_by_concept("Revenue")  # 71 rows
assets = facts.get_facts_by_concept("*Assets*")  # All assets

# Exact match
assets_exact = facts.get_facts_by_concept("us-gaap:Assets", exact=True)  # 2 rows

# Common concepts:
# - RevenueFromContractWithCustomer
# - NetIncomeLoss
# - Assets, AssetsCurrent, AssetsNoncurrent
# - Liabilities, StockholdersEquity
# - CashAndCashEquivalents
```

**Storage Script:**
```python
import json

concepts_to_extract = [
    "Revenue",
    "NetIncomeLoss", 
    "Assets",
    "Liabilities",
    "StockholdersEquity",
    "CashAndCashEquivalents"
]

for concept in concepts_to_extract:
    df = facts.get_facts_by_concept(concept)
    df.to_json(f"concept_{concept}.json", orient="records", indent=2)
    print(f"Saved {concept}: {len(df)} rows")
```

---

#### `get_facts_by_period(period_key)` → pd.DataFrame
Get facts for a specific period.

```python
# Get period key from data
period_key = "duration_2024-09-29_2025-09-27"
period_facts = facts.get_facts_by_period(period_key)  # 301 rows
```

---

#### `get_facts_by_fiscal_period(fiscal_year, fiscal_period)` → pd.DataFrame
Filter by fiscal year and period.

```python
# Full year 2025
fy2025 = facts.get_facts_by_fiscal_period(2025, "FY")  # 459 rows

# Q1 2025 (if available)
q1_2025 = facts.get_facts_by_fiscal_period(2025, "Q1")
```

---

#### `get_facts_with_dimensions()` → pd.DataFrame
Get only facts with dimension breakdowns.

```python
dim_facts = facts.get_facts_with_dimensions()  # 460 rows

# Dimensions include:
# - ProductOrServiceAxis: iPhone, Mac, iPad, Services
# - StatementBusinessSegmentsAxis: Americas, Europe, GreaterChina
# - StatementGeographicalAxis: US, CN, OtherCountries
```

---

#### `get_unique_dimensions()` → Dict[str, Set]
Get all dimension axes and their member values.

```python
dims = facts.get_unique_dimensions()
# Returns:
# {
#   "srt_ProductOrServiceAxis": {"iPhone", "Mac", "iPad", "Services", ...},
#   "us-gaap_StatementBusinessSegmentsAxis": {"Americas", "Europe", ...},
#   ...
# }
```

---

#### `search_facts(text_pattern)` → pd.DataFrame
Full-text search across concepts, labels, and values.

```python
cash_facts = facts.search_facts("cash")      # 75 rows
income_facts = facts.search_facts("income")  # 169 rows
```

---

#### `get_unique_concepts()` → List[str]
Get list of all unique XBRL concepts.

```python
concepts = facts.get_unique_concepts()  # 384 concepts
```

---

#### `summarize()` → Dict
Get summary statistics.

```python
summary = facts.summarize()
# Returns:
# {
#   "total_facts": 1131,
#   "by_statement": {
#     "IncomeStatement": 180,
#     "BalanceSheet": 182,
#     "CashFlowStatement": 90,
#     ...
#   },
#   "by_period_type": {"duration": 622, "instant": 509},
#   "dimensions": ["ProductOrServiceAxis", "StatementBusinessSegmentsAxis", ...]
# }
```

---

#### `get_statement_facts(statement_type)` → pd.DataFrame
Get all facts belonging to a statement type.

```python
income_facts = facts.get_statement_facts("IncomeStatement")    # 180 rows
balance_facts = facts.get_statement_facts("BalanceSheet")      # 182 rows
cashflow_facts = facts.get_statement_facts("CashFlowStatement") # 90 rows
```

**Available Statement Types:**
- `IncomeStatement`
- `BalanceSheet`
- `CashFlowStatement`
- `StatementOfEquity`
- `ComprehensiveIncome`

---

## Query Builder Methods

Access via: `facts.query()` (returns FactQuery object)

Chain methods and end with `.execute()` (returns List) or `.to_dataframe()` (returns DataFrame).

### Filter Methods

```python
# By concept (regex)
facts.query().by_concept("Revenue").to_dataframe()           # 71 rows
facts.query().by_concept("Assets", exact=True).to_dataframe() # Exact match

# By fiscal year
facts.query().by_fiscal_year(2025).to_dataframe()            # 953 rows

# By fiscal period (FY, Q1, Q2, Q3, Q4)
facts.query().by_fiscal_period("FY").to_dataframe()          # 613 rows

# By statement type
facts.query().by_statement_type("IncomeStatement").to_dataframe()  # 180 rows

# By period type (instant/duration)
facts.query().by_period_type("instant").to_dataframe()       # 509 rows

# With dimensions only
facts.query().with_dimensions().to_dataframe()               # 1131 rows

# By specific dimension
facts.query().by_dimension("srt:ProductOrServiceAxis").to_dataframe()  # 27 rows

# By unit
facts.query().by_unit("usd").to_dataframe()                  # 861 rows

# By label
facts.query().by_label("Revenue").to_dataframe()             # 24 rows
```

### Complex Queries

```python
# Chain multiple filters
result = facts.query()\
    .by_statement_type("IncomeStatement")\
    .by_fiscal_year(2025)\
    .with_dimensions()\
    .to_dataframe()  # 120 rows

# Limit results
facts.query().limit(100).to_dataframe()

# Sort results
facts.query().sort_by("concept").to_dataframe()
```

---

## Financials Methods

Access via: `company.get_financials()` or `filing.financials`

### Get Financials

```python
# Annual financials (10-K)
financials = apple.get_financials()  # or filing.financials

# Quarterly financials (10-Q)
quarterly = apple.get_quarterly_financials()
```

### Statement Methods

```python
# Income Statement
income_stmt = financials.income_statement()
print(type(income_stmt))  # Statement object

# Balance Sheet
balance_sheet = financials.balance_sheet()

# Cash Flow Statement
cashflow = financials.cashflow_statement()

# Statement of Equity
equity = financials.statement_of_equity()

# Comprehensive Income
comp_income = financials.comprehensive_income()
```

---

## Statement Methods

`Statement` object methods (returned by financials methods).

### Get DataFrame

```python
# Get statement as DataFrame
income_df = financials.income_statement().to_dataframe()

# With presentation mode (matches SEC HTML display)
income_df = financials.income_statement().to_dataframe(
    include_dimensions=True,    # Add dimension columns
    include_unit=True,          # Add unit column
    include_point_in_time=True, # Add point-in-time column
    presentation=True           # Match SEC HTML display format
)
```

**⚠️ DEPRECATION WARNING:** `include_dimensions` is deprecated in v6.0. Use `view` parameter instead:
- `view='standard'` - Default view
- `view='detailed'` - Includes dimensions (same as include_dimensions=True)
- `view='summary'` - Summary view

### Render Statement

```python
# Render as formatted text (matches SEC display)
rendered = financials.income_statement().render()
print(rendered)
```

Output:
```
                                  APPLE INC.   AAPL
                                  CONSOLIDATED STATEMENT OF INCOME
                                  Sep 30, 2023 to Sep 27, 2025

                                                       Sep 27, 2025   Sep 28, 2024   Sep 30, 2023
   ────────────────────────────────────────────────────────────────────────────────────────────
            Net sales:                                     $416,161       $391,035       $383,285
            Products                                       $307,003       $294,866       $298,085
            Services                                       $109,158        $96,169        $85,200
            ...
```

### Iterate Over Statements

```python
# Iterate through all statements
for statement in financials:
    print(f"Statement: {statement.name}")
    df = statement.get_dataframe()
    print(df.head())
```

### Statement Class Signature

```python
class Statement:
    """Single financial statement"""
    
    def render(self, **kwargs) -> RenderedStatement
        """Render statement as formatted text"""
    
    def to_dataframe(
        self,
        include_dimensions: bool = True,   # Deprecated: Use view='detailed'
        include_unit: bool = False,         # Add unit column
        include_point_in_time: bool = False,# Add point-in-time column
        presentation: bool = False          # Match SEC HTML display
    ) -> pd.DataFrame
        """Convert statement to DataFrame"""
```

---

## Data Storage Scripts

### Complete Script: Store All Facts

```python
#!/usr/bin/env python3
"""
Store all FactsView data for Apple 2025
"""

import json
import os
from edgar import Company, set_identity
import pandas as pd

set_identity("your@email.com")
OUTPUT_DIR = "apple_2025_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Setup
apple = Company("AAPL")
filing = apple.get_filings(form="10-K").latest()
facts = filing.xbrl().facts

# 1. All raw facts
all_facts = facts.get_facts()
with open(f"{OUTPUT_DIR}/01_all_facts_raw.json", "w") as f:
    json.dump(all_facts, f, indent=2, default=str)

# 2. All facts as DataFrame
df_all = facts.to_dataframe()
df_all.to_json(f"{OUTPUT_DIR}/02_all_facts_dataframe.json", orient="records", indent=2)
df_all.to_csv(f"{OUTPUT_DIR}/02_all_facts.csv", index=False)

# 3. Key concepts
key_concepts = ["Revenue", "NetIncomeLoss", "Assets", "Liabilities", "StockholdersEquity"]
for concept in key_concepts:
    df = facts.get_facts_by_concept(concept)
    df.to_json(f"{OUTPUT_DIR}/concept_{concept}.json", orient="records", indent=2)

# 4. By statement
for stmt in ["IncomeStatement", "BalanceSheet", "CashFlowStatement"]:
    df = facts.get_statement_facts(stmt)
    df.to_json(f"{OUTPUT_DIR}/statement_{stmt}.json", orient="records", indent=2)

# 5. With dimensions
dim_df = facts.get_facts_with_dimensions()
dim_df.to_json(f"{OUTPUT_DIR}/facts_with_dimensions.json", orient="records", indent=2)

# 6. Dimensions mapping
dims = facts.get_unique_dimensions()
dims_serializable = {k: list(v) for k, v in dims.items()}
with open(f"{OUTPUT_DIR}/dimensions_mapping.json", "w") as f:
    json.dump(dims_serializable, f, indent=2)

# 7. Summary
summary = facts.summarize()
with open(f"{OUTPUT_DIR}/summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

print(f"All data saved to {OUTPUT_DIR}/")
```

---

### Complete Script: Store Financial Statements

```python
#!/usr/bin/env python3
"""
Store all Financial Statements for Apple 2025
"""

import json
import os
from edgar import Company, set_identity

set_identity("your@email.com")
OUTPUT_DIR = "apple_2025_financials"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Setup
apple = Company("AAPL")
filing = apple.get_filings(form="10-K").latest()
financials = filing.financials

# Store each statement
statements = {
    "income_statement": financials.income_statement(),
    "balance_sheet": financials.balance_sheet(),
    "cashflow_statement": financials.cashflow_statement(),
    "statement_of_equity": financials.statement_of_equity(),
    "comprehensive_income": financials.comprehensive_income()
}

for name, statement in statements.items():
    # Save as JSON
    df = statement.get_dataframe()
    df.to_json(f"{OUTPUT_DIR}/{name}.json", orient="records", indent=2)
    
    # Save as CSV
    df.to_csv(f"{OUTPUT_DIR}/{name}.csv", index=False)
    
    print(f"Saved {name}: {df.shape}")

print(f"\nAll statements saved to {OUTPUT_DIR}/")
```

### Complete Script: Store Statements with Presentation Mode

```python
#!/usr/bin/env python3
"""
Store all Financial Statements with Presentation Mode
Uses to_dataframe(presentation=True) to match SEC HTML display
"""

import json
import os
from edgar import Company, set_identity
import pandas as pd

set_identity("your@email.com")
OUTPUT_DIR = "apple_2025_presentation_mode"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Setup
apple = Company("AAPL")
financials = apple.get_financials()

# Statements to export
statements = {
    "income_statement": financials.income_statement(),
    "balance_sheet": financials.balance_sheet(),
    "cashflow_statement": financials.cashflow_statement(),
    "statement_of_equity": financials.statement_of_equity(),
    "comprehensive_income": financials.comprehensive_income()
}

for name, statement in statements.items():
    # Default mode
    df_default = statement.to_dataframe()
    df_default.to_json(f"{OUTPUT_DIR}/{name}_default.json", orient="records", indent=2)
    
    # Presentation mode (matches SEC HTML)
    df_presentation = statement.to_dataframe(
        include_dimensions=True,
        include_unit=True,
        include_point_in_time=True,
        presentation=True  # <-- Match SEC HTML display
    )
    df_presentation.to_json(f"{OUTPUT_DIR}/{name}_presentation.json", orient="records", indent=2)
    
    # Rendered text
    rendered = statement.render()
    with open(f"{OUTPUT_DIR}/{name}_rendered.txt", "w") as f:
        f.write(str(rendered))
    
    print(f"Saved {name}:")
    print(f"  Default: {df_default.shape}")
    print(f"  Presentation: {df_presentation.shape}")

print(f"\nAll files saved to {OUTPUT_DIR}/")
```

---

## Quick Reference

### FactsView Methods Summary

| Method | Returns | Purpose |
|--------|---------|---------|
| `get_facts()` | List[Dict] | All raw facts |
| `to_dataframe()` | DataFrame | All facts as DF |
| `get_facts_by_concept()` | DataFrame | Filter by concept |
| `get_facts_by_period()` | DataFrame | Filter by period |
| `get_facts_by_fiscal_period()` | DataFrame | Filter by FY/period |
| `get_facts_with_dimensions()` | DataFrame | Dimensioned facts only |
| `get_unique_dimensions()` | Dict | All dimensions |
| `search_facts()` | DataFrame | Text search |
| `get_unique_concepts()` | List[str] | All concepts |
| `get_statement_facts()` | DataFrame | By statement type |
| `summarize()` | Dict | Summary stats |
| `query()` | FactQuery | Chainable builder |

### Financials Methods Summary

| Method | Returns | Purpose |
|--------|---------|---------|
| `get_financials()` | Financials | Annual statements |
| `get_quarterly_financials()` | Financials | Quarterly statements |
| `income_statement()` | Statement | Income statement |
| `balance_sheet()` | Statement | Balance sheet |
| `cashflow_statement()` | Statement | Cash flow |
| `statement_of_equity()` | Statement | Equity statement |
| `comprehensive_income()` | Statement | Comprehensive income |

### Statement.to_dataframe() Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_dimensions` | bool | True | Add dimension columns (Deprecated: use `view`) |
| `include_unit` | bool | False | Add unit column |
| `include_point_in_time` | bool | False | Add point-in-time column |
| `presentation` | bool | False | Match SEC HTML display format |
| `view` | str | 'standard' | View mode: 'standard', 'detailed', 'summary' |

---

## Update Log

| Date | Changes |
|------|---------|
| 2026-02-20 | Initial documentation - FactsView methods |
| 2026-02-20 | Added Financials and Statement methods |
| 2026-02-20 | Added complete storage scripts |
| 2026-02-20 | Added Statement.to_dataframe(presentation=True) documentation |
| | Added Statement.render() documentation |

---

*This document is maintained and updated as new methods are discovered.*
