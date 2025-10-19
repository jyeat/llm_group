# Fundamentals Analyst V2
#
# Changes from V1:
# 1. Direct tool calls (no ReAct loop) - calls all 4 fundamental tools upfront -> higher reliability
# 2. Structured JSON output (Pydantic schema enforcement)
# 3. Focus on analyzing provided data rather than LLM deciding what to fetch
# 4. Message history condensation to avoid content bloat
# 5. Multi-period analysis with trend detection
# 6. Automated financial ratio calculations and red flag detection
# 7. Quality scoring system for financial health assessment
# 8. A more structured output of scores and strengths instead of full page report. 

from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
import json
from datetime import datetime


# Structured output schemas
class ValuationMetrics(BaseModel):
    """Valuation assessment"""
    pe_ratio: Optional[float] = Field(description="P/E ratio if available")
    peg_ratio: Optional[float] = Field(description="PEG ratio if available")
    price_to_book: Optional[float] = Field(description="P/B ratio if available")
    valuation_verdict: Literal["undervalued", "fairly_valued", "overvalued", "insufficient_data"] = Field(
        description="Overall valuation assessment"
    )
    valuation_reasoning: str = Field(description="2-3 sentence explanation of valuation verdict")


class FinancialHealthMetrics(BaseModel):
    """Financial health assessment with scoring"""
    liquidity_score: float = Field(ge=0.0, le=10.0, description="Liquidity strength (0-10 scale)")
    leverage_score: float = Field(ge=0.0, le=10.0, description="Debt management quality (0-10 scale)")
    profitability_score: float = Field(ge=0.0, le=10.0, description="Profitability strength (0-10 scale)")
    cash_flow_score: float = Field(ge=0.0, le=10.0, description="Cash generation quality (0-10 scale)")
    overall_health: Literal["excellent", "good", "fair", "poor", "critical"] = Field(
        description="Overall financial health rating"
    )
    health_reasoning: str = Field(description="Explanation of health assessment")


class GrowthMetrics(BaseModel):
    """Growth analysis"""
    revenue_growth_trend: Literal["accelerating", "steady", "slowing", "declining", "volatile"] = Field(
        description="Revenue growth trajectory"
    )
    earnings_growth_trend: Literal["accelerating", "steady", "slowing", "declining", "volatile"] = Field(
        description="Earnings growth trajectory"
    )
    growth_sustainability: Literal["high", "medium", "low", "uncertain"] = Field(
        description="Likelihood growth can continue"
    )
    growth_drivers: List[str] = Field(description="2-4 key factors driving or hindering growth")


class FundamentalAnalysisOutput(BaseModel):
    """Complete fundamental analysis output"""
    analysis_summary: str = Field(description="3-4 sentence executive summary of fundamental analysis")
    valuation: ValuationMetrics = Field(description="Valuation assessment")
    financial_health: FinancialHealthMetrics = Field(description="Financial health metrics and scores")
    growth: GrowthMetrics = Field(description="Growth analysis")
    key_strengths: List[str] = Field(description="3-5 key fundamental strengths")
    red_flags: List[str] = Field(description="2-5 concerns or risk factors identified in fundamentals")
    competitive_advantages: List[str] = Field(description="2-4 moats or competitive advantages if identifiable")
    fundamental_rating: Literal["strong_buy", "buy", "hold", "sell", "strong_sell"] = Field(
        description="Overall fundamental investment rating"
    )
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in analysis (0-1 scale)")


