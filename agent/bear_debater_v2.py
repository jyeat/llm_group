# Bear Debater V2
#
# Purpose: Build the strongest bearish case by synthesizing technical and fundamental analysis
# Approach: Extract and amplify bearish signals, identify risks, provide counter-arguments to bulls
# Output: Structured JSON with bearish thesis and conviction scoring

from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List, Literal
import json


# Structured output schema
class BearishSignals(BaseModel):
    """Bearish signals from analysis"""
    technical_signals: List[str] = Field(description="3-5 bearish technical indicators/patterns")
    fundamental_signals: List[str] = Field(description="3-5 bearish fundamental weaknesses")


class DownsideRisks(BaseModel):
    """Potential risks for downside"""
    near_term: List[str] = Field(description="1-3 risks that could drive price down in days/weeks")
    long_term: List[str] = Field(description="1-3 structural risks over months")


class CounterArguments(BaseModel):
    """Rebuttals to bullish case"""
    bull_case_weaknesses: List[str] = Field(description="2-4 flaws or risks in the bullish argument")
    why_bulls_are_wrong: str = Field(description="2-3 sentences explaining why bulls may be overlooking key risks")


class BearCaseOutput(BaseModel):
    """Complete bearish case output"""
    thesis_summary: str = Field(description="3-4 sentence executive summary of why this is a SELL or AVOID")
    bearish_signals: BearishSignals = Field(description="Technical and fundamental bearish evidence")
    downside_risks: DownsideRisks = Field(description="What could drive price lower")
    target_price_direction: Literal["significantly_lower", "moderately_lower", "slightly_lower"] = Field(
        description="Expected price movement magnitude"
    )
    time_horizon: Literal["short_term", "medium_term", "long_term", "multi_timeframe"] = Field(
        description="When the bearish case is expected to play out"
    )
    counter_arguments: CounterArguments = Field(description="Rebuttals to bullish thesis")
    conviction_score: float = Field(ge=0.0, le=1.0, description="Conviction in bearish case (0-1)")
    recommended_action: Literal["strong_sell", "sell", "avoid"] = Field(
        description="Recommended bearish action"
    )


