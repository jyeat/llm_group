# tools/news_tools_newsapi.py
# -*- coding: utf-8 -*-
"""
News Tools (NewsAPI - Free 100 requests/day)
---------------------------------------------
Free alternative to Alpha Vantage using NewsAPI.org
- Free tier: 100 requests/day, 1 month of historical data
- No credit card required for free tier
- Sign up at: https://newsapi.org/

Provides 5 @tool functions:
  1) get_company_news        -> str   (formatted text)
  2) get_industry_news       -> str   (formatted text)
  3) get_macro_news          -> str   (formatted text)
  4) get_news                -> list  (raw list for news_analyst)
  5) get_global_news         -> list  (raw list for news_analyst)
"""

from __future__ import annotations
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import os

import requests
from langchain_core.tools import tool

# Get NewsAPI key from environment
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
NEWSAPI_BASE = "https://newsapi.org/v2/everything"

# Try to import yfinance as fallback
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


# ---------------- Helpers ----------------

def _format_article_block(i: int, it: Dict) -> str:
    """Render one article dict to a readable multi-line block."""
    title = it.get("title") or "N/A"
    url = it.get("url") or ""

    # Handle source field (can be dict or string)
    src = it.get("source", {})
    if isinstance(src, dict):
        src = src.get("name", "N/A")
    elif isinstance(src, str):
        src = src
    else:
        src = "N/A"

    # Parse published date
    when = it.get("publishedAt") or it.get("published_at") or it.get("time_published") or ""
    if when and "T" in when:
        when = when.split("T")[0]  # Just date part

    # Get sentiment if available
    sent = it.get("sentiment", "N/A")
    if sent == "N/A" and "overall_sentiment_label" in it:
        sent = it["overall_sentiment_label"]

    # Get description/summary
    desc = (it.get("description") or it.get("summary") or "").strip()
    if desc:
        desc = desc[:400] + ("..." if len(desc) > 400 else "")

    return (
        f"[{i}] {title}\n"
        f"    Source: {src} | Published: {when} | Sentiment: {sent}\n"
        f"    URL: {url}\n"
        f"    Summary: {desc}\n"
    )


def _fetch_newsapi(
    q: str,
    from_date: str,
    to_date: str,
    language: str = "en",
    sort_by: str = "publishedAt",
    limit: int = 50,
) -> List[Dict]:
    """
    Fetch news from NewsAPI.org (free tier: 100 requests/day).

    Args:
        q: Search query
        from_date: ISO date 'YYYY-MM-DD'
        to_date: ISO date 'YYYY-MM-DD'
        language: Language code (default 'en')
        sort_by: 'publishedAt', 'relevancy', or 'popularity'
        limit: Max results (NewsAPI free tier maxes at 100 total)

    Returns:
        List of article dicts
    """
    if not NEWSAPI_KEY:
        print("Warning: NEWSAPI_KEY not configured in .env file")
        return []

    try:
        params = {
            "q": q,
            "from": from_date,
            "to": to_date,
            "language": language,
            "sortBy": sort_by,
            "pageSize": min(limit, 100),
            "apiKey": NEWSAPI_KEY,
        }

        r = requests.get(NEWSAPI_BASE, params=params, timeout=10)
        data = r.json()

        if data.get("status") == "ok":
            articles = data.get("articles", [])
            # Filter out articles without title or url
            articles = [a for a in articles if a.get("title") and a.get("url")]
            return articles[:limit]
        else:
            error_msg = data.get("message", "Unknown error")
            print(f"NewsAPI error: {error_msg}")
            return []
    except Exception as e:
        print(f"Error fetching from NewsAPI: {str(e)}")
        return []


def _fetch_yfinance_news(ticker: str, limit: int = 50) -> List[Dict]:
    """
    Fetch news from Yahoo Finance using yfinance (free, unlimited, no API key).

    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        limit: Max results

    Returns:
        List of news article dicts
    """
    if not YFINANCE_AVAILABLE:
        return []

    try:
        stock = yf.Ticker(ticker.upper())
        news = stock.news or []

        # Convert yfinance news format to standard format
        standardized = []
        for item in news[:limit]:
            standardized.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "source": {"name": item.get("publisher", "Yahoo Finance")},
                "publishedAt": datetime.fromtimestamp(
                    item.get("providerPublishTime", 0)
                ).isoformat() if item.get("providerPublishTime") else "",
                "description": item.get("title", ""),  # yfinance doesn't provide description
                "summary": item.get("title", ""),
                "sentiment": "N/A"
            })

        return [a for a in standardized if a.get("title") and a.get("url")]
    except Exception as e:
        print(f"Error fetching from yfinance for {ticker}: {str(e)}")
        return []


