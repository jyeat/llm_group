"""
Technical Analysis Tools using Financial Modeling Prep (FMP) API

This module provides tools for fetching stock price data and technical indicators
using FMP instead of Alpha Vantage. FMP offers 250 API calls/day on free tier.
"""

from langchain_core.tools import tool
import requests
import pandas as pd
from datetime import datetime, timedelta
from config import FMP_API_KEY, FMP_BASE_URL, FMP_TIMEOUT


@tool
def get_stock_data(ticker: str, date: str = None, days: int = 30) -> str:
    """Get recent stock price data (OHLCV) from Financial Modeling Prep.

    This tool fetches historical price data for technical analysis.

    Args:
        ticker: Stock symbol (e.g., "AAPL")
        date: Current date (optional, not used in this implementation)
        days: Number of days of history (default 30)

    Returns:
        str: Formatted string of recent stock data and key statistics
    """
    try:
        # FMP v4 API endpoint for historical prices (v3 is deprecated)
        url = f"https://financialmodelingprep.com/api/v4/historical-price/{ticker}"
        params = {
            "apikey": FMP_API_KEY
        }

        response = requests.get(url, params=params, timeout=FMP_TIMEOUT)
        data = response.json()

        # Check for errors
        if isinstance(data, dict) and "Error Message" in data:
            return f"Error fetching data for {ticker}: {data['Error Message']}"

        if not data or not isinstance(data, list):
            return f"No historical data found for {ticker}."

        # Convert to DataFrame (v4 returns list directly)
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date', ascending=False).head(days)

        # Calculate key statistics
        current_price = df['close'].iloc[0]
        high = df['high'].max()
        low = df['low'].min()
        avg_volume = df['volume'].mean()
        start_price = df['close'].iloc[-1]
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

    except requests.exceptions.Timeout:
        return f"Error: Request timeout for {ticker}."
    except Exception as e:
        return f"Error fetching stock data for {ticker}: {str(e)}"


@tool
def get_technical_indicators(ticker: str) -> str:
    """Get technical indicators (RSI, SMA) from Financial Modeling Prep.

    This tool provides key technical analysis indicators.

    Args:
        ticker: Stock symbol

    Returns:
        str: Formatted string with technical indicators
    """
    try:
        indicators = {}

        # 1. Get RSI (14-day)
        url_rsi = f"{FMP_BASE_URL}/technical_indicator/daily/{ticker}"
        params_rsi = {
            "period": 14,
            "type": "rsi",
            "apikey": FMP_API_KEY
        }

        response_rsi = requests.get(url_rsi, params=params_rsi, timeout=FMP_TIMEOUT)
        data_rsi = response_rsi.json()

        if data_rsi and isinstance(data_rsi, list) and len(data_rsi) > 0:
            rsi_value = data_rsi[0].get('rsi')
            if rsi_value:
                indicators['RSI'] = float(rsi_value)

        # 2. Get SMA (50-day)
        url_sma = f"{FMP_BASE_URL}/technical_indicator/daily/{ticker}"
        params_sma = {
            "period": 50,
            "type": "sma",
            "apikey": FMP_API_KEY
        }

        response_sma = requests.get(url_sma, params=params_sma, timeout=FMP_TIMEOUT)
        data_sma = response_sma.json()

        if data_sma and isinstance(data_sma, list) and len(data_sma) > 0:
            sma_value = data_sma[0].get('sma')
            if sma_value:
                indicators['SMA_50'] = float(sma_value)

        # 3. Get current price (from quote)
        url_quote = f"{FMP_BASE_URL}/quote/{ticker}"
        params_quote = {
            "apikey": FMP_API_KEY
        }

        response_quote = requests.get(url_quote, params=params_quote, timeout=FMP_TIMEOUT)
        data_quote = response_quote.json()

        current_price = 0
        if data_quote and isinstance(data_quote, list) and len(data_quote) > 0:
            current_price = data_quote[0].get('price', 0)

        # Format output
        output = f"""
Technical Indicators for {ticker}:
"""

        if 'RSI' in indicators:
            rsi = indicators['RSI']
            rsi_signal = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
            output += f"RSI (14-day): {rsi:.2f} - {rsi_signal}\n"

        if 'SMA_50' in indicators and current_price > 0:
            sma = indicators['SMA_50']
            position = "Above" if current_price > sma else "Below"
            output += f"50-day SMA: ${sma:.2f}\n"
            output += f"Current Price: ${current_price:.2f} ({position} SMA)\n"
            output += f"Signal: {'Bullish ↑' if current_price > sma else 'Bearish ↓'}\n"

        if not indicators:
            output += "Unable to fetch technical indicators. API may be rate-limited.\n"

        return output.strip()

    except Exception as e:
        return f"Error calculating indicators: {str(e)}"
