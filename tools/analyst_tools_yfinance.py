"""
Technical Analysis Tools using Yahoo Finance (yfinance)

This module provides tools for fetching stock price data and technical indicators
using yfinance - completely FREE with no API key required!
"""

from langchain_core.tools import tool
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


@tool
def get_stock_data(ticker: str, date: str = None, days: int = 30) -> str:
    """Get recent stock price data (OHLCV) from Yahoo Finance.

    This tool fetches historical price data for technical analysis.
    Completely FREE - no API key required!

    Args:
        ticker: Stock symbol (e.g., "AAPL")
        date: Current date (optional, not used in this implementation)
        days: Number of days of history (default 30)

    Returns:
        str: Formatted string of recent stock data and key statistics
    """
    try:
        # Get stock data from yfinance
        stock = yf.Ticker(ticker)

        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 10)  # Extra buffer

        df = stock.history(start=start_date, end=end_date)

        if df.empty:
            return f"No historical data found for {ticker}."

        # Get last N days
        df = df.tail(days)

        # Calculate key statistics
        current_price = df['Close'].iloc[-1]
        high = df['High'].max()
        low = df['Low'].min()
        avg_volume = df['Volume'].mean()
        start_price = df['Close'].iloc[0]
        price_change = ((current_price - start_price) / start_price) * 100

        summary = f"""
Stock Data for {ticker} (Last {days} days):
Current Price: ${current_price:.2f}
Period High: ${high:.2f}
Period Low: ${low:.2f}
Average Volume: {avg_volume:,.0f}
Price Change over Period: {price_change:.2f}%
Trend: {"Bullish ↑" if price_change > 0 else "Bearish ↓" if price_change < 0 else "Neutral →"}
        """
        return summary.strip()

    except Exception as e:
        return f"Error fetching stock data for {ticker}: {str(e)}"


@tool
def get_technical_indicators(ticker: str) -> str:
    """Get technical indicators (RSI, SMA) calculated from Yahoo Finance data.

    This tool provides key technical analysis indicators.
    Completely FREE - no API key required!

    Args:
        ticker: Stock symbol

    Returns:
        str: Formatted string with technical indicators
    """
    try:
        # Get stock data
        stock = yf.Ticker(ticker)

        # Get 6 months of data for indicators
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)
        df = stock.history(start=start_date, end=end_date)

        if df.empty:
            return f"No data available to calculate indicators for {ticker}"

        indicators = {}

        # Calculate RSI (14-day)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        if not rsi.empty and not pd.isna(rsi.iloc[-1]):
            indicators['RSI'] = rsi.iloc[-1]

        # Calculate SMA (50-day)
        sma_50 = df['Close'].rolling(window=50).mean()
        if not sma_50.empty and not pd.isna(sma_50.iloc[-1]):
            indicators['SMA_50'] = sma_50.iloc[-1]

        # Get current price
        current_price = df['Close'].iloc[-1]

        # Format output
        output = f"""
Technical Indicators for {ticker}:
"""

        if 'RSI' in indicators:
            rsi_val = indicators['RSI']
            rsi_signal = "Oversold" if rsi_val < 30 else "Overbought" if rsi_val > 70 else "Neutral"
            output += f"RSI (14-day): {rsi_val:.2f} - {rsi_signal}\n"

        if 'SMA_50' in indicators:
            sma = indicators['SMA_50']
            position = "Above" if current_price > sma else "Below"
            output += f"50-day SMA: ${sma:.2f}\n"
            output += f"Current Price: ${current_price:.2f} ({position} SMA)\n"
            output += f"Signal: {'Bullish ↑' if current_price > sma else 'Bearish ↓'}\n"

        if not indicators:
            output += "Unable to calculate technical indicators.\n"

        return output.strip()

    except Exception as e:
        return f"Error calculating indicators for {ticker}: {str(e)}"
