"""
Data repository for fetching market data from database.
"""
from typing import List, Optional, Tuple, Dict, Any
from datetime import date, datetime, timedelta
import json

from core.database import db_manager
from data.models import (
    Company, IncomeStatementLineItem, FiscalPeriod, IncomeStatementData,
    NewsArticle, TickerSentiment, CompanyOverview, EarningsCall,
    BalanceSheetLineItem, BalanceSheetData,
    CashFlowLineItem, CashFlowData
)


class CompanyRepository:
    """Repository for coreiq_companies table."""
    
    @staticmethod
    def get_all_sources() -> List[str]:
        """Get distinct data sources."""
        query = "SELECT DISTINCT source FROM coreiq_companies WHERE source IS NOT NULL ORDER BY source"
        results = db_manager.execute_query(query)
        return [row['source'] for row in results if row['source']]
    
    @staticmethod
    def get_companies_by_source() -> List[Company]:
        """Get all companies for a data source."""
        query = """
            SELECT ticker, name, name_coresight, exchange
            FROM coreiq_companies
            WHERE source = 'SEC'
            ORDER BY name_coresight, name
        """
        results = db_manager.execute_query(query)
        return [Company(
            ticker=row['ticker'],
            name=row['name'],
            name_coresight=row['name_coresight'],
            exchange=row['exchange'],
        ) for row in results]
    
    @staticmethod
    def get_company_by_ticker(ticker: str) -> Optional[Company]:
        """Get single company by ticker."""
        query = """
            SELECT ticker, name, name_coresight, exchange, source
            FROM coreiq_companies
            WHERE ticker = :ticker
            LIMIT 1
        """
        results = db_manager.execute_query(query, {"ticker": ticker})
        if not results:
            return None
        row = results[0]
        return Company(
            ticker=row['ticker'],
            name=row['name'],
            name_coresight=row['name_coresight'],
            exchange=row['exchange'],
        )
    
    @staticmethod
    def get_companies() -> List[Dict[str, str]]:
        """Get companies with ticker and name for dropdown."""
        query = """
            SELECT 
                ticker,
                COALESCE(name_coresight, name) as display_name
            FROM coreiq_companies
            WHERE ticker IS NOT NULL
            ORDER BY display_name
        """
        results = db_manager.execute_query(query)
        return [
            {'ticker': row['ticker'], 'name': row['display_name']}
            for row in results
        ]


class IncomeStatementRepository:
    """Repository for coreiq_av_financials_income_statement table."""
    
    # Mapping of UI labels to database columns
    LINE_ITEMS = [
        ("Revenue", "total_revenue", False),
        ("Other Revenue", None, True),  # Will calculate or show "-"
        ("Total Revenue", "total_revenue", False),
        ("Cost Of Goods Sold", "cost_of_revenue", False),
        ("Gross Profit", "gross_profit", False),
        ("Selling General & Admin Exp.", "selling_general_and_administrative", False),
        ("R&D Exp.", "research_and_development", False),
        ("Depreciation & Amort.", "depreciation_and_amortization", False),
        ("Other Operating Expense/(Income)", "other_non_operating_income", False),
        ("Other Operating Exp., Total", "operating_expenses", False),
        ("Operating Income", "operating_income", False),
        ("Interest Expense", "interest_expense", False),
        ("Interest and Invest. Income", "interest_income", False),
        ("Net Interest Exp.", "net_interest_income", False),
    ]
    
    @staticmethod
    def get_date_range(ticker: str) -> Tuple[Optional[date], Optional[date]]:
        """Get min and max fiscal dates for a ticker."""
        query = """
            SELECT 
                MIN(fiscal_date_ending) as min_date,
                MAX(fiscal_date_ending) as max_date
            FROM coreiq_av_financials_income_statement
            WHERE ticker = :ticker
              AND report_type = 'annual'
        """
        results = db_manager.execute_query(query, {"ticker": ticker})
        if not results:
            return None, None
        row = results[0]
        return row['min_date'], row['max_date']
    
    @staticmethod
    def get_available_dates(ticker: str) -> List[date]:
        """Get all available fiscal dates for dropdown."""
        query = """
            SELECT DISTINCT fiscal_date_ending
            FROM coreiq_av_financials_income_statement
            WHERE ticker = :ticker
              AND report_type = 'annual'
            ORDER BY fiscal_date_ending ASC
        """
        results = db_manager.execute_query(query, {"ticker": ticker})
        return [row['fiscal_date_ending'] for row in results]
    
    @staticmethod
    def get_income_statement_data(
        ticker: str,
        start_date: date,
        end_date: date
    ) -> IncomeStatementData:
        """Get income statement data for date range."""
        # Fetch company info
        company = CompanyRepository.get_company_by_ticker(ticker)
        if not company:
            raise ValueError(f"Company not found: {ticker}")
        
        # Fetch raw data - use DISTINCT to avoid duplicates
        query = """
            SELECT DISTINCT fiscal_date_ending, total_revenue, cost_of_revenue, 
                   gross_profit, selling_general_and_administrative, research_and_development,
                   depreciation_and_amortization, operating_income, interest_expense,
                   interest_income, net_income, reported_currency
            FROM coreiq_av_financials_income_statement
            WHERE ticker = :ticker
              AND fiscal_date_ending BETWEEN :start_date AND :end_date
              AND report_type = 'annual'
            ORDER BY fiscal_date_ending ASC
        """
        results = db_manager.execute_query(query, {
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date
        })
        
        if not results:
            # Return empty structure
            return IncomeStatementData(
                company=company,
                periods=[],
                line_items=[]
            )
        
        # Create periods from results
        periods = [
            FiscalPeriod.from_date(row['fiscal_date_ending'])
            for row in results
        ]
        
        # Build line items
        line_items = []
        for label, column, is_calc in IncomeStatementRepository.LINE_ITEMS:
            values = []
            for row in results:
                if column and row.get(column) is not None:
                    # Convert to millions
                    values.append(float(row[column]) / 1_000_000)
                else:
                    values.append(None)
            
            line_items.append(IncomeStatementLineItem(
                label=label,
                key=column or label,
                values=values,
                is_calculated=is_calc
            ))
        
        return IncomeStatementData(
            company=company,
            periods=periods,
            line_items=line_items
        )
    
    @staticmethod
    def get_reported_currency(ticker: str, fiscal_date: date) -> str:
        """Get the reported currency for a specific fiscal period."""
        query = """
            SELECT reported_currency
            FROM coreiq_av_financials_income_statement
            WHERE ticker = :ticker
              AND fiscal_date_ending = :fiscal_date
              AND report_type = 'annual'
            LIMIT 1
        """
        results = db_manager.execute_query(query, {
            "ticker": ticker,
            "fiscal_date": fiscal_date
        })
        if results and results[0].get('reported_currency'):
            return results[0]['reported_currency']
        return "USD"  # Default fallback


