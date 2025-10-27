# -*- coding: utf-8 -*-
"""
Strict News Analyst Node (company-focused with macro relevance filtering)
-----------------------------------------------------------------------
- Direct tool calls (no ReAct)
- Strongly constrained JSON via Pydantic
- Filters macro/sector news to ONLY those relevant to the target company
- Cleans, dedupes, limits, and standardizes inputs
- Structured-output first (llm.with_structured_output), with robust JSON fallback
- Condensed message history

Drop this file into your project (e.g., simplified_tradingagents/nodes/news_analyst_strict.py)
and import `create_company_relevant_news_analyst(llm)` to build the node.
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Literal, Optional, Dict, Any, Tuple

from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage

# =========================
# 1) Pydantic Schemas
# =========================

class NewsItem(BaseModel):
    title: str = Field(description="Headline")
    published_at: str = Field(description="ISO-8601 datetime of the article")
    source: str = Field(description="Publisher/source name")
    url: str = Field(description="Canonical URL")
    tags: List[str] = Field(description="1-5 tags summarizing the topic")
    sentiment: Literal["bullish", "bearish", "neutral"] = Field(description="Article-level sentiment")
    impact_scope: Literal["company", "sector", "macro"] = Field(description="Scope of impact")
    relevance_score: float = Field(ge=0.0, le=1.0, description="Estimated relevance to the target company (0-1)")
    summary: str = Field(description="<= 60-word abstractive summary of the article (concise)")

class MacroTheme(BaseModel):
    theme: str = Field(description="Short name of the macro/sector theme")
    direction: Literal["tailwind", "headwind", "mixed"] = Field(description="Net impact direction")
    evidence_count: int = Field(ge=0, description="How many supporting articles in the kept set")
    representative_titles: List[str] = Field(description="1-3 representative headlines from kept articles")

class CompanyImpact(BaseModel):
    demand_outlook: Literal["positive", "negative", "neutral", "uncertain"]
    cost_pressure: Literal["increasing", "decreasing", "stable", "uncertain"]
    regulatory_risk: Literal["elevated", "moderate", "low", "uncertain"]
    valuation_impact: Literal["expansion", "compression", "neutral", "uncertain"]
    reasoning: str = Field(description="2-3 sentences grounded in kept news evidence")

class NewsAnalysisOutput(BaseModel):
    analysis_summary: str = Field(description="3-4 sentence executive summary grounded in kept company-relevant news")
    lookback_window_days: int = Field(ge=1, le=30, description="Days looked back")
    coverage_stats: Dict[str, int] = Field(
        description="Counts like {'articles': n_kept, 'sources': m_kept, 'unique_topics': k_est, 'raw_articles': n_raw}"
    )
    macro_themes: List[MacroTheme] = Field(description="2-5 macro/sector themes driving/company-relevant")
    company_impact: CompanyImpact = Field(description="Company-specific impact synthesis")
    catalysts: List[str] = Field(description="2-5 near-term catalysts to watch (with timing if possible)")
    risk_radar: List[str] = Field(description="3-6 key risks inferred from kept news")
    overall_sentiment: Literal["bullish", "bearish", "neutral"] = Field(description="Topline sentiment for the company")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence 0-1 given breadth/consistency of kept news")
    highlighted_articles: List[NewsItem] = Field(description="3-10 high-signal, company-relevant articles (kept)")
    sources: List[str] = Field(description="Distinct source domains used among kept articles")

# =========================
# 2) Tunables / Dictionaries
# =========================

# Default aliases/competitors/sector tags for a few well-known tickers (extend as needed).
DEFAULT_ALIASES: Dict[str, List[str]] = {
    "AMD": ["Advanced Micro Devices", "Radeon", "Ryzen", "EPYC", "Instinct MI", "MI300", "Zen"],
    "AAPL": ["Apple", "iPhone", "iPad", "MacBook", "Vision Pro"],
    "NVDA": ["NVIDIA", "GeForce", "CUDA", "Hopper", "Blackwell", "RTX"],
    "TSLA": ["Tesla", "Model 3", "Cybertruck", "Gigafactory", "Autopilot", "FSD"],
}

DEFAULT_COMPETITORS: Dict[str, List[str]] = {
    "AMD": ["NVIDIA", "NVDA", "Intel", "INTC", "TSMC", "Qualcomm", "QCOM"],
    "AAPL": ["Samsung", "Xiaomi", "Huawei", "Google", "Alphabet", "Microsoft", "MSFT"],
    "NVDA": ["AMD", "Intel", "Broadcom", "AVGO", "Qualcomm"],
    "TSLA": ["BYD", "NIO", "Xpeng", "XPENG", "GM", "Ford", "F"],
}

DEFAULT_SECTOR_TAGS: Dict[str, List[str]] = {
    "AMD": ["semiconductor", "chips", "GPU", "AI accelerator", "data center", "pc shipments", "server cpu", "foundry"],
    "AAPL": ["smartphone", "handset", "wearables", "services revenue", "app store", "supply chain"],
    "NVDA": ["gpu", "ai accelerator", "datacenter", "h100", "blackwell"],
    "TSLA": ["ev", "electric vehicle", "battery", "autonomous driving", "charging network"],
}

# Macro factor keywords that often imply company impact (extend to your use case)
DEFAULT_MACRO_TERMS: List[str] = [
    "oil price", "brent", "wti", "usd index", "dxy", "tariff", "export control", "subsidy",
    "interest rate", "fed", "ecb", "boe", "pboC".lower(), "inflation", "cpi", "ppi", "jobs report",
    "unemployment", "chips act", "supply chain", "geopolitical", "sanction"
]

# =========================
# 3) Helpers (clean / dedupe / limit / iso / relevance)
# =========================

def _hash_url(url: str) -> str:
    return hashlib.md5(url.strip().lower().encode()).hexdigest()

def _dedupe_articles(items: List[dict]) -> List[dict]:
    seen = set()
    out = []
    for it in items:
        url = it.get("url") or it.get("link") or ""
        h = _hash_url(url) if url else hashlib.md5((it.get("title", "")[:64]).encode()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        out.append(it)
    return out

def _limit(items: List[dict], n: int) -> List[dict]:
    return items[:n] if len(items) > n else items

def _iso(dt) -> str:
    if isinstance(dt, str):
        return dt
    try:
        return dt.isoformat()
    except Exception:
        return str(dt)

def _compact(items: List[dict]) -> List[dict]:
    out = []
    for it in items:
        out.append({
            "title": it.get("title") or "",
            "published_at": _iso(it.get("published_at") or it.get("date") or it.get("time") or ""),
            "source": it.get("source") or it.get("publisher") or it.get("domain") or "",
            "url": it.get("url") or it.get("link") or "",
            "snippet": (it.get("snippet") or it.get("summary") or it.get("description") or "")[:500],
        })
    return out

def _normalize_dict_list(items: List[dict]) -> List[dict]:
    """Ensure minimal keys exist to avoid KeyErrors downstream."""
    norm = []
    for it in items:
        norm.append({
            "title": it.get("title") or "",
            "published_at": _iso(it.get("published_at") or it.get("date") or ""),
            "source": it.get("source") or it.get("publisher") or "",
            "url": it.get("url") or it.get("link") or "",
            "snippet": it.get("snippet") or it.get("summary") or "",
        })
    return norm

def compute_relevance(
    item: Dict[str, Any],
    ticker: str,
    aliases: List[str],
    competitors: List[str],
    sector_tags: List[str],
    macro_terms: List[str],
) -> Tuple[float, str]:
    """
    Returns (relevance_score, impact_scope)
    - scope 'company' if explicit company/alias hit
    - 'sector' if sector tag hit (no direct company hit)
    - 'macro' if only macro factor hit
    """
    title = (item.get("title") or "").lower()
    snippet = (item.get("snippet") or "").lower()
    text = f"{title} {snippet}"

    score = 0.0

    # Direct company/ticker/alias hit
    if ticker and ticker.lower() in text:
        score += 0.55
    for alias in aliases:
        if alias.lower() in text:
            score += 0.45

    # Competitors / supply chain / customers
    for rival in competitors:
        if rival.lower() in text:
            score += 0.25

    # Sector/track terms
    sector_hit = False
    for tag in sector_tags:
        if tag.lower() in text:
            score += 0.2
            sector_hit = True

    # Macro factors
    macro_hit = False
    for macro in macro_terms:
        if macro.lower() in text:
            score += 0.12
            macro_hit = True

    # Noise guard
    if len(title) < 8:
        score -= 0.08

    score = max(0.0, min(score, 1.0))

    # Decide scope
    if (ticker and ticker.lower() in text) or any(a.lower() in text for a in aliases):
        scope = "company"
    elif sector_hit:
        scope = "sector"
    elif macro_hit:
        scope = "macro"
    else:
        scope = "macro"  # default weakest scope

    return score, scope

def filter_company_relevant(
    company_items: List[dict],
    macro_items: List[dict],
    ticker: str,
    aliases: List[str],
    competitors: List[str],
    sector_tags: List[str],
    macro_terms: List[str],
    threshold: float = 0.6,
) -> List[dict]:
    kept = []
    for it in (company_items + macro_items):
        sc, scope = compute_relevance(it, ticker, aliases, competitors, sector_tags, macro_terms)
        if sc >= threshold:
            it["relevance_score"] = sc
            it["impact_scope"] = scope
            kept.append(it)
    return kept

def _sort_kept(items: List[dict]) -> List[dict]:
    """Sort by relevance desc, then recency desc (if published_at parseable)."""
    def _key(it: dict):
        sc = it.get("relevance_score", 0.0)
        ts = it.get("published_at") or ""
        try:
            d = datetime.fromisoformat(ts.replace("Z", ""))
        except Exception:
            d = datetime.min
        return (-sc, -d.timestamp())
    return sorted(items, key=_key)

def _estimate_unique_topics(items: List[dict]) -> int:
    """A light heuristic using title shingles hash to estimate topic diversity."""
    seen = set()
    for it in items:
        title = (it.get("title") or "").strip().lower()
        if not title:
            continue
        key = hashlib.md5(" ".join(title.split()[:7]).encode()).hexdigest()
        seen.add(key)
    return len(seen)

# =========================
# 4) The Node Factory
# =========================

def create_news_analyst(llm):
    """
    Build a news analyst node that:
    - Fetches company news + macro/sector news
    - Keeps ONLY items relevant to the target company (with a relevance score)
    - Produces a strongly-constrained JSON (Pydantic)
    - Condenses message history
    """

    def news_analyst_node(state: Dict[str, Any]) -> Dict[str, Any]:
        ticker: str = state.get("ticker", "").upper().strip()
        date_str: str = state.get("date") or datetime.utcnow().date().isoformat()
        lookback_days: int = int(state.get("lookback_days", 7))

        # Optional overrides for dictionaries via state
        aliases = state.get("aliases") or DEFAULT_ALIASES.get(ticker, [])
        competitors = state.get("competitors") or DEFAULT_COMPETITORS.get(ticker, [])
        sector_tags = state.get("sector_tags") or DEFAULT_SECTOR_TAGS.get(ticker, [])
        macro_terms = state.get("macro_terms") or DEFAULT_MACRO_TERMS
        relevance_threshold: float = float(state.get("relevance_threshold", 0.6))
        max_company = int(state.get("max_company_articles", 50))
        max_macro = int(state.get("max_macro_articles", 80))
        max_kept = int(state.get("max_kept_articles", 80))  # after relevance filter

        # Import your existing tools (adapt path to your project)
        try:
            from simplified_tradingagents.tools.news_tools import get_news, get_global_news
        except Exception:
            from tools.news_tools import (
                get_news,         # .invoke({"query": str, "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "limit": int})
                get_global_news   # .invoke({"curr_date": "YYYY-MM-DD", "look_back_days": int, "limit": int})
            )

        # ---- Step 1: Fetch raw data deterministically ----
        end_date = datetime.fromisoformat(date_str).date()
        start_date = end_date - timedelta(days=lookback_days)

        raw_company, raw_macro = [], []
        errors: List[str] = []

        try:
            raw_company = get_news.invoke({
                "query": ticker,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "limit": max_company
            }) or []
        except Exception as e:
            errors.append(f"get_news error: {e}")

        try:
            raw_macro = get_global_news.invoke({
                "curr_date": end_date.isoformat(),
                "look_back_days": lookback_days,
                "limit": max_macro
            }) or []
        except Exception as e:
            errors.append(f"get_global_news error: {e}")

        raw_total = len(raw_company) + len(raw_macro)

        # Clean / dedupe / compact
        company_clean = _normalize_dict_list(_dedupe_articles(raw_company))
        macro_clean   = _normalize_dict_list(_dedupe_articles(raw_macro))

        # ---- Step 2: Relevance filter (company + macro) ----
        relevant_items = filter_company_relevant(
            company_items=company_clean,
            macro_items=macro_clean,
            ticker=ticker,
            aliases=aliases,
            competitors=competitors,
            sector_tags=sector_tags,
            macro_terms=macro_terms,
            threshold=relevance_threshold,
        )

        if not relevant_items:
            # Hard fallback if nothing kept
            fallback = NewsAnalysisOutput(
                analysis_summary=f"No company-relevant news found for {ticker} in the past {lookback_days} days.",
                lookback_window_days=lookback_days,
                coverage_stats={"articles": 0, "sources": 0, "unique_topics": 0, "raw_articles": raw_total},
                macro_themes=[],
                company_impact=CompanyImpact(
                    demand_outlook="uncertain",
                    cost_pressure="uncertain",
                    regulatory_risk="uncertain",
                    valuation_impact="uncertain",
                    reasoning="No relevant articles were identified within the selected window."
                ),
                catalysts=[],
                risk_radar=[],
                overall_sentiment="neutral",
                confidence_score=0.15,
                highlighted_articles=[],
                sources=[]
            )
            msg = AIMessage(content=f"News Analysis for {ticker}:\n{json.dumps(fallback.model_dump(), indent=2, ensure_ascii=False)}")
            return {"messages": [msg], "news_analysis": json.dumps(fallback.model_dump(), indent=2, ensure_ascii=False)}

        # Sort and limit kept items
        relevant_sorted = _sort_kept(relevant_items)
        relevant_kept = _limit(relevant_sorted, max_kept)

        # Build minimal pack for LLM (compact but kept items only)
        compact_kept = _compact(relevant_kept)
        # Carry the computed fields along for LLM grounding
        for i, it in enumerate(compact_kept):
            it["impact_scope"] = relevant_kept[i].get("impact_scope", "macro")
            it["relevance_score"] = float(relevant_kept[i].get("relevance_score", 0.0))

        # Stats
        srcs = sorted(list({(it.get("source") or "").strip() for it in compact_kept if it.get("source")}))  # kept sources
        unique_topics = _estimate_unique_topics(compact_kept)

        # ---- Step 3: Strict prompt (JSON only) ----
        analysis_prompt = f"""You are a company-focused markets news analyst. Using ONLY the provided company-relevant articles below (already filtered for relevance to {ticker}), produce a strictly structured JSON analysis for {ticker} as of {end_date.isoformat()}.

