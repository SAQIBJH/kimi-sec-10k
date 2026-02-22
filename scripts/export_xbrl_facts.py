#!/usr/bin/env python3
"""
XBRL Facts Export - Generalized Version
Supports multiple companies and years with robust error handling

Usage:
    python export_xbrl_facts.py

Configuration:
    Edit the CONFIG section below to set tickers, years, and other options
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

import pandas as pd
from edgar import Company, set_identity

# ========== CONFIGURATION ==========
@dataclass
class Config:
    """Configuration for the export process"""
    # Companies to process
    TICKERS: List[str] = field(default_factory=lambda: ["AAPL"])
    
    # Years to process
    YEARS: List[int] = field(default_factory=lambda: [2022, 2023, 2024, 2025])
    
    # Filing form type
    FORM: str = "10-K"
    
    # Output directory
    OUTPUT_BASE_DIR: str = "data/filings"
    
    # Processing options
    SKIP_EXISTING: bool = False      # Skip if output already exists
    DRY_RUN: bool = False            # Don't save files, just log
    LOG_LEVEL: str = "INFO"          # DEBUG, INFO, WARNING, ERROR
    
    # Identity for SEC
    SEC_IDENTITY: str = "Mohd Saeed Afri mohdsaeedafri@coresight.com"

# ========== STANDARD CONCEPT MAPPING ==========
# This can be extended for more companies
STANDARD_CONCEPT_MAP = {
    # ===== INCOME STATEMENT =====
    "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax": "Revenue",
    "us-gaap:Revenues": "Revenue",
    "us-gaap:SalesRevenueNet": "Revenue",
    "us-gaap:RevenueFromContractWithCustomerIncludingAssessedTax": "Revenue",
    "aapl:NetSales": "Revenue",
    "us-gaap:CostOfGoodsAndServicesSold": "Cost of Goods Sold",
    "us-gaap:CostOfRevenue": "Cost of Revenue",
    "us-gaap:CostOfGoodsSold": "Cost of Goods Sold",
    "us-gaap:GrossProfit": "Gross Profit",
    "us-gaap:GrossProfitLoss": "Gross Profit",
    "us-gaap:OperatingIncomeLoss": "Operating Income",
    "us-gaap:NetIncomeLoss": "Net Income",
    "us-gaap:ProfitLoss": "Net Income",
    
    # ===== BALANCE SHEET =====
    "us-gaap:Assets": "Total Assets",
    "us-gaap:AssetsCurrent": "Current Assets",
    "us-gaap:Liabilities": "Total Liabilities",
    "us-gaap:LiabilitiesCurrent": "Current Liabilities",
    "us-gaap:StockholdersEquity": "Stockholders Equity",
    
    # ===== CASH FLOW =====
    "us-gaap:NetCashProvidedByUsedInOperatingActivities": "Operating Cash Flow",
    "us-gaap:NetCashProvidedByUsedInInvestingActivities": "Investing Cash Flow",
    "us-gaap:NetCashProvidedByUsedInFinancingActivities": "Financing Cash Flow",
    
    # ===== DEI =====
    "dei:DocumentFiscalYearFocus": "Fiscal Year",
    "dei:EntityCentralIndexKey": "CIK",
    "dei:TradingSymbol": "Trading Symbol",
    "dei:EntityRegistrantName": "Company Name",
}

# ========== UTILITY FUNCTIONS ==========

def log(message: str, level: str = "INFO"):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def ensure_dir(path: str) -> Path:
    """Ensure directory exists"""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

# ========== STEP 1: FETCH DATA ==========

def download_filing(ticker: str, year: int, form_type: str) -> Optional[Any]:
    """Download filing for a company/year"""
    try:
        company = Company(ticker)
        filings = company.get_filings(form=form_type, year=year)
        
        if len(filings) == 0:
            log(f"No {form_type} filing found for {ticker} {year}", "WARNING")
            return None
        
        return filings.latest()
    except Exception as e:
        log(f"Error downloading filing for {ticker} {year}: {e}", "ERROR")
        return None

def extract_ixbrl_locations(html_content: str) -> Dict[Tuple[str, str], Dict]:
    """
    Extract all ixbrl tag locations from HTML content.
    Handles nested ixbrl tags and self-closing tags.
    Returns: {(concept, context): {ixbrl_id, start_pos, end_pos}}
    """
    locations = {}
    
    def extract_attrs(tag_content: str) -> Dict[str, str]:
        """Extract attributes from tag content"""
        attrs = {}
        patterns = [
            (r'contextRef="([^"]*)"', 'contextRef'),
            (r'name="([^"]*)"', 'name'),
            (r'id="([^"]*)"', 'id'),
        ]
        for pattern, key in patterns:
            m = re.search(pattern, tag_content, re.IGNORECASE)
            if m:
                attrs[key] = m.group(1)
        return attrs
    
    # Find all ixbrl tags (opening and self-closing)
    tag_pattern = r'<ix:(nonNumeric|nonFraction)\s+([^>]*?)(/?>)'
    
    for match in re.finditer(tag_pattern, html_content, re.IGNORECASE | re.DOTALL):
        tag_type = match.group(1)
        tag_content = match.group(2)
        is_self_closing = match.group(3) == '/>'
        start_pos = match.start()
        
        attrs = extract_attrs(tag_content)
        if 'name' not in attrs or 'id' not in attrs:
            continue
        
        concept = attrs['name'].lower()
        context_ref = attrs.get('contextRef', '').lower()
        
        if not context_ref:
            continue
        
        if is_self_closing:
            end_pos = match.end()
            key = (concept, context_ref)
            locations[key] = {
                'ixbrl_id': attrs['id'],
                'start_position': start_pos,
                'end_position': end_pos
            }
        else:
            # Handle nested tags
            search_start = match.end()
            depth = 1
            pos = search_start
            
            while depth > 0 and pos < len(html_content):
                next_open = html_content.find(f'<ix:{tag_type}', pos)
                next_close = html_content.find(f'</ix:{tag_type}>', pos)
                
                if next_close == -1:
                    break
                
                if next_open != -1 and next_open < next_close:
                    depth += 1
                    pos = next_open + len(f'<ix:{tag_type}')
                else:
                    depth -= 1
                    if depth == 0:
                        end_pos = next_close + len(f'</ix:{tag_type}>')
                        break
                    pos = next_close + len(f'</ix:{tag_type}>')
            
            if depth == 0:
                key = (concept, context_ref)
                locations[key] = {
                    'ixbrl_id': attrs['id'],
                    'start_position': start_pos,
                    'end_position': end_pos
                }
    
    return locations

def fetch_xbrl_facts(filing) -> Optional[pd.DataFrame]:
    """Fetch XBRL facts from a filing"""
    try:
        facts = filing.xbrl().facts
        return facts.to_dataframe()
    except Exception as e:
        log(f"Error fetching XBRL facts: {e}", "ERROR")
        return None

def step_1_fetch_data(ticker: str, year: int, form_type: str) -> Optional[Tuple]:
    """
    Step 1: Fetch all required data from SEC
    Returns: (html_content, ixbrl_locations, facts_df, filing_date) or None
    """
    log(f"Step 1: Fetching data for {ticker} {year}")
    
    # Download filing
    filing = download_filing(ticker, year, form_type)
    if not filing:
        return None
    
    filing_date = filing.filing_date
    log(f"  Filing date: {filing_date}")
    
    # Download HTML
    try:
        html_content = filing.html()
        log(f"  Downloaded HTML: {len(html_content)} bytes")
    except Exception as e:
        log(f"  Error downloading HTML: {e}", "ERROR")
        return None
    
    # Extract ixbrl locations
    ixbrl_locations = extract_ixbrl_locations(html_content)
    log(f"  Extracted {len(ixbrl_locations)} ixbrl locations")
    
    # Fetch XBRL facts
    facts_df = fetch_xbrl_facts(filing)
    if facts_df is None:
        return None
    log(f"  Fetched {len(facts_df)} XBRL facts")
    
    return (html_content, ixbrl_locations, facts_df, filing_date)

# ========== STEP 2: FILTER & DEDUPLICATE ==========

def filter_by_fiscal_year(facts_list: List[Dict], fiscal_year: int) -> List[Dict]:
    """Filter facts by fiscal year"""
    filtered = []
    
    for fact in facts_list:
        period_type = fact.get('period_type')
        include = False
        
        if period_type == 'duration':
            period_end = fact.get('period_end')
            if period_end:
                date_str = period_end.split('T')[0] if 'T' in str(period_end) else str(period_end)
                try:
                    fact_year = datetime.strptime(date_str, '%Y-%m-%d').year
                    if fact_year == fiscal_year:
                        include = True
                except ValueError:
                    pass
        
        elif period_type == 'instant':
            period_instant = fact.get('period_instant')
            if period_instant:
                date_str = period_instant.split('T')[0] if 'T' in str(period_instant) else str(period_instant)
                try:
                    fact_year = datetime.strptime(date_str, '%Y-%m-%d').year
                    if fact_year == fiscal_year:
                        include = True
                except ValueError:
                    pass
        
        if include:
            filtered.append(fact)
    
    return filtered

def remove_duplicates(facts: List[Dict]) -> List[Dict]:
    """Remove duplicate facts (same fields except fact_key)"""
    seen = set()
    unique_facts = []
    
    for fact in facts:
        fact_copy = {k: v for k, v in fact.items() if k != 'fact_key'}
        hash_key = json.dumps(fact_copy, sort_keys=True, default=str)
        
        if hash_key not in seen:
            seen.add(hash_key)
            unique_facts.append(fact)
    
    return unique_facts

def step_2_filter_dedupe(facts_df: pd.DataFrame, year: int) -> Tuple[List[Dict], int]:
    """
    Step 2: Filter and deduplicate facts
    Returns: (filtered_facts, actual_fiscal_year)
    """
    log("Step 2: Filtering and deduplicating")
    
    facts_list = json.loads(facts_df.to_json(orient="records", date_format='iso'))
    
    # Determine fiscal year
    fiscal_year = year
    fy_facts = facts_df[facts_df['concept'] == 'dei:DocumentFiscalYearFocus']
    if len(fy_facts) > 0:
        fiscal_year = int(fy_facts.iloc[0]['value'])
    log(f"  Fiscal year: {fiscal_year}")
    
    # Filter by fiscal year
    filtered = filter_by_fiscal_year(facts_list, fiscal_year)
    log(f"  After year filter: {len(filtered)} facts")
    
    # Remove duplicates
    unique_facts = remove_duplicates(filtered)
    removed = len(filtered) - len(unique_facts)
    log(f"  After dedup: {len(unique_facts)} facts (removed {removed})")
    
    return unique_facts, fiscal_year

# ========== STEP 3: ENRICH ==========

def get_standard_concept(concept: str) -> str:
    """Get standard concept name for a company concept"""
    if concept in STANDARD_CONCEPT_MAP:
        return STANDARD_CONCEPT_MAP[concept]
    
    # Fallback: convert CamelCase to words
    concept_name = concept.split(':')[-1] if ':' in concept else concept
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', concept_name)

def get_html_location(fact: Dict, ixbrl_locations: Dict) -> Optional[Dict]:
    """Get html_location for a fact"""
    concept = fact.get('concept', '').lower()
    context_ref = fact.get('context_ref', '').lower()
    key = (concept, context_ref)
    return ixbrl_locations.get(key)

def step_3_enrich(facts: List[Dict], ixbrl_locations: Dict) -> List[Dict]:
    """
    Step 3: Enrich facts with standard_concept and html_location
    """
    log("Step 3: Enriching facts")
    
    enriched_count = 0
    location_count = 0
    
    for fact in facts:
        # Add standard_concept
        concept = fact.get('concept', '')
        fact['standard_concept'] = get_standard_concept(concept)
        if concept in STANDARD_CONCEPT_MAP:
            enriched_count += 1
        
        # Add html_location
        location = get_html_location(fact, ixbrl_locations)
        if location:
            fact['html_location'] = location
            location_count += 1
        else:
            fact['html_location'] = None
    
    log(f"  Added standard_concept: {enriched_count}/{len(facts)}")
    log(f"  Added html_location: {location_count}/{len(facts)} ({location_count/len(facts)*100:.1f}%)")
    
    return facts

# ========== STEP 4: CLEAN ==========

def clean_text_value(text: str) -> str:
    """Clean text value: remove HTML, normalize unicode, normalize whitespace"""
    if not isinstance(text, str):
        return text
    
    # Remove HTML tags
    cleaned = re.sub(r'<[^>]+>', '', text)
    
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Decode HTML entities
    import html
    cleaned = html.unescape(cleaned)
    
    # Normalize unicode to ASCII
    unicode_replacements = [
        ('\u2018', "'"), ('\u2019', "'"), ('\u201a', ","), ('\u201b', "'"),  # Single quotes
        ('\u201c', '"'), ('\u201d', '"'), ('\u201e', '"'), ('\u201f', '"'),  # Double quotes
        ('\u2010', '-'), ('\u2011', '-'), ('\u2012', '-'), ('\u2013', '-'),  # Dashes
        ('\u2014', '-'), ('\u2015', '-'),                                    # More dashes
        ('\u00ae', '(R)'), ('\u00a9', '(C)'), ('\u2122', '(TM)'),           # Symbols
        ('\u00b0', ' deg'), ('\u20ac', 'EUR'), ('\u00a3', 'GBP'),           # Currency
        ('\u00a5', 'JPY'), ('\u00a2', 'c'),                                 # More currency
    ]
    
    for unicode_char, ascii_char in unicode_replacements:
        cleaned = cleaned.replace(unicode_char, ascii_char)
    
    return cleaned.strip()

def step_4_clean(facts: List[Dict]) -> List[Dict]:
    """
    Step 4: Clean text values
    """
    log("Step 4: Cleaning text values")
    
    cleaned_count = 0
    textblock_count = 0
    
    for fact in facts:
        value = fact.get('value')
        if value and isinstance(value, str):
            has_html = bool(re.search(r'<[^>]+>', value))
            has_special = any(ord(c) > 127 for c in value)
            
            if has_html or has_special:
                fact['value'] = clean_text_value(value)
                cleaned_count += 1
                
                concept = fact.get('concept', '')
                if concept.endswith('TextBlock'):
                    textblock_count += 1
    
    log(f"  Cleaned {cleaned_count} values ({textblock_count} TextBlock + {cleaned_count - textblock_count} other)")
    return facts

# ========== STEP 5: FINALIZE ==========

def step_5_finalize(facts: List[Dict]) -> List[Dict]:
    """
    Step 5: Finalize by removing internal fields
    """
    log("Step 5: Finalizing")
    
    # Remove internal fields
    fields_to_remove = ['fact_key']
    
    for fact in facts:
        for field in fields_to_remove:
            fact.pop(field, None)
    
    return facts

# ========== SAVE OUTPUT ==========

def save_output(facts: List[Dict], ticker: str, year: int, config: Config) -> bool:
    """Save output to JSON file"""
    output_dir = Path(config.OUTPUT_BASE_DIR) / ticker / str(year) / config.FORM
    output_path = output_dir / "FINAL_FACTS_FILTERED.json"
    
    if config.DRY_RUN:
        log(f"  DRY RUN: Would save to {output_path}")
        return True
    
    try:
        ensure_dir(output_dir)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(facts, f, indent=2, ensure_ascii=False)
        log(f"  Saved: {output_path}")
        return True
    except Exception as e:
        log(f"  Error saving output: {e}", "ERROR")
        return False

def save_html(html_content: str, ticker: str, year: int, config: Config) -> bool:
    """Save HTML file"""
    output_dir = Path(config.OUTPUT_BASE_DIR) / ticker / str(year) / config.FORM
    html_path = output_dir / "filing.html"
    
    if config.DRY_RUN:
        return True
    
    try:
        ensure_dir(output_dir)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        log(f"  Saved HTML: {html_path}")
        return True
    except Exception as e:
        log(f"  Error saving HTML: {e}", "ERROR")
        return False

# ========== MAIN PROCESSING ==========

def process_company_year(ticker: str, year: int, config: Config) -> bool:
    """Process a single company-year combination"""
    print("\n" + "="*60)
    print(f"🔄 Processing: {ticker} - Year {year}")
    print("="*60)
    
    # Check if output already exists
    output_path = Path(config.OUTPUT_BASE_DIR) / ticker / str(year) / config.FORM / "FINAL_FACTS_FILTERED.json"
    if config.SKIP_EXISTING and output_path.exists():
        log(f"Skipping (output exists): {output_path}")
        return True
    
    # Step 1: Fetch data
    data = step_1_fetch_data(ticker, year, config.FORM)
    if not data:
        return False
    
    html_content, ixbrl_locations, facts_df, filing_date = data
    
    # Save HTML
    save_html(html_content, ticker, year, config)
    
    # Step 2: Filter & deduplicate
    facts, fiscal_year = step_2_filter_dedupe(facts_df, year)
    
    # Step 3: Enrich
    facts = step_3_enrich(facts, ixbrl_locations)
    
    # Step 4: Clean
    facts = step_4_clean(facts)
    
    # Step 5: Finalize
    facts = step_5_finalize(facts)
    
    # Save output
    if not save_output(facts, ticker, year, config):
        return False
    
    # Summary
    all_concepts = set(f['concept'] for f in facts)
    with_location = sum(1 for f in facts if f.get('html_location'))
    
    print(f"\n📊 Summary for {ticker} FY{fiscal_year}:")
    print(f"   Total facts: {len(facts)}")
    print(f"   Unique concepts: {len(all_concepts)}")
    print(f"   With html_location: {with_location} ({with_location/len(facts)*100:.1f}%)")
    
    return True

def main():
    """Main entry point"""
    config = Config()
    
    # Set identity
    set_identity(config.SEC_IDENTITY)
    
    # Statistics
    success_count = 0
    fail_count = 0
    total = len(config.TICKERS) * len(config.YEARS)
    
    print("="*60)
    print("🚀 XBRL Facts Export - Generalized")
    print("="*60)
    print(f"Companies: {', '.join(config.TICKERS)}")
    print(f"Years: {', '.join(map(str, config.YEARS))}")
    print(f"Form: {config.FORM}")
    print(f"Total combinations: {total}")
    print("="*60)
    
    # Process each combination
    for ticker in config.TICKERS:
        for year in config.YEARS:
            try:
                if process_company_year(ticker, year, config):
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                log(f"Unexpected error processing {ticker} {year}: {e}", "ERROR")
                fail_count += 1
    
    # Final summary
    print("\n" + "="*60)
    print("🏁 FINAL SUMMARY")
    print("="*60)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📊 Total: {total}")
    print(f"📁 Output: {config.OUTPUT_BASE_DIR}/<TICKER>/<YEAR>/{config.FORM}/FINAL_FACTS_FILTERED.json")
    print("="*60)
    
    if fail_count == 0:
        print("🎉 All combinations processed successfully!")
    else:
        print(f"⚠️  {fail_count} combination(s) failed. Check logs above.")

if __name__ == "__main__":
    main()
