#!/usr/bin/env python3
"""
Recreate FINAL_COMPLETE_WITH_LOCATIONS.json for 2025
Exact same structure - NO filters
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict
from edgar import set_identity, Company
from dotenv import load_dotenv

load_dotenv()
set_identity(os.getenv('EDGAR_IDENTITY', 'test@test.com'))

OUTPUT_FILE = '/Users/mohdsaeedafri/Documents/Documents/Code-Base/CoresightIQ/CapIQ/data/filings/AAPL/2025/10K/FINAL_COMPLETE_WITH_LOCATIONS_NEW.json'

def extract_ixbrl_id(html_content, fact_key):
    """Extract ixbrl ID from HTML"""
    if not fact_key:
        return None
    patterns = [
        rf'id="(fact-{re.escape(fact_key)})"',
        rf'id="({re.escape(fact_key)})"',
    ]
    for pattern in patterns:
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            return match.group(1)
    match = re.search(rf'id="([^"]*{re.escape(fact_key)}[^"]*)"', html_content, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def main():
    print("="*80)
    print("RECREATE FINAL_COMPLETE_WITH_LOCATIONS.json FOR 2025")
    print("="*80)
    
    # Get filing
    apple = Company("AAPL")
    filing = apple.get_filings(form="10-K").latest()
    
    print(f"\nFiling: {filing.form}")
    print(f"Date: {filing.filing_date}")
    
    # Get XBRL and HTML
    xbrl = filing.xbrl()
    html_content = filing.html()
    
    # Initialize output
    output_data = {
        "metadata": {
            "company": f"{filing.company} (AAPL)",
            "filing": "10-K FY2025",
            "filing_date": str(filing.filing_date),
            "total_records": 0,
            "with_html_location": 0,
            "without_location": 0,
            "coverage": "0%"
        },
        "data": {
            "summary": {
                "fiscal_year": 2025,
                "total_records": 0,
                "numeric": {
                    "total": 0,
                    "non_dimensioned": 0,
                    "dimensioned": 0
                },
                "text": {
                    "total": 0,
                    "non_dimensioned": 0,
                    "dimensioned": 0
                }
            },
            "numeric": {
                "non_dimensioned": [],
                "dimensioned": {}
            },
            "text": {
                "non_dimensioned": [],
                "dimensioned": {}
            }
        }
    }
    
    # Get all facts using to_dataframe
    print("\n[1/2] Getting facts from XBRL...")
    facts_df = xbrl.facts.to_dataframe()
    facts_list = facts_df.to_dict('records')
    
    print(f"Total facts: {len(facts_list)}")
    
    # Process all facts
    print("\n[2/2] Processing facts...")
    
    numeric_non_dim = []
    text_non_dim = []
    numeric_dim = {}
    text_dim = {}
    
    with_html = 0
    without_html = 0
    
    for i, fact in enumerate(facts_list):
        # Skip empty values
        value = fact.get('value')
        if not value or str(value).strip() == '':
            continue
        
        # Get fiscal year from fact
        fiscal_year = fact.get('fiscal_year')
        
        # Skip if fiscal year is not 2025 (like original had only FY2025 facts)
        if fiscal_year and fiscal_year != 2025:
            continue
        
        # Determine if numeric
        numeric_value_raw = fact.get('numeric_value')
        is_numeric = numeric_value_raw is not None and str(numeric_value_raw) not in ['nan', '']
        
        # Get numeric value
        numeric_value = None
        if is_numeric:
            try:
                numeric_value = float(numeric_value_raw)
            except:
                numeric_value = None
        
        # Get HTML location
        fact_key = fact.get('fact_key') or fact.get('id')
        ixbrl_id = extract_ixbrl_id(html_content, str(fact_key)) if fact_key else None
        
        html_loc = {
            "ixbrl_id": ixbrl_id,
            "start_position": None,
            "end_position": None
        }
        
        if ixbrl_id:
            with_html += 1
        else:
            without_html += 1
        
        # Get concept and label
        concept = fact.get('concept')
        label = fact.get('label') or fact.get('original_label') or concept
        
        # Determine period type
        period_type = fact.get('period_type')
        if not period_type:
            # Infer from period_instant vs period_start/end
            if fact.get('period_instant'):
                period_type = 'instant'
            else:
                period_type = 'duration'
        
        # Determine date
        date_val = fact.get('period_end') or fact.get('period_instant') or fact.get('period_start')
        
        # Get fiscal year from fact or infer from date
        fiscal_year = fact.get('fiscal_year')
        if not fiscal_year and date_val:
            # Extract year from date
            match = re.search(r'(\d{4})', str(date_val))
            if match:
                fy = int(match.group(1))
                # If date is in previous year but fiscal year is different, use fiscal_year from fact
                fiscal_year = fy
        
        # Build item - EXACT same as original
        item = {
            "concept": concept,
            "original_label": label,
            "value": str(value),
            "unit_ref": fact.get('unit_ref'),
            "decimals": str(fact.get('decimals')) if fact.get('decimals') is not None else None,
            "is_numeric": is_numeric,
            "numeric_value": numeric_value,
            "period_type": period_type,
            "date": str(date_val) if date_val else None,
            "fiscal_year": fiscal_year if fiscal_year else 2025,
            "is_dimensioned": bool(fact.get('is_dimensioned', False)),
            "dimension": fact.get('dimension'),
            "dimension_label": fact.get('dimension_label'),
            "member": fact.get('member'),
            "dimension_member_label": fact.get('dimension_member_label'),
            "full_dimension_label": fact.get('full_dimension_label'),
            "statement_type": fact.get('statement_type'),
            "preferred_sign": float(fact.get('preferred_sign')) if fact.get('preferred_sign') is not None else None,
            "html_location": html_loc
        }
        
        # Handle dimensions
        is_dim = bool(fact.get('is_dimensioned', False))
        dimension = fact.get('dimension')
        member = fact.get('member')
        
        if is_dim and dimension:
            # Get dimension name
            if ':' in dimension:
                dim_name = dimension.split(':')[-1].replace('Axis', '')
            else:
                dim_name = dimension
            
            # Get member name
            if member and ':' in member:
                member_name = member.split(':')[-1].replace('Member', '')
            elif member:
                member_name = member
            else:
                member_name = 'Unknown'
            
            # Add to dimensioned
            if is_numeric:
                target = numeric_dim
            else:
                target = text_dim
            
            # Initialize dimension
            if dim_name not in target:
                target[dim_name] = {
                    "dimension_name": dimension,
                    "dimension_label": fact.get('dimension_label', ''),
                    "total_items": 0,
                    "members": {}
                }
            
            # Initialize member
            if member_name not in target[dim_name]["members"]:
                target[dim_name]["members"][member_name] = {
                    "member_name": member,
                    "member_label": fact.get('dimension_member_label', ''),
                    "count": 0,
                    "items": []
                }
            
            target[dim_name]["total_items"] += 1
            target[dim_name]["members"][member_name]["count"] += 1
            target[dim_name]["members"][member_name]["items"].append(item)
        else:
            # Add to non-dimensioned
            if is_numeric:
                numeric_non_dim.append(item)
            else:
                text_non_dim.append(item)
        
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}...")
    
    # Update output
    output_data["data"]["numeric"]["non_dimensioned"] = numeric_non_dim
    output_data["data"]["numeric"]["dimensioned"] = numeric_dim
    output_data["data"]["text"]["non_dimensioned"] = text_non_dim
    output_data["data"]["text"]["dimensioned"] = text_dim
    
    # Update counts
    total_records = len(numeric_non_dim) + len(text_non_dim) + sum(d['total_items'] for d in numeric_dim.values()) + sum(d['total_items'] for d in text_dim.values())
    
    output_data["metadata"]["total_records"] = total_records
    output_data["metadata"]["with_html_location"] = with_html
    output_data["metadata"]["without_location"] = without_html
    output_data["metadata"]["coverage"] = f"{(with_html/total_records*100):.1f}%" if total_records > 0 else "0%"
    
    output_data["data"]["summary"]["total_records"] = total_records
    output_data["data"]["summary"]["numeric"]["non_dimensioned"] = len(numeric_non_dim)
    output_data["data"]["summary"]["numeric"]["dimensioned"] = sum(d['total_items'] for d in numeric_dim.values())
    output_data["data"]["summary"]["text"]["non_dimensioned"] = len(text_non_dim)
    output_data["data"]["summary"]["text"]["dimensioned"] = sum(d['total_items'] for d in text_dim.values())
    output_data["data"]["summary"]["numeric"]["total"] = output_data["data"]["summary"]["numeric"]["non_dimensioned"] + output_data["data"]["summary"]["numeric"]["dimensioned"]
    output_data["data"]["summary"]["text"]["total"] = output_data["data"]["summary"]["text"]["non_dimensioned"] + output_data["data"]["summary"]["text"]["dimensioned"]
    
    # Save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ Saved: {OUTPUT_FILE}")
    print(f"Total records: {total_records}")
    print(f"With HTML: {with_html}")
    print(f"Without HTML: {without_html}")

if __name__ == "__main__":
    main()
