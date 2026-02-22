# Standard Concept - Complete Explanation

> **What is `standard_concept` in Statement DataFrame?**

---

## Overview

The `standard_concept` column in the Statement DataFrame provides **standardized concept names** that map company-specific XBRL concepts to common financial terms.

### Example Mapping

| Company Concept (XBRL) | Standard Concept |
|------------------------|------------------|
| `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` | `Revenue` |
| `us-gaap:NetIncomeLoss` | `NetIncome` |
| `us-gaap:Assets` | `Total Assets` |

---

## How It Works

### 1. Concept Mapping System

EdgarTools uses a mapping system to standardize XBRL concepts:

```python
# From edgar/xbrl/standardization/concept_mappings.json
{
  "Revenue": [
    "us-gaap:Revenue",
    "us-gaap:Revenues",
    "us-gaap:RevenueFromContractWithCustomer",
    "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
  ],
  "NetIncome": [
    "us-gaap:NetIncomeLoss",
    "us-gaap:ProfitLoss"
  ],
  "Total Assets": [
    "us-gaap:Assets"
  ]
}
```

### 2. ConceptMapper Class

The `ConceptMapper` handles the mapping:

```python
from edgar.xbrl.standardization import ConceptMapper, initialize_default_mappings

# Initialize mappings
store = initialize_default_mappings()
mapper = ConceptMapper(store)

# Map a concept with context
context = {
    'statement_type': 'IncomeStatement',
    'level': 0,
    'is_total': True
}

standard_concept = mapper.map_concept(
    company_concept='us-gaap:Assets',
    label='Total Assets',
    context=context
)
# Returns: "Total Assets"
```

### 3. StandardConcept Enum

Standard concepts are defined as enums:

```python
from edgar.xbrl.standardization import StandardConcept

class StandardConcept(str, Enum):
    # Balance Sheet - Assets
    CASH_AND_EQUIVALENTS = "Cash and Cash Equivalents"
    TOTAL_ASSETS = "Total Assets"
    
    # Income Statement
    REVENUE = "Revenue"
    NET_INCOME = "Net Income"
    GROSS_PROFIT = "Gross Profit"
    OPERATING_INCOME = "Operating Income"
    
    # Cash Flow
    OPERATING_CASH_FLOW = "Operating Cash Flow"
    FREE_CASH_FLOW = "Free Cash Flow"
```

---

## Why Use Standard Concepts?

### 1. Cross-Company Comparison

Different companies use different XBRL tags for the same financial metric:

- **Apple**: `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax`
- **Microsoft**: `us-gaap:RevenueFromContractWithCustomer`
- **Google**: `us-gaap:Revenues`

All map to standard concept: **`Revenue`**

### 2. Consistent Analysis

```python
# Without standardization - need to check multiple concepts
if concept in ['us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax', 
               'us-gaap:Revenues', 
               'us-gaap:Revenue']:
    revenue = value

# With standardization - simple check
if standard_concept == 'Revenue':
    revenue = value
```

### 3. Automated Financial Analysis

```python
# Get all revenue rows across different companies
revenue_rows = df[df['standard_concept'] == 'Revenue']
```

---

## DataFrame Columns

### Statement.to_dataframe() Output

| Column | Description | Example |
|--------|-------------|---------|
| `concept` | Original XBRL concept | `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` |
| `label` | Human-readable label | `Net sales` |
| `standard_concept` | Standardized concept name | `Revenue` |
| `2025-09-27` | Period value | `416161000000` |

### Example Row

```json
{
  "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
  "label": "Net sales",
  "standard_concept": "Revenue",
  "2025-09-27": 416161000000,
  "2024-09-28": 391035000000,
  "2023-09-30": 383285000000
}
```

---

## Usage Examples

### Filter by Standard Concept

```python
from edgar import Company, set_identity
set_identity("your@email.com")

apple = Company("AAPL")
financials = apple.get_financials()
income = financials.income_statement()
df = income.to_dataframe()

# Filter by standard concept
revenue_row = df[df['standard_concept'] == 'Revenue']
net_income_row = df[df['standard_concept'] == 'NetIncome']
```

### Cross-Company Analysis

```python
# Get revenue for multiple companies
companies = ['AAPL', 'MSFT', 'GOOGL']
revenues = []

for ticker in companies:
    company = Company(ticker)
    financials = company.get_financials()
    income = financials.income_statement().to_dataframe()
    
    # Works regardless of company-specific XBRL tags
    rev_row = income[income['standard_concept'] == 'Revenue']
    if not rev_row.empty:
        revenues.append({
            'company': ticker,
            'revenue': rev_row.iloc[0]['2025-09-27']
        })
```

### Custom Mappings

```python
from edgar.xbrl.standardization import MappingStore

# Create custom mapping
store = MappingStore()
store.add_mapping(
    standard_concept="My Custom Revenue",
    company_concept="aapl:CustomRevenueTag"
)

# Use with ConceptMapper
mapper = ConceptMapper(store)
```

---

## Common Standard Concepts

### Income Statement
- `Revenue`
- `CostOfGoodsSold`
- `GrossProfit`
- `OperatingExpenses`
- `OperatingIncome`
- `NetIncome`
- `EarningsPerShareBasic`
- `EarningsPerShareDiluted`

### Balance Sheet
- `CashAndCashEquivalents`
- `TotalAssets`
- `TotalLiabilities`
- `StockholdersEquity`
- `TotalLiabilitiesAndEquity`

### Cash Flow
- `OperatingCashFlow`
- `CapitalExpenditures`
- `FreeCashFlow`

---

## Implementation Notes

### 1. Source of Mappings

Mappings are stored in:
```
edgar/xbrl/standardization/concept_mappings.json
```

### 2. Context-Aware Mapping

The mapper considers:
- Statement type (IncomeStatement, BalanceSheet, etc.)
- Hierarchy level
- Whether it's a total/subtotal
- Label text

### 3. Confidence Scoring

The mapper returns confidence scores for matches:
- Exact match: High confidence
- Similarity match: Medium confidence
- No match: None

---

## Adding to FINAL_COMPLETE_WITH_LOCATION

### Suggested JSON Structure

```json
{
  "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
  "label": "Net sales",
  "standard_concept": {
    "name": "Revenue",
    "description": "Total revenue from all sources",
    "category": "IncomeStatement",
    "mapping_confidence": "high",
    "alternative_names": [
      "us-gaap:Revenue",
      "us-gaap:Revenues",
      "us-gaap:RevenueFromContractWithCustomer"
    ]
  },
  "value_2025": 416161000000,
  "value_2024": 391035000000
}
```

### Python Code to Add Standard Concept

```python
from edgar.xbrl.standardization import initialize_default_mappings

def enrich_with_standard_concept(fact_dict):
    """Add standard concept info to fact dictionary"""
    store = initialize_default_mappings()
    
    concept = fact_dict.get('concept')
    if concept:
        # Get standard concept mapping
        standard = store.get_standard_concept(concept)
        if standard:
            fact_dict['standard_concept'] = {
                'name': standard,
                'all_mappings': store.get_company_concepts(standard)
            }
    
    return fact_dict
```

---

## References

- EdgarTools Standardization: `/dgunning/edgartools/edgar/xbrl/standardization/`
- Concept Mappings: `concept_mappings.json`
- ConceptMapper: `standardization.py`
- StandardConcept Enum: `standard_concept.py`

---

*Generated from Context7 documentation and source code analysis*
