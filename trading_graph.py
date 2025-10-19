# Simplified Trading Agents Graph
#
# This module sets up the LangGraph workflow for the simplified trading agents system.
# The graph coordinates the flow between analysts, debaters, and supervisor.
#
# Workflow:
# 1. Market Analyst (technical analysis)
# 2. Fundamental Analyst (financial analysis)
# 3. Bull Debater (bullish case)
# 4. Bear Debater (bearish case)
# 5. Supervisor (final risk-tiered recommendations)

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

from simplified_tradingagents.state import TradingState
from simplified_tradingagents.config import (
    LLM_MODEL,
    LLM_TEMPERATURE,
    SUPERVISOR_MODEL,
    SUPERVISOR_TEMPERATURE,
    GOOGLE_GENAI_API_KEY
)

# Import agent factories
from simplified_tradingagents.agent.market_analyst_v2 import create_market_analyst
from simplified_tradingagents.agent.fundamentals_analyst_v2 import create_fundamentals_analyst
from simplified_tradingagents.agent.bull_debater_v2 import create_bull_debater
from simplified_tradingagents.agent.bear_debater_v2 import create_bear_debater
from simplified_tradingagents.agent.supervisor_v2 import create_supervisor


class TradingAgentsGraph:
    """
    Main graph coordinator for simplified trading agents system.

    Sets up a linear workflow:
    START → Market Analyst → Fundamental Analyst → Bull Debater → Bear Debater → Supervisor → END

    Each agent:
    - Reads from shared state
    - Performs its specialized analysis
    - Writes results back to state
    - Passes control to next agent
    """

    def __init__(
        self,
        llm_model: str = None,
        llm_temperature: float = None,
        debug: bool = False
    ):
        """
        Initialize the trading agents graph.

        Args:
            llm_model: LLM model name (defaults to config.LLM_MODEL)
            llm_temperature: LLM temperature (defaults to config.LLM_TEMPERATURE)
            debug: Whether to enable debug mode with detailed logging
        """
        self.debug = debug

        # Initialize LLMs - separate models for analysts/debaters vs supervisor
        model_name = llm_model or LLM_MODEL
        temperature = llm_temperature if llm_temperature is not None else LLM_TEMPERATURE

        # Fast model for analysts and debaters
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=GOOGLE_GENAI_API_KEY
        )

        # Deep thinking model for supervisor
        self.supervisor_llm = ChatGoogleGenerativeAI(
            model=SUPERVISOR_MODEL,
            temperature=SUPERVISOR_TEMPERATURE,
            google_api_key=GOOGLE_GENAI_API_KEY
        )

        if self.debug:
            print(f"[TradingAgentsGraph] Initialized with:")
            print(f"  - Analysts/Debaters: {model_name}, temperature: {temperature}")
            print(f"  - Supervisor: {SUPERVISOR_MODEL}, temperature: {SUPERVISOR_TEMPERATURE}")

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self):
        """
        Build the LangGraph workflow.

        Graph structure:

        START
          ↓
        market_analyst (technical analysis)
          ↓
        fundamentals_analyst (financial analysis)
          ↓
        bull_debater (bullish case)
          ↓
        bear_debater (bearish case)
          ↓
        supervisor (final recommendations)
          ↓
        END

        Returns:
            Compiled StateGraph ready for execution
        """
        # Create the graph
        workflow = StateGraph(TradingState)

        # Create agent nodes using factory functions
        market_analyst_node = create_market_analyst(self.llm)
        fundamentals_analyst_node = create_fundamentals_analyst(self.llm)
        bull_debater_node = create_bull_debater(self.llm)
        bear_debater_node = create_bear_debater(self.llm)
        supervisor_node = create_supervisor(self.supervisor_llm)  # Use deep thinking model

        # Add nodes to the graph
        workflow.add_node("market_analyst", market_analyst_node)
        workflow.add_node("fundamentals_analyst", fundamentals_analyst_node)
        workflow.add_node("bull_debater", bull_debater_node)
        workflow.add_node("bear_debater", bear_debater_node)
        workflow.add_node("supervisor", supervisor_node)

        # Define the linear workflow edges
        workflow.set_entry_point("market_analyst")
        workflow.add_edge("market_analyst", "fundamentals_analyst")
        workflow.add_edge("fundamentals_analyst", "bull_debater")
        workflow.add_edge("bull_debater", "bear_debater")
        workflow.add_edge("bear_debater", "supervisor")
        workflow.add_edge("supervisor", END)

        # Compile and return
        compiled_graph = workflow.compile()

        if self.debug:
            print("[TradingAgentsGraph] Graph compiled successfully")
            print("Workflow: market_analyst → fundamentals_analyst → bull_debater → bear_debater → supervisor")

        return compiled_graph

    def analyze(self, ticker: str, date: str) -> Dict[str, Any]:
        """
        Run the complete trading analysis for a given ticker and date.

        This executes the full agent workflow:
        1. Fetches technical data and analyzes market conditions
        2. Fetches fundamental data and analyzes financial health
        3. Builds bullish case from both analyses
        4. Builds bearish case from both analyses
        5. Synthesizes all perspectives into risk-tiered recommendations

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL", "MSFT")
            date: Analysis date in YYYY-MM-DD format

        Returns:
            Dictionary containing the final state with all analysis results:
            - market_analysis: Technical analysis JSON
            - fundamental_analysis: Fundamental analysis JSON
            - bull_argument: Bullish case JSON
            - bear_argument: Bearish case JSON
            - decision: Final consensus direction (from supervisor)
            - rationale: Executive summary (from supervisor)
            - confidence: Overall confidence score (from supervisor)

        Example:
            >>> graph = TradingAgentsGraph()
            >>> result = graph.analyze("AAPL", "2024-01-15")
            >>> print(result['decision'])  # 'buy', 'sell', or 'hold'
            >>> print(result['rationale'])  # Executive summary
        """
        if self.debug:
            print(f"\n[TradingAgentsGraph] Starting analysis for {ticker} on {date}")

        # Create initial state
        initial_state = {
            "ticker": ticker,
            "date": date,
            "messages": [],
            "market_analysis": "",
            "fundamental_analysis": "",
            "bull_argument": "",
            "bear_argument": "",
            "decision": "neutral",
            "rationale": "",
            "confidence": 0.0,
            "supervisor_decision": ""
        }

        # Execute the graph
        if self.debug:
            # Debug mode: stream and print each step
            print("\n" + "="*80)
            print("STARTING WORKFLOW EXECUTION")
            print("="*80 + "\n")

            final_state = None
            for step_num, output in enumerate(self.graph.stream(initial_state), 1):
                node_name = list(output.keys())[0]
                print(f"\n--- Step {step_num}: {node_name.upper()} ---")

                if "messages" in output[node_name] and output[node_name]["messages"]:
                    last_message = output[node_name]["messages"][-1]
                    print(f"Message type: {type(last_message).__name__}")
                    if hasattr(last_message, 'content'):
                        content_preview = last_message.content[:200] + "..." if len(last_message.content) > 200 else last_message.content
                        print(f"Content preview: {content_preview}")

                final_state = output[node_name]

            print("\n" + "="*80)
            print("WORKFLOW EXECUTION COMPLETED")
            print("="*80 + "\n")

        else:
            # Standard mode: just invoke and get final result
            final_state = self.graph.invoke(initial_state)

        if self.debug:
            print(f"[TradingAgentsGraph] Analysis complete")
            print(f"  - Decision: {final_state.get('decision', 'N/A')}")
            print(f"  - Confidence: {final_state.get('confidence', 0.0):.2f}")
            print(f"  - Rationale: {final_state.get('rationale', 'N/A')[:100]}...")

        return final_state

    def get_graph_visualization(self) -> str:
        """
        Get a text representation of the graph structure.

        Returns:
            String describing the workflow
        """
        visualization = """
Trading Agents Workflow:

┌─────────────────────────────────────────────────────────────┐
│                          START                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    MARKET ANALYST                           │
│  - Fetches stock price data (OHLCV)                        │
│  - Fetches technical indicators (RSI, SMA)                 │
│  - Analyzes trends and momentum                            │
│  - Outputs: market_analysis (structured JSON)              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 FUNDAMENTALS ANALYST                        │
│  - Fetches company overview                                │
│  - Fetches financial statements (BS, IS, CF)               │
│  - Fetches earnings history                                │
│  - Analyzes financial health and valuation                 │
│  - Outputs: fundamental_analysis (structured JSON)         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     BULL DEBATER                            │
│  - Reads market + fundamental analysis                     │
│  - Extracts all bullish signals                            │
│  - Identifies upside catalysts                             │
│  - Outputs: bull_argument (structured JSON)                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     BEAR DEBATER                            │
│  - Reads market + fundamental analysis                     │
│  - Extracts all bearish signals                            │
│  - Identifies downside risks                               │
│  - Counters bullish arguments                              │
│  - Outputs: bear_argument (structured JSON)                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      SUPERVISOR                             │
│  - Reads ALL prior analysis                                │
│  - Weighs bull vs bear strength                            │
│  - Provides 3 risk-tiered recommendations:                 │
│    * Low risk (conservative)                               │
│    * Medium risk (balanced)                                │
│    * High risk (aggressive)                                │
│  - Outputs: decision, rationale, confidence                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                          END                                │
└─────────────────────────────────────────────────────────────┘

State Flow:
- ticker, date → market_analysis → fundamental_analysis →
  bull_argument → bear_argument → decision, rationale, confidence
"""
        return visualization


# Convenience function for quick usage
def create_trading_graph(debug: bool = False) -> TradingAgentsGraph:
    """
    Factory function to create a TradingAgentsGraph instance.

    Args:
        debug: Whether to enable debug mode

    Returns:
        Configured TradingAgentsGraph ready for analysis

    Example:
        >>> graph = create_trading_graph(debug=True)
        >>> result = graph.analyze("AAPL", "2024-01-15")
    """
    return TradingAgentsGraph(debug=debug)