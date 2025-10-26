# Bull Debater V2
#
# Purpose: Build the strongest bullish case by synthesizing technical and fundamental analysis
# Approach: Extract and amplify bullish signals, identify catalysts, acknowledge risks
# Output: Structured JSON with bullish thesis and conviction scoring

from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List, Literal
import json


# Structured output schema
class BullishSignals(BaseModel):
    """Bullish signals from analysis"""
    technical_signals: List[str] = Field(description="3-5 bullish technical indicators/patterns")
    fundamental_signals: List[str] = Field(description="3-5 bullish fundamental strengths")


class BullishCatalysts(BaseModel):
    """Potential catalysts for upside"""
    near_term: List[str] = Field(description="1-3 catalysts that could drive price up in days/weeks")
    long_term: List[str] = Field(description="1-3 catalysts for sustained growth over months")


class RiskAcknowledgment(BaseModel):
    """Honest assessment of what could go wrong"""
    key_risks: List[str] = Field(description="2-4 main risks to the bullish thesis")
    risk_mitigation: str = Field(description="1-2 sentences on how to manage these risks")


class BullCaseOutput(BaseModel):
    """Complete bullish case output"""
    thesis_summary: str = Field(description="3-4 sentence executive summary of why this is a BUY")
    bullish_signals: BullishSignals = Field(description="Technical and fundamental bullish evidence")
    catalysts: BullishCatalysts = Field(description="What could drive upside")
    target_price_direction: Literal["significantly_higher", "moderately_higher", "slightly_higher"] = Field(
        description="Expected price movement magnitude"
    )
    time_horizon: Literal["short_term", "medium_term", "long_term", "multi_timeframe"] = Field(
        description="When the bullish case is expected to play out"
    )
    risk_acknowledgment: RiskAcknowledgment = Field(description="Honest risks to this thesis")
    conviction_score: float = Field(ge=0.0, le=1.0, description="Conviction in bullish case (0-1)")
    recommended_action: Literal["strong_buy", "buy", "accumulate"] = Field(
        description="Recommended bullish action"
    )


def create_bull_debater(llm):
    """
    Creates a bull debater node that:
<<<<<<< HEAD
    1. Reads market_analysis and fundamental_analysis from state
=======
    1. Reads news_analysis, market_analysis and fundamental_analysis from state
>>>>>>> 6c286e9 (upload my own trading agent)
    2. Extracts and amplifies all bullish signals
    3. Builds strongest possible buy case
    4. Provides structured JSON output
    5. Condenses message history

    Args:
        llm: Language model instance

    Returns:
        A function that takes state and returns updated state
    """

    def bull_debater_node(state):
        ticker = state.get("ticker", "")
        date = state.get("date", "")
<<<<<<< HEAD
=======
        news_analysis = state.get("news_analysis", "No news analysis available")
