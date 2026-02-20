#!/usr/bin/env python3
"""
SEC Filing Search Engine - Multi-Company, Multi-Year Support
Handles FINAL_COMPLETE_WITH_LOCATIONS.json structure
"""

import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class SearchResult:
    """Single search result card data"""
    # Display fields (shown in UI)
    original_label: str
    value: str
    formatted_value: str
    dimension_label: Optional[str]  # iPhone, Americas, Europe, etc.
    
    # Additional context (shown in expanded view)
    concept: str
    fiscal_year: int
    date: str
    statement_type: Optional[str]
    unit_ref: Optional[str]
    period_type: Optional[str]
    
    # Dimension info
    is_dimensioned: bool
    dimension: Optional[str]  # full axis name
    member: Optional[str]     # full member name
    full_dimension_label: Optional[str]
    
    # HTML location (NOT shown to user, used for scroll)
    html_location: Optional[Dict[str, Any]]
    
    # Source tracking (for multi-company support)
    company_ticker: str
    company_name: str
    filing_type: str
    filing_date: str


class SECFilingSearchEngine:
    """
    Search engine for SEC filing JSON data
    Supports multiple companies and multiple years
    """
    
    def __init__(self, json_path: str):
        self.json_path = Path(json_path)
        self.data = None
        self.metadata = None
        self._flat_index = []  # Pre-built index for fast search
        self._load_data()
        self._build_index()
    
    def _load_data(self):
        """Load JSON file"""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.metadata = self.data.get('metadata', {})
    
    def _build_index(self):
        """Build flat index of all items for fast searching"""
        company = self.metadata.get('company', 'Unknown')
        ticker = self._extract_ticker(company)
        filing_type = self.metadata.get('filing', 'Unknown')
        filing_date = self.metadata.get('filing_date', 'Unknown')
        
        data_section = self.data.get('data', {})
        
        # Process numeric items
        numeric = data_section.get('numeric', {})
        self._index_numeric_items(numeric, ticker, company, filing_type, filing_date)
        
        # Process text items
        text = data_section.get('text', {})
        self._index_text_items(text, ticker, company, filing_type, filing_date)
        
        print(f"📊 Index built: {len(self._flat_index)} items")
    
    def _extract_ticker(self, company_str: str) -> str:
        """Extract ticker from company string like 'Apple Inc. (AAPL)'"""
        match = re.search(r'\(([A-Z]+)\)', company_str)
        return match.group(1) if match else 'UNKNOWN'
    
    def _index_numeric_items(self, numeric: Dict, ticker: str, company: str, 
                             filing_type: str, filing_date: str):
        """Index all numeric items (both dimensioned and non-dimensioned)"""
        
        # Non-dimensioned numeric items
        for item in numeric.get('non_dimensioned', []):
            self._flat_index.append(self._create_result(item, ticker, company, 
                                                        filing_type, filing_date))
        
        # Dimensioned numeric items
        for dim_key, dim_data in numeric.get('dimensioned', {}).items():
            for member_key, member_data in dim_data.get('members', {}).items():
                for item in member_data.get('items', []):
                    self._flat_index.append(self._create_result(item, ticker, company,
                                                                filing_type, filing_date))
    
    def _index_text_items(self, text: Dict, ticker: str, company: str,
                          filing_type: str, filing_date: str):
        """Index all text items"""
        
        # Non-dimensioned text items
        for item in text.get('non_dimensioned', []):
            self._flat_index.append(self._create_result(item, ticker, company,
                                                        filing_type, filing_date))
        
        # Dimensioned text items
        for dim_key, dim_data in text.get('dimensioned', {}).items():
            for member_key, member_data in dim_data.get('members', {}).items():
                for item in member_data.get('items', []):
                    self._flat_index.append(self._create_result(item, ticker, company,
                                                                filing_type, filing_date))
    
    def _create_result(self, item: Dict, ticker: str, company: str,
                       filing_type: str, filing_date: str) -> SearchResult:
        """Create SearchResult from JSON item"""
        
        # Format value for display
        value = item.get('value', '')
        formatted_value = self._format_value(value, item.get('unit_ref'), 
                                              item.get('is_numeric', False),
                                              item.get('decimals'))
        
        return SearchResult(
            original_label=item.get('original_label', ''),
            value=value,
            formatted_value=formatted_value,
            dimension_label=item.get('dimension_label'),  # iPhone, Americas, etc.
            concept=item.get('concept', ''),
            fiscal_year=item.get('fiscal_year', 0),
            date=item.get('date', ''),
            statement_type=item.get('statement_type'),
            unit_ref=item.get('unit_ref'),
            period_type=item.get('period_type'),
            is_dimensioned=item.get('is_dimensioned', False),
            dimension=item.get('dimension'),
            member=item.get('member'),
            full_dimension_label=item.get('full_dimension_label'),
            html_location=item.get('html_location'),
            company_ticker=ticker,
            company_name=company,
            filing_type=filing_type,
            filing_date=filing_date
        )
    
    def _format_value(self, value: str, unit_ref: Optional[str], 
                      is_numeric: bool, decimals: Optional[str]) -> str:
        """Format value for display"""
        if not is_numeric or not value:
            return value
        
        try:
            num = float(value)
            
            # Handle large numbers (millions/billions)
            if abs(num) >= 1e9:
                return f"${num/1e9:.2f}B"
            elif abs(num) >= 1e6:
                return f"${num/1e6:.2f}M"
            elif abs(num) >= 1e3:
                return f"${num/1e3:.2f}K"
            else:
                return f"${num:,.2f}"
        except (ValueError, TypeError):
            return value
    
    def search(self, query: str, filters: Optional[Dict] = None) -> List[SearchResult]:
        """
        Search by original_label
        
        Args:
            query: Search string (case-insensitive partial match)
            filters: Optional filters like {'fiscal_year': 2025, 'is_numeric': True}
        
        Returns:
            List of SearchResult objects grouped for display
        """
        query_lower = query.lower()
        results = []
        
        for result in self._flat_index:
            # Match by original_label (partial, case-insensitive)
            if result.original_label and query_lower in result.original_label.lower():
                # Apply filters if provided
                if self._apply_filters(result, filters):
                    results.append(result)
        
        # Sort: non-dimensioned first, then by dimension_label
        results.sort(key=lambda x: (x.is_dimensioned, x.dimension_label or ''))
        
        return results
    
    def _apply_filters(self, result: SearchResult, filters: Optional[Dict]) -> bool:
        """Apply filters to result"""
        if not filters:
            return True
        
        if 'fiscal_year' in filters and result.fiscal_year != filters['fiscal_year']:
            return False
        if 'is_numeric' in filters and result.concept.startswith('us-gaap:') == False:
            # Simplistic check - improve as needed
            pass
        if 'statement_type' in filters and result.statement_type != filters['statement_type']:
            return False
        
        return True
    
    def get_unique_labels(self) -> List[str]:
        """Get all unique original_labels (for autocomplete)"""
        labels = set()
        for result in self._flat_index:
            if result.original_label:
                labels.add(result.original_label)
        return sorted(labels)
    
    def get_stats(self) -> Dict:
        """Get search index statistics"""
        return {
            'total_indexed': len(self._flat_index),
            'company': self.metadata.get('company'),
            'filing': self.metadata.get('filing'),
            'filing_date': self.metadata.get('filing_date'),
            'unique_labels': len(self.get_unique_labels())
        }


