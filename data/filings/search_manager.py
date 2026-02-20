#!/usr/bin/env python3
"""
Multi-Company SEC Filing Search Manager
Handles multiple companies and multiple years
"""

import json
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import asdict

# Add AAPL directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "AAPL"))
from search_engine import SECFilingSearchEngine, ResultsGrouper, SearchResult


class MultiCompanySearchManager:
    """
    Manages search across multiple companies and years
    Directory structure expected:
        data/filings/
            AAPL/
                FINAL_COMPLETE_WITH_LOCATIONS.json (2025)
                FINAL_COMPLETE_WITH_LOCATIONS_2024.json (2024)
            MSFT/
                FINAL_COMPLETE_WITH_LOCATIONS.json
            GOOGL/
                FINAL_COMPLETE_WITH_LOCATIONS.json
    """
    
    def __init__(self, base_path: str = "/Users/mohdsaeedafri/Documents/Documents/Code-Base/CoresightIQ/CapIQ/data/filings"):
        self.base_path = Path(base_path)
        self.engines: Dict[str, SECFilingSearchEngine] = {}
        self.company_index: Dict[str, Dict] = {}  # ticker -> {years: [], name: ''}
        self._scan_directory()
    
    def _scan_directory(self):
        """Scan directory for available companies and filings"""
        if not self.base_path.exists():
            print(f"⚠️  Base path not found: {self.base_path}")
            return
        
        for company_dir in self.base_path.iterdir():
            if company_dir.is_dir():
                ticker = company_dir.name
                json_files = list(company_dir.glob("FINAL_COMPLETE_WITH_LOCATIONS*.json"))
                
                if json_files:
                    # Parse years from filenames
                    years = []
                    for f in json_files:
                        # Extract year from filename (e.g., FINAL_COMPLETE_WITH_LOCATIONS_2024.json)
                        year_str = f.stem.split('_')[-1]
                        try:
                            year = int(year_str)
                            years.append(year)
                        except ValueError:
                            # Default file (no year suffix) = latest/current
                            years.append('current')
                    
                    self.company_index[ticker] = {
                        'path': company_dir,
                        'years': sorted(years, reverse=True),
                        'json_files': [str(f) for f in json_files]
                    }
        
        print(f"📊 Found {len(self.company_index)} companies: {list(self.company_index.keys())}")
    
    def _get_engine(self, ticker: str, year: Optional[str] = None) -> Optional[SECFilingSearchEngine]:
        """Get or create search engine for company/year"""
        cache_key = f"{ticker}_{year or 'current'}"
        
        if cache_key in self.engines:
            return self.engines[cache_key]
        
        if ticker not in self.company_index:
            return None
        
        company_info = self.company_index[ticker]
        
        # Select appropriate file
        if year and year != 'current':
            json_file = company_info['path'] / f"FINAL_COMPLETE_WITH_LOCATIONS_{year}.json"
        else:
            json_file = company_info['path'] / "FINAL_COMPLETE_WITH_LOCATIONS.json"
        
        if not json_file.exists():
            return None
        
        # Create engine
        engine = SECFilingSearchEngine(str(json_file))
        self.engines[cache_key] = engine
        return engine
    
    def search(self, 
               query: str,
               ticker: Optional[str] = None,
               year: Optional[str] = None,
               filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Search across companies and years
        
        Args:
            query: Search string
            ticker: Specific ticker (None = search all)
            year: Specific year (None = search all available years)
            filters: Additional filters
        
        Returns:
            {
                'query': str,
                'total_results': int,
                'results_by_company': {
                    'AAPL': {
                        '2025': [SearchResult, ...],
                        '2024': [SearchResult, ...]
                    }
                }
            }
        """
        results_by_company = {}
        total_results = 0
        
        # Determine which companies to search
        if ticker:
            companies = [ticker] if ticker in self.company_index else []
        else:
            companies = list(self.company_index.keys())
        
        for comp in companies:
            company_results = {}
            company_info = self.company_index[comp]
            
            # Determine which years to search
            if year:
                years = [year]
            else:
                years = company_info['years']
            
            for yr in years:
                engine = self._get_engine(comp, yr if yr != 'current' else None)
                if engine:
                    results = engine.search(query, filters)
                    if results:
                        company_results[str(yr)] = results
                        total_results += len(results)
            
            if company_results:
                results_by_company[comp] = company_results
        
        return {
            'query': query,
            'total_results': total_results,
            'results_by_company': results_by_company
        }
    
    def get_companies(self) -> List[Dict]:
        """Get list of available companies"""
        companies = []
        for ticker, info in self.company_index.items():
            # Load first engine to get metadata
            engine = self._get_engine(ticker)
            if engine:
                companies.append({
                    'ticker': ticker,
                    'name': engine.metadata.get('company', ticker),
                    'available_years': info['years'],
                    'latest_filing': engine.metadata.get('filing'),
                    'latest_filing_date': engine.metadata.get('filing_date')
                })
        return companies
    
    def format_results_for_frontend(self, search_response: Dict) -> Dict:
        """
        Format search results for frontend consumption
        
        Returns structure:
        {
            'query': 'Operating income',
            'total_results': 15,
            'companies': [
                {
                    'ticker': 'AAPL',
                    'name': 'Apple Inc. (AAPL)',
                    'years': [
                        {
                            'year': '2025',
                            'groups': [
                                {
                                    'type': 'non_dimensioned',
                                    'title': 'Total/Aggregate',
                                    'cards': [...]
                                },
                                {
                                    'type': 'dimensioned',
                                    'dimension': 'Americas',
                                    'cards': [...]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        """
        formatted = {
            'query': search_response['query'],
            'total_results': search_response['total_results'],
            'companies': []
        }
        
        for ticker, years_data in search_response['results_by_company'].items():
            engine = self._get_engine(ticker)
            company_data = {
                'ticker': ticker,
                'name': engine.metadata.get('company', ticker) if engine else ticker,
                'years': []
            }
            
            for year, results in years_data.items():
                # Group results by dimension
                groups = ResultsGrouper.group_by_dimension(results)
                
                year_data = {
                    'year': year,
                    'groups': []
                }
                
                # Non-dimensioned group
                if groups['non_dimensioned']:
                    year_data['groups'].append({
                        'type': 'non_dimensioned',
                        'title': 'Total / Aggregate',
                        'cards': self._format_cards(groups['non_dimensioned'])
                    })
                
                # Dimensioned groups
                for dim_label, items in groups['dimensioned'].items():
                    year_data['groups'].append({
                        'type': 'dimensioned',
                        'dimension': dim_label,
                        'cards': self._format_cards(items)
                    })
                
                company_data['years'].append(year_data)
            
            formatted['companies'].append(company_data)
        
        return formatted
    
    def _format_cards(self, results: List[SearchResult]) -> List[Dict]:
        """Format search results as display cards"""
        return ResultsGrouper.format_for_display(results)


# ============== API USAGE EXAMPLE ==============

def demo_api():
    """Demonstrate the multi-company search API"""
    
    print("=" * 80)
    print("🔍 MULTI-COMPANY SEC FILING SEARCH API DEMO")
    print("=" * 80)
    
    # Initialize manager
    manager = MultiCompanySearchManager()
    
    # Get available companies
    print("\n📊 AVAILABLE COMPANIES:")
    companies = manager.get_companies()
    for comp in companies:
        print(f"   • {comp['ticker']}: {comp['name']}")
        print(f"     Years: {comp['available_years']}")
        print(f"     Latest: {comp['latest_filing']} ({comp['latest_filing_date']})")
    
    # Search example
    print("\n" + "=" * 80)
    print("🔎 EXAMPLE SEARCH: 'Net sales' for AAPL")
    print("=" * 80)
    
    search_result = manager.search(
        query="Net sales",
        ticker="AAPL",
        # year="2025"  # Optional: specific year
    )
    
    # Format for frontend
    frontend_data = manager.format_results_for_frontend(search_result)
    
    print(f"\n📈 Total Results: {frontend_data['total_results']}")
    
    for company in frontend_data['companies']:
        print(f"\n🏢 {company['name']}")
        for year_data in company['years']:
            print(f"\n   📅 Year: {year_data['year']}")
            for group in year_data['groups']:
                if group['type'] == 'non_dimensioned':
                    print(f"\n   📋 {group['title']}")
                    for card in group['cards'][:2]:  # Show first 2
                        print(f"      • {card['label']} = {card['value']}")
                        print(f"        → Click to: {card['_meta']['html_location'].get('ixbrl_id') if card['_meta']['html_location'] else 'N/A'}")
                else:
                    print(f"\n   📦 {group['dimension']}")
                    for card in group['cards'][:2]:
                        print(f"      • {card['label']} = {card['value']}")
                        print(f"        → Click to: {card['_meta']['html_location'].get('ixbrl_id') if card['_meta']['html_location'] else 'N/A'}")
    
    # Show JSON structure
    print("\n" + "=" * 80)
    print("📦 JSON STRUCTURE FOR FRONTEND:")
    print("=" * 80)
    print(json.dumps(frontend_data, indent=2)[:2000] + "...")
    
    print("\n✅ DEMO COMPLETE")


if __name__ == "__main__":
    demo_api()
