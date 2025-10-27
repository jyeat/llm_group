
#1.1 This react agent call two tools and summarize the results
#1.2 Direct tool call instead of llm driven tool selection
#1.3 Ofiginal urgent select 8 indicators from a list, justify choice, call parametrics. It is more independent and opinionated. \

#3.1 This agent output is unstructured and short (3-4 sentences)
#3.2 Force structured json output schema
#3.3 Original agent mandates a markdown table, This allows downstream agent to use. 

#5 This agent summarizes and update the message
#6 Original agents updates the message with the entire message



"""Market Analyst Agent - Technical Analysis.

This agent analyzes price trends and technical indicators.
Uses ReAct pattern: Reason → Act (call tools) → Observe → Repeat
"""

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import 
from langgraph.prebuilt import create_react_agent
<<<<<<< HEAD
from analyst_tools.tools import get_stock_data, get_technical_indicators
=======
from tools.analyst_tools import get_stock_data, get_technical_indicators
>>>>>>> 6c286e9 (upload my own trading agent)


def create_market_analyst(llm: ChatOpenAI):
    """Factory function to create a market analyst agent node.
    
    Args:
        llm: The language model to use
        
    Returns:
        A function that takes state and returns updated state
    """
    
    # Tools this agent can use
    tools = [get_stock_data, get_technical_indicators]
    
    def market_analyst_node(state):
        """Analyze market using technical indicators.
        
        This is a ReAct agent:
        1. LLM decides what tools to call
        2. Tools execute and return data
        3. LLM processes data
        4. Repeat until analysis complete
        """
        ticker = state['ticker']
        
        # Prompt for the agent
        prompt = f"""You are a technical market analyst. Analyze {ticker} using available tools.

Your analysis should cover:
1. Recent price trends (use get_stock_data for last 30 days)
2. Technical indicators (use get_technical_indicators for RSI, SMA)
3. Overall technical outlook: BULLISH, BEARISH, or NEUTRAL

Be concise (3-4 sentences). Focus on actionable signals.
End with a clear technical outlook statement.

Call the tools to get data first, then analyze."""
        
        # Create ReAct agent
        agent = create_react_agent(llm, tools)
        
        # Run agent
        result = agent.invoke({
            "messages": [HumanMessage(content=prompt)]
        })
        
        # Extract final analysis (last message from agent)
        analysis = result["messages"][-1].content
        
        # Return updated state
        return {
            "market_analysis": analysis,
            "messages": []  # Clear messages for next agent
        }
    
    return market_analyst_node