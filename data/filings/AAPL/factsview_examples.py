"""
FactsView Examples - XBRL Facts Filtering and Analysis

This script demonstrates the powerful FactsView methods available through:
    filing.xbrl().facts

These methods allow you to filter, search, and analyze XBRL facts from filings.
"""

from edgar import Company, set_identity
import os
from dotenv import load_dotenv

# Load environment and set identity
load_dotenv()
identity = os.getenv('EDGAR_IDENTITY', 'default@email.com')
set_identity(identity)

print("=" * 80)
print("FACTSVIEW EXAMPLES - XBRL Facts Filtering")
print("=" * 80)

# Get a specific filing with XBRL data
apple = Company("AAPL")
filing = apple.get_filings(form="10-K").latest()
xbrl = filing.xbrl()

# Access FactsView through xbrl().facts
facts = xbrl.facts
print(f"\nFiling: {filing.form} - {filing.filing_date}")
print(f"FactsView contains {len(facts.get_facts())} facts")

# =============================================================================
# 1. get_facts_by_concept(concept_name)
# =============================================================================
print("\n" + "=" * 80)
print("1. get_facts_by_concept(concept_name)")
print("=" * 80)
print("Get all facts for a specific XBRL concept - RETURNS DataFrame")

revenue_facts = facts.get_facts_by_concept("us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax")
print(f"\nRevenue facts found: {len(revenue_facts)} rows")
if len(revenue_facts) > 0:
    print("\nRevenue fact details (first 3 rows):")
    print(revenue_facts.head(3)[['concept', 'value', 'fiscal_year']].to_string())

assets_facts = facts.get_facts_by_concept("us-gaap:Assets")
print(f"\nAssets facts found: {len(assets_facts)} rows")

# =============================================================================
# 2. get_facts_by_period(period_key) / get_facts_by_fiscal_period()
# =============================================================================
print("\n" + "=" * 80)
print("2. Period-based Filtering")
print("=" * 80)
print("Get facts filtered by fiscal periods")

# Get available periods for Income Statement
period_views = facts.get_available_period_views("IncomeStatement")
print(f"\nAvailable period views for IncomeStatement: {len(period_views)}")
if period_views:
    print("Period view structure:")
    pv = period_views[0]
    print(f"  - Name: {pv.get('name')}")
    print(f"  - Description: {pv.get('description')}")
    print(f"  - Facts count: {pv.get('facts_count')}")

# =============================================================================
# 3. get_facts_with_dimensions()
# =============================================================================
print("\n" + "=" * 80)
print("3. get_facts_with_dimensions()")
print("=" * 80)
print("Get only facts that have dimensions (breakdowns) - RETURNS DataFrame")

dimensioned_facts = facts.get_facts_with_dimensions()
print(f"\nFacts with dimensions: {len(dimensioned_facts)} rows")

if len(dimensioned_facts) > 0:
    print("\nSample dimensioned facts:")
    cols = ['concept', 'value']
    if 'dimensions' in dimensioned_facts.columns:
        cols.append('dimensions')
    print(dimensioned_facts.head(3)[[c for c in cols if c in dimensioned_facts.columns]].to_string())

# =============================================================================
# 4. query() - Chainable Query Builder
# =============================================================================
print("\n" + "=" * 80)
print("4. query() - Chainable Query Builder")
print("=" * 80)
print("Build complex queries using chainable methods - RETURNS list of facts")

# Simple query by concept - returns list of dicts
revenue_query_result = facts.query().by_concept("Revenue").execute()
print(f"\nFacts with 'Revenue' in concept: {len(revenue_query_result)} items (list)")
if revenue_query_result:
    sample = revenue_query_result[0]
    print(f"  Sample: {sample.get('concept')} = {sample.get('value')}")

# Query with multiple filters - chain methods
income_2025_result = facts.query()\
    .by_statement_type("IncomeStatement")\
    .by_fiscal_year(2025)\
    .execute()
print(f"Income statement facts for FY2025: {len(income_2025_result)} items (list)")

# Convert list of dicts to DataFrame for easier viewing
import pandas as pd
if income_2025_result:
    income_df = pd.DataFrame(income_2025_result)
    print("\nSample income statement 2025 facts (converted to DataFrame):")
    print(income_df.head(5)[['concept', 'value']].to_string())

