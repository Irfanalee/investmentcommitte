"""
Data Layer: Financial data fetching using yfinance
"""
from typing import Dict, List, Optional
from datetime import datetime
import yfinance as yf
from pydantic import BaseModel, Field


class FinancialMetrics(BaseModel):
    """Structured financial data for a stock ticker"""
    ticker: str
    current_price: Optional[float] = None
    pe_ratio: Optional[float] = None
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    market_cap: Optional[float] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    news_headlines: List[str] = Field(default_factory=list)
    fetch_timestamp: datetime = Field(default_factory=datetime.now)
    error: Optional[str] = None


def get_financial_metrics(ticker: str) -> FinancialMetrics:
    """
    Fetch comprehensive financial metrics for a given stock ticker.

    Args:
        ticker: Stock ticker symbol (e.g., "NVDA", "AAPL", "SAAB-B.ST")

    Returns:
        FinancialMetrics object with all available data
    """
    try:
        # Auto-correct common international ticker formats
        # Swedish stocks (e.g., SAAB-B -> SAAB-B.ST)
        if '-' in ticker and '.' not in ticker:
            # Try adding Stockholm exchange suffix
            ticker_variants = [ticker, f"{ticker}.ST"]
        else:
            ticker_variants = [ticker]

        # Try each variant
        stock = None
        working_ticker = ticker
        for variant in ticker_variants:
            try:
                test_stock = yf.Ticker(variant)
                test_info = test_stock.info
                # Check if we got valid data
                if test_info.get('currentPrice') or test_info.get('regularMarketPrice'):
                    stock = test_stock
                    working_ticker = variant
                    break
            except:
                continue

        if stock is None:
            stock = yf.Ticker(ticker)
            working_ticker = ticker
        info = stock.info

        # Fetch recent news (last 5 headlines)
        news = stock.news[:5] if hasattr(stock, 'news') and stock.news else []
        headlines = []
        for article in news:
            # Try different paths for title (yfinance API structure varies)
            title = (
                article.get('title') or
                article.get('content', {}).get('title') or
                'No title available'
            )
            headlines.append(title)

        # Extract key metrics with safe fallbacks
        metrics = FinancialMetrics(
            ticker=working_ticker.upper(),
            current_price=info.get('currentPrice') or info.get('regularMarketPrice'),
            pe_ratio=info.get('trailingPE') or info.get('forwardPE'),
            week_52_high=info.get('fiftyTwoWeekHigh'),
            week_52_low=info.get('fiftyTwoWeekLow'),
            market_cap=info.get('marketCap'),
            volume=info.get('volume'),
            avg_volume=info.get('averageVolume'),
            news_headlines=headlines if headlines else ["No recent news available"]
        )

        return metrics

    except Exception as e:
        return FinancialMetrics(
            ticker=ticker.upper(),
            error=f"Failed to fetch data: {str(e)}"
        )


def format_metrics_for_agent(metrics: FinancialMetrics) -> str:
    """
    Format financial metrics into a clean text block for LLM consumption.

    Args:
        metrics: FinancialMetrics object

    Returns:
        Formatted string with all relevant data
    """
    if metrics.error:
        return f"ERROR: {metrics.error}"

    output = f"""
FINANCIAL DATA FOR {metrics.ticker}
{'=' * 50}

PRICE METRICS:
- Current Price: ${metrics.current_price:.2f} if metrics.current_price else 'N/A'
- 52-Week High: ${metrics.week_52_high:.2f} if metrics.week_52_high else 'N/A'
- 52-Week Low: ${metrics.week_52_low:.2f} if metrics.week_52_low else 'N/A'

VALUATION:
- P/E Ratio: {f"{metrics.pe_ratio:.2f}" if metrics.pe_ratio else 'N/A'}
- Market Cap: ${metrics.market_cap:,.0f} if metrics.market_cap else 'N/A'

VOLUME:
- Current Volume: {f"{metrics.volume:,}" if metrics.volume else 'N/A'}
- Average Volume: {f"{metrics.avg_volume:,}" if metrics.avg_volume else 'N/A'}

RECENT NEWS HEADLINES:
"""

    for i, headline in enumerate(metrics.news_headlines, 1):
        output += f"{i}. {headline}\n"

    output += f"\nData fetched at: {metrics.fetch_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    return output
