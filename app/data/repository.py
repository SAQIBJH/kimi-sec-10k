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
    CashFlowLineItem, CashFlowData,
    FilingMetricResult
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
        """Get companies common across all data tables for dropdown.

        Only returns companies that have data in income statement,
        balance sheet, cash flow, company overview, and earnings calls.
        """
        query = """
            SELECT
                c.ticker,
                COALESCE(c.name_coresight, c.name) as display_name
            FROM coreiq_companies c
            WHERE c.ticker IS NOT NULL
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_financials_income_statement)
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_financials_balance_sheet)
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_financials_cash_flow)
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_company_overview)
              AND c.ticker IN (SELECT DISTINCT ticker FROM coreiq_av_earnings_call_transcripts)
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
        keyword: Optional[str] = None,
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
            keyword: Keyword to search in title and summary
            limit: Maximum number of articles to return
            offset: Offset for pagination
        """
        # Build base query
        has_keyword = keyword and keyword.strip()
        
        if has_keyword:
            clean_keyword = keyword.strip()
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
                    raw_json,
                    MATCH(title, summary) AGAINST(:keyword_rel IN NATURAL LANGUAGE MODE) as relevance
                FROM coreiq_av_market_news_sentiment
                WHERE 1=1
            """
        else:
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
        
        # FULLTEXT keyword search in title and summary (with LIKE fallback)
        if has_keyword:
            query += " AND MATCH(title, summary) AGAINST(:keyword IN NATURAL LANGUAGE MODE)"
            params['keyword'] = clean_keyword
            params['keyword_rel'] = clean_keyword
        
        # Order by relevance when searching, else by date
        if has_keyword:
            query += " ORDER BY relevance DESC"
        else:
            query += " ORDER BY time_published_utc DESC"
        
        # Add limit and offset
        query += " LIMIT :limit OFFSET :offset"
        params['limit'] = limit
        params['offset'] = offset
        
        # Execute with FULLTEXT; fallback to LIKE if 0 results or FULLTEXT not available
        try:
            results = db_manager.execute_query(query, params)
        except Exception:
            results = []
        
        if not results and has_keyword:
            # Fallback: rebuild with LIKE for each word (ensures keyword match is never lost)
            like_query = """
                SELECT 
                    id, title, summary, url,
                    source_name as source, source_domain,
                    time_published_utc as time_published,
                    time_published_raw,
                    overall_sentiment_score, overall_sentiment_label,
                    banner_image, ticker_sentiment_json,
                    topics_json, category_within_source, raw_json
                FROM coreiq_av_market_news_sentiment
                WHERE 1=1
            """
            like_params = {}
            if date_from:
                like_query += " AND DATE(time_published_utc) >= :date_from"
                like_params['date_from'] = date_from
            if date_to:
                like_query += " AND DATE(time_published_utc) <= :date_to"
                like_params['date_to'] = date_to
            if sector:
                like_query += """ AND EXISTS (
                    SELECT 1 FROM coreiq_companies c 
                    WHERE c.primary_industry_coresight = :sector
                    AND (
                        JSON_CONTAINS(ticker_sentiment_json, JSON_OBJECT('ticker', c.ticker))
                        OR ticker_sentiment_json LIKE CONCAT('%"ticker": "', c.ticker, '"%')
                    )
                )"""
                like_params['sector'] = sector
            if company_ticker:
                like_query += """ AND (
                    JSON_CONTAINS(ticker_sentiment_json, JSON_OBJECT('ticker', :company_ticker))
                    OR ticker_sentiment_json LIKE CONCAT('%"ticker": "', :company_ticker, '"%')
                )"""
                like_params['company_ticker'] = company_ticker
            
            # LIKE match: search each word individually with OR
            words = clean_keyword.split()
            like_clauses = []
            for i, word in enumerate(words):
                key = f'kw_{i}'
                like_clauses.append(f"(LOWER(title) LIKE :{key} OR LOWER(summary) LIKE :{key})")
                like_params[key] = f'%{word.lower()}%'
            if like_clauses:
                like_query += " AND (" + " OR ".join(like_clauses) + ")"
            
            like_query += " ORDER BY time_published_utc DESC"
            like_query += " LIMIT :limit OFFSET :offset"
            like_params['limit'] = limit
            like_params['offset'] = offset
            
            results = db_manager.execute_query(like_query, like_params)
        
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
    def get_news_date_range() -> Dict[str, Any]:
        """Get min and max time_published_utc from news table."""
        query = """
            SELECT 
                MIN(DATE(time_published_utc)) as min_date,
                MAX(DATE(time_published_utc)) as max_date
            FROM coreiq_av_market_news_sentiment
            WHERE time_published_utc IS NOT NULL
        """
        results = db_manager.execute_query(query)
        if results and results[0]['min_date']:
            return {
                'min_date': results[0]['min_date'],
                'max_date': results[0]['max_date']
            }
        return {'min_date': date.today() - timedelta(days=30), 'max_date': date.today()}

    @staticmethod
    def get_news_tickers(
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[str]:
        """Get distinct tickers from news articles within a date range."""
        query = """
            SELECT DISTINCT
                JSON_UNQUOTE(JSON_EXTRACT(ts.val, '$.ticker')) as ticker
            FROM coreiq_av_market_news_sentiment n,
                 JSON_TABLE(n.ticker_sentiment_json, '$[*]' COLUMNS (val JSON PATH '$')) ts
            WHERE 1=1
        """
        params = {}
        if date_from:
            query += " AND DATE(n.time_published_utc) >= :date_from"
            params['date_from'] = date_from
        if date_to:
            query += " AND DATE(n.time_published_utc) <= :date_to"
            params['date_to'] = date_to
        
        results = db_manager.execute_query(query, params)
        return [row['ticker'] for row in results if row['ticker']]

    @staticmethod
    def get_sectors(
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[str]:
        """Get distinct sectors for companies that appear in news articles within date range."""
        # First get tickers from news within date range
        news_tickers = NewsRepository.get_news_tickers(date_from=date_from, date_to=date_to)
        if not news_tickers:
            return []
        
        # Build parameterized IN clause
        placeholders = ', '.join([f':t{i}' for i in range(len(news_tickers))])
        params = {f't{i}': t for i, t in enumerate(news_tickers)}
        
        query = f"""
            SELECT DISTINCT c.primary_industry_coresight as sector
            FROM coreiq_companies c
            WHERE c.primary_industry_coresight IS NOT NULL
              AND c.primary_industry_coresight != ''
              AND c.ticker IN ({placeholders})
            ORDER BY c.primary_industry_coresight
        """
        results = db_manager.execute_query(query, params)
        return [row['sector'] for row in results if row['sector']]
    
    @staticmethod
    def get_companies(
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        sector: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Get companies that appear in news articles within date range, filtered by sector."""
        # First get tickers from news within date range
        news_tickers = NewsRepository.get_news_tickers(date_from=date_from, date_to=date_to)
        if not news_tickers:
            return []
        
        # Build parameterized IN clause
        placeholders = ', '.join([f':t{i}' for i in range(len(news_tickers))])
        params = {f't{i}': t for i, t in enumerate(news_tickers)}
        
        query = f"""
            SELECT DISTINCT
                c.ticker,
                COALESCE(c.name_coresight, c.name) as display_name
            FROM coreiq_companies c
            WHERE c.ticker IN ({placeholders})
        """
        
        if sector:
            query += " AND c.primary_industry_coresight = :sector"
            params['sector'] = sector
        
        query += " ORDER BY display_name"
        
        results = db_manager.execute_query(query, params)
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
        """Get only companies that have earnings call transcripts (with actual transcript text).
        
        Returns:
            List of dicts with 'ticker' and 'name' keys.
        """
        query = """
            SELECT DISTINCT 
                c.ticker,
                COALESCE(c.name_coresight, c.name) as display_name
            FROM coreiq_companies c
            INNER JOIN coreiq_av_earnings_call_transcripts e ON c.ticker = e.ticker
            WHERE e.has_transcript = 1
              AND e.transcript_text IS NOT NULL
            ORDER BY display_name
        """
        results = db_manager.execute_query(query)
        return [
            {'ticker': row['ticker'], 'name': row['display_name']}
            for row in results
        ]
    
    @staticmethod
    def _parse_quarter_param(quarter) -> Optional[int]:
        """Convert quarter param (int, str like 'Q1', or 'Q1') to integer 1-4."""
        if quarter is None:
            return None
        if isinstance(quarter, int):
            return quarter
        # Handle string like "Q1", "Q2", etc.
        q_str = str(quarter).strip().upper()
        if q_str.startswith('Q') and len(q_str) == 2 and q_str[1].isdigit():
            return int(q_str[1])
        # Try direct int parse
        try:
            return int(q_str)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def get_earnings_calls(
        ticker: Optional[str] = None,
        year: Optional[int] = None,
        quarter=None,
        has_transcript_only: bool = True,
        limit: int = 100
    ) -> List[EarningsCall]:
        """Get earnings calls with optional filtering.
        
        Args:
            ticker: Filter by company ticker
            year: Filter by year
            quarter: Filter by quarter — accepts int (1-4) or str ('Q1'-'Q4')
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
            # Handle string year from selectbox
            params['year'] = int(year) if isinstance(year, str) else year
            query += " AND year = :year"
        
        q_int = EarningsCallRepository._parse_quarter_param(quarter)
        if q_int:
            query += " AND q = :quarter"
            params['quarter'] = q_int
        
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
    def get_available_years(ticker: str) -> List[int]:
        """Get distinct years that have transcripts for a given company.
        
        Args:
            ticker: Company ticker (required)
            
        Returns:
            List of years (descending order)
        """
        query = """
            SELECT DISTINCT year 
            FROM coreiq_av_earnings_call_transcripts
            WHERE year IS NOT NULL
              AND has_transcript = 1
              AND ticker = :ticker
            ORDER BY year DESC
        """
        results = db_manager.execute_query(query, {'ticker': ticker})
        return [row['year'] for row in results]
    
    @staticmethod
    def get_available_quarters(ticker: str, year) -> List[str]:
        """Get distinct quarters that have transcripts for a company+year.
        
        Args:
            ticker: Company ticker (required)
            year: Year to filter by (required, accepts str or int)
            
        Returns:
            List of quarter strings like ['Q1', 'Q2', 'Q3', 'Q4'] (ascending)
        """
        year_int = int(year) if isinstance(year, str) else year
        query = """
            SELECT DISTINCT q 
            FROM coreiq_av_earnings_call_transcripts
            WHERE q IS NOT NULL
              AND has_transcript = 1
              AND ticker = :ticker
              AND year = :year
            ORDER BY q
        """
        results = db_manager.execute_query(query, {'ticker': ticker, 'year': year_int})
        return [f"Q{row['q']}" for row in results]


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


class KeyStatsRepository:
    """Repository for Key Stats data combining multiple tables.
    
    Combines data from:
    - coreiq_av_financials_income_statement (revenue, ebitda, ebit, net income)
    - coreiq_av_financials_balance_sheet (cash, debt, equity for TEV calculations)
    - coreiq_av_company_overview (market cap, share price, eps)
    """
    
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
    def get_key_stats_data(
        ticker: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Get key stats data for date range.
        
        Returns a dictionary with:
        - periods: List of FiscalPeriod
        - line_items: List of dict with label and values
        - reported_currency: str
        """
        from data.models import FiscalPeriod
        
        # Fetch income statement data with all needed fields
        query = """
            SELECT DISTINCT 
                i.fiscal_date_ending,
                i.total_revenue,
                i.gross_profit,
                i.ebitda,
                i.ebit,
                i.net_income_from_continuing_operations,
                i.net_income,
                i.reported_currency,
                i.raw_json
            FROM coreiq_av_financials_income_statement i
            WHERE i.ticker = :ticker
              AND i.fiscal_date_ending BETWEEN :start_date AND :end_date
              AND i.report_type = 'annual'
            ORDER BY i.fiscal_date_ending ASC
        """
        results = db_manager.execute_query(query, {
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date
        })
        
        if not results:
            return {"periods": [], "line_items": [], "reported_currency": "USD"}
        
        # Get company overview for latest EPS and Market Cap
        overview_query = """
            SELECT 
                market_capitalization,
                eps,
                pe_ratio,
                raw_json as overview_raw_json
            FROM coreiq_av_company_overview
            WHERE ticker = :ticker
            ORDER BY fetched_at_utc DESC
            LIMIT 1
        """
        overview_results = db_manager.execute_query(overview_query, {"ticker": ticker})
        overview = overview_results[0] if overview_results else {}
        
        # Parse overview raw_json
        overview_raw = {}
        if overview and overview.get('overview_raw_json'):
            try:
                overview_raw = json.loads(overview['overview_raw_json'])
            except (json.JSONDecodeError, TypeError):
                overview_raw = {}
        
        # Get shares outstanding from overview
        shares_outstanding = None
        if overview_raw.get('SharesOutstanding'):
            try:
                shares_outstanding = float(overview_raw['SharesOutstanding'])
            except (ValueError, TypeError):
                shares_outstanding = None
        
        # Get latest balance sheet for TEV calculation
        bs_query = """
            SELECT 
                raw_json as bs_raw_json,
                fiscal_date_ending
            FROM coreiq_av_financials_balance_sheet
            WHERE ticker = :ticker
              AND report_type = 'annual'
            ORDER BY fiscal_date_ending DESC
            LIMIT 1
        """
        bs_results = db_manager.execute_query(bs_query, {"ticker": ticker})
        latest_bs = bs_results[0] if bs_results else {}
        
        # Parse balance sheet raw_json
        bs_raw = {}
        if latest_bs and latest_bs.get('bs_raw_json'):
            try:
                bs_raw = json.loads(latest_bs['bs_raw_json'])
            except (json.JSONDecodeError, TypeError):
                bs_raw = {}
        
        # Extract cash and debt from balance sheet
        cash_and_st_investments = None
        if bs_raw.get('cashAndShortTermInvestments'):
            try:
                cash_and_st_investments = float(bs_raw['cashAndShortTermInvestments'])
            except (ValueError, TypeError):
                cash_and_st_investments = None
        
        total_debt = None
        if bs_raw.get('shortLongTermDebtTotal'):
            try:
                total_debt = float(bs_raw['shortLongTermDebtTotal'])
            except (ValueError, TypeError):
                total_debt = None
        
        total_shareholder_equity = None
        if bs_raw.get('totalShareholderEquity'):
            try:
                total_shareholder_equity = float(bs_raw['totalShareholderEquity'])
            except (ValueError, TypeError):
                total_shareholder_equity = None
        
        # Get market cap from overview (in millions for consistency)
        market_cap = None
        if overview and overview.get('market_capitalization'):
            try:
                market_cap = float(overview['market_capitalization'])
            except (ValueError, TypeError):
                market_cap = None
        
        # Create periods
        periods = [FiscalPeriod.from_date(row['fiscal_date_ending']) for row in results]
        
        # Build line items
        line_items = []
        
        # Helper to safely get float value
        def safe_float_val(val):
            if val is None or val == 'None':
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None
        
        # Helper to convert to millions
        def to_millions(val):
            if val is None:
                return None
            return val / 1_000_000
        
        # Get reported currency from first row
        reported_currency = results[0]['reported_currency'] if results else 'USD'
        
        # 1. Total Revenue
        total_revenue_vals = [to_millions(safe_float_val(row['total_revenue'])) for row in results]
        line_items.append({"label": "Total Revenue", "values": total_revenue_vals, "is_bold": True, "indent": 0})
        
        # 2. Growth Over Prior Year (calculated)
        growth_vals = []
        for i, row in enumerate(results):
            curr = safe_float_val(row['total_revenue'])
            if i > 0:
                prev = safe_float_val(results[i-1]['total_revenue'])
                if curr is not None and prev is not None and prev != 0:
                    growth = ((curr - prev) / abs(prev)) * 100
                    growth_vals.append(growth)
                else:
                    growth_vals.append(None)
            else:
                growth_vals.append(None)  # No growth for first period
        line_items.append({"label": "Growth Over Prior Year", "values": growth_vals, "is_bold": False, "indent": 1, "is_percent": True})
        
        # 3. Gross Profit
        gross_profit_vals = [to_millions(safe_float_val(row['gross_profit'])) for row in results]
        line_items.append({"label": "Gross Profit", "values": gross_profit_vals, "is_bold": True, "indent": 0})
        
        # 5. Margin % (calculated from raw_json for accuracy)
        gp_margin_vals = []
        for row in results:
            raw = json.loads(row['raw_json']) if row['raw_json'] else {}
            gp = safe_float_val(row['gross_profit'])
            tr = safe_float_val(row['total_revenue'])
            if gp is not None and tr is not None and tr != 0:
                gp_margin_vals.append((gp / tr) * 100)
            else:
                gp_margin_vals.append(None)
        line_items.append({"label": "Margin %", "values": gp_margin_vals, "is_bold": False, "indent": 1, "is_percent": True})
        
        # 4. EBITDA
        ebitda_vals = [to_millions(safe_float_val(row['ebitda'])) for row in results]
        line_items.append({"label": "EBITDA", "values": ebitda_vals, "is_bold": True, "indent": 0})
        
        # 8. EBITDA Margin %
        ebitda_margin_vals = []
        for row in results:
            ebitda = safe_float_val(row['ebitda'])
            tr = safe_float_val(row['total_revenue'])
            if ebitda is not None and tr is not None and tr != 0:
                ebitda_margin_vals.append((ebitda / tr) * 100)
            else:
                ebitda_margin_vals.append(None)
        line_items.append({"label": "Margin %", "values": ebitda_margin_vals, "is_bold": False, "indent": 1, "is_percent": True})
        
        # 5. EBIT
        ebit_vals = [to_millions(safe_float_val(row['ebit'])) for row in results]
        line_items.append({"label": "EBIT", "values": ebit_vals, "is_bold": True, "indent": 0})
        
        # 11. EBIT Margin %
        ebit_margin_vals = []
        for row in results:
            ebit = safe_float_val(row['ebit'])
            tr = safe_float_val(row['total_revenue'])
            if ebit is not None and tr is not None and tr != 0:
                ebit_margin_vals.append((ebit / tr) * 100)
            else:
                ebit_margin_vals.append(None)
        line_items.append({"label": "Margin %", "values": ebit_margin_vals, "is_bold": False, "indent": 1, "is_percent": True})
        
        # 6. Earnings from Cont. Ops
        cont_ops_vals = [to_millions(safe_float_val(row['net_income_from_continuing_operations'])) for row in results]
        line_items.append({"label": "Earnings from Cont. Ops.", "values": cont_ops_vals, "is_bold": True, "indent": 0})
        
        # 14. Cont Ops Margin %
        cont_ops_margin_vals = []
        for row in results:
            cont_ops = safe_float_val(row['net_income_from_continuing_operations'])
            tr = safe_float_val(row['total_revenue'])
            if cont_ops is not None and tr is not None and tr != 0:
                cont_ops_margin_vals.append((cont_ops / tr) * 100)
            else:
                cont_ops_margin_vals.append(None)
        line_items.append({"label": "Margin %", "values": cont_ops_margin_vals, "is_bold": False, "indent": 1, "is_percent": True})
        
        # 7. Net Income
        net_income_vals = [to_millions(safe_float_val(row['net_income'])) for row in results]
        line_items.append({"label": "Net Income", "values": net_income_vals, "is_bold": True, "indent": 0})
        
        # 17. Net Income Margin %
        ni_margin_vals = []
        for row in results:
            ni = safe_float_val(row['net_income'])
            tr = safe_float_val(row['total_revenue'])
            if ni is not None and tr is not None and tr != 0:
                ni_margin_vals.append((ni / tr) * 100)
            else:
                ni_margin_vals.append(None)
        line_items.append({"label": "Margin %", "values": ni_margin_vals, "is_bold": False, "indent": 1, "is_percent": True})
        
        # 8. Diluted EPS - from raw_json
        eps_vals = []
        for row in results:
            raw = json.loads(row['raw_json']) if row['raw_json'] else {}
            # Try to get diluted EPS from raw_json if available
            eps = safe_float_val(raw.get('dilutedEPS') or raw.get('dilutedEps'))
            if eps is None and row['net_income'] and shares_outstanding:
                # Calculate if not available
                ni = safe_float_val(row['net_income'])
                if ni is not None and shares_outstanding > 0:
                    eps = ni / shares_outstanding
            eps_vals.append(eps)
        line_items.append({"label": "Diluted EPS Excl. Extra Items", "values": eps_vals, "is_bold": True, "indent": 0})
        
        # 9. EPS Growth Over Prior Year
        eps_growth_vals = []
        for i, eps in enumerate(eps_vals):
            if i > 0 and eps is not None and eps_vals[i-1] is not None and eps_vals[i-1] != 0:
                growth = ((eps - eps_vals[i-1]) / abs(eps_vals[i-1])) * 100
                eps_growth_vals.append(growth)
            else:
                eps_growth_vals.append(None)
        line_items.append({"label": "Growth Over Prior Year", "values": eps_growth_vals, "is_bold": False, "indent": 1, "is_percent": True, "has_grey_sep": True})
        
        # 10. Same Store Sales Growth % (not available in most data, will show NA or -)
        same_store_vals = [None] * len(results)
        line_items.append({"label": "Same Store Sales Growth %", "values": same_store_vals, "is_bold": True, "indent": 0, "has_grey_sep": True})

        # --- Append Next Fiscal Year Estimate column (E) ---
        # Only show estimate if end_date equals the maximum available date in the income statement
        max_date_query = """
            SELECT MAX(fiscal_date_ending) AS max_date
            FROM coreiq_av_financials_income_statement
            WHERE ticker = :ticker
              AND report_type = 'annual'
        """
        max_date_results = db_manager.execute_query(max_date_query, {"ticker": ticker})
        max_available_date = max_date_results[0]["max_date"] if max_date_results else None
        if max_available_date and hasattr(max_available_date, "date"):
            max_available_date = max_available_date.date()

        estimates = []
        if max_available_date and end_date >= max_available_date:
            estimates = KeyStatsRepository.get_estimated_data(ticker, end_date)

        if estimates and line_items:
            # Last actual revenue (millions) and EPS — used for growth calc of first E column
            last_actual_rev_mm = None
            for row in reversed(results):
                if row["total_revenue"] is not None:
                    last_actual_rev_mm = to_millions(safe_float_val(row["total_revenue"]))
                    break

            last_actual_eps = None
            for eps in reversed(eps_vals):
                if eps is not None:
                    last_actual_eps = eps
                    break

            prev_est_rev_mm = last_actual_rev_mm
            prev_est_eps = last_actual_eps

            for est in estimates:
                est_date = est["estimate_date"]
                est_period = FiscalPeriod(
                    date=est_date,
                    label=f"12 Months\n{est_date.strftime('%b-%d-%Y')}",
                    is_estimated=True,
                )
                periods.append(est_period)

                est_rev_mm = est["rev_avg"] / 1_000_000 if est["rev_avg"] is not None else None
                est_eps = est["eps_avg"]

                # Growth vs previous period (actual or prior estimate)
                if est_rev_mm is not None and prev_est_rev_mm is not None and prev_est_rev_mm != 0:
                    rev_growth_est = ((est_rev_mm - prev_est_rev_mm) / abs(prev_est_rev_mm)) * 100
                else:
                    rev_growth_est = None

                if est_eps is not None and prev_est_eps is not None and prev_est_eps != 0:
                    eps_growth_est = ((est_eps - prev_est_eps) / abs(prev_est_eps)) * 100
                else:
                    eps_growth_est = None

                # Append one value per line item for this E column
                seen_revenue = False
                seen_eps = False
                for item in line_items:
                    lbl = item["label"]
                    is_bold_item = item.get("is_bold", False)
                    if lbl == "Total Revenue" and is_bold_item:
                        item["values"].append(est_rev_mm)
                        seen_revenue = True
                    elif lbl == "Growth Over Prior Year" and seen_revenue and not seen_eps:
                        item["values"].append(rev_growth_est)
                    elif lbl == "Diluted EPS Excl. Extra Items" and is_bold_item:
                        item["values"].append(est_eps)
                        seen_eps = True
                    elif lbl == "Growth Over Prior Year" and seen_eps:
                        item["values"].append(eps_growth_est)
                    else:
                        item["values"].append(None)

                prev_est_rev_mm = est_rev_mm
                prev_est_eps = est_eps

        return {
            "periods": periods,
            "line_items": line_items,
            "reported_currency": reported_currency,
            # Additional data for capitalization section
            "market_cap": to_millions(market_cap),
            "cash": to_millions(cash_and_st_investments),
            "total_debt": to_millions(total_debt),
            "total_equity": to_millions(total_shareholder_equity),
            "latest_eps": overview.get('eps'),
            "latest_pe": overview.get('pe_ratio')
        }
    
    @staticmethod
    def get_estimated_data(ticker: str, end_date: date) -> List[Dict[str, Any]]:
        """Fetch ALL annual analyst estimates whose estimate_date > end_date.

        Only fiscal-year horizons (not quarterly) — returns list, may be empty.
        Each dict: estimate_date (date), rev_avg (float|None in USD), eps_avg (float|None).
        """
        query = """
            SELECT estimate_date, eps_est_avg, rev_est_avg
            FROM coreiq_av_financials_earnings_estimates
            WHERE ticker = :ticker
              AND estimate_date > :end_date
              AND horizon IN ('historical fiscal year', 'next fiscal year')
            ORDER BY estimate_date ASC
        """
        results = db_manager.execute_query(query, {"ticker": ticker, "end_date": end_date})
        estimates = []
        for row in results:
            if row["eps_est_avg"] is None and row["rev_est_avg"] is None:
                continue
            est_date = row["estimate_date"]
            if hasattr(est_date, "date"):
                est_date = est_date.date()
            estimates.append({
                "estimate_date": est_date,
                "eps_avg": float(row["eps_est_avg"]) if row["eps_est_avg"] is not None else None,
                "rev_avg": float(row["rev_est_avg"]) if row["rev_est_avg"] is not None else None,
            })
        return estimates

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
        return "USD"


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

    @staticmethod
    def get_conversion_rates_bulk(
        from_currency: str,
        to_currency: str,
        as_of_dates: List[date]
    ) -> Dict[date, float]:
        """
        Get conversion rates for multiple dates in a single query.
        
        For each as_of_date, finds the closest rate on or before that date.
        Returns a dict mapping each requested date to its conversion rate.
        
        Args:
            from_currency: Source currency code (e.g., 'USD')
            to_currency: Target currency code (e.g., 'EUR')
            as_of_dates: List of dates for which rates are needed
            
        Returns:
            Dict mapping each date to its conversion rate (1.0 if same currency or not found)
        """
        if from_currency == to_currency:
            return {d: 1.0 for d in as_of_dates}
        
        if not as_of_dates:
            return {}
        
        # Build a query that fetches the closest rate on or before each date
        # We use a lateral-join style approach via a subquery for each date
        rate_map: Dict[date, float] = {}
        
        # Get all forex data for this pair within a reasonable range
        min_date = min(as_of_dates)
        max_date = max(as_of_dates)
        
        query = """
            SELECT day_date, close
            FROM coreiq_av_forex_daily
            WHERE from_currency = :from_currency
              AND to_currency = :to_currency
              AND day_date <= :max_date
            ORDER BY day_date DESC
        """
        results = db_manager.execute_query(query, {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "max_date": max_date
        })
        
        # Try reverse direction if no results
        reverse = False
        if not results:
            query = """
                SELECT day_date, close
                FROM coreiq_av_forex_daily
                WHERE from_currency = :to_currency
                  AND to_currency = :from_currency
                  AND day_date <= :max_date
                ORDER BY day_date DESC
            """
            results = db_manager.execute_query(query, {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "max_date": max_date
            })
            reverse = True
        
        if not results:
            return {d: 1.0 for d in as_of_dates}
        
        # Build sorted list of (day_date, rate) for binary-search style lookup
        # Results are already sorted DESC by day_date
        for target_date in as_of_dates:
            # Find the first result where day_date <= target_date
            found_rate = None
            for row in results:
                row_date = row['day_date']
                # Handle both date and datetime objects
                if hasattr(row_date, 'date'):
                    row_date = row_date.date()
                if row_date <= target_date:
                    try:
                        rate = float(row['close'])
                        found_rate = (1.0 / rate) if reverse else rate
                    except (ValueError, TypeError, ZeroDivisionError):
                        found_rate = 1.0
                    break
            
            rate_map[target_date] = found_rate if found_rate is not None else 1.0
        
        return rate_map


class StockQuoteRepository:
    """Repository for Stock Quote table — fetches latest price data + company overview."""

    @staticmethod
    def get_latest_quote(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch the most recent day's bar data from coreiq_av_time_series_daily.

        Returns a dict with keys:
            open, high, low, close, volume, day_date,
            change_on_day, change_percent_on_day
        or None if no data found.
        """
        query = """
            SELECT raw_json, day_date
            FROM coreiq_av_time_series_daily
            WHERE ticker = :ticker
              AND raw_json IS NOT NULL
            ORDER BY day_date DESC
            LIMIT 1
        """
        results = db_manager.execute_query(query, {"ticker": ticker})
        if not results:
            return None

        row = results[0]
        raw = {}
        if row.get("raw_json"):
            try:
                raw = json.loads(row["raw_json"])
            except (json.JSONDecodeError, TypeError):
                pass

        bar = raw.get("bar", {})

        def _f(val: Any) -> Optional[float]:
            if val is None:
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        open_p  = _f(bar.get("1. open"))
        high_p  = _f(bar.get("2. high"))
        low_p   = _f(bar.get("3. low"))
        close_p = _f(bar.get("4. close"))
        volume  = _f(bar.get("5. volume"))

        change_on_day = None
        change_pct    = None
        if open_p is not None and close_p is not None and open_p != 0:
            change_on_day = close_p - open_p
            change_pct    = (change_on_day / open_p) * 100.0

        return {
            "open":              open_p,
            "high":              high_p,
            "low":               low_p,
            "close":             close_p,
            "volume":            int(volume) if volume is not None else None,
            "day_date":          row.get("day_date"),
            "change_on_day":     change_on_day,
            "change_percent":    change_pct,
        }

    @staticmethod
    def get_price_history(ticker: str, days: int = 365) -> List[Dict[str, Any]]:
        """
        Fetch daily close prices for charting (last `days` calendar days).

        Returns list of dicts sorted ASC by date:
            [{"date": "2025-01-30", "close": 204.79, "volume": 12345678}, ...]
        """
        query = """
            SELECT day_date, close, raw_json
            FROM coreiq_av_time_series_daily
            WHERE ticker = :ticker
              AND day_date >= DATE_SUB(CURDATE(), INTERVAL :days DAY)
              AND raw_json IS NOT NULL
            ORDER BY day_date ASC
        """
        results = db_manager.execute_query(query, {"ticker": ticker, "days": days})
        history = []
        for row in results:
            close_val = None
            volume_val = None
            # Prefer the dedicated column; fall back to raw_json
            if row.get("close") is not None:
                try:
                    close_val = float(row["close"])
                except (ValueError, TypeError):
                    pass
            if close_val is None and row.get("raw_json"):
                try:
                    bar = json.loads(row["raw_json"]).get("bar", {})
                    close_val = float(bar.get("4. close", 0)) or None
                    volume_val = int(float(bar.get("5. volume", 0))) or None
                except (ValueError, TypeError, json.JSONDecodeError):
                    pass
            if close_val is not None:
                day = row["day_date"]
                history.append({
                    "date":   str(day) if not isinstance(day, str) else day,
                    "close":  close_val,
                    "volume": volume_val,
                })
        return history

    @staticmethod
    def get_overview_data(ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch company overview fields needed for the Stock Quote table.

        Returns a dict with keys:
            market_cap_mm, shares_outstanding_mm, dividend_yield,
            diluted_eps, pe_ratio, week_52_high, week_52_low
        or None if no data found.
        """
        query = """
            SELECT market_capitalization, dividend_yield, eps, pe_ratio, raw_json
            FROM coreiq_av_company_overview
            WHERE ticker = :ticker
            ORDER BY fetched_at_utc DESC
            LIMIT 1
        """
        results = db_manager.execute_query(query, {"ticker": ticker})
        if not results:
            return None

        row = results[0]
        raw = {}
        if row.get("raw_json"):
            try:
                raw = json.loads(row["raw_json"])
            except (json.JSONDecodeError, TypeError):
                pass

        def _f(val: Any) -> Optional[float]:
            if val is None or val == "None":
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        market_cap = _f(row.get("market_capitalization"))
        market_cap_mm = (market_cap / 1_000_000) if market_cap is not None else None

        shares_raw = _f(raw.get("SharesOutstanding"))
        shares_mm  = (shares_raw / 1_000_000) if shares_raw is not None else None

        week_52_high = _f(raw.get("52WeekHigh"))
        week_52_low  = _f(raw.get("52WeekLow"))

        return {
            "market_cap_mm":        market_cap_mm,
            "shares_outstanding_mm": shares_mm,
            "dividend_yield":       _f(row.get("dividend_yield")),
            "diluted_eps":          _f(row.get("eps")),
            "pe_ratio":             _f(row.get("pe_ratio")),
            "week_52_high":         week_52_high,
            "week_52_low":          week_52_low,
        }


class FilingMetricRepository:
    """Repository for filing_metrics table — SEC filing metric search."""

    # Synonym map: user-typed term → list of DB label variants.
    # All keys and values must be lowercase. The original query is always
    # searched as well — these are ADDITIONAL terms, not replacements.
    SYNONYM_MAP: Dict[str, List[str]] = {
        # Income Statement
        "revenue":                   ["net sales", "total revenue", "revenues", "total net revenue"],
        "total revenue":             ["net sales", "revenue", "total net revenue"],
        "net revenue":               ["net sales", "revenue"],
        "sales":                     ["net sales", "revenue", "total revenue"],
        "gross profit":              ["gross margin", "gross income"],
        "gross margin":              ["gross profit", "gross income"],
        "cost of goods sold":        ["cost of sales", "cost of revenue", "cost of products"],
        "cogs":                      ["cost of sales", "cost of revenue", "cost of goods sold"],
        "cost of revenue":           ["cost of sales", "cost of goods sold"],
        "selling general":           ["selling, general and administrative", "sg&a", "sga"],
        "sg&a":                      ["selling, general and administrative", "selling general"],
        "sga":                       ["selling, general and administrative", "selling general and admin"],
        "operating expenses":        ["total operating expenses", "operating expense"],
        "operating income":          ["income from operations", "operating profit", "ebit"],
        "operating profit":          ["operating income", "income from operations"],
        "ebit":                      ["operating income", "operating profit", "income from operations"],
        "interest expense":          ["other income", "interest and other income", "net interest expense"],
        "interest income":           ["other income", "interest and other income", "investment income"],
        "net interest":              ["other income", "interest expense", "interest income"],
        "other income":              ["other income/(expense), net", "other income/expense"],
        "r&d":                       ["research and development", "research & development"],
        "research and development":  ["r&d", "research & development"],
        "depreciation":              ["depreciation and amortization", "depreciation & amortization", "d&a"],
        "amortization":              ["depreciation and amortization", "depreciation & amortization"],
        "d&a":                       ["depreciation and amortization", "depreciation"],
        "depreciation amortization": ["depreciation and amortization"],
        "net income":                ["net income (loss)", "net earnings", "profit after tax", "earnings"],
        "earnings":                  ["net income", "net earnings"],
        "diluted eps":               ["diluted (in dollars per share)", "earnings per share diluted"],
        "eps":                       ["diluted (in dollars per share)", "basic (in dollars per share)", "earnings per share"],
        "basic eps":                 ["basic (in dollars per share)", "earnings per share basic"],
        "stock based comp":          ["share-based compensation expense", "stock-based compensation"],
        "stock compensation":        ["share-based compensation expense", "stock-based compensation"],
        "share based compensation":  ["share-based compensation expense"],
        "advertising":               ["advertising expense", "advertising costs"],
        "income tax":                ["provision for income taxes", "income tax expense"],
        "tax expense":               ["provision for income taxes", "income tax expense"],

        # Balance Sheet — Assets
        "cash":                      ["cash and cash equivalents", "cash & cash equivalents"],
        "cash equivalents":          ["cash and cash equivalents"],
        "short term investments":    ["marketable securities", "short-term investments"],
        "marketable securities":     ["short-term investments", "short term investments"],
        "accounts receivable":       ["accounts receivable, net", "trade receivables"],
        "receivables":               ["accounts receivable, net", "vendor non-trade receivables"],
        "inventory":                 ["inventories"],
        "inventories":               ["inventory"],
        "prepaid":                   ["prepaid expenses", "other current assets"],
        "current assets":            ["total current assets"],
        "total current assets":      ["current assets"],
        "ppe":                       ["property, plant and equipment, net", "property plant equipment"],
        "property plant equipment":  ["property, plant and equipment, net", "gross property, plant and equipment"],
        "net ppe":                   ["property, plant and equipment, net"],
        "gross ppe":                 ["gross property, plant and equipment"],
        "accumulated depreciation":  ["accumulated depreciation"],
        "goodwill":                  ["goodwill and intangible assets", "intangible assets"],
        "intangibles":               ["intangible assets", "goodwill"],
        "total assets":              ["assets, total"],

        # Balance Sheet — Liabilities
        "accounts payable":          ["accounts payable", "trade payables"],
        "current liabilities":       ["total current liabilities"],
        "long term debt":            ["term debt", "total term debt", "long-term debt"],
        "long-term debt":            ["term debt", "total term debt"],
        "term debt":                 ["long-term debt", "long term debt", "total term debt"],
        "total debt":                ["term debt", "total term debt", "long-term debt"],
        "debt to equity":            ["debt-to-equity", "total debt-to-equity", "lt debt-to-equity"],
        "debt equity":               ["debt-to-equity", "total debt-to-equity"],
        "deferred revenue":          ["deferred revenue", "unearned revenue"],
        "unearned revenue":          ["deferred revenue"],
        "total liabilities":         ["liabilities, total"],
        "operating lease":           ["operating lease liabilities, current", "operating lease liabilities, non-current"],
        "finance lease":             ["finance lease liabilities, current", "finance lease liabilities, non-current"],
        "commercial paper":          ["commercial paper"],

        # Balance Sheet — Equity
        "retained earnings":         ["accumulated deficit", "retained deficit"],
        "accumulated deficit":       ["retained earnings"],
        "shareholders equity":       ["total shareholders' equity", "stockholders equity"],
        "stockholders equity":       ["total shareholders' equity", "shareholders equity"],
        "total equity":              ["total shareholders' equity", "shareholders equity"],
        "book value":                ["total shareholders' equity", "book value of equity"],

        # Cash Flow
        "cash from operations":      ["cash generated by operating activities", "operating cash flow", "cash from operating"],
        "operating cash flow":       ["cash generated by operating activities", "cash from operations"],
        "capex":                     ["payments for acquisition of property, plant and equipment", "capital expenditure", "capital expenditures"],
        "capital expenditure":       ["payments for acquisition of property, plant and equipment", "capex"],
        "capital expenditures":      ["payments for acquisition of property, plant and equipment", "capex"],
        "cash from investing":       ["cash generated by/(used in) investing activities"],
        "investing activities":      ["cash generated by/(used in) investing activities"],
        "cash from financing":       ["cash used in financing activities"],
        "financing activities":      ["cash used in financing activities"],
        "dividends":                 ["payments for dividends and dividend equivalents", "dividends paid"],
        "dividends paid":            ["payments for dividends and dividend equivalents"],
        "buyback":                   ["common stock repurchased", "repurchases of common stock", "share repurchase"],
        "share repurchase":          ["common stock repurchased", "repurchases of common stock"],
        "stock repurchase":          ["common stock repurchased", "repurchases of common stock"],
        "debt issuance":             ["proceeds from issuance of term debt, net"],
        "debt repayment":            ["repayments of term debt", "repayment of debt"],

        # Calculated / Derived (will exist after Phase 6.3)
        "ebitda":                    ["ebitda", "earnings before interest tax depreciation"],
        "net debt":                  ["net debt"],
        "enterprise value":          ["enterprise value", "tev"],
        "gross margin %":            ["gross margin percentage", "gross margin %"],
        "operating margin":          ["operating margin %", "operating income margin"],
        "net margin":                ["net income margin", "net margin %", "profit margin"],

        # Shares
        "shares outstanding":        ["common stock, shares outstanding (in shares)", "entity common stock, shares outstanding"],
        "diluted shares":            ["diluted (in shares)", "weighted average diluted shares"],
        "basic shares":              ["basic (in shares)", "weighted average basic shares"],

        # Segments (search by dimension_label via original_label="Net sales")
        # AAPL segments
        "iphone":                    ["iphone revenue", "iphone net sales"],
        "iphone revenue":            ["iphone", "net sales"],
        "mac":                       ["mac revenue", "mac net sales"],
        "ipad":                      ["ipad revenue", "ipad net sales"],
        "services":                  ["services revenue", "services net sales"],
        "wearables":                 ["wearables, home and accessories", "wearables revenue"],
        "americas":                  ["americas revenue", "americas net sales"],
        "europe":                    ["europe revenue", "europe net sales"],
        "china":                     ["greater china", "china revenue"],
        "greater china":             ["china", "greater china revenue"],

        # AMZN segments
        "aws":                       ["amazon web services"],
        "north america":             ["north america revenue", "north america net sales"],
        "international":             ["international revenue", "international net sales"],
        "total net sales":           ["net sales", "total revenue", "revenue"],

        # M (Macy's) segments
        "macy's":                    ["macys", "macy's first"],
        "bloomingdale":              ["bloomingdale's", "bloomingdales"],
        "net sales":                 ["total net sales", "total revenue", "revenue"],
    }

    @staticmethod
    def _expand_query(query: str) -> List[str]:
        """Return list of LIKE patterns: original query + all synonym expansions."""
        q = query.strip().lower()
        patterns = [f"%{q}%"]
        for synonym in FilingMetricRepository.SYNONYM_MAP.get(q, []):
            patterns.append(f"%{synonym.lower()}%")
        return patterns

    @staticmethod
    def search(
        ticker: str,
        fiscal_year: int,
        doc_type: str,
        query: str,
        limit: int = 20,
    ) -> List[FilingMetricResult]:
        """
        Search filing metrics by original_label OR standard_concept OR dimension_label.
        Expands the query with synonyms so e.g. 'Gross Profit' finds 'Gross margin'.
        """
        patterns = FilingMetricRepository._expand_query(query)

        # Build dynamic OR clauses — one per pattern, across label + concept + dimension
        or_clauses = []
        params: Dict[str, Any] = {
            "ticker": ticker,
            "fiscal_year": fiscal_year,
            "doc_type": doc_type,
            "limit": limit,
        }
        for i, pattern in enumerate(patterns):
            k = f"q{i}"
            or_clauses.append(
                f"(LOWER(original_label) LIKE :{k} OR LOWER(standard_concept) LIKE :{k} OR LOWER(dimension_label) LIKE :{k})"
            )
            params[k] = pattern

        where_synonyms = " OR ".join(or_clauses)

        sql = f"""
            SELECT original_label, numeric_value, unit_ref, fiscal_year,
                   is_dimensioned, dimension_label, statement_type, ixbrl_id,
                   standard_concept, concept, balance, period_type,
                   period_start, period_end, period_instant,
                   value, source, llm_query, dimension
            FROM filing_metrics
            WHERE ticker = :ticker
              AND fiscal_year = :fiscal_year
              AND doc_type = :doc_type
              AND ({where_synonyms})
              AND (standard_concept IS NULL OR standard_concept NOT LIKE '%Text Block')
              AND numeric_value IS NOT NULL
            ORDER BY CASE LOWER(original_label)
                       WHEN 'net sales'               THEN 0
                       WHEN 'total net sales'          THEN 0
                       WHEN 'revenue'                  THEN 0
                       WHEN 'net revenue'               THEN 0
                       WHEN 'revenues'                 THEN 0
                       WHEN 'total revenue'             THEN 0
                       WHEN 'operating income'          THEN 1
                       WHEN 'operating income (loss)'   THEN 1
                       WHEN 'net income'                THEN 2
                       WHEN 'net income (loss)'         THEN 2
                       WHEN 'net earnings'              THEN 2
                       WHEN 'total assets'              THEN 3
                       WHEN 'cash and cash equivalents' THEN 3
                       WHEN 'ebitda'                    THEN 4
                       WHEN 'free cash flow'            THEN 4
                       WHEN 'long-term debt'            THEN 5
                       WHEN 'total debt'                THEN 5
                       WHEN 'net debt'                  THEN 6
                       ELSE 10
                     END ASC,
                     is_dimensioned ASC,
                     CHAR_LENGTH(original_label) ASC, original_label ASC
            LIMIT :limit
        """

        results = db_manager.execute_query(sql, params)
        return [
            FilingMetricResult(
                original_label=row["original_label"] or "",
                numeric_value=row["numeric_value"],
                unit_ref=row["unit_ref"],
                fiscal_year=row["fiscal_year"],
                is_dimensioned=bool(row["is_dimensioned"]),
                dimension_label=row["dimension_label"],
                statement_type=row["statement_type"],
                ixbrl_id=row["ixbrl_id"],
                standard_concept=row["standard_concept"],
                concept=row["concept"],
                balance=row["balance"],
                period_type=row["period_type"],
                period_start=str(row["period_start"]) if row.get("period_start") else None,
                period_end=str(row["period_end"]) if row.get("period_end") else None,
                period_instant=str(row["period_instant"]) if row.get("period_instant") else None,
                value=row["value"],
                source=row.get("source"),
                calculation_note=row.get("llm_query") if row.get("source") == "calculated" else None,
                dimension=row.get("dimension"),
            )
            for row in results
        ]

    @staticmethod
    def search_with_llm_fallback(
        ticker: str,
        fiscal_year: int,
        doc_type: str,
        query: str,
        limit: int = 20,
    ) -> tuple:
        """
        Search filing metrics; if DB returns no results, attempt LLM extraction.

        Returns:
            (results: List[FilingMetricResult], used_llm: bool)
            used_llm=True means LLM was called (show spinner before calling this)
        """
        db_results = FilingMetricRepository.search(
            ticker=ticker,
            fiscal_year=fiscal_year,
            doc_type=doc_type,
            query=query,
            limit=limit,
        )

        if db_results:
            return db_results, False

        # DB miss — try LLM extraction
        api_key = __import__("os").getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            return [], False

        try:
            from core.llm_extractor import LLMExtractor
            from core.database import db_manager as _dbm

            engine = _dbm._engine
            if engine is None:
                return [], False

            with engine.begin() as conn:
                llm_results = LLMExtractor.extract(
                    conn=conn,
                    ticker=ticker,
                    fiscal_year=fiscal_year,
                    doc_type=doc_type,
                    query=query,
                )
            return llm_results, True
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"[LLM fallback] error: {e}")
            return [], False
