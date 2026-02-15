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


@dataclass
class CompanyOverview:
    """Company overview data from coreiq_av_company_overview table."""
    ticker: str
    name: str
    exchange: Optional[str]
    currency: Optional[str]
    country: Optional[str]
    sector: Optional[str]
    industry: Optional[str]
    company_description: Optional[str]
    official_site: Optional[str]
    fiscal_year_end: Optional[str]
    cik: Optional[str]
    market_capitalization: Optional[int]
    pe_ratio: Optional[float]
    eps: Optional[float]
    dividend_yield: Optional[float]
    analyst_target_price: Optional[float]
    fetched_at_utc: datetime
    
    # Fields from raw_json
    address: Optional[str] = None
    revenue_ttm: Optional[float] = None
    ebitda: Optional[float] = None
    profit_margin: Optional[float] = None
    shares_outstanding: Optional[int] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    dividend_per_share: Optional[float] = None
    latest_quarter: Optional[str] = None
    
    # Placeholder fields (not in database, will show N/A)
    employees: Optional[str] = None
    year_founded: Optional[str] = None
    professionals_profiled: Optional[str] = None
    coverage_summary: Optional[str] = None
    coverage_list: Optional[str] = None
    relationships: Optional[str] = None
    projects: Optional[str] = None
    activity_logs: Optional[str] = None
    
    @property
    def display_name(self) -> str:
        """Format: 'Macy's Inc. (NYSE:M)'"""
        exchange = self.exchange or ""
        return f"{self.name} ({exchange}:{self.ticker})"
    
    @property
    def formatted_market_cap(self) -> str:
        """Format market cap in billions/millions."""
        if not self.market_capitalization:
            return "N/A"
        if self.market_capitalization >= 1_000_000_000:
            return f"${self.market_capitalization / 1_000_000_000:.2f}B"
        elif self.market_capitalization >= 1_000_000:
            return f"${self.market_capitalization / 1_000_000:.2f}M"
        else:
            return f"${self.market_capitalization:,}"
    
    @property
    def website_display(self) -> str:
        """Clean website URL for display - matches wireframe format (macys.com)."""
        if not self.official_site:
            return "N/A"
        # Remove https://, http://, www., and trailing slashes
        cleaned = self.official_site.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
        return cleaned


@dataclass
class BalanceSheetLineItem:
    """Balance sheet line item for display."""
    label: str
    key: str  # Database column name
    values: List[Optional[float]]  # Values for each period
    is_calculated: bool = False
    section: str = ""  # 'assets', 'liabilities', 'equity'


@dataclass
class BalanceSheetData:
    """Complete balance sheet data for a company."""
    company: Company
    periods: List[FiscalPeriod]
    line_items: List[BalanceSheetLineItem]


@dataclass
class CashFlowLineItem:
    """Cash flow statement line item for display."""
    label: str
    key: str  # Database column name or raw_json key
    values: List[Optional[float]]  # Values for each period
    is_calculated: bool = False
    section: str = ""  # 'operating', 'investing', 'financing'


@dataclass
class CashFlowData:
    """Complete cash flow statement data for a company."""
    company: Company
    periods: List[FiscalPeriod]
    line_items: List[CashFlowLineItem]


@dataclass
class EarningsCall:
    """Earnings call transcript model from coreiq_av_earnings_call_transcripts table."""
    id: int
    source: Optional[str]
    ticker: str
    quarter: str  # e.g., "2025Q4"
    year: int
    q: int  # Quarter number 1-4
    transcript_text: Optional[str]
    has_transcript: bool
    title: Optional[str]
    event_datetime_utc: Optional[datetime]
    fetched_at_utc: datetime
    
    @property
    def display_title(self) -> str:
        """Format: 'Amazon (AMZN) Earnings Call 2025 - Q1'"""
        return f"{self.ticker} Earnings Call {self.year} - Q{self.q}"
    
    @property
    def formatted_quarter(self) -> str:
        """Format: 'Q1 2025'"""
        return f"Q{self.q} {self.year}"
    
    @property
    def formatted_date(self) -> str:
        """Format event date or return N/A."""
        if self.event_datetime_utc:
            return self.event_datetime_utc.strftime("%B %d, %Y")
        return "N/A"
    
    @property
    def speaker_sections(self) -> List[Dict[str, str]]:
        """Parse transcript into speaker sections.
        
        Returns list of dicts with 'speaker' and 'text' keys.
        Speaker names are identified by pattern: "Name:" at start of line.
        """
        if not self.transcript_text:
            return []
        
        sections = []
        current_speaker = "Operator"
        current_text = []
        
        for line in self.transcript_text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts with a speaker name (Pattern: "Name:" or "Name :")
            if ':' in line:
                potential_speaker = line.split(':')[0].strip()
                # If the rest of the line after colon is not empty, it's likely a speaker
                remaining_text = line[len(potential_speaker) + 1:].strip()
                
                # Common speaker patterns
                if potential_speaker and (
                    potential_speaker.isupper() or  # OPERATOR, DAVE FILDES
                    potential_speaker.istitle() or  # Operator, Dave Fildes
                    ' ' in potential_speaker or     # Full names
                    potential_speaker.lower() in ['operator', 'ceo', 'cfo']
                ):
                    # Save previous section
                    if current_text:
                        sections.append({
                            'speaker': current_speaker,
                            'text': ' '.join(current_text)
                        })
                    
                    current_speaker = potential_speaker
                    if remaining_text:
                        current_text = [remaining_text]
                    else:
                        current_text = []
                else:
                    current_text.append(line)
            else:
                current_text.append(line)
        
        # Don't forget the last section
        if current_text:
            sections.append({
                'speaker': current_speaker,
                'text': ' '.join(current_text)
            })
        
        return sections
