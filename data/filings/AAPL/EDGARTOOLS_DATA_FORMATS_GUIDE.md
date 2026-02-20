# EDGARTOOLS DATA FORMATS - COMPLETE GUIDE

## 1. XBRL FACTS DATAFRAME (53 COLUMNS)

**File:** `full_edgartools_data.json` (1,131 records)

### Important Columns:

| # | Column | Description | Example |
|---|--------|-------------|---------|
| 1 | **concept** | XBRL concept name | `us-gaap:NetIncomeLoss` |
| 2 | **value** | The actual value | `112010000000` |
| 3 | **label** | Display label | `Net income` |
| 4 | **numeric_value** | Numeric version | `112010000000.0` |
| 5 | **unit_ref** | Unit (USD, shares) | `u-1` |
| 6 | **decimals** | Decimal precision | `-6` (means millions) |
| 7 | **period_type** | duration or instant | `duration` |
| 8 | **period_start** | Start date | `2024-09-29` |
| 9 | **period_end** | End date | `2025-09-27` |
| 10 | **period_instant** | For balance sheet | `2025-09-27` |
| 11 | **fiscal_year** | Filing year | `2025` |
| 12 | **fiscal_period** | FY or Q1/Q2/Q3 | `FY` |
| 13 | **is_dimensioned** | Has breakdown | `False` |
| 14 | **dimension** | Dimension axis | `us-gaap:ProductAxis` |
| 15 | **member** | Dimension member | `us-gaap:IPhoneMember` |
| 16 | **statement_type** | Which statement | `IncomeStatement` |
| 17 | **balance** | debit/credit | `credit` |
| 18 | **context_ref** | Context ID | `c-1` |
| 19 | **fact_key** | Unique fact ID | `dei_AmendmentFlag_c-1` |

### Dimension Columns (for breakdowns):
- `dim_srt_ProductOrServiceAxis` - Products vs Services
- `dim_us-gaap_StatementBusinessSegmentsAxis` - Business segments
- `dim_srt_StatementGeographicalAxis` - Geographic regions
- `dim_us-gaap_FairValueByFairValueHierarchyLevelAxis` - Level 1/2/3
- etc.

---

## 2. HOW DATA COMES FROM EDGARTOOLS

### A. DataFrame Format (Default)
```python
xbrl = filing.xbrl()
facts = xbrl.facts.to_dataframe()  # pandas DataFrame
```
**Output:** 1,131 rows × 53 columns

### B. JSON Format
```python
import json
json_data = facts.to_json(orient='records')
```
**Output:** Array of objects

### C. CSV Format
```python
facts.to_csv('output.csv', index=False)
```
**Output:** CSV file with 53 columns

### D. Financial Statements (Separate DataFrames)
```python
income = xbrl.statements.income_statement().to_dataframe()
balance = xbrl.statements.balance_sheet().to_dataframe()
cashflow = xbrl.statements.cash_flow_statement().to_dataframe()
```
**Output:** Structured financial statements

---

## 3. OTHER OUTPUT FORMATS

### Markdown (LLM-friendly)
```python
md = filing.markdown()
```
- Size: 279,757 chars
- Lines: 1,933
- Format: Clean markdown with tables

### HTML (Raw)
```python
html = filing.html()
```
- Size: 1,520,208 chars
- Format: iXBRL with embedded tags
- Use: For rendering/display

### Text (Plain)
```python
text = filing.text()
```
- Size: 261,019 chars
- Format: Plain text extraction
- Use: For simple text analysis

### TenK Object (Structured)
```python
obj = filing.obj()
sections = obj.sections  # 23 sections
```
- Access by: `obj.sections['part_i_item_1a'].text()`
- Use: For section-by-section analysis

---

## 4. KEY POINTS

### Why Tags Appear:
The `concept` column has XBRL tags like:
- `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax`
- `us-gaap:NetIncomeLoss`
- `dei:EntityCentralIndexKey`

These are **standard XBRL taxonomy names** - not display labels!

### How to Get Display Labels:
Use the `label` column:
- Concept: `us-gaap:NetIncomeLoss`
- Label: `Net income`

### Period Columns Explained:
- `period_end`: For income statement (duration)
- `period_instant`: For balance sheet (point in time)
- `fiscal_year`: The filing year (2025)

### Dimension Columns:
When `is_dimensioned=True`, you get:
- `dimension`: The axis (e.g., ProductOrServiceAxis)
- `member`: The value (e.g., iPhone, Mac, Services)
- This gives you breakdowns!

---

## 5. SIMPLE JSON STRUCTURE

### Option 1: Just Metric + Value
```json
[
  {"metric": "NetIncomeLoss", "value": "112010000000"},
  {"metric": "Revenue", "value": "416161000000"}
]
```

### Option 2: With Label
```json
[
  {"metric": "NetIncomeLoss", "label": "Net income", "value": "112010000000"},
  {"metric": "Revenue", "label": "Net sales", "value": "416161000000"}
]
```

### Option 3: Full Data
```json
[
  {
    "metric": "NetIncomeLoss",
    "label": "Net income",
    "value": "112010000000",
    "date": "2025-09-27",
    "fiscal_year": 2025,
    "concept": "us-gaap:NetIncomeLoss"
  }
]
```

---

## 6. FILES GENERATED

1. `full_edgartools_data.json` - All 53 columns, 1,131 records
2. `simple_metrics.json` - Just metric + value
3. `metrics_with_labels.json` - Metric + label + value + location
4. `EDGARTOOLS_DATA_FORMATS_GUIDE.md` - This guide

---

**Bhai ab samajh aaya? Kya chahiye?** 🎯
