from langchain_core.tools import tool
import requests
import pandas as pd
<<<<<<< HEAD
from simplified_tradingagents.config import ALPHA_VANTAGE_API_KEY, AV_BASE_URL, AV_TIMEOUT
=======
from config import ALPHA_VANTAGE_API_KEY, AV_BASE_URL, AV_TIMEOUT
>>>>>>> 6c286e9 (upload my own trading agent)
from langchain_google_genai import ChatGoogleGenerativeAI


#main changes
#1. Clear use of Alpha Vantage clearer stock data fetching. 
#2. Tools to get stock data, technical indicators, and then fundamental data. 
#3. Original version has a better route to vendor that allow more flexibility and scalability as vendor might change route. 
#4. Original allow dynamic indicator. The current version hard coded from Alpha Vantage, and specify indicators to take. 

@tool
def get_stock_data(ticker: str, date: str = None, days: int = 30) -> str:
    """Get recent stock price data (OHLCV) from Alpha Vantage.

    This tools fetches historical price data for technical analysis

    Args:
        ticker: Stock Symbol
        date: Current date (optional, not used in this implementation)
        days: Number of days of history (default 30)

    Returns:
        str: Formatted string of recent stock data and key statistics
    """
    try:
        #Call Alpha Vantage TIME_SERIES_DAILY
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "apikey": ALPHA_VANTAGE_API_KEY,
            "outputsize": "compact"
        }
        response = requests.get(AV_BASE_URL, params=params, timeout=AV_TIMEOUT)
        data=response.json()

        #check for errors
        if "Error Message" in data:
            return f"Error fetching data for {ticker}: {data['Error Message']}" 
        if "Note" in data:
            return f"API call frequency exceeded: {data['Note']}"
        
        #Extract time series data
        time_series=data.get("Time Series (Daily)",{})
        if not time_series:
            return f"No time series data found for {ticker}."
        
        #Convert to DataFrame
        df=pd.DataFrame.from_dict(time_series, orient='index')
        df.columns=['Open','High','Low','Close','Volume']
        df.index=pd.to_datetime(df.index)
        df=df.astype(float)
        df=df.sort_index(ascending=False).head(days)

        #Calculate key statistics
        current_price=df['Close'].iloc[0]
        high=df['High'].max()
        low=df['Low'].min()
        avg_volume=df['Volume'].mean()
        start_price=df['Close'].iloc[-1]
        price_change=((current_price - start_price)/start_price)*100

        summary=f"""
Stock Data for {ticker} (Last {days} days):
Current Price: ${current_price:.2f}
52-Week High: ${high:.2f}
52-Week Low: ${low:.2f}
Average Volume: {avg_volume:,.0f}
Price Change over Period: {price_change:.2f}%
Trend: {"Bullish ↑" if price_change > 0 else "Bearish ↓" if price_change < 0 else "Neutral →"}
        """
        return summary.strip()
    
    except requests.exceptions.Timeout:
        return f"Error: Request time out for {ticker}."
    except Exception as e:
        return f"Error fetching stock data for {ticker}: {str(e)}"
    

@tool
def get_technical_indicators(ticker:str) -> str:
    """Get technical indicators (RSI, MACD, SMA) from Alpha Vantage,

    This tool provides key technical analysis indicators. 

    Args:
        ticker: Stock symbol

    Returns:
        Formatted string with technical indicators. 
    """
    
    try:
        indicators={}

        #1. Get RSI (14 days)
        params_rsi={
            "function": "RSI",
            "symbol": ticker,
            "interval": "daily",
            "time_period": 14,
            "series_type": "close",
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        response_rsi=requests.get(AV_BASE_URL, params=params_rsi, timeout=AV_TIMEOUT)
        data=response.json()

        if 'Technical Analysis: RSI' in data:
            rsi_data=data['Techncial Analysis: RSI']
            latest_date=list(rsi_data.keys())[0]
            rsi_value=float(rsi_data[latest_data]['RSI'])
            indicators['RSI'] = rsi_value

        # 2. Get SMA (50-day)
        params_sma = {
            'function': 'SMA',
            'symbol': ticker,
            'interval': 'daily',
            'time_period': 50,
            'series_type': 'close',
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        response = requests.get(AV_BASE_URL, params=params_sma, timeout=AV_TIMEOUT)
        data = response.json()
        
        if 'Technical Analysis: SMA' in data:
            sma_data = data['Technical Analysis: SMA']
            latest_date = list(sma_data.keys())[0]
            sma_value = float(sma_data[latest_date]['SMA'])
            indicators['SMA_50'] = sma_value
        
        # 3. Get current price for comparison
        params_price = {
            'function': 'GLOBAL_QUOTE',
            'symbol': ticker,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        response = requests.get(AV_BASE_URL, params=params_price, timeout=AV_TIMEOUT)
        data = response.json()
        
        current_price = 0
        if 'Global Quote' in data and '05. price' in data['Global Quote']:
            current_price = float(data['Global Quote']['05. price'])
        
        # Format output
        output = f"""
Technical Indicators for {ticker}:
"""
        
        if 'RSI' in indicators:
            rsi = indicators['RSI']
            rsi_signal = "Oversold 📉" if rsi < 30 else "Overbought 📈" if rsi > 70 else "Neutral ➡️"
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
    
#tool list
ANALYST_TOOLS=[get_stock_data, get_technical_indicators]

