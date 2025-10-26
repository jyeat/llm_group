
#changes
#4 steps approach. Take data, analyse, enforce output, update memory with summary
#enforce structured output (Pydantic structure)
#Instead of LLM planning what indicators to take, we take the results and focus 100% on analyzing the provided data. 
#Less flexibility on indicator, but focus more on reasoning with fixed indicator. 
#Less LLM call without React loop. 
#message history condensation -> avoid content bloat



from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from config import LLM_MODEL, LLM_TEMPERATURE, GOOGLE_GENAI_API_KEY
from pydantic import BaseModel, Field
from typing import List, Literal
import json
from datetime import datetime

# Structured output schema
class IndicatorAnalysis(BaseModel):
    """Analysis of a single technical indicator"""
    name: str = Field(description="Indicator name (e.g., RSI, SMA_50)")
    value: float = Field(description="Current indicator value")
    interpretation: str = Field(description="Brief explanation of what this value means")
    signal: Literal["bullish", "bearish", "neutral"] = Field(description="Trading signal from this indicator")


class TrendAnalysis(BaseModel):
    """Multi-timeframe trend analysis"""
    short_term: Literal["bullish", "bearish", "neutral"] = Field(description="Short-term trend (1-5 days)")
    medium_term: Literal["bullish", "bearish", "neutral"] = Field(description="Medium-term trend (1-4 weeks)")
    long_term: Literal["bullish", "bearish", "neutral"] = Field(description="Long-term trend (1-3 months)")


class MarketAnalysisOutput(BaseModel):
    """Structured market analysis output"""
    analysis_summary: str = Field(description="2-3 sentence executive summary of the market analysis")
    selected_indicators: List[IndicatorAnalysis] = Field(description="List of analyzed technical indicators (max 8)")
    trend_analysis: TrendAnalysis = Field(description="Multi-timeframe trend assessment")
    key_insights: List[str] = Field(description="3-5 actionable insights for traders")
    risk_factors: List[str] = Field(description="2-4 key risk factors to monitor")
    market_sentiment: Literal["bullish", "bearish", "neutral"] = Field(description="Overall market sentiment")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in analysis (0-1 scale)")


def create_market_analyst(llm):
    """
    Creates a market analyst node that:
    1. Fetches stock data and technical indicators directly (no React)
    2. Generates structured JSON analysis
    3. Condenses message history to single clean summary
    """

    def market_analyst_node(state):
        ticker = state.get("ticker", "")
        date = state.get("date", "")

        # Import tools from Yahoo Finance (yfinance) - FREE, no API key needed!
        from tools.analyst_tools_yfinance import (
            get_stock_data,
            get_technical_indicators
        )

        # Step 1: Fetch data directly (no LLM tool calling)
        try:
            stock_data = get_stock_data.invoke({"ticker": ticker, "date": date})
            technical_data = get_technical_indicators.invoke({"ticker": ticker})
        except Exception as e:
            # Fallback error handling
            error_output = MarketAnalysisOutput(
                analysis_summary=f"Unable to analyze {ticker} due to data fetching error.",
                selected_indicators=[],
                trend_analysis=TrendAnalysis(
                    short_term="neutral",
                    medium_term="neutral",
                    long_term="neutral"
                ),
                key_insights=[f"Data error: {str(e)}"],
                risk_factors=["Unable to fetch market data"],
                market_sentiment="neutral",
                confidence_score=0.0
            )

            summary_message = AIMessage(
                content=f"Market Analysis for {ticker}:\n{json.dumps(error_output.model_dump(), indent=2)}"
            )

            return {
                "messages": [summary_message],
                "market_analysis": json.dumps(error_output.model_dump(), indent=2)
            }

        # Step 2: Create analysis prompt with structured output requirement
        analysis_prompt = f"""You are an expert market analyst. Analyze the following market data for {ticker} as of {date}.

**Stock Data:**
{stock_data}

**Technical Indicators:**
{technical_data}

Provide a comprehensive technical analysis with the following requirements:

1. **Analysis Summary**: 2-3 sentence executive summary
2. **Indicator Analysis**: Analyze the most relevant technical indicators (up to 8) with specific values and interpretations
3. **Trend Analysis**: Assess short-term (1-5 days), medium-term (1-4 weeks), and long-term (1-3 months) trends
4. **Key Insights**: Provide 3-5 actionable insights for traders based on the data
5. **Risk Factors**: Identify 2-4 key risk factors or concerns
6. **Market Sentiment**: Determine overall sentiment (bullish/bearish/neutral)
7. **Confidence Score**: Rate your confidence in this analysis (0.0 to 1.0)

Be specific, data-driven, and avoid generic statements. Focus on what the numbers actually indicate.

Respond ONLY with valid JSON matching this exact structure (no markdown, no extra text):
{{
  "analysis_summary": "string",
  "selected_indicators": [
    {{
      "name": "string",
      "value": number,
      "interpretation": "string",
      "signal": "bullish|bearish|neutral"
    }}
  ],
  "trend_analysis": {{
    "short_term": "bullish|bearish|neutral",
    "medium_term": "bullish|bearish|neutral",
    "long_term": "bullish|bearish|neutral"
  }},
  "key_insights": ["string"],
  "risk_factors": ["string"],
  "market_sentiment": "bullish|bearish|neutral",
  "confidence_score": number
}}"""

        # Step 3: Get structured response from LLM
        try:
            # Use structured output if available, otherwise parse JSON
            if hasattr(llm, 'with_structured_output'):
                structured_llm = llm.with_structured_output(MarketAnalysisOutput)
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
                analysis_result = MarketAnalysisOutput(**analysis_dict)
                analysis_json = analysis_result.model_dump()

        except Exception as e:
            # Parsing fallback
            analysis_json = {
                "analysis_summary": f"Analysis completed for {ticker} but encountered formatting issues.",
                "selected_indicators": [],
                "trend_analysis": {
                    "short_term": "neutral",
                    "medium_term": "neutral",
                    "long_term": "neutral"
                },
                "key_insights": ["Unable to parse structured analysis", f"Error: {str(e)}"],
                "risk_factors": ["Analysis parsing error"],
                "market_sentiment": "neutral",
                "confidence_score": 0.3
            }

        # Step 4: Create clean, condensed message history
        # Replace all messages with a single clean summary

        # User message: original request context
        user_summary = HumanMessage(
            content=f"Analyze market conditions for {ticker} as of {date}"
        )

        # Assistant message: structured JSON result
        formatted_analysis = json.dumps(analysis_json, indent=2)
        assistant_summary = AIMessage(
            content=f"Market Analysis for {ticker}:\n\n{formatted_analysis}"
        )

        # Step 5: Return with clean state
        return {
            "messages": [user_summary, assistant_summary],  # Overwrites old messages
            "market_analysis": formatted_analysis
        }

    return market_analyst_node