All items are relevant to the company either directly (company scope), indirectly via sector dynamics (sector scope), or through macro transmission channels (macro scope). Ignore any speculation not grounded in these items.

### COMPANY-RELEVANT ARTICLES (deduped, filtered, {len(compact_kept)} items)
{json.dumps(compact_kept, ensure_ascii=False)}

GUIDELINES:
1) Use ONLY the kept articles above; do not invent information.
2) Assign article-level sentiment (bullish/bearish/neutral) and respect the given impact_scope.
3) Synthesize 2-5 macro/sector themes that materially affect the company; mark direction = tailwind/headwind/mixed and cite 1-3 representative titles.
4) Infer company impact on demand/cost/regulatory/valuation—state reasoning grounded in article evidence.
5) Extract 2-5 upcoming catalysts (events, decisions, data prints) and 3-6 risks.
6) Set overall_sentiment; calibrate confidence by breadth/diversity/consistency of the kept set.
7) Output ONLY valid JSON matching EXACTLY the schema below. No markdown, no prose outside JSON.

REQUIRED JSON SHAPE:
{{
  "analysis_summary": "string (3-4 sentences)",
  "lookback_window_days": {lookback_days},
  "coverage_stats": {{"articles": number, "sources": number, "unique_topics": number, "raw_articles": number}},
  "macro_themes": [
    {{"theme": "string", "direction": "tailwind|headwind|mixed", "evidence_count": number, "representative_titles": ["string"]}}
  ],
  "company_impact": {{
    "demand_outlook": "positive|negative|neutral|uncertain",
    "cost_pressure": "increasing|decreasing|stable|uncertain",
    "regulatory_risk": "elevated|moderate|low|uncertain",
    "valuation_impact": "expansion|compression|neutral|uncertain",
    "reasoning": "string"
  }},
  "catalysts": ["string"],
  "risk_radar": ["string"],
  "overall_sentiment": "bullish|bearish|neutral",
  "confidence_score": number (0.0-1.0),
  "highlighted_articles": [
    {{
      "title": "string",
      "published_at": "YYYY-MM-DDTHH:MM:SS",
      "source": "string",
      "url": "string",
      "tags": ["string"],
      "sentiment": "bullish|bearish|neutral",
      "impact_scope": "company|sector|macro",
      "relevance_score": number (0.0-1.0),
      "summary": "string"
    }}
  ],
  "sources": ["string"]
}}