def create_bear_debater(llm):
    """
    Creates a bear debater node that:
    1. Reads news_analysis, market_analysis and fundamental_analysis from state
    2. Extracts and amplifies all bearish signals
    3. Builds strongest possible sell/avoid case
    4. Provides counter-arguments to bullish thesis
    5. Provides structured JSON output
    6. Condenses message history

    Args:
        llm: Language model instance

    Returns:
        A function that takes state and returns updated state
    """

    def bear_debater_node(state):
        ticker = state.get("ticker", "")
        date = state.get("date", "")
        news_analysis = state.get("news_analysis", "No news analysis available")
        market_analysis = state.get("market_analysis", "No market analysis available")
        fundamental_analysis = state.get("fundamental_analysis", "No fundamental analysis available")

        # Step 1: Create bearish debate prompt
        debate_prompt = f"""You are an expert BEAR analyst making the strongest possible case for SELLING or AVOIDING {ticker}.

Your role is to advocate for the BEARISH position by:
1. Extracting ALL negative signals from the analysis
2. Identifying downside risks that could drive the price lower
3. Building a compelling case for why this stock will FALL or underperform
4. Providing counter-arguments to any bullish thesis
5. Being a critical skeptic who finds flaws and risks

**NEWS ANALYSIS (Company-relevant):**
{news_analysis}

**MARKET ANALYSIS:**
{market_analysis}

**FUNDAMENTAL ANALYSIS:**
{fundamental_analysis}

---

**YOUR TASK: BUILD THE STRONGEST BEAR CASE**

**1. THESIS SUMMARY (3-4 sentences)**
- Why is {ticker} a SELL or AVOID right now?
- What's the core bearish thesis?
- What makes this a risky or poor investment?

**2. BEARISH SIGNALS**
**Technical Signals (3-5 items):**
- Extract bearish technical indicators from market analysis
- Examples: overbought RSI, price below SMA, bearish trend, negative momentum, resistance rejection
- Be specific with values and interpretations

**Fundamental Signals (3-5 items):**
- Extract bearish fundamental weaknesses
- Examples: weak balance sheet, declining revenue, deteriorating margins, overvalued multiples, rising debt
- Cite specific metrics and scores

**3. DOWNSIDE RISKS**
**Near-term (1-3 items):** What could drive price down in days/weeks?
- Examples: earnings miss, technical breakdown, sector weakness, profit-taking, overbought conditions

**Long-term (1-3 items):** What structural risks exist over months?
- Examples: market share loss, margin compression, competitive threats, debt maturity, slowing growth

**4. TARGET PRICE DIRECTION**
- significantly_lower (20%+ downside expected)
- moderately_lower (10-20% downside)
- slightly_lower (5-10% downside)

**5. TIME HORIZON**
- short_term: Days to weeks
- medium_term: Weeks to months
- long_term: Months to years
- multi_timeframe: Bearish across all timeframes

**6. COUNTER-ARGUMENTS TO BULLS**
**Bull Case Weaknesses (2-4 items):** What are bulls missing or ignoring?
- Point out red flags that bulls may downplay
- Identify risks that offset bullish catalysts
- Challenge optimistic assumptions

**Why Bulls Are Wrong (2-3 sentences):**
- Explain the key flaws in the bullish argument
- What risks are bulls underestimating?

**7. CONVICTION SCORE (0.0 to 1.0)**
- How strong is the bearish case based on available evidence?
- Higher score = stronger conviction in downside

**8. RECOMMENDED ACTION**
- strong_sell: Compelling evidence for immediate exit or short
- sell: Solid bearish case, moderate downside risk
- avoid: Concerning signs, better opportunities elsewhere

---

**DEBATE GUIDELINES:**
- Extract EVERY bearish signal from the provided analysis
- Steelman the bearish position - make it as strong as possible
- Use specific data points and metrics to support your case
- Act as a critical skeptic looking for flaws and risks
- Think like a passionate bear who wants others to see the danger
- Challenge bullish narratives with evidence
- Cite evidence from technical, news analysis and fundamental analysis
- Be intellectually honest but maintain bearish stance

---

Respond ONLY with valid JSON matching this exact structure (no markdown, no extra text):
{{
  "thesis_summary": "string",
  "bearish_signals": {{
    "technical_signals": ["string"],
    "fundamental_signals": ["string"]
  }},
  "downside_risks": {{
    "near_term": ["string"],
    "long_term": ["string"]
  }},
  "target_price_direction": "significantly_lower|moderately_lower|slightly_lower",
  "time_horizon": "short_term|medium_term|long_term|multi_timeframe",
  "counter_arguments": {{
    "bull_case_weaknesses": ["string"],
    "why_bulls_are_wrong": "string"
  }},
  "conviction_score": number (0.0-1.0),
  "recommended_action": "strong_sell|sell|avoid"
}}"""

        # Step 2: Get structured response from LLM
        try:
            if hasattr(llm, 'with_structured_output'):
                structured_llm = llm.with_structured_output(BearCaseOutput)
                bear_case = structured_llm.invoke(debate_prompt)
                bear_case_json = bear_case.model_dump()
            else:
                # Fallback: request JSON and parse
                response = llm.invoke(debate_prompt)
                response_text = response.content if hasattr(response, 'content') else str(response)

                # Clean markdown formatting
                response_text = response_text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.startswith("```"):
                    response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                # Parse and validate
                bear_dict = json.loads(response_text)
                bear_case = BearCaseOutput(**bear_dict)
                bear_case_json = bear_case.model_dump()

        except Exception as e:
            # Fallback bear case
            bear_case_json = {
                "thesis_summary": f"Bear case for {ticker} could not be fully formulated due to parsing error, but data suggests potential downside risks exist.",
                "bearish_signals": {
                    "technical_signals": ["Analysis data collected - see market_analysis"],
                    "fundamental_signals": ["Analysis data collected - see fundamental_analysis", 
                                            "News-related risks present - see news_analysis for negative themes/catalysts"]
                },
                "downside_risks": {
                    "near_term": ["Technical weakness or fundamental concerns may create downside",
                                  "News catalysts could trigger volatility (see news_analysis)"],
                    "long_term": ["Company fundamentals may present risks",
                                  "Macro/sector headwinds indicated in news may persist"]
                },
                "target_price_direction": "moderately_lower",
                "time_horizon": "medium_term",
                "counter_arguments": {
                    "bull_case_weaknesses": [f"Bear case formatting error: {str(e)}", "Incomplete analysis due to parsing issue"],
                    "why_bulls_are_wrong": "Cannot fully assess bull case weaknesses due to formatting error. Review raw analysis data."
                },
                "conviction_score": 0.3,
                "recommended_action": "avoid"
            }

        # Step 3: Create condensed message history
        user_summary = HumanMessage(
            content=f"Build the strongest bearish case for {ticker} based on news, market and fundamental analysis"
        )

        formatted_bear_case = json.dumps(bear_case_json, indent=2)
        assistant_summary = AIMessage(
            content=f"Bear Case for {ticker}:\n\n{formatted_bear_case}"
        )

        # Step 4: Return updated state
        return {
            "messages": [user_summary, assistant_summary],
            "bear_argument": formatted_bear_case
        }

    return bear_debater_node