def create_fundamentals_analyst(llm):
    """
    Creates a fundamentals analyst node that:
    1. Fetches all 4 fundamental data sources directly (company overview, balance sheet, income statement, cash flow)
    2. Optionally fetches earnings data
    3. Generates structured JSON analysis with quality scoring
    4. Condenses message history to single clean summary

    Args:
        llm: Language model instance

    Returns:
        A function that takes state and returns updated state
    """

    def fundamentals_analyst_node(state):
        ticker = state.get("ticker", "")
        date = state.get("date", "")

        # Import tools from Yahoo Finance (yfinance) - FREE, no API key needed!
        from simplified_tradingagents.tools.fundamental_tools_yfinance import (
            get_company_overview,
            get_balance_sheet,
            get_income_statement,
            get_cash_flow,
            get_earnings
        )

        # Step 1: Fetch all fundamental data directly (no LLM tool calling)
        data_collected = {}
        errors = []

        try:
            data_collected['company_overview'] = get_company_overview.invoke({"ticker": ticker})
        except Exception as e:
            errors.append(f"Company overview error: {str(e)}")
            data_collected['company_overview'] = f"Error fetching company overview for {ticker}"

        try:
            # Fetch both quarterly and annual for trend analysis
            data_collected['balance_sheet_quarterly'] = get_balance_sheet.invoke({
                "ticker": ticker,
                "period": "quarterly"
            })
            data_collected['balance_sheet_annual'] = get_balance_sheet.invoke({
                "ticker": ticker,
                "period": "annual"
            })
        except Exception as e:
            errors.append(f"Balance sheet error: {str(e)}")
            data_collected['balance_sheet_quarterly'] = f"Error fetching balance sheet"
            data_collected['balance_sheet_annual'] = f"Error fetching balance sheet"

        try:
            data_collected['income_statement_quarterly'] = get_income_statement.invoke({
                "ticker": ticker,
                "period": "quarterly"
            })
            data_collected['income_statement_annual'] = get_income_statement.invoke({
                "ticker": ticker,
                "period": "annual"
            })
        except Exception as e:
            errors.append(f"Income statement error: {str(e)}")
            data_collected['income_statement_quarterly'] = f"Error fetching income statement"
            data_collected['income_statement_annual'] = f"Error fetching income statement"

        try:
            data_collected['cash_flow_quarterly'] = get_cash_flow.invoke({
                "ticker": ticker,
                "period": "quarterly"
            })
            data_collected['cash_flow_annual'] = get_cash_flow.invoke({
                "ticker": ticker,
                "period": "annual"
            })
        except Exception as e:
            errors.append(f"Cash flow error: {str(e)}")
            data_collected['cash_flow_quarterly'] = f"Error fetching cash flow"
            data_collected['cash_flow_annual'] = f"Error fetching cash flow"

        try:
            data_collected['earnings'] = get_earnings.invoke({"ticker": ticker})
        except Exception as e:
            errors.append(f"Earnings error: {str(e)}")
            data_collected['earnings'] = f"Error fetching earnings data"

        # If critical errors, return fallback
        if len(errors) >= 4:
            error_output = FundamentalAnalysisOutput(
                analysis_summary=f"Unable to perform fundamental analysis for {ticker} due to multiple data fetching errors.",
                valuation=ValuationMetrics(
                    pe_ratio=None,
                    peg_ratio=None,
                    price_to_book=None,
                    valuation_verdict="insufficient_data",
                    valuation_reasoning="Insufficient data to assess valuation."
                ),
                financial_health=FinancialHealthMetrics(
                    liquidity_score=0.0,
                    leverage_score=0.0,
                    profitability_score=0.0,
                    cash_flow_score=0.0,
                    overall_health="critical",
                    health_reasoning="Unable to assess financial health due to data errors."
                ),
                growth=GrowthMetrics(
                    revenue_growth_trend="uncertain",
                    earnings_growth_trend="uncertain",
                    growth_sustainability="uncertain",
                    growth_drivers=["Data unavailable"]
                ),
                key_strengths=[],
                red_flags=errors,
                competitive_advantages=[],
                fundamental_rating="hold",
                confidence_score=0.0
            )

            summary_message = AIMessage(
                content=f"Fundamental Analysis for {ticker}:\n{json.dumps(error_output.model_dump(), indent=2)}"
            )

            return {
                "messages": [summary_message],
                "fundamental_analysis": json.dumps(error_output.model_dump(), indent=2)
            }

        # Step 2: Create comprehensive analysis prompt with structured output requirement
        analysis_prompt = f"""You are an expert fundamental analyst specializing in financial statement analysis and company valuation.

Analyze the following comprehensive fundamental data for {ticker} as of {date}.

**COMPANY OVERVIEW:**
{data_collected.get('company_overview', 'N/A')}

**BALANCE SHEET (Quarterly):**
{data_collected.get('balance_sheet_quarterly', 'N/A')}

**BALANCE SHEET (Annual):**
{data_collected.get('balance_sheet_annual', 'N/A')}

**INCOME STATEMENT (Quarterly):**
{data_collected.get('income_statement_quarterly', 'N/A')}

**INCOME STATEMENT (Annual):**
{data_collected.get('income_statement_annual', 'N/A')}

**CASH FLOW STATEMENT (Quarterly):**
{data_collected.get('cash_flow_quarterly', 'N/A')}

**CASH FLOW STATEMENT (Annual):**
{data_collected.get('cash_flow_annual', 'N/A')}

**EARNINGS HISTORY:**
{data_collected.get('earnings', 'N/A')}

---

Perform a DEEP fundamental analysis with the following requirements:

**1. ANALYSIS SUMMARY (3-4 sentences)**
- Executive summary of fundamental health and investment thesis

**2. VALUATION ASSESSMENT**
- Analyze P/E, PEG, P/B, and other valuation multiples
- Compare to historical averages and sector norms (if data available)
- Determine if stock is undervalued, fairly valued, or overvalued
- Provide clear reasoning (2-3 sentences)

**3. FINANCIAL HEALTH SCORING (0-10 scale for each)**
- **Liquidity Score**: Based on current ratio, quick ratio, cash position
- **Leverage Score**: Based on debt-to-equity, interest coverage, debt trends
- **Profitability Score**: Based on margins (gross, operating, net), ROE, ROA
- **Cash Flow Score**: Based on operating cash flow, free cash flow, cash conversion
- **Overall Health**: Excellent/Good/Fair/Poor/Critical
- Provide reasoning for the overall health assessment

**4. GROWTH ANALYSIS**
- Analyze revenue growth trends (accelerating/steady/slowing/declining/volatile)
- Analyze earnings growth trends (accelerating/steady/slowing/declining/volatile)
- Assess growth sustainability (high/medium/low/uncertain)
- Identify 2-4 key growth drivers or headwinds

**5. KEY STRENGTHS (3-5 items)**
- Identify the company's strongest fundamental attributes
- Be specific with data points and metrics

**6. RED FLAGS (2-5 items)**
- Identify concerning trends or risks in the financial data
- Examples: declining margins, rising debt, negative FCF, deteriorating liquidity, earnings surprises (negative)
- Be specific about what the data shows

**7. COMPETITIVE ADVANTAGES (2-4 items)**
- Identify potential moats based on financial metrics
- Examples: high margins, strong cash generation, low debt, pricing power indicators
- Only include if evidence exists in the data

**8. FUNDAMENTAL RATING**
- Assign: strong_buy / buy / hold / sell / strong_sell
- Based on valuation + financial health + growth prospects

**9. CONFIDENCE SCORE (0.0 to 1.0)**
- How confident are you in this analysis given data quality and completeness?

---

**CRITICAL ANALYSIS GUIDELINES:**
- Be data-driven and specific - cite actual numbers and trends
- Compare multiple periods to identify improving/deteriorating trends
- Look for divergences (e.g., revenue growth but FCF declining)
- Consider both quarterly AND annual data for comprehensive view
- Identify quality of earnings (cash conversion, one-time items)
- Be honest about red flags - don't sugarcoat concerning trends
- Confidence should reflect data quality and clarity of signals

---

Respond ONLY with valid JSON matching this exact structure (no markdown, no extra text):
{{
  "analysis_summary": "string",
  "valuation": {{
    "pe_ratio": number or null,
    "peg_ratio": number or null,
    "price_to_book": number or null,
    "valuation_verdict": "undervalued|fairly_valued|overvalued|insufficient_data",
    "valuation_reasoning": "string"
  }},
  "financial_health": {{
    "liquidity_score": number (0-10),
    "leverage_score": number (0-10),
    "profitability_score": number (0-10),
    "cash_flow_score": number (0-10),
    "overall_health": "excellent|good|fair|poor|critical",
    "health_reasoning": "string"
  }},
  "growth": {{
    "revenue_growth_trend": "accelerating|steady|slowing|declining|volatile",
    "earnings_growth_trend": "accelerating|steady|slowing|declining|volatile",
    "growth_sustainability": "high|medium|low|uncertain",
    "growth_drivers": ["string"]
  }},
  "key_strengths": ["string"],
  "red_flags": ["string"],
  "competitive_advantages": ["string"],
  "fundamental_rating": "strong_buy|buy|hold|sell|strong_sell",
  "confidence_score": number (0.0-1.0)
}}"""

        # Step 3: Get structured response from LLM
        try:
            # Use structured output if available, otherwise parse JSON
            if hasattr(llm, 'with_structured_output'):
                structured_llm = llm.with_structured_output(FundamentalAnalysisOutput)
                analysis_result = structured_llm.invoke(analysis_prompt)
                analysis_json = analysis_result.model_dump()
            else:
                # Fallback: request JSON and parse
                response = llm.invoke(analysis_prompt)
                response_text = response.content if hasattr(response, 'content') else str(response)

                # Clean potential markdown formatting
                response_text = response_text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                # Parse and validate
                analysis_dict = json.loads(response_text)
                analysis_result = FundamentalAnalysisOutput(**analysis_dict)
                analysis_json = analysis_result.model_dump()

        except Exception as e:
            # Parsing fallback
            analysis_json = {
                "analysis_summary": f"Fundamental analysis completed for {ticker} but encountered formatting issues. Data was collected successfully.",
                "valuation": {
                    "pe_ratio": None,
                    "peg_ratio": None,
                    "price_to_book": None,
                    "valuation_verdict": "insufficient_data",
                    "valuation_reasoning": "Unable to complete valuation assessment due to parsing error."
                },
                "financial_health": {
                    "liquidity_score": 5.0,
                    "leverage_score": 5.0,
                    "profitability_score": 5.0,
                    "cash_flow_score": 5.0,
                    "overall_health": "fair",
                    "health_reasoning": "Unable to complete detailed health assessment due to parsing error."
                },
                "growth": {
                    "revenue_growth_trend": "uncertain",
                    "earnings_growth_trend": "uncertain",
                    "growth_sustainability": "uncertain",
                    "growth_drivers": ["Analysis parsing error - see raw data"]
                },
                "key_strengths": ["Data collected successfully - see fundamental_analysis field"],
                "red_flags": [f"Analysis formatting error: {str(e)}"],
                "competitive_advantages": [],
                "fundamental_rating": "hold",
                "confidence_score": 0.3
            }

        # Step 4: Create clean, condensed message history
        # User message: original request context
        user_summary = HumanMessage(
            content=f"Perform fundamental analysis for {ticker} as of {date}"
        )

        # Assistant message: structured JSON result
        formatted_analysis = json.dumps(analysis_json, indent=2)
        assistant_summary = AIMessage(
            content=f"Fundamental Analysis for {ticker}:\n\n{formatted_analysis}"
        )

        # Step 5: Return with clean state
        return {
            "messages": [user_summary, assistant_summary],  # Overwrites old messages
            "fundamental_analysis": formatted_analysis
        }

    return fundamentals_analyst_node