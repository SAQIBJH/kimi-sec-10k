"""
Data repository for fetching market data from database.
"""
from typing import List, Optional, Tuple, Dict, Any
from datetime import date, datetime, timedelta
import json

from core.database import db_manager
from data.models import (
    Company, IncomeStatementLineItem, FiscalPeriod, IncomeStatementData,
    NewsArticle, TickerSentiment
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
        
        # Fetch raw data
        query = """
            SELECT *
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
