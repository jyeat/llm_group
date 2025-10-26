"""Fundamentals Analyst Agent - Financial Analysis.

This agent analyzes company financials and valuation metrics.
"""

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from tools.fundamental_tools_v2 import get_company_overview, get_balance_sheet,get_income_statement, get_cash_flow,get_earnings


def create_fundamentals_analyst(llm):
    """Factory function to create a fundamentals analyst agent node.
    
    Args:
        llm: The language model to use
        
    Returns:
        A function that takes state and returns updated state
    """
    
    tools = [FUNDAMENTAL_TOOLS]
    
    def fundamentals_analyst_node(state):
        """Analyze company fundamentals.
        
        Evaluates:
        - Valuation (P/E, PEG ratios)
        - Financial health (debt, margins)
        - Growth prospects
        """
        ticker = state['ticker']
        
        prompt = f"""You are a fundamental analyst. Analyze {ticker}'s financial health.

Your analysis should cover:
1. Valuation metrics (P/E, PEG, P/B ratios) - are they reasonable?
2. Financial health (debt levels, profit margins, ROE)
3. Growth prospects (revenue growth)
4. Overall fundamental outlook: STRONG, WEAK, or NEUTRAL

Be concise (3-4 sentences). Focus on investment quality.
End with a clear fundamental outlook statement.

Use get_fundamentals tool to fetch data first."""
        
        agent = create_react_agent(llm, tools)
        result = agent.invoke({
            "messages": [HumanMessage(content=prompt)]
        })
        
        analysis = result["messages"][-1].content
        
        return {
            "fundamentals_analysis": analysis,
            "messages": []
        }
    
    return fundamentals_analyst_node