>>>>>>> 6c286e9 (upload my own trading agent)
        market_analysis = state.get("market_analysis", "No market analysis available")
        fundamental_analysis = state.get("fundamental_analysis", "No fundamental analysis available")

        # Step 1: Create bullish debate prompt
        debate_prompt = f"""You are an expert BULL analyst making the strongest possible case for BUYING {ticker}.

Your role is to advocate for the BULLISH position by:
1. Extracting ALL positive signals from the analysis
2. Identifying catalysts that could drive the price higher
3. Building a compelling investment thesis for why this stock will RISE
4. Being intellectually honest about risks (but still maintaining bullish stance)

<<<<<<< HEAD
=======
**NEWS ANALYSIS:**
{news_analysis}

>>>>>>> 6c286e9 (upload my own trading agent)
**MARKET ANALYSIS:**
{market_analysis}

**FUNDAMENTAL ANALYSIS:**
{fundamental_analysis}

---
<<<<<<< HEAD
=======
IMPORTANT NEWS GUIDANCE:
- Use positive/constructive items from NEWS for bullish signals and catalysts (e.g., demand strength, easing regulation, favorable sector flows).
- If referencing articles, use their titles or themes only (NO URLs; do not fabricate details).
- Include near-term NEWS catalysts with dates/timings when available (events, product launches, guidance, regulatory milestones).
- Use macro/sector items ONLY if they are relevant to {ticker} per the news analysis.
>>>>>>> 6c286e9 (upload my own trading agent)

**YOUR TASK: BUILD THE STRONGEST BULL CASE**

**1. THESIS SUMMARY (3-4 sentences)**
- Why is {ticker} a BUY right now?
- What's the core investment thesis?
- What makes this opportunity compelling?

**2. BULLISH SIGNALS**
**Technical Signals (3-5 items):**
- Extract bullish technical indicators from market analysis
- Examples: oversold RSI, price above SMA, bullish trend, positive momentum
- Be specific with values and interpretations

**Fundamental Signals (3-5 items):**
- Extract bullish fundamental strengths
- Examples: strong balance sheet, growing revenue, improving margins, undervalued multiples
- Cite specific metrics and scores

**3. CATALYSTS**
**Near-term (1-3 items):** What could drive price up in days/weeks?
- Examples: earnings beat, technical breakout, sector rotation, oversold bounce

**Long-term (1-3 items):** What supports sustained growth over months?
- Examples: market expansion, margin improvement, debt reduction, competitive advantages

**4. TARGET PRICE DIRECTION**
- significantly_higher (20%+ upside expected)
- moderately_higher (10-20% upside)
- slightly_higher (5-10% upside)

**5. TIME HORIZON**
- short_term: Days to weeks
- medium_term: Weeks to months
- long_term: Months to years
- multi_timeframe: Bullish across all timeframes

**6. RISK ACKNOWLEDGMENT (Be honest)**
**Key Risks (2-4 items):** What could go wrong with this bullish thesis?
- Technical risks (e.g., overbought, resistance levels)
- Fundamental risks (e.g., debt concerns, slowing growth)

**Risk Mitigation (1-2 sentences):** How should bulls manage these risks?

**7. CONVICTION SCORE (0.0 to 1.0)**
- How strong is the bullish case based on available evidence?
- Higher score = stronger conviction in upside

**8. RECOMMENDED ACTION**
- strong_buy: Compelling evidence, high conviction
- buy: Solid case, moderate conviction
- accumulate: Good long-term case, lower urgency

---

**DEBATE GUIDELINES:**
- Extract EVERY bullish signal from the provided analysis
- Steelman the bullish position - make it as strong as possible
- Use specific data points and metrics to support your case
- Be intellectually honest about risks (but maintain bullish stance)
- Think like a passionate bull who wants others to see the opportunity
- Cite evidence from both technical and fundamental analysis
<<<<<<< HEAD
=======
- Do NOT invent facts beyond what is provided
>>>>>>> 6c286e9 (upload my own trading agent)

---

Respond ONLY with valid JSON matching this exact structure (no markdown, no extra text):
{{
  "thesis_summary": "string",
  "bullish_signals": {{
    "technical_signals": ["string"],
    "fundamental_signals": ["string"]
  }},
  "catalysts": {{
    "near_term": ["string"],
    "long_term": ["string"]
  }},
  "target_price_direction": "significantly_higher|moderately_higher|slightly_higher",
  "time_horizon": "short_term|medium_term|long_term|multi_timeframe",
  "risk_acknowledgment": {{
    "key_risks": ["string"],
    "risk_mitigation": "string"
  }},
  "conviction_score": number (0.0-1.0),
  "recommended_action": "strong_buy|buy|accumulate"
}}"""

        # Step 2: Get structured response from LLM
        try:
            if hasattr(llm, 'with_structured_output'):
                structured_llm = llm.with_structured_output(BullCaseOutput)
                bull_case = structured_llm.invoke(debate_prompt)
                bull_case_json = bull_case.model_dump()
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
                bull_dict = json.loads(response_text)
                bull_case = BullCaseOutput(**bull_dict)
                bull_case_json = bull_case.model_dump()

        except Exception as e:
            # Fallback bull case
            bull_case_json = {
                "thesis_summary": f"Bull case for {ticker} could not be fully formulated due to parsing error, but data suggests potential upside opportunities exist.",
                "bullish_signals": {
                    "technical_signals": ["Analysis data collected - see market_analysis"],
<<<<<<< HEAD
                    "fundamental_signals": ["Analysis data collected - see fundamental_analysis"]
                },
                "catalysts": {
                    "near_term": ["Technical setup or fundamental strength may provide upside"],
                    "long_term": ["Company fundamentals may support growth"]
=======
                    "fundamental_signals": ["Analysis data collected - see fundamental_analysis",
                                            "News indicates potential positives — see news_analysis for supportive themes/catalysts"]
                },
                "catalysts": {
                    "near_term": ["Technical setup or fundamental strength may provide upside",
                                  "News-dated catalysts may act as near-term triggers (see news_analysis)"],
                    "long_term": ["Company fundamentals may support growth",
                                  "Durable positive themes in news could reinforce long-term thesis"]
>>>>>>> 6c286e9 (upload my own trading agent)
                },
                "target_price_direction": "moderately_higher",
                "time_horizon": "medium_term",
                "risk_acknowledgment": {
                    "key_risks": [f"Bull case formatting error: {str(e)}", "Incomplete analysis due to parsing issue"],
                    "risk_mitigation": "Review raw analysis data before taking action."
                },
                "conviction_score": 0.3,
                "recommended_action": "accumulate"
            }

        # Step 3: Create condensed message history
        user_summary = HumanMessage(
            content=f"Build the strongest bullish case for {ticker} based on market and fundamental analysis"
        )

        formatted_bull_case = json.dumps(bull_case_json, indent=2)
        assistant_summary = AIMessage(
            content=f"Bull Case for {ticker}:\n\n{formatted_bull_case}"
        )

        # Step 4: Return updated state
        return {
            "messages": [user_summary, assistant_summary],
            "bull_argument": formatted_bull_case
        }

    return bull_debater_node