class ResultsGrouper:
    """Groups search results for UI display"""
    
    @staticmethod
    def group_by_dimension(results: List[SearchResult]) -> Dict[str, List[SearchResult]]:
        """
        Group results by dimension type
        Returns: {
            'non_dimensioned': [...],
            'Products': [...],
            'Geography': [...],
            'Segment': [...]
        }
        """
        groups = {
            'non_dimensioned': [],
            'dimensioned': {}
        }
        
        for result in results:
            if not result.is_dimensioned:
                groups['non_dimensioned'].append(result)
            else:
                # Use dimension_label as group key (Products, Americas, etc.)
                dim_label = result.dimension_label or 'Other'
                if dim_label not in groups['dimensioned']:
                    groups['dimensioned'][dim_label] = []
                groups['dimensioned'][dim_label].append(result)
        
        return groups
    
    @staticmethod
    def format_for_display(results: List[SearchResult]) -> List[Dict]:
        """Format results for frontend display"""
        display_cards = []
        
        for result in results:
            card = {
                # Main display (what user sees)
                'label': result.original_label,
                'value': result.formatted_value,
                'dimension': result.dimension_label,  # iPhone, Americas, etc.
                
                # Hidden data (for click handlers)
                '_meta': {
                    'concept': result.concept,
                    'fiscal_year': result.fiscal_year,
                    'html_location': result.html_location,  # For scroll
                    'company_ticker': result.company_ticker,
                    'is_dimensioned': result.is_dimensioned
                }
            }
            display_cards.append(card)
        
        return display_cards


