"""
LangSmith Configuration and Setup
Enables tracing and monitoring for the Trading Agents system
"""
import os
from typing import Optional

def setup_langsmith() -> bool:
    """
    Configure LangSmith tracing if API key is available.

    Returns:
        bool: True if LangSmith is enabled, False otherwise
    """
    langsmith_api_key = os.getenv("LANGCHAIN_API_KEY")

    if not langsmith_api_key:
        print("[WARNING] LangSmith API key not found. Tracing disabled.")
        print("   To enable LangSmith tracing:")
        print("   1. Sign up at https://smith.langchain.com/")
        print("   2. Get your API key from Settings > API Keys")
        print("   3. Add to .env: LANGCHAIN_API_KEY=your_key_here")
        return False

    # Set environment variables for LangSmith
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = os.getenv(
        "LANGCHAIN_ENDPOINT",
        "https://api.smith.langchain.com"
    )
    os.environ["LANGCHAIN_PROJECT"] = os.getenv(
        "LANGCHAIN_PROJECT",
        "trading-agents"
    )

    print("[SUCCESS] LangSmith tracing enabled")
    print(f"   Project: {os.environ['LANGCHAIN_PROJECT']}")
    print(f"   Dashboard: https://smith.langchain.com/o/{get_org_id()}/projects/p/{os.environ['LANGCHAIN_PROJECT']}")

    return True


def get_org_id() -> str:
    """
    Get organization ID for LangSmith URL.

    Returns:
        str: Organization ID or placeholder
    """
    # This will be set automatically when you log in
    # For now, return a generic placeholder
    return "your-org"


def get_trace_url(run_id: Optional[str] = None) -> str:
    """
    Get the LangSmith trace URL for a specific run.

    Args:
        run_id: The run ID from LangSmith

    Returns:
        str: URL to view the trace
    """
    project = os.getenv("LANGCHAIN_PROJECT", "trading-agents")
    if run_id:
        return f"https://smith.langchain.com/o/{get_org_id()}/projects/p/{project}/r/{run_id}"
    return f"https://smith.langchain.com/o/{get_org_id()}/projects/p/{project}"


def log_analysis_metadata(ticker: str, date: str, decision: str) -> dict:
    """
    Create metadata for LangSmith logging.

    Args:
        ticker: Stock ticker symbol
        date: Analysis date
        decision: Trading decision

    Returns:
        dict: Metadata for tracing
    """
    return {
        "ticker": ticker,
        "analysis_date": date,
        "decision": decision,
        "system": "trading-agents",
        "version": "1.0"
    }