class NewsRepository:
    """Repository for coreiq_av_market_news_sentiment table."""
    
    @staticmethod
    def _parse_ticker_sentiment(ticker_sentiment_json: str) -> List[TickerSentiment]:
        """Parse ticker_sentiment JSON string into list of TickerSentiment objects."""
        if not ticker_sentiment_json:
            return []
        try:
            data = json.loads(ticker_sentiment_json)
            return [
                TickerSentiment(
                    ticker=ts.get('ticker', ''),
                    relevance_score=ts.get('relevance_score', '0'),
                    ticker_sentiment_label=ts.get('ticker_sentiment_label', 'Neutral'),
                    ticker_sentiment_score=ts.get('ticker_sentiment_score', '0')
                )
                for ts in data
            ]
        except (json.JSONDecodeError, TypeError):
            return []
    
    @staticmethod
    def _parse_topics(topics_json: str) -> List[Dict[str, str]]:
        """Parse topics JSON string into list of topic dictionaries."""
        if not topics_json:
            return []
        try:
            return json.loads(topics_json)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @staticmethod
    def get_articles(
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        sector: Optional[str] = None,
        company_ticker: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[NewsArticle]:
        """
        Get news articles with optional filtering.
        
        Args:
            date_from: Start date filter
            date_to: End date filter  
            sector: Filter by company sector (primary_industry_coresight)
            company_ticker: Filter by specific company ticker
            limit: Maximum number of articles to return
            offset: Offset for pagination
        """
        # Build base query
        query = """
            SELECT 
                id,
                title,
                summary,
                url,
                source_name as source,
                source_domain,
                time_published_utc as time_published,
                time_published_raw,
                overall_sentiment_score,
                overall_sentiment_label,
                banner_image,
                ticker_sentiment_json,
                topics_json,
                category_within_source,
                raw_json
            FROM coreiq_av_market_news_sentiment
            WHERE 1=1
        """
        params = {}
        
        # Add date filters
        if date_from:
            query += " AND DATE(time_published_utc) >= :date_from"
            params['date_from'] = date_from
        
        if date_to:
            query += " AND DATE(time_published_utc) <= :date_to"
            params['date_to'] = date_to
        
        # Add sector filter - requires join with companies table
        if sector:
            query += """ AND EXISTS (
                SELECT 1 FROM coreiq_companies c 
                WHERE c.primary_industry_coresight = :sector
                AND (
                    JSON_CONTAINS(ticker_sentiment_json, JSON_OBJECT('ticker', c.ticker))
                    OR ticker_sentiment_json LIKE CONCAT('%"ticker": "', c.ticker, '"%')
                )
            )"""
            params['sector'] = sector
        
        # Add company ticker filter
        if company_ticker:
            query += """ AND (
                JSON_CONTAINS(ticker_sentiment_json, JSON_OBJECT('ticker', :company_ticker))
                OR ticker_sentiment_json LIKE CONCAT('%"ticker": "', :company_ticker, '"%')
            )"""
            params['company_ticker'] = company_ticker
        
        # Order by publication date (newest first)
        query += " ORDER BY time_published_utc DESC"
        
        # Add limit and offset
        query += " LIMIT :limit OFFSET :offset"
        params['limit'] = limit
        params['offset'] = offset
        
        results = db_manager.execute_query(query, params)
        
        articles = []
        for row in results:
            # Parse JSON fields
            raw_json_data = {}
            if row.get('raw_json'):
                try:
                    raw_json_data = json.loads(row['raw_json'])
                except json.JSONDecodeError:
                    pass
            
            article = NewsArticle(
                id=row['id'],
                title=row['title'] or raw_json_data.get('title', ''),
                summary=row['summary'] or raw_json_data.get('summary', ''),
                url=row['url'] or raw_json_data.get('url', ''),
                source=row['source'] or raw_json_data.get('source', ''),
                source_domain=row['source_domain'] or raw_json_data.get('source_domain', ''),
                time_published=row['time_published'],
                time_published_raw=row['time_published_raw'] or '',
                overall_sentiment_score=float(row['overall_sentiment_score']) if row['overall_sentiment_score'] else 0.0,
                overall_sentiment_label=row['overall_sentiment_label'] or 'Neutral',
                banner_image=row['banner_image'],
                ticker_sentiment=NewsRepository._parse_ticker_sentiment(
                    row['ticker_sentiment_json'] or raw_json_data.get('ticker_sentiment', '[]')
                ),
                topics=NewsRepository._parse_topics(
                    row['topics_json'] or raw_json_data.get('topics', '[]')
                ),
                category_within_source=row['category_within_source'] or ''
            )
            articles.append(article)
        
        return articles
    
    @staticmethod
    def get_sectors() -> List[str]:
        """Get distinct sectors (primary_industry_coresight) from companies table."""
        query = """
            SELECT DISTINCT primary_industry_coresight as sector
            FROM coreiq_companies
            WHERE primary_industry_coresight IS NOT NULL
              AND primary_industry_coresight != ''
            ORDER BY primary_industry_coresight
        """
        results = db_manager.execute_query(query)
        return [row['sector'] for row in results if row['sector']]
    
    @staticmethod
    def get_companies() -> List[Dict[str, str]]:
        """Get companies with ticker and name for dropdown."""
        query = """
            SELECT 
                ticker,
                COALESCE(name_coresight, name) as display_name
            FROM coreiq_companies
            WHERE ticker IS NOT NULL
            ORDER BY display_name
        """
        results = db_manager.execute_query(query)
        return [
            {'ticker': row['ticker'], 'name': row['display_name']}
            for row in results
        ]
    
    @staticmethod
    def get_company_name_by_ticker(ticker: str) -> Optional[str]:
        """Get company display name by ticker."""
        query = """
            SELECT COALESCE(name_coresight, name) as display_name
            FROM coreiq_companies
            WHERE ticker = :ticker
            LIMIT 1
        """
        results = db_manager.execute_query(query, {'ticker': ticker})
        if results:
            return results[0]['display_name']
        return ticker  # Return ticker if company not found


class CompanyOverviewRepository:
    """Repository for coreiq_av_company_overview table."""
    
    @staticmethod
    def get_company_overview(ticker: str) -> Optional[CompanyOverview]:
        """
        Get company overview by ticker.
        
        Args:
            ticker: Company ticker symbol
            
        Returns:
            CompanyOverview object or None if not found
        """
        query = """
            SELECT 
                ticker,
                name,
                exchange,
                currency,
                country,
                sector,
                industry,
                company_description,
                official_site,
                fiscal_year_end,
                cik,
                market_capitalization,
                pe_ratio,
                eps,
                dividend_yield,
                analyst_target_price,
                raw_json,
                fetched_at_utc
            FROM coreiq_av_company_overview
            WHERE ticker = :ticker
            ORDER BY fetched_at_utc DESC
            LIMIT 1
        """
        results = db_manager.execute_query(query, {"ticker": ticker})
        
        if not results:
            return None
        
        row = results[0]
        
        # Parse raw_json for additional fields
        raw_json_data = {}
        if row.get('raw_json'):
            try:
                raw_json_data = json.loads(row['raw_json'])
            except json.JSONDecodeError:
                pass
        
        # Helper function to safely get float from various formats
        def safe_float(value, default=None):
            if value is None:
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # Helper function to safely get int
        def safe_int(value, default=None):
            if value is None:
                return default
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return default
        
        return CompanyOverview(
            ticker=row['ticker'] or ticker,
            name=row['name'] or ticker,
            exchange=row['exchange'],
            currency=row['currency'],
            country=row['country'],
            sector=row['sector'],
            industry=row['industry'],
            company_description=row['company_description'],
            official_site=row['official_site'],
            fiscal_year_end=row['fiscal_year_end'],
            cik=row['cik'],
            market_capitalization=safe_int(row['market_capitalization']),
            pe_ratio=safe_float(row['pe_ratio']),
            eps=safe_float(row['eps']),
            dividend_yield=safe_float(row['dividend_yield']),
            analyst_target_price=safe_float(row['analyst_target_price']),
            fetched_at_utc=row['fetched_at_utc'],
            # From raw_json
            address=raw_json_data.get('Address'),
            revenue_ttm=safe_float(raw_json_data.get('RevenueTTM')),
            ebitda=safe_float(raw_json_data.get('EBITDA')),
            profit_margin=safe_float(raw_json_data.get('ProfitMargin')),
            shares_outstanding=safe_int(raw_json_data.get('SharesOutstanding')),
            week_52_high=safe_float(raw_json_data.get('52WeekHigh')),
            week_52_low=safe_float(raw_json_data.get('52WeekLow')),
            dividend_per_share=safe_float(raw_json_data.get('DividendPerShare')),
            latest_quarter=raw_json_data.get('LatestQuarter'),
            # Placeholder fields - not in database
            employees="N/A",
            year_founded="N/A",
            professionals_profiled="N/A",
            coverage_summary="N/A",
            coverage_list="N/A",
            relationships="N/A",
            projects="N/A",
            activity_logs="N/A"
        )
    
    @staticmethod
    def company_exists(ticker: str) -> bool:
        """Check if company overview exists for ticker."""
        query = """
            SELECT 1
            FROM coreiq_av_company_overview
            WHERE ticker = :ticker
            LIMIT 1
        """
        results = db_manager.execute_query(query, {"ticker": ticker})
        return len(results) > 0


class EarningsCallRepository:
    """Repository for coreiq_av_earnings_call_transcripts table."""
    
    @staticmethod
    def get_companies_with_earnings() -> List[Dict[str, str]]:
        """Get only companies that have earnings call transcripts.
        
        Returns:
            List of dicts with 'ticker' and 'name' keys.
        """
        query = """
            SELECT DISTINCT 
                c.ticker,
                COALESCE(c.name_coresight, c.name) as display_name
            FROM coreiq_companies c
            INNER JOIN coreiq_av_earnings_call_transcripts e ON c.ticker = e.ticker
            WHERE e.ticker IS NOT NULL
            ORDER BY display_name
        """
        results = db_manager.execute_query(query)
        return [
            {'ticker': row['ticker'], 'name': row['display_name']}
            for row in results
        ]
    
    @staticmethod
    def get_earnings_calls(
        ticker: Optional[str] = None,
        year: Optional[int] = None,
        quarter: Optional[int] = None,
        has_transcript_only: bool = True,
        limit: int = 100
    ) -> List[EarningsCall]:
        """Get earnings calls with optional filtering.
        
        Args:
            ticker: Filter by company ticker
            year: Filter by year
            quarter: Filter by quarter (1-4)
            has_transcript_only: Only return calls with transcripts
            limit: Maximum number of results
            
        Returns:
            List of EarningsCall objects
        """
        query = """
            SELECT 
                id,
                source,
                ticker,
                quarter,
                year,
                q,
                transcript_text,
                has_transcript,
                title,
                event_datetime_utc,
                fetched_at_utc
            FROM coreiq_av_earnings_call_transcripts
            WHERE 1=1
        """
        params = {}
        
        if ticker:
            query += " AND ticker = :ticker"
            params['ticker'] = ticker
        
        if year:
            query += " AND year = :year"
            params['year'] = year
        
        if quarter:
            query += " AND q = :quarter"
            params['quarter'] = quarter
        
        if has_transcript_only:
            query += " AND has_transcript = 1"
        
        query += " ORDER BY year DESC, q DESC"
        query += " LIMIT :limit"
        params['limit'] = limit
        
        results = db_manager.execute_query(query, params)
        
        earnings_calls = []
        for row in results:
            earnings_calls.append(EarningsCall(
                id=row['id'],
                source=row['source'],
                ticker=row['ticker'],
                quarter=row['quarter'],
                year=row['year'],
                q=row['q'],
                transcript_text=row['transcript_text'],
                has_transcript=bool(row['has_transcript']),
                title=row['title'],
                event_datetime_utc=row['event_datetime_utc'],
                fetched_at_utc=row['fetched_at_utc']
            ))
        
        return earnings_calls
    
    @staticmethod
    def get_earnings_call_by_id(earnings_id: int) -> Optional[EarningsCall]:
        """Get a single earnings call by ID."""
        query = """
            SELECT 
                id,
                source,
                ticker,
                quarter,
                year,
                q,
                transcript_text,
                has_transcript,
                title,
                event_datetime_utc,
                fetched_at_utc
            FROM coreiq_av_earnings_call_transcripts
            WHERE id = :id
            LIMIT 1
        """
        results = db_manager.execute_query(query, {"id": earnings_id})
        
        if not results:
            return None
        
        row = results[0]
        return EarningsCall(
            id=row['id'],
            source=row['source'],
            ticker=row['ticker'],
            quarter=row['quarter'],
            year=row['year'],
            q=row['q'],
            transcript_text=row['transcript_text'],
            has_transcript=bool(row['has_transcript']),
            title=row['title'],
            event_datetime_utc=row['event_datetime_utc'],
            fetched_at_utc=row['fetched_at_utc']
        )
    
    @staticmethod
    def get_available_years(ticker: Optional[str] = None) -> List[int]:
        """Get distinct years available for earnings calls.
        
        Args:
            ticker: Optional ticker to filter by
            
        Returns:
            List of years (descending order)
        """
        query = """
            SELECT DISTINCT year 
            FROM coreiq_av_earnings_call_transcripts
            WHERE year IS NOT NULL
        """
        params = {}
        
        if ticker:
            query += " AND ticker = :ticker"
            params['ticker'] = ticker
        
        query += " ORDER BY year DESC"
        
        results = db_manager.execute_query(query, params)
        return [row['year'] for row in results]
    
    @staticmethod
    def get_available_quarters(ticker: Optional[str] = None, year: Optional[int] = None) -> List[int]:
        """Get distinct quarters available.
        
        Args:
            ticker: Optional ticker to filter by
            year: Optional year to filter by
            
        Returns:
            List of quarters (1-4)
        """
        query = """
            SELECT DISTINCT q 
            FROM coreiq_av_earnings_call_transcripts
            WHERE q IS NOT NULL
        """
        params = {}
        
        if ticker:
            query += " AND ticker = :ticker"
            params['ticker'] = ticker
        
        if year:
            query += " AND year = :year"
            params['year'] = year
        
        query += " ORDER BY q"
        
        results = db_manager.execute_query(query, params)
        return [row['q'] for row in results]


class BalanceSheetRepository:
    """Repository for coreiq_av_financials_balance_sheet table.
    
    Uses raw_json column for data extraction as per manager requirements.
    """
    
    # Mapping of UI labels to raw_json keys
    # Organized by section: Assets, Liabilities, Shareholders' Equity
    # IMPORTANT: Totals come AFTER their components (at the bottom)
    LINE_ITEMS = [
        # ASSETS - Current
        ("Cash & Cash Equivalents", "cashAndCashEquivalentsAtCarryingValue", False, "assets"),
        ("Cash & Short Term Investments", "cashAndShortTermInvestments", False, "assets"),
        ("Inventory", "inventory", False, "assets"),
        ("Current Net Receivables", "currentNetReceivables", False, "assets"),
        ("Other Current Assets", "otherCurrentAssets", False, "assets"),
        ("Total Current Assets", "totalCurrentAssets", False, "assets"),
        
        # ASSETS - Non-Current
        ("Property Plant & Equipment", "propertyPlantEquipment", False, "assets"),
        ("Intangible Assets", "intangibleAssets", False, "assets"),
        ("Intangible Assets Excl. Goodwill", "intangibleAssetsExcludingGoodwill", False, "assets"),
        ("Goodwill", "goodwill", False, "assets"),
        ("Long Term Investments", "longTermInvestments", False, "assets"),
        ("Other Non-Current Assets", "otherNonCurrentAssets", False, "assets"),
        ("Total Non-Current Assets", "totalNonCurrentAssets", False, "assets"),
        
        # ASSETS - Total
        ("Total Assets", "totalAssets", False, "assets"),
        
        # LIABILITIES - Current
        ("Current Accounts Payable", "currentAccountsPayable", False, "liabilities"),
        ("Deferred Revenue", "deferredRevenue", False, "liabilities"),
        ("Current Debt", "currentDebt", False, "liabilities"),
        ("Short Term Debt", "shortTermDebt", False, "liabilities"),
        ("Other Current Liabilities", "otherCurrentLiabilities", False, "liabilities"),
        ("Total Current Liabilities", "totalCurrentLiabilities", False, "liabilities"),
        
        # LIABILITIES - Non-Current
        ("Long Term Debt", "longTermDebt", False, "liabilities"),
        ("Long Term Debt Noncurrent", "longTermDebtNoncurrent", False, "liabilities"),
        ("Capital Lease Obligations", "capitalLeaseObligations", False, "liabilities"),
        ("Other Non-Current Liabilities", "otherNonCurrentLiabilities", False, "liabilities"),
        ("Total Non-Current Liabilities", "totalNonCurrentLiabilities", False, "liabilities"),
        
        # LIABILITIES - Total
        ("Total Liabilities", "totalLiabilities", False, "liabilities"),
        
        # SHAREHOLDERS' EQUITY - Components
        ("Common Stock", "commonStock", False, "equity"),
        ("Retained Earnings", "retainedEarnings", False, "equity"),
        ("Treasury Stock", "treasuryStock", False, "equity"),
        
        # SHAREHOLDERS' EQUITY - Total
        ("Total Shareholder Equity", "totalShareholderEquity", False, "equity"),
    ]
    
    @staticmethod
    def get_date_range(ticker: str) -> Tuple[Optional[date], Optional[date]]:
        """Get min and max fiscal dates for a ticker."""
        query = """
            SELECT 
                MIN(fiscal_date_ending) as min_date,
                MAX(fiscal_date_ending) as max_date
            FROM coreiq_av_financials_balance_sheet
            WHERE ticker = :ticker
              AND report_type = 'annual'
        """
        results = db_manager.execute_query(query, {"ticker": ticker})
        if not results:
            return None, None
        row = results[0]
        return row['min_date'], row['max_date']
    
    @staticmethod
    def get_available_dates(ticker: str) -> List[date]:
        """Get all available fiscal dates for dropdown."""
        query = """
            SELECT DISTINCT fiscal_date_ending
            FROM coreiq_av_financials_balance_sheet
            WHERE ticker = :ticker
              AND report_type = 'annual'
            ORDER BY fiscal_date_ending ASC
        """
        results = db_manager.execute_query(query, {"ticker": ticker})
        return [row['fiscal_date_ending'] for row in results]
    
    @staticmethod
    def _parse_raw_json(raw_json: Any) -> Dict[str, Any]:
        """Parse raw_json field from database."""
        if raw_json is None:
            return {}
        if isinstance(raw_json, str):
            try:
                return json.loads(raw_json)
            except json.JSONDecodeError:
                return {}
        if isinstance(raw_json, dict):
            return raw_json
        return {}
    
    @staticmethod
    def _get_nested_value(data: Dict[str, Any], key: str) -> Optional[float]:
        """Get value from nested dict structure."""
        if not data:
            return None
        # Try direct key first
        if key in data:
            val = data[key]
            if val is not None and val != "None":
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return None
        # Try camelCase conversion for some common variations
        return None
    
    @staticmethod
    def get_balance_sheet_data(
        ticker: str,
        start_date: date,
        end_date: date
    ) -> BalanceSheetData:
        """Get balance sheet data for date range using raw_json."""
        # Fetch company info
        company = CompanyRepository.get_company_by_ticker(ticker)
        if not company:
            raise ValueError(f"Company not found: {ticker}")
        
        # Fetch raw_json data
        query = """
            SELECT fiscal_date_ending, raw_json, reported_currency
            FROM coreiq_av_financials_balance_sheet
            WHERE ticker = :ticker
              AND fiscal_date_ending BETWEEN :start_date AND :end_date
              AND report_type = 'annual'
            ORDER BY fiscal_date_ending ASC
        """
        results = db_manager.execute_query(query, {
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date
        })
        
        if not results:
            # Return empty structure
            return BalanceSheetData(
                company=company,
                periods=[],
                line_items=[]
            )
        
        # Create periods from results
        periods = [
            FiscalPeriod.from_date(row['fiscal_date_ending'])
            for row in results
        ]
        
        # Parse all raw_json data
        json_data_list = [
            BalanceSheetRepository._parse_raw_json(row['raw_json'])
            for row in results
        ]
        
        # Build line items from raw_json
        line_items = []
        for label, json_key, is_calc, section in BalanceSheetRepository.LINE_ITEMS:
            values = []
            for json_data in json_data_list:
                val = BalanceSheetRepository._get_nested_value(json_data, json_key)
                if val is not None:
                    # Convert to millions
                    values.append(val / 1_000_000)
                else:
                    values.append(None)
            
            # Only add line item if at least one period has data
            if any(v is not None for v in values):
                line_items.append(BalanceSheetLineItem(
                    label=label,
                    key=json_key,
                    values=values,
                    is_calculated=is_calc,
                    section=section
                ))
        
        return BalanceSheetData(
            company=company,
            periods=periods,
            line_items=line_items
        )
    
    @staticmethod
    def get_reported_currency(ticker: str, fiscal_date: date) -> str:
        """Get the reported currency for a specific fiscal period."""
        query = """
            SELECT reported_currency
            FROM coreiq_av_financials_balance_sheet
            WHERE ticker = :ticker
              AND fiscal_date_ending = :fiscal_date
              AND report_type = 'annual'
            LIMIT 1
        """
        results = db_manager.execute_query(query, {
            "ticker": ticker,
            "fiscal_date": fiscal_date
        })
        if results and results[0].get('reported_currency'):
            return results[0]['reported_currency']
        return "USD"  # Default fallback


class CashFlowRepository:
    """Repository for coreiq_av_financials_cash_flow table.
    
    Uses raw_json column for data extraction.
    """
    
    # Mapping of UI labels to raw_json keys
    # Organized by section: Operating, Investing, Financing
    # IMPORTANT: Totals come AFTER their components (at the bottom)
    LINE_ITEMS = [
        # OPERATING ACTIVITIES
        ("Net Income", "netIncome", False, "operating"),
        ("Depreciation & Amortization", "depreciationDepletionAndAmortization", False, "operating"),
        ("Deferred Tax", "deferredIncomeTax", False, "operating"),
        ("Stock-Based Compensation", "stockBasedCompensation", False, "operating"),
        ("Change in Working Capital", "changeInWorkingCapital", False, "operating"),
        ("Accounts Receivable", "changeInReceivables", False, "operating"),
        ("Inventory", "changeInInventory", False, "operating"),
        ("Accounts Payable", "changeInPayables", False, "operating"),
        ("Other Operating Activities", "changeInOtherOperatingAssets", False, "operating"),
        ("Operating Cash Flow", "operatingCashflow", False, "operating"),
        
        # INVESTING ACTIVITIES
        ("Capital Expenditures", "capitalExpenditures", False, "investing"),
        ("Acquisitions", "acquisitions", False, "investing"),
        ("Purchases of Investments", "purchaseOfInvestment", False, "investing"),
        ("Sales/Maturities of Investments", "saleOfInvestment", False, "investing"),
        ("Other Investing Activities", "otherCashflowFromInvestment", False, "investing"),
        ("Investing Cash Flow", "cashflowFromInvestment", False, "investing"),
        
        # FINANCING ACTIVITIES
        ("Debt Repayment", "debtRepayment", False, "financing"),
        ("Common Stock Issued", "commonStockIssued", False, "financing"),
        ("Common Stock Repurchased", "commonStockRepurchased", False, "financing"),
        ("Dividends Paid", "dividendsPaid", False, "financing"),
        ("Other Financing Activities", "otherCashflowFromFinancing", False, "financing"),
        ("Financing Cash Flow", "cashflowFromFinancing", False, "financing"),
        
        # SUMMARY
        ("Effect of Forex Changes", "exchangeRateChanges", False, "summary"),
        ("Net Change in Cash", "netChangeInCash", False, "summary"),
        ("Cash at Beginning of Period", "cashAtBeginningOfPeriod", False, "summary"),
        ("Cash at End of Period", "cashAtEndOfPeriod", False, "summary"),
    ]
    
    @staticmethod
    def get_date_range(ticker: str) -> Tuple[Optional[date], Optional[date]]:
        """Get min and max fiscal dates for a ticker."""
        query = """
            SELECT 
                MIN(fiscal_date_ending) as min_date,
                MAX(fiscal_date_ending) as max_date
            FROM coreiq_av_financials_cash_flow
            WHERE ticker = :ticker
              AND report_type = 'annual'
        """
        results = db_manager.execute_query(query, {"ticker": ticker})
        if not results:
            return None, None
        row = results[0]
        return row['min_date'], row['max_date']
    
    @staticmethod
    def get_available_dates(ticker: str) -> List[date]:
        """Get all available fiscal dates for dropdown."""
        query = """
            SELECT DISTINCT fiscal_date_ending
            FROM coreiq_av_financials_cash_flow
            WHERE ticker = :ticker
              AND report_type = 'annual'
            ORDER BY fiscal_date_ending ASC
        """
        results = db_manager.execute_query(query, {"ticker": ticker})
        return [row['fiscal_date_ending'] for row in results]
    
    @staticmethod
    def _parse_raw_json(raw_json: Any) -> Dict[str, Any]:
        """Parse raw_json field from database."""
        if raw_json is None:
            return {}
        if isinstance(raw_json, str):
            try:
                return json.loads(raw_json)
            except json.JSONDecodeError:
                return {}
        if isinstance(raw_json, dict):
            return raw_json
        return {}
    
    @staticmethod
    def _get_nested_value(data: Dict[str, Any], key: str) -> Optional[float]:
        """Get value from nested dict structure."""
        if not data:
            return None
        # Try direct key first
        if key in data:
            val = data[key]
            if val is not None and val != "None":
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return None
        return None
    
    @staticmethod
    def get_cash_flow_data(
        ticker: str,
        start_date: date,
        end_date: date
    ) -> CashFlowData:
        """Get cash flow data for date range using raw_json."""
        # Fetch company info
        company = CompanyRepository.get_company_by_ticker(ticker)
        if not company:
            raise ValueError(f"Company not found: {ticker}")
        
        # Fetch raw_json data
        query = """
            SELECT fiscal_date_ending, raw_json, reported_currency
            FROM coreiq_av_financials_cash_flow
            WHERE ticker = :ticker
              AND fiscal_date_ending BETWEEN :start_date AND :end_date
              AND report_type = 'annual'
            ORDER BY fiscal_date_ending ASC
        """
        results = db_manager.execute_query(query, {
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date
        })
        
        if not results:
            # Return empty structure
            return CashFlowData(
                company=company,
                periods=[],
                line_items=[]
            )
        
        # Create periods from results
        periods = [
            FiscalPeriod.from_date(row['fiscal_date_ending'])
            for row in results
        ]
        
        # Parse all raw_json data
        json_data_list = [
            CashFlowRepository._parse_raw_json(row['raw_json'])
            for row in results
        ]
        
        # Build line items from raw_json
        line_items = []
        for label, json_key, is_calc, section in CashFlowRepository.LINE_ITEMS:
            values = []
            for json_data in json_data_list:
                val = CashFlowRepository._get_nested_value(json_data, json_key)
                if val is not None:
                    # Convert to millions
                    values.append(val / 1_000_000)
                else:
                    values.append(None)
            
            # Only add line item if at least one period has data
            if any(v is not None for v in values):
                line_items.append(CashFlowLineItem(
                    label=label,
                    key=json_key,
                    values=values,
                    is_calculated=is_calc,
                    section=section
                ))
        
        return CashFlowData(
            company=company,
            periods=periods,
            line_items=line_items
        )
    
    @staticmethod
    def get_reported_currency(ticker: str, fiscal_date: date) -> str:
        """Get the reported currency for a specific fiscal period."""
        query = """
            SELECT reported_currency
            FROM coreiq_av_financials_cash_flow
            WHERE ticker = :ticker
              AND fiscal_date_ending = :fiscal_date
              AND report_type = 'annual'
            LIMIT 1
        """
        results = db_manager.execute_query(query, {
            "ticker": ticker,
            "fiscal_date": fiscal_date
        })
        if results and results[0].get('reported_currency'):
            return results[0]['reported_currency']
        return "USD"  # Default fallback


class ForexRepository:
    """Repository for currency conversion rates from coreiq_av_forex_daily table."""
    
    @staticmethod
    def get_conversion_rate(from_currency: str, to_currency: str, as_of_date: Optional[date] = None) -> float:
        """
        Get conversion rate between two currencies from the forex table.
        
        Args:
            from_currency: Source currency code (e.g., 'USD')
            to_currency: Target currency code (e.g., 'EUR')
            as_of_date: Date for the rate (defaults to most recent)
            
        Returns:
            Conversion rate as float (1.0 if same currency or not found)
        """
        if from_currency == to_currency:
            return 1.0
        
        # Query the forex table for the most recent rate
        if as_of_date:
            query = """
                SELECT close
                FROM coreiq_av_forex_daily
                WHERE from_currency = :from_currency
                  AND to_currency = :to_currency
                  AND day_date <= :as_of_date
                ORDER BY day_date DESC
                LIMIT 1
            """
            params = {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "as_of_date": as_of_date
            }
        else:
            query = """
                SELECT close
                FROM coreiq_av_forex_daily
                WHERE from_currency = :from_currency
                  AND to_currency = :to_currency
                ORDER BY day_date DESC
                LIMIT 1
            """
            params = {
                "from_currency": from_currency,
                "to_currency": to_currency
            }
        
        results = db_manager.execute_query(query, params)
        
        if results and results[0].get('close'):
            return float(results[0]['close'])
        
        # Fallback: try reverse rate (1/rate)
        reverse_query = """
            SELECT close
            FROM coreiq_av_forex_daily
            WHERE from_currency = :to_currency
              AND to_currency = :from_currency
            ORDER BY day_date DESC
            LIMIT 1
        """
        reverse_results = db_manager.execute_query(reverse_query, {
            "from_currency": from_currency,
            "to_currency": to_currency
        })
        
        if reverse_results and reverse_results[0].get('close'):
            return 1.0 / float(reverse_results[0]['close'])
        
        # If no rate found, return 1.0 (no conversion)
        return 1.0
    
    @staticmethod
    def get_available_currencies() -> List[str]:
        """Get list of available currencies from the forex table."""
        query = """
            SELECT DISTINCT from_currency as currency
            FROM coreiq_av_forex_daily
            UNION
            SELECT DISTINCT to_currency as currency
            FROM coreiq_av_forex_daily
            ORDER BY currency
        """
        results = db_manager.execute_query(query)
        return [row['currency'] for row in results if row['currency']]
