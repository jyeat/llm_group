from typing import TypedDict, List, Literal
from langchain_core.messages import BaseMessage


#Rationale for this design. 

#1. Original deeplly nested state can be a debugging nightmare. 
#2. Using BaseMessage instead of MessageState. Have many history in the original design. 
#3. Original version use state to represent workflow. It might not be effective.  
#4. This is a version to use nodes and edges to represent workflow. 

class TradingState(TypedDict):
    """Simplified trading state that flows through the graph. A shared whiteboard for all agents"""

    #input
    ticker: str
    date: str

    #react tool calling
    messages: List[BaseMessage]

    #output (phase 1 Analyst)
    market_analysis: str
    fundamental_analysis: str

    #debate output (phase 2 Debators)
    bull_argument: str
    bear_argument: str

    #final decision (phase 3 Supervisor)
    decision: Literal["bullish", "bearish", "neutral", "mixed"]
    rationale: str
    confidence: float #0 to 1 scale
    supervisor_decision: str  # Full supervisor JSON with risk-tiered recommendations
