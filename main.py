"""
Simplified Trading Agents - Main Entry Point

This script demonstrates how to use the simplified trading agents system
to analyze stocks and get risk-tiered investment recommendations.

Usage:
    python main.py                          # Run with default example (AAPL)
    python main.py --ticker MSFT            # Analyze specific ticker
    python main.py --ticker NVDA --debug    # Run with debug output
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to Python path so we can import simplified_tradingagents
sys.path.insert(0, str(Path(__file__).parent.parent))

from trading_graph import create_trading_graph
from langsmith_config import setup_langsmith

# Load environment variables from .env file
load_dotenv()

# Setup LangSmith tracing (optional - will skip if not configured)
setup_langsmith()


def print_section(title: str, content: str = None, width: int = 80):
    """Print a formatted section header."""
    print("\n" + "=" * width)
    print(f" {title.center(width - 2)} ")
    print("=" * width)
    if content:
        print(content)


def print_analysis_summary(result: dict):
    """Print a formatted summary of the analysis results."""

    print_section("TRADING ANALYSIS SUMMARY")

    print(f"\nTicker: {result['ticker']}")
    print(f"Date: {result['date']}")
    print(f"Final Decision: {result['decision'].upper()}")
    print(f"Confidence: {result['confidence']:.2%}")

    # Parse JSON results
    try:
        news_analysis = json.loads(result.get('news_analysis', '{}'))
        market_analysis = json.loads(result['market_analysis'])
        fundamental_analysis = json.loads(result['fundamental_analysis'])
        bull_argument = json.loads(result['bull_argument'])
        bear_argument = json.loads(result['bear_argument'])

        # News Analysis Summary
        print_section("NEWS ANALYSIS", width=80)
        print(f"Overall Sentiment: {str(news_analysis.get('overall_sentiment', 'N/A')).upper()}")
        print(f"Confidence: {news_analysis.get('confidence_score', 0):.2%}")
        print(f"Summary: {news_analysis.get('analysis_summary', 'N/A')}")

        # Market Analysis Summary
        print_section("MARKET ANALYSIS (Technical)", width=80)
        print(f"Market Sentiment: {market_analysis.get('market_sentiment', 'N/A').upper()}")
        print(f"Confidence: {market_analysis.get('confidence_score', 0):.2%}")
        print(f"Summary: {market_analysis.get('analysis_summary', 'N/A')}")

        # Fundamental Analysis Summary
        print_section("FUNDAMENTAL ANALYSIS (Financial)", width=80)
        fundamental_rating = fundamental_analysis.get('fundamental_rating', 'N/A')
        print(f"Fundamental Rating: {fundamental_rating.upper().replace('_', ' ')}")
        print(f"Confidence: {fundamental_analysis.get('confidence_score', 0):.2%}")
        print(f"Summary: {fundamental_analysis.get('analysis_summary', 'N/A')}")

        # Valuation
        valuation = fundamental_analysis.get('valuation', {})
        print(f"\nValuation Verdict: {valuation.get('valuation_verdict', 'N/A').upper()}")

        # Financial Health
        health = fundamental_analysis.get('financial_health', {})
        print(f"Financial Health: {health.get('overall_health', 'N/A').upper()}")
        print(f"  - Liquidity Score: {health.get('liquidity_score', 0)}/10")
        print(f"  - Leverage Score: {health.get('leverage_score', 0)}/10")
        print(f"  - Profitability Score: {health.get('profitability_score', 0)}/10")
        print(f"  - Cash Flow Score: {health.get('cash_flow_score', 0)}/10")

        # Bull vs Bear
        print_section("DEBATE RESULTS", width=80)

        bull_conviction = bull_argument.get('conviction_score', 0)
        bear_conviction = bear_argument.get('conviction_score', 0)

        print(f"\nBull Case Conviction: {bull_conviction:.2%}")
        print(f"Bull Recommendation: {bull_argument.get('recommended_action', 'N/A').upper().replace('_', ' ')}")
        print(f"Bull Summary: {bull_argument.get('thesis_summary', 'N/A')}")

        print(f"\nBear Case Conviction: {bear_conviction:.2%}")
        print(f"Bear Recommendation: {bear_argument.get('recommended_action', 'N/A').upper().replace('_', ' ')}")
        print(f"Bear Summary: {bear_argument.get('thesis_summary', 'N/A')}")

        # Final Recommendation
        print_section("FINAL RECOMMENDATION", width=80)
        print(f"\n{result['rationale']}")

        # Risk-Tiered Recommendations (from supervisor_decision)
        if 'supervisor_decision' in result and result['supervisor_decision']:
            try:
                supervisor = json.loads(result['supervisor_decision'])

                print_section("RISK-TIERED RECOMMENDATIONS", width=80)

                # Low Risk
                low_risk = supervisor.get('low_risk_recommendation', {})
                print(f"\n🛡️  LOW RISK (Conservative Investors):")
                print(f"  Action: {low_risk.get('action', 'N/A').upper().replace('_', ' ')}")
                print(f"  Position Size: {low_risk.get('position_size', 'N/A').upper()}")
                print(f"  Entry Strategy: {low_risk.get('entry_strategy', 'N/A')}")
                if low_risk.get('stop_loss'):
                    print(f"  Stop Loss: {low_risk.get('stop_loss')}")
                print(f"  Rationale: {low_risk.get('rationale', 'N/A')}")

                # Medium Risk
                medium_risk = supervisor.get('medium_risk_recommendation', {})
                print(f"\n⚖️  MEDIUM RISK (Balanced Investors):")
                print(f"  Action: {medium_risk.get('action', 'N/A').upper().replace('_', ' ')}")
                print(f"  Position Size: {medium_risk.get('position_size', 'N/A').upper()}")
                print(f"  Entry Strategy: {medium_risk.get('entry_strategy', 'N/A')}")
                if medium_risk.get('stop_loss'):
                    print(f"  Stop Loss: {medium_risk.get('stop_loss')}")
                print(f"  Rationale: {medium_risk.get('rationale', 'N/A')}")

                # High Risk
                high_risk = supervisor.get('high_risk_recommendation', {})
                print(f"\n🚀 HIGH RISK (Aggressive Traders):")
                print(f"  Action: {high_risk.get('action', 'N/A').upper().replace('_', ' ')}")
                print(f"  Position Size: {high_risk.get('position_size', 'N/A').upper()}")
                print(f"  Entry Strategy: {high_risk.get('entry_strategy', 'N/A')}")
                if high_risk.get('stop_loss'):
                    print(f"  Stop Loss: {high_risk.get('stop_loss')}")
                print(f"  Rationale: {high_risk.get('rationale', 'N/A')}")

                # Additional supervisor insights
                print(f"\n📊 Bull vs Bear Strength:")
                print(f"  Bull Case Strength: {supervisor.get('bull_case_strength', 0)}/10")
                print(f"  Bear Case Strength: {supervisor.get('bear_case_strength', 0)}/10")

            except json.JSONDecodeError:
                print("\n⚠️  Could not parse supervisor decision")

    except json.JSONDecodeError as e:
        print(f"\nWarning: Could not parse some analysis results: {e}")
        print(f"\nRaw rationale: {result.get('rationale', 'N/A')}")


def print_detailed_results(result: dict):
    """Print detailed JSON results for all analyses."""

    print_section("DETAILED RESULTS (JSON)", width=80)

    sections = [
        ("NEWS ANALYSIS", result.get('news_analysis', '{}')),
        ("MARKET ANALYSIS", result['market_analysis']),
        ("FUNDAMENTAL ANALYSIS", result['fundamental_analysis']),
        ("BULL ARGUMENT", result['bull_argument']),
        ("BEAR ARGUMENT", result['bear_argument'])
    ]

    for title, data in sections:
        print(f"\n{title}:")
        print("-" * 80)
        try:
            parsed = json.loads(data)
            print(json.dumps(parsed, indent=2))
        except json.JSONDecodeError:
            print(data)


def main():
    """Main entry point for the simplified trading agents system."""

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Simplified Trading Agents - Multi-Agent Stock Analysis System"
    )
    parser.add_argument(
        "--ticker",
        type=str,
        default="AAPL",
        help="Stock ticker symbol to analyze (default: AAPL)"
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Analysis date in YYYY-MM-DD format (default: today)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with step-by-step output"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Print detailed JSON results for all analyses"
    )

    args = parser.parse_args()

    # Use today's date if not specified
    analysis_date = args.date or datetime.now().strftime("%Y-%m-%d")

    # Print header
    print_section("SIMPLIFIED TRADING AGENTS SYSTEM", width=80)
    print(f"\nAnalyzing: {args.ticker}")
    print(f"Date: {analysis_date}")
    print(f"Debug Mode: {'ON' if args.debug else 'OFF'}")

    # Create the trading graph
    print("\nInitializing trading agents...")
    graph = create_trading_graph(debug=args.debug)

    # Run the analysis
    print(f"\nStarting analysis pipeline for {args.ticker}...")
    print("This will:")
    print("  1. Fetch and analyze market/technical data")
    print("  2. Fetch and analyze fundamental/financial data")
    print("  3. Build bullish case")
    print("  4. Build bearish case")
    print("  5. Generate risk-tiered recommendations")
    print("\nPlease wait...\n")

    try:
        result = graph.analyze(ticker=args.ticker, date=analysis_date)

        # Print results
        print_analysis_summary(result)

        if args.detailed:
            print_detailed_results(result)

        print_section("ANALYSIS COMPLETE", width=80)
        print(f"\nFinal Decision: {result['decision'].upper()}")
        print(f"Confidence: {result['confidence']:.2%}")

        # Save results to file (exclude messages field which contains non-serializable objects)
        output_file = f"analysis_{args.ticker}_{analysis_date}.json"
        result_to_save = {k: v for k, v in result.items() if k != 'messages'}
        with open(output_file, 'w') as f:
            json.dump(result_to_save, f, indent=2)
        print(f"\nDetailed results saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())