CONTEXT TO RESPECT:
- kept_articles_count = {len(compact_kept)}
- kept_sources_count = {len(srcs)}
- kept_unique_topics_est = {unique_topics}
- raw_articles_total = {raw_total}
"""

        # ---- Step 4: LLM with strict output (prefer structured), else parse ----
        try:
            if hasattr(llm, "with_structured_output"):
                strict_llm = llm.with_structured_output(NewsAnalysisOutput)
                result_obj = strict_llm.invoke(analysis_prompt)
                result_json = result_obj.model_dump()
            else:
                raw = llm.invoke(analysis_prompt)
                text = raw.content if hasattr(raw, "content") else str(raw)
                text = text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                result_json = NewsAnalysisOutput(**json.loads(text)).model_dump()
        except Exception as e:
            # ---- Parsing fallback JSON ----
            fallback = NewsAnalysisOutput(
                analysis_summary=f"News analysis completed but encountered formatting issues: {e}.",
                lookback_window_days=lookback_days,
                coverage_stats={
                    "articles": len(compact_kept),
                    "sources": len(srcs),
                    "unique_topics": unique_topics,
                    "raw_articles": raw_total
                },
                macro_themes=[],
                company_impact=CompanyImpact(
                    demand_outlook="uncertain",
                    cost_pressure="uncertain",
                    regulatory_risk="uncertain",
                    valuation_impact="uncertain",
                    reasoning="Parser fallback; see highlighted articles list."
                ),
                catalysts=[],
                risk_radar=[],
                overall_sentiment="neutral",
                confidence_score=0.35,
                highlighted_articles=[],
                sources=srcs
            )
            result_json = fallback.model_dump()

        # ---- Step 5: Condense history ----
        user_msg = HumanMessage(
            content=f"Analyze last {lookback_days} days of company-relevant news for {ticker} as of {end_date.isoformat()}"
        )
        out_str = json.dumps(result_json, indent=2, ensure_ascii=False)
        ai_msg = AIMessage(content=f"News Analysis for {ticker}:\n\n{out_str}")

        return {
            "messages": [user_msg, ai_msg],
            "news_analysis": out_str
        }

    return news_analyst_node


# =========================
# 5) Minimal usage example (pseudo)
# =========================
# from langchain_google_genai import ChatGoogleGenerativeAI
# llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)
# node = create_company_relevant_news_analyst(llm)
# state = {"ticker": "AMD", "date": "2025-10-23", "lookback_days": 7}
# out = node(state)
# print(out["news_analysis"])
