# Supervisor V2
#
# Purpose: Synthesize all analysis perspectives and provide risk-tiered recommendations
# Approach: Weigh bull/bear arguments, consider technical/fundamental data, output differentiated advice
# Output: Structured JSON with low/medium/high risk recommendations

from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
import json


# Structured output schemas
class RiskTieredRecommendation(BaseModel):
    """Recommendation for a specific risk profile"""
    action: Literal["strong_buy", "buy", "accumulate", "hold", "reduce", "sell", "strong_sell"] = Field(
        description="Recommended trading action"
    )
    position_size: Literal["full", "half", "quarter", "minimal", "zero"] = Field(
        description="Suggested position sizing relative to normal allocation"
    )
    entry_strategy: str = Field(description="How to enter/exit position (e.g., 'Scale in over 3 days', 'Immediate exit')")
    stop_loss: Optional[str] = Field(description="Suggested stop-loss level or condition (if applicable)")
    rationale: str = Field(description="2-3 sentences explaining recommendation for this risk profile")


class TimeHorizonOutlook(BaseModel):
    """Outlook across different time horizons"""
    short_term: Literal["bullish", "bearish", "neutral"] = Field(description="Days to weeks outlook")
    medium_term: Literal["bullish", "bearish", "neutral"] = Field(description="Weeks to months outlook")
    long_term: Literal["bullish", "bearish", "neutral"] = Field(description="Months to years outlook")


class SupervisorDecision(BaseModel):
    """Complete supervisor synthesis and recommendations"""
    executive_summary: str = Field(description="4-5 sentence synthesis of all analysis - the complete picture")

    market_thesis: str = Field(description="2-3 sentences on overall market/technical view")
    fundamental_thesis: str = Field(description="2-3 sentences on overall fundamental view")

    bull_case_strength: float = Field(ge=0.0, le=10.0, description="Strength of bullish arguments (0-10 scale)")
    bear_case_strength: float = Field(ge=0.0, le=10.0, description="Strength of bearish arguments (0-10 scale)")

    consensus_direction: Literal["bullish", "bearish", "neutral", "mixed"] = Field(
        description="Overall directional bias after weighing all evidence"
    )

    low_risk_recommendation: RiskTieredRecommendation = Field(
        description="Conservative recommendation for risk-averse investors"
    )
    medium_risk_recommendation: RiskTieredRecommendation = Field(
        description="Balanced recommendation for moderate risk tolerance"
    )
    high_risk_recommendation: RiskTieredRecommendation = Field(
        description="Aggressive recommendation for high risk tolerance"
    )

    time_horizon_outlook: TimeHorizonOutlook = Field(description="Outlook across time horizons")

    key_decision_factors: List[str] = Field(
        description="3-5 most important factors driving these recommendations"
    )

    monitoring_points: List[str] = Field(
        description="2-4 key metrics/events to watch that could change the thesis"
    )

    final_confidence: float = Field(ge=0.0, le=1.0, description="Overall confidence in analysis (0-1)")


def create_supervisor(llm):
    """
    Creates a supervisor node that:
<<<<<<< HEAD
    1. Reads all prior analysis from state (market, fundamental, bull, bear)
=======
    1. Reads all prior analysis from state (news, market, fundamental, bull, bear)
>>>>>>> 6c286e9 (upload my own trading agent)
    2. Synthesizes competing viewpoints
    3. Weighs evidence and arguments
    4. Provides risk-tiered recommendations (low/medium/high risk)
    5. Outputs structured decision with clear rationale
    6. Condenses message history

    Args:
        llm: Language model instance

    Returns:
        A function that takes state and returns updated state
    """

    def supervisor_node(state):
        ticker = state.get("ticker", "")
        date = state.get("date", "")
<<<<<<< HEAD
=======
        news_analysis = state.get("news_analysis", "No news analysis available")