# ---------------- Tools (formatted string variants) ----------------

@tool
def get_company_news(
    ticker: str,
    lookback_days: int = 7,
    limit: int = 50,
    sort: str = "LATEST",
) -> str:
    """
    Get company-specific news (formatted string) using free APIs.

    Uses yfinance (free, unlimited) with NewsAPI as fallback.

    Args:
        ticker: Stock symbol (e.g., 'AAPL').
        lookback_days: Days to look back (default 7).
        limit: Max articles (default 50).
        sort: 'LATEST' | 'EARLIEST' | 'RELEVANCE'.

    Returns:
        Multi-line formatted string with top articles for the company.
    """
    try:
        if not ticker:
            return "Ticker is required for company news."

        # Try yfinance first (free, unlimited)
        feed = _fetch_yfinance_news(ticker, limit)

        # Fallback to NewsAPI if yfinance fails and API key is available
        if not feed and NEWSAPI_KEY:
            today = datetime.now()
            to_date = today.strftime("%Y-%m-%d")
            from_date = (today - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

            sort_by = "publishedAt" if sort == "LATEST" else "relevancy"
            feed = _fetch_newsapi(
                q=f"{ticker} stock",
                from_date=from_date,
                to_date=to_date,
                sort_by=sort_by,
                limit=limit
            )

        if not feed:
            api_info = "yfinance" if YFINANCE_AVAILABLE else "NewsAPI (configure NEWSAPI_KEY in .env)"
            return f"No company news found for {ticker} using {api_info}."

        source_api = "yfinance" if YFINANCE_AVAILABLE and feed else "NewsAPI"
        header = f"Company News for {ticker.upper()} via {source_api} (last {lookback_days} days, limit={limit}):\n\n"
        blocks = [_format_article_block(i + 1, it) for i, it in enumerate(feed)]
        return header + "\n".join(blocks)

    except Exception as e:
        return f"Error fetching company news for {ticker}: {str(e)}"


@tool
def get_industry_news(
    industry: Optional[str] = None,
    lookback_days: int = 7,
    limit: int = 50,
    sort: str = "LATEST",
) -> str:
    """
    Get industry/sector news (formatted string) via NewsAPI.

    Requires NEWSAPI_KEY in .env file.

    Args:
        industry: Industry keyword (e.g., 'semiconductors', 'software', 'energy').
                  Defaults to 'technology' if None.
        lookback_days: Days to look back (default 7).
        limit: Max articles (1..100).
        sort: 'LATEST' | 'EARLIEST' | 'RELEVANCE'.

    Returns:
        Multi-line formatted string with industry/sector articles.
    """
    try:
        key = (industry or "technology").strip().lower()

        if not NEWSAPI_KEY:
            return "NewsAPI key not configured. Set NEWSAPI_KEY in .env file. Sign up free at https://newsapi.org/"

        today = datetime.now()
        to_date = today.strftime("%Y-%m-%d")
        from_date = (today - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

        sort_by = "publishedAt" if sort == "LATEST" else "relevancy"

        # Build industry-specific query
        query = f"{key} industry"
        feed = _fetch_newsapi(
            q=query,
            from_date=from_date,
            to_date=to_date,
            sort_by=sort_by,
            limit=limit
        )

        if not feed:
            return f"No industry news found for '{key}' in last {lookback_days} days."

        header = f"Industry News (industry='{key}', via NewsAPI, last {lookback_days} days, limit={limit}):\n\n"
        blocks = [_format_article_block(i + 1, it) for i, it in enumerate(feed)]
        return header + "\n".join(blocks)

    except Exception as e:
        return f"Error fetching industry news (industry='{industry}'): {str(e)}"


@tool
def get_macro_news(
    lookback_days: int = 7,
    limit: int = 50,
    sort: str = "LATEST",
    topics: Optional[str] = None,
) -> str:
    """
    Get macro/market news (formatted string) via NewsAPI.

    Requires NEWSAPI_KEY in .env file.

    Args:
        lookback_days: Days to look back (default 7).
        limit: Max articles (1..100).
        sort: 'LATEST' | 'EARLIEST' | 'RELEVANCE'.
        topics: Optional custom search query; defaults to broad market terms.

    Returns:
        Multi-line formatted string with macro/market articles.
    """
    try:
        if not NEWSAPI_KEY:
            return "NewsAPI key not configured. Set NEWSAPI_KEY in .env file. Sign up free at https://newsapi.org/"

        today = datetime.now()
        to_date = today.strftime("%Y-%m-%d")
        from_date = (today - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

        sort_by = "publishedAt" if sort == "LATEST" else "relevancy"

        # Default macro query
        query = topics or "stock market OR economy OR federal reserve OR interest rates"
        feed = _fetch_newsapi(
            q=query,
            from_date=from_date,
            to_date=to_date,
            sort_by=sort_by,
            limit=limit
        )

        if not feed:
            return f"No macro news found in last {lookback_days} days."

        header = f"Macro / Market News (via NewsAPI, last {lookback_days} days, limit={limit}):\n\n"
        blocks = [_format_article_block(i + 1, it) for i, it in enumerate(feed)]
        return header + "\n".join(blocks)

    except Exception as e:
        return f"Error fetching macro news: {str(e)}"


# ---------------- Tools (raw list variants for strict node) ----------------

@tool
def get_news(
    query: str,
    start_date: str,
    end_date: str,
    limit: int = 50,
) -> list:
    """
    Fetch RAW company news list[dict] (NOT formatted) using free APIs.

    This version is intended for news_analyst nodes which will perform
    relevance filtering and Pydantic-constrained synthesis downstream.

    Args:
        query: Ticker symbol (e.g., 'AAPL').
        start_date: ISO 'YYYY-MM-DD' (inclusive start of window).
        end_date: ISO 'YYYY-MM-DD' (inclusive end of window).
        limit: Max number of articles to return.

    Returns:
        A list of news item dicts (trimmed, filtered for title/url).
    """
    try:
        # Try yfinance first
        feed = _fetch_yfinance_news(query, limit)

        # Fallback to NewsAPI if available
        if not feed and NEWSAPI_KEY:
            feed = _fetch_newsapi(
                q=f"{query} stock",
                from_date=start_date,
                to_date=end_date,
                sort_by="publishedAt",
                limit=limit
            )

        # Normalize field names for compatibility with news_analyst.py
        for article in feed:
            # Add Alpha Vantage compatible fields if not present
            if "time_published" not in article and "publishedAt" in article:
                # Convert ISO format to Alpha Vantage format (YYYYMMDDTHHMMSS)
                try:
                    dt = datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00"))
                    article["time_published"] = dt.strftime("%Y%m%dT%H%M%S")
                except:
                    article["time_published"] = article["publishedAt"]

            # Ensure summary field exists
            if "summary" not in article:
                article["summary"] = article.get("description", "")

        return feed or []
    except Exception:
        return []


@tool
def get_global_news(
    curr_date: str,
    look_back_days: int = 7,
    limit: int = 50,
) -> list:
    """
    Fetch RAW macro/market news list[dict] (NOT formatted) via NewsAPI.

    This version is intended for news_analyst nodes which will perform
    relevance filtering and Pydantic-constrained synthesis downstream.

    Args:
        curr_date: ISO 'YYYY-MM-DD' used as the end date of the lookback window.
        look_back_days: Number of days to look back from curr_date (default 7).
        limit: Max number of articles to return.

    Returns:
        A list of news item dicts for macro topics.
    """
    try:
        if not NEWSAPI_KEY:
            return []

        end_dt = datetime.fromisoformat(curr_date).date()
        start_dt = end_dt - timedelta(days=look_back_days)

        feed = _fetch_newsapi(
            q="stock market OR economy OR federal reserve",
            from_date=start_dt.strftime("%Y-%m-%d"),
            to_date=end_dt.strftime("%Y-%m-%d"),
            sort_by="publishedAt",
            limit=limit
        )

        # Normalize field names for compatibility with news_analyst.py
        for article in feed:
            # Add Alpha Vantage compatible fields if not present
            if "time_published" not in article and "publishedAt" in article:
                try:
                    dt = datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00"))
                    article["time_published"] = dt.strftime("%Y%m%dT%H%M%S")
                except:
                    article["time_published"] = article["publishedAt"]

            # Ensure summary field exists
            if "summary" not in article:
                article["summary"] = article.get("description", "")

        return feed or []
    except Exception:
        return []


# Export
NEWS_TOOLS = [
    get_company_news,
    get_industry_news,
    get_macro_news,
    get_news,
    get_global_news,
]