# Query with dimension filter - use to_dataframe() instead of execute()
dimensioned_df = facts.query().with_dimensions().to_dataframe()
print(f"\nFacts with dimensions (via query to_dataframe): {len(dimensioned_df)} rows")

# =============================================================================
# 5. search_facts(query_string)
# =============================================================================
print("\n" + "=" * 80)
print("5. search_facts(query_string)")
print("=" * 80)
print("Text search across concepts and values - RETURNS DataFrame")

# Search for cash-related facts
cash_search = facts.search_facts("cash")
print(f"\nFacts matching 'cash': {len(cash_search)} rows")

# Search for income-related facts
income_search = facts.search_facts("income")
print(f"Facts matching 'income': {len(income_search)} rows")

if len(income_search) > 0:
    print("\nSample income search results:")
    display_cols = ['concept', 'value', 'label']
    print(income_search.head(3)[[c for c in display_cols if c in income_search.columns]].to_string())

# =============================================================================
# Additional Useful Methods
# =============================================================================
print("\n" + "=" * 80)
print("ADDITIONAL USEFUL METHODS")
print("=" * 80)

# Get unique concepts
concepts = facts.get_unique_concepts()
print(f"\nTotal unique concepts: {len(concepts)}")
print(f"Sample concepts: {concepts[:5]}")

# Get unique dimensions
dimensions = facts.get_unique_dimensions()
print(f"\nTotal unique dimensions: {len(dimensions)}")
if dimensions:
    dim_keys = list(dimensions.keys())[:3]
    print(f"Sample dimension axes:")
    for key in dim_keys:
        members = list(dimensions[key])[:3]
        print(f"  - {key}: {members}")

# Convert all facts to DataFrame
print("\n" + "-" * 40)
print("Converting all facts to DataFrame:")
df = facts.to_dataframe()
print(f"DataFrame shape: {df.shape}")
print(f"\nColumns: {list(df.columns)}")

# =============================================================================
# Advanced Query Examples
# =============================================================================
print("\n" + "=" * 80)
print("ADVANCED QUERY EXAMPLES")
print("=" * 80)

# Example 1: Get all cash facts using query and convert to dataframe
cash_query_df = facts.query().by_concept("Cash").to_dataframe()
print(f"\n1. Cash facts (via query to_dataframe): {len(cash_query_df)} rows")
if len(cash_query_df) > 0:
    print(cash_query_df[['concept', 'value', 'fiscal_year']].head(3).to_string())

# Example 2: Balance sheet facts with instant period type
balance_instant = facts.query()\
    .by_statement_type("BalanceSheet")\
    .by_period_type("instant")\
    .to_dataframe()
print(f"\n2. Balance sheet instant facts: {len(balance_instant)} rows")

# Example 3: Get specific concept by exact match
gross_profit = facts.query()\
    .by_concept("GrossProfit")\
    .to_dataframe()
print(f"\n3. Gross profit facts: {len(gross_profit)} rows")

# =============================================================================
# Summary
# =============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
FactsView Key Methods (return DataFrames):
-----------------------------------------
✓ get_facts_by_concept(concept)    - Filter by XBRL concept name
✓ get_facts_by_period(period_key)  - Filter by calendar period key
✓ get_facts_with_dimensions()      - Get dimensioned/breakdown facts
✓ search_facts(text)               - Text search across facts
✓ to_dataframe()                   - Convert all facts to DataFrame

Query Builder Pattern (FactQuery):
---------------------------------
query = facts.query()              # Returns FactQuery object
query.by_concept(pattern)          # Filter by concept (regex)
query.by_label(pattern)            # Filter by label (regex)
query.by_fiscal_year(year)         # Filter by fiscal year
query.by_statement_type(type)      - Filter by statement type
query.by_period_type(type)         - Filter by period type (instant/duration)
query.with_dimensions()            - Only facts with dimensions
query.by_dimension(dim)            - Filter by specific dimension
query.by_unit(unit)                - Filter by unit
query.execute()                    - Execute and return LIST of facts
query.to_dataframe()               - Execute and return DataFrame

Access Pattern:
--------------
company = Company("AAPL")
filing = company.get_filings(form="10-K").latest()
facts = filing.xbrl().facts  # Returns FactsView object

Key Differences:
---------------
• Direct methods (get_facts_by_*, search_facts) → return DataFrames
• query() builder methods → use .execute() for list, .to_dataframe() for DataFrame
""")
