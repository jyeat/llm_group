# tools/news_tools.py
# -*- coding: utf-8 -*-
"""
News Tools (Alpha Vantage - News & Sentiment)
---------------------------------------------
- 统一提供 5 个 @tool：
  1) get_company_news        -> str   (格式化文本，便于拼 Prompt)
  2) get_industry_news       -> str   (格式化文本，便于拼 Prompt)
  3) get_macro_news          -> str   (格式化文本，便于拼 Prompt)
  4) get_news                -> list  (原始列表，用于严格版 news_analyst 的相关性过滤)
  5) get_global_news         -> list  (原始列表，用于严格版 news_analyst 的相关性过滤)

依赖：
- Alpha Vantage NEWS_SENTIMENT 接口
- 从配置中读取：ALPHA_VANTAGE_API_KEY, AV_BASE_URL, AV_TIMEOUT
"""

from __future__ import annotations
from typing import List, Optional, Dict
from datetime import datetime, timedelta

import requests
from langchain_core.tools import tool

# 按你的工程结构选择正确的导入：
# 如果 tools 与 config 同级，且 main 在项目根目录运行，下面这行 OK：
from config import ALPHA_VANTAGE_API_KEY, AV_BASE_URL, AV_TIMEOUT
# 如果你是在包内使用，请改为：
# from simplified_tradingagents.config import ALPHA_VANTAGE_API_KEY, AV_BASE_URL, AV_TIMEOUT


# ---------------- Helpers ----------------

def _av_ts(dt: datetime) -> str:
    """Format datetime to Alpha Vantage 'YYYYMMDDTHHMMSS' string."""
    return dt.strftime("%Y%m%dT%H%M%S")


def _iso(ts: str) -> str:
    """Convert Alpha Vantage 'YYYYMMDDTHHMMSS' timestamp to ISO 8601; fallback to original if parsing fails."""
    if not ts:
        return ""
    try:
        return datetime.strptime(ts, "%Y%m%dT%H%M%S").isoformat()
    except Exception:
        return ts


def _format_article_block(i: int, it: Dict) -> str:
    """Render one article dict to a readable multi-line block."""
    title = it.get("title") or "N/A"
    url = it.get("url") or ""
    src = it.get("source") or "N/A"
    when = _iso(it.get("time_published") or "")
    sent = it.get("overall_sentiment_label") or "N/A"
    smry = (it.get("summary") or "").strip()
    if smry:
        smry = smry[:400] + ("..." if len(smry) > 400 else "")
    return (
        f"[{i}] {title}\n"
        f"    Source: {src} | Published: {when} | Sentiment: {sent}\n"
        f"    URL: {url}\n"
        f"    Summary: {smry}\n"
    )


def _fetch_news(
    tickers: Optional[str] = None,
    topics: Optional[str] = None,
    lookback_days: int = 7,
    limit: int = 50,
    sort: str = "LATEST",
) -> List[Dict]:
    """Low-level Alpha Vantage NEWS_SENTIMENT fetcher. Returns trimmed 'feed' list[dict]."""
    limit = max(1, min(int(limit), 50))
    lb_days = max(1, int(lookback_days))

    # Alpha Vantage 按相对时间抓取更稳，这里用 lookback_days 窗口
    now = datetime.utcnow()
    time_to = _av_ts(now)
    time_from = _av_ts(now - timedelta(days=lb_days))

    params = {
        "function": "NEWS_SENTIMENT",
        "apikey": ALPHA_VANTAGE_API_KEY,
        "time_from": time_from,
        "time_to": time_to,
        "sort": sort,
        "limit": limit,
    }
    if tickers:
        params["tickers"] = tickers
    if topics:
        params["topics"] = topics

    r = requests.get(AV_BASE_URL, params=params, timeout=AV_TIMEOUT)
    data = r.json() if r is not None else {}
    feed = data.get("feed") or []
    # 过滤掉缺少标题/链接的项
    feed = [x for x in feed if x.get("title") and x.get("url")]
    return feed[:limit]


# 行业 -> topics 的简易映射（可按需扩展）
_TOPIC_MAP = {
    "technology": "technology",
    "semiconductors": "technology,earnings,iponews",
    "software": "technology,earnings",
    "energy": "energy",
    "financials": "finance",
    "healthcare": "healthcare",
    "industrials": "manufacturing",
    "consumer": "retail",
}

# 宏观 topics 默认集合（可按需调整）
_DEFAULT_MACRO_TOPICS = "economy,financial_markets,earnings"


# ---------------- Tools (formatted string variants) ----------------

@tool
def get_company_news(
    ticker: str,
    lookback_days: int = 7,
    limit: int = 50,
    sort: str = "LATEST",
) -> str:
    """
    Get company-specific news (formatted string) via Alpha Vantage News & Sentiment.

    Args:
        ticker: Stock symbol (e.g., 'AAPL').
        lookback_days: Days to look back (default 7).
        limit: Max articles (1..50, default 50).
        sort: 'LATEST' | 'EARLIEST' | 'RELEVANCE'.

    Returns:
        Multi-line formatted string with top articles for the company.
    """
    try:
        if not ticker:
            return "Ticker is required for company news."
        feed = _fetch_news(
            tickers=ticker.upper(),
            topics=None,
            lookback_days=lookback_days,
            limit=limit,
            sort=sort,
        )
        if not feed:
            return f"No company news found for {ticker} in last {lookback_days} days."

        header = f"Company News for {ticker.upper()} (last {lookback_days} days, limit={limit}, sort={sort}):\n\n"
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
    Get industry/sector news (formatted string) via Alpha Vantage topics.

    Args:
        industry: Plain text industry key (e.g., 'semiconductors', 'software', 'energy').
                  Defaults to 'technology' if None.
        lookback_days: Days to look back (default 7).
        limit: Max articles (1..50).
        sort: 'LATEST' | 'EARLIEST' | 'RELEVANCE'.

    Returns:
        Multi-line formatted string with industry/sector articles.
    """
    try:
        key = (industry or "technology").strip().lower()
        topics = _TOPIC_MAP.get(key, "technology")
        feed = _fetch_news(
            tickers=None,
            topics=topics,
            lookback_days=lookback_days,
            limit=limit,
            sort=sort,
        )
        if not feed:
            return f"No industry news found (industry='{key}', topics='{topics}') in last {lookback_days} days."

        header = f"Industry News (industry='{key}', topics='{topics}', last {lookback_days} days, limit={limit}, sort={sort}):\n\n"
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
    Get macro/market news (formatted string) via Alpha Vantage topics.

    Args:
        lookback_days: Days to look back (default 7).
        limit: Max articles (1..50).
        sort: 'LATEST' | 'EARLIEST' | 'RELEVANCE'.
        topics: Optional comma-separated topics override; defaults to economy/financial_markets/earnings.

    Returns:
        Multi-line formatted string with macro/market articles.
    """
    try:
        used_topics = topics or _DEFAULT_MACRO_TOPICS
        feed = _fetch_news(
            tickers=None,
            topics=used_topics,
            lookback_days=lookback_days,
            limit=limit,
            sort=sort,
        )
        if not feed:
            return f"No macro news found (topics='{used_topics}') in last {lookback_days} days."

        header = f"Macro / Market News (topics='{used_topics}', last {lookback_days} days, limit={limit}, sort={sort}):\n\n"
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
    Fetch RAW company news list[dict] (NOT formatted) via Alpha Vantage.

    This version is intended for strict news analyst nodes which will perform
    relevance filtering and Pydantic-constrained synthesis downstream.

    Args:
        query: Ticker symbol (e.g., 'AAPL'); passed as tickers to Alpha Vantage.
        start_date: ISO 'YYYY-MM-DD' (inclusive start of window).
        end_date: ISO 'YYYY-MM-DD' (inclusive end of window).
        limit: Max number of articles to return (1..50).

    Returns:
        A list of news item dicts from Alpha Vantage 'feed' (trimmed, filtered for title/url).
    """
    try:
        dt_start = datetime.fromisoformat(start_date).date()
        dt_end = datetime.fromisoformat(end_date).date()
        lb = max(1, (dt_end - dt_start).days or 1)
        feed = _fetch_news(
            tickers=(query or "").upper(),
            topics=None,
            lookback_days=lb,
            limit=max(1, min(int(limit), 50)),
            sort="LATEST",
        )
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
    Fetch RAW macro/market news list[dict] (NOT formatted) via Alpha Vantage topics.

    This version is intended for strict news analyst nodes which will perform
    relevance filtering and Pydantic-constrained synthesis downstream.

    Args:
        curr_date: ISO 'YYYY-MM-DD' used as the end date of the lookback window.
        look_back_days: Number of days to look back from curr_date (default 7).
        limit: Max number of articles to return (1..50).

    Returns:
        A list of news item dicts from Alpha Vantage 'feed' for macro topics.
    """
    try:
        _ = datetime.fromisoformat(curr_date).date()  # 校验格式
        feed = _fetch_news(
            tickers=None,
            topics=_DEFAULT_MACRO_TOPICS,
            lookback_days=max(1, int(look_back_days)),
            limit=max(1, min(int(limit), 50)),
            sort="LATEST",
        )
        return feed or []
    except Exception:
        return []


# 导出
NEWS_TOOLS = [
    get_company_news,
    get_industry_news,
    get_macro_news,
    get_news,
    get_global_news,
]
