"""
Data models for Market Data and Newsroom pages.
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List, Dict, Any


@dataclass
class TickerSentiment:
    """Ticker sentiment data from news article."""
    ticker: str
    relevance_score: str
    ticker_sentiment_label: str
    ticker_sentiment_score: str


@dataclass
class NewsArticle:
    """News article model from coreiq_av_market_news_sentiment table."""
    id: int
    title: str
    summary: str
    url: str
    source: str
    source_domain: str
    time_published: datetime
    time_published_raw: str
    overall_sentiment_score: float
    overall_sentiment_label: str
    banner_image: Optional[str]
    ticker_sentiment: List[TickerSentiment]
    topics: List[Dict[str, str]]
    category_within_source: str
    
    @property
    def formatted_date(self) -> str:
        """Format date as 'January 21, 2026'."""
        return self.time_published.strftime("%B %d, %Y")
    
    @property
    def company_tickers(self) -> List[str]:
        """Get list of company tickers."""
        return [ts.ticker for ts in self.ticker_sentiment]


@dataclass
class Company:
    """Company model from coreiq_companies table."""
    ticker: str
    name: str
    name_coresight: Optional[str]
    exchange: Optional[str]
    
    @property
    def display_name(self) -> str:
        """Format: 'Macy's Inc. (NYSE:M)'"""
        name = self.name_coresight or self.name
        exchange = self.exchange or ""
        return f"{name} ({exchange}:{self.ticker})"


@dataclass
class IncomeStatementLineItem:
    """Income statement line item for display."""
    label: str
    key: str  # Database column name
    values: List[Optional[float]]  # Values for each period
    is_calculated: bool = False


@dataclass
class FiscalPeriod:
    """Fiscal period for column headers."""
    date: date
    label: str
    
    @classmethod
    def from_date(cls, dt: date) -> "FiscalPeriod":
        """Create from date: '12 Months\nJan-29-2021'"""
        return cls(
            date=dt,
            label=f"12 Months\n{dt.strftime('%b-%d-%Y')}"
        )


@dataclass
class IncomeStatementData:
    """Complete income statement data for a company."""
    company: Company
    periods: List[FiscalPeriod]
    line_items: List[IncomeStatementLineItem]