# ============== TEST & DEMONSTRATION ==============

def test_search():
    """Test the search engine with detailed logs"""
    
    json_path = "/Users/mohdsaeedafri/Documents/Documents/Code-Base/CoresightIQ/CapIQ/data/filings/AAPL/FINAL_COMPLETE_WITH_LOCATIONS.json"
    
    print("=" * 80)
    print("🔍 SEC FILING SEARCH ENGINE - TEST")
    print("=" * 80)
    
    # Initialize
    print("\n📂 Loading JSON and building index...")
    engine = SECFilingSearchEngine(json_path)
    
    stats = engine.get_stats()
    print(f"\n📊 INDEX STATS:")
    print(f"   Company: {stats['company']}")
    print(f"   Filing: {stats['filing']}")
    print(f"   Filing Date: {stats['filing_date']}")
    print(f"   Total Items: {stats['total_indexed']:,}")
    print(f"   Unique Labels: {stats['unique_labels']:,}")
    
    # Test searches
    test_queries = [
        "Net sales",
        "Gross margin", 
        "Operating income",
        "Total assets"
    ]
    
    for query in test_queries:
        print("\n" + "=" * 80)
        print(f"🔎 SEARCH QUERY: '{query}'")
        print("=" * 80)
        
        results = engine.search(query)
        print(f"\n📈 Found {len(results)} results\n")
        
        # Group for display
        groups = ResultsGrouper.group_by_dimension(results)
        
        # Non-dimensioned results
        if groups['non_dimensioned']:
            print("┌" + "─" * 78 + "┐")
            print("│ 📋 NON-DIMENSIONED (Total/Aggregate Values)" + " " * 35 + "│")
            print("├" + "─" * 78 + "┤")
            for r in groups['non_dimensioned'][:3]:  # Show first 3
                print(f"│ 🏷️  Label:     {r.original_label:<51} │")
                print(f"│ 💰 Value:     {r.formatted_value:<51} │")
                print(f"│ 📅 Date:      {r.date:<51} │")
                print(f"│ 🔗 HTML ID:   {r.html_location.get('ixbrl_id') if r.html_location else 'N/A':<51} │")
                print("├" + "─" * 78 + "┤")
            print("└" + "─" * 78 + "┘")
        
        # Dimensioned results
        if groups['dimensioned']:
            for dim_label, items in list(groups['dimensioned'].items())[:3]:  # First 3 dimensions
                print(f"\n┌" + "─" * 78 + "┐")
                print(f"│ 🏷️  DIMENSION: {dim_label:<60} │")
                print("├" + "─" * 78 + "┤")
                for r in items[:2]:  # Show first 2 items per dimension
                    print(f"│ 📊 {r.original_label:<20} = {r.formatted_value:<30} │")
                    print(f"│    Concept: {r.concept:<50} │")
                    print(f"    Location: {r.html_location.get('ixbrl_id') if r.html_location else 'N/A':<50} │")
                print("└" + "─" * 78 + "┘")
        
        # Show display format
        print(f"\n🎴 FRONTEND DISPLAY CARDS:")
        display_cards = ResultsGrouper.format_for_display(results[:5])
        for i, card in enumerate(display_cards, 1):
            dim_text = f" [{card['dimension']}]" if card['dimension'] else ""
            print(f"   Card {i}: {card['label']}{dim_text} = {card['value']}")
            print(f"           → Click scrolls to: {card['_meta']['html_location'].get('ixbrl_id') if card['_meta']['html_location'] else 'N/A'}")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_search()