>>>>>>> 6c286e9 (upload my own trading agent)
        market_analysis = state.get("market_analysis", "No market analysis available")
        fundamental_analysis = state.get("fundamental_analysis", "No fundamental analysis available")
        bull_argument = state.get("bull_argument", "No bull case available")
        bear_argument = state.get("bear_argument", "No bear case available")

        # Step 1: Create supervisor synthesis prompt
        supervisor_prompt = f"""You are the CHIEF INVESTMENT OFFICER making final trading recommendations for {ticker}.

You have received comprehensive analysis from your team:
<<<<<<< HEAD
1. Market Analyst (technical analysis)
2. Fundamental Analyst (financial analysis)
3. Bull Advocate (strongest bullish case)
4. Bear Advocate (strongest bearish case)
=======
1. News Analyst (company + industry + macro news)
2. Market Analyst (technical analysis)
3. Fundamental Analyst (financial analysis)
4. Bull Advocate (strongest bullish case)
5. Bear Advocate (strongest bearish case)
>>>>>>> 6c286e9 (upload my own trading agent)

Your role is to:
- Synthesize all perspectives into a coherent investment thesis
- Weigh the strength of bull vs bear arguments
- Provide RISK-TIERED recommendations for different investor profiles
- Give clear, actionable guidance with specific entry/exit strategies

<<<<<<< HEAD
=======
**NEWS ANALYSIS (Company-relevant):**  
{news_analysis}

>>>>>>> 6c286e9 (upload my own trading agent)
**MARKET ANALYSIS (Technical):**
{market_analysis}

**FUNDAMENTAL ANALYSIS (Financial):**
{fundamental_analysis}

**BULL CASE:**
{bull_argument}

**BEAR CASE:**
{bear_argument}

---
<<<<<<< HEAD
=======
IMPORTANT NEWS GUIDANCE:                 # ✅ 新增指引（不改输出结构）
- Integrate NEWS themes/catalysts/risks into your synthesis where they materially affect {ticker}.
- Prefer dated catalysts and concrete events for monitoring_points (earnings dates, product launches, regulatory milestones).
- Reference titles/themes only (no URLs) and do NOT invent facts beyond the provided analyses.

>>>>>>> 6c286e9 (upload my own trading agent)

**YOUR TASK: PROVIDE FINAL INVESTMENT DECISION**

**1. EXECUTIVE SUMMARY (4-5 sentences)**
- Synthesize the complete picture for {ticker}
<<<<<<< HEAD
- What do technicals + fundamentals + bull/bear debate tell you?
=======
- What do technicals + fundamentals + new + bull/bear debate tell you?
>>>>>>> 6c286e9 (upload my own trading agent)
- What's the balanced investment thesis?
- What's the recommended overall approach?

**2. MARKET THESIS (2-3 sentences)**
- What's your view on the technical/market setup?
- Summarize key technical signals

**3. FUNDAMENTAL THESIS (2-3 sentences)**
- What's your view on the company's financial health?
- Summarize key fundamental strengths/weaknesses

**4. BULL VS BEAR STRENGTH SCORING (0-10 scale)**
**Bull Case Strength:** Rate the strength of bullish arguments
- Consider: quality of signals, conviction scores, catalyst strength
- 0 = no bull case, 10 = extremely compelling bull case

**Bear Case Strength:** Rate the strength of bearish arguments
- Consider: severity of risks, conviction scores, downside probability
- 0 = no bear case, 10 = extremely compelling bear case

**5. CONSENSUS DIRECTION**
After weighing all evidence:
- bullish: Bulls have stronger case
- bearish: Bears have stronger case
- neutral: Cases are balanced, or insufficient conviction either way
- mixed: Different signals across timeframes or conflicting evidence

**6. RISK-TIERED RECOMMENDATIONS**

You must provide THREE separate recommendations for different risk profiles:

**LOW RISK (Conservative investors):**
- Action: What should they do? (strong_buy/buy/accumulate/hold/reduce/sell/strong_sell)
- Position Size: How much? (full/half/quarter/minimal/zero)
- Entry Strategy: How to execute? (e.g., "Hold current positions", "Scale out 25% immediately")
- Stop Loss: Risk management level (if applicable)
- Rationale: 2-3 sentences explaining why this is appropriate for LOW RISK

**MEDIUM RISK (Balanced investors):**
- Action: What should they do?
- Position Size: How much?
- Entry Strategy: How to execute?
- Stop Loss: Risk management level (if applicable)
- Rationale: 2-3 sentences explaining why this is appropriate for MEDIUM RISK

**HIGH RISK (Aggressive traders):**
- Action: What should they do?
- Position Size: How much?
- Entry Strategy: How to execute?
- Stop Loss: Risk management level (if applicable)
- Rationale: 2-3 sentences explaining why this is appropriate for HIGH RISK

**7. TIME HORIZON OUTLOOK**
- Short-term (days to weeks): bullish/bearish/neutral
- Medium-term (weeks to months): bullish/bearish/neutral
- Long-term (months to years): bullish/bearish/neutral

**8. KEY DECISION FACTORS (3-5 items)**
What are the MOST important factors driving your recommendations?
- Be specific about what data/signals matter most
<<<<<<< HEAD
=======
- Include material NEWS themes/catalysts if applicable
>>>>>>> 6c286e9 (upload my own trading agent)
- Examples: "Oversold RSI with support holding", "Deteriorating margins despite revenue growth"

**9. MONITORING POINTS (2-4 items)**
What should investors watch that could change your thesis?
- Key levels, metrics, events that would invalidate or strengthen the thesis
<<<<<<< HEAD
=======
- Prefer dated NEWS events when available (e.g., announced timelines) 
>>>>>>> 6c286e9 (upload my own trading agent)
- Examples: "Break below $50 invalidates bullish case", "Q4 earnings report crucial for growth thesis"

**10. FINAL CONFIDENCE (0.0 to 1.0)**
How confident are you in this overall analysis?
- Consider data quality, signal clarity, consensus among analyses

---

**SUPERVISION GUIDELINES:**
- Be impartial - don't favor bulls or bears, favor EVIDENCE
- Weight arguments by quality of evidence, not just conviction scores
- Risk-tiered recommendations should be DIFFERENT (not same action for all profiles)
- Low risk = more conservative (favor holds/smaller positions/tighter stops)
- High risk = more aggressive (willing to trade on weaker signals)
- Be specific with entry/exit strategies (not generic advice)
- Acknowledge uncertainty where it exists
- Provide actionable guidance that investors can execute

---

Respond ONLY with valid JSON matching this exact structure (no markdown, no extra text):
{{
  "executive_summary": "string",
  "market_thesis": "string",
  "fundamental_thesis": "string",
  "bull_case_strength": number (0-10),
  "bear_case_strength": number (0-10),
  "consensus_direction": "bullish|bearish|neutral|mixed",
  "low_risk_recommendation": {{
    "action": "strong_buy|buy|accumulate|hold|reduce|sell|strong_sell",
    "position_size": "full|half|quarter|minimal|zero",
    "entry_strategy": "string",
    "stop_loss": "string or null",
    "rationale": "string"
  }},
  "medium_risk_recommendation": {{
    "action": "strong_buy|buy|accumulate|hold|reduce|sell|strong_sell",
    "position_size": "full|half|quarter|minimal|zero",
    "entry_strategy": "string",
    "stop_loss": "string or null",
    "rationale": "string"
  }},
  "high_risk_recommendation": {{
    "action": "strong_buy|buy|accumulate|hold|reduce|sell|strong_sell",
    "position_size": "full|half|quarter|minimal|zero",
    "entry_strategy": "string",
    "stop_loss": "string or null",
    "rationale": "string"
  }},
  "time_horizon_outlook": {{
    "short_term": "bullish|bearish|neutral",
    "medium_term": "bullish|bearish|neutral",
    "long_term": "bullish|bearish|neutral"
  }},
  "key_decision_factors": ["string"],
  "monitoring_points": ["string"],
  "final_confidence": number (0.0-1.0)
}}"""

        # Step 2: Get structured response from LLM
        try:
            if hasattr(llm, 'with_structured_output'):
                structured_llm = llm.with_structured_output(SupervisorDecision)
                decision = structured_llm.invoke(supervisor_prompt)
                decision_json = decision.model_dump()
            else:
                # Fallback: request JSON and parse
                response = llm.invoke(supervisor_prompt)
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
                decision_dict = json.loads(response_text)
                decision = SupervisorDecision(**decision_dict)
                decision_json = decision.model_dump()

        except Exception as e:
            # Fallback decision
            decision_json = {
                "executive_summary": f"Investment decision for {ticker} could not be fully formulated due to parsing error. Review individual analysis components before making decisions.",
                "market_thesis": "Technical analysis completed - see market_analysis for details.",
                "fundamental_thesis": "Fundamental analysis completed - see fundamental_analysis for details.",
                "bull_case_strength": 5.0,
                "bear_case_strength": 5.0,
                "consensus_direction": "neutral",
                "low_risk_recommendation": {
                    "action": "hold",
                    "position_size": "minimal",
                    "entry_strategy": "Wait for clearer signals before acting",
                    "stop_loss": None,
                    "rationale": "Conservative approach warranted due to analysis formatting issues."
                },
                "medium_risk_recommendation": {
                    "action": "hold",
                    "position_size": "quarter",
                    "entry_strategy": "Review raw analysis before making moves",
                    "stop_loss": None,
                    "rationale": "Moderate caution advised given incomplete synthesis."
                },
                "high_risk_recommendation": {
                    "action": "hold",
                    "position_size": "half",
                    "entry_strategy": "Consider raw analysis data for trading decisions",
                    "stop_loss": None,
                    "rationale": "Even aggressive traders should review individual analyses given formatting error."
                },
                "time_horizon_outlook": {
                    "short_term": "neutral",
                    "medium_term": "neutral",
                    "long_term": "neutral"
                },
                "key_decision_factors": [
                    f"Decision formatting error: {str(e)}",
                    "Review individual analysis components",
                    "Wait for successful analysis run"
                ],
                "monitoring_points": [
                    "Re-run analysis to get proper synthesis",
                    "Check data quality and API connectivity"
                ],
                "final_confidence": 0.2
            }

        # Step 3: Create condensed message history
        user_summary = HumanMessage(
            content=f"Provide final investment decision for {ticker} based on all analysis and debate"
        )

        formatted_decision = json.dumps(decision_json, indent=2)
        assistant_summary = AIMessage(
            content=f"Final Investment Decision for {ticker}:\n\n{formatted_decision}"
        )

        # Step 4: Return updated state with final decision
        return {
            "messages": [user_summary, assistant_summary],
            "decision": decision_json.get("consensus_direction", "neutral"),
            "rationale": decision_json.get("executive_summary", ""),
            "confidence": decision_json.get("final_confidence", 0.0),
            "supervisor_decision": formatted_decision  # Full JSON with risk-tiered recommendations
        }

    return supervisor_node
