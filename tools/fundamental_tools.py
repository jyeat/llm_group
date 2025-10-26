@tool
def get_fundamentals(ticker:str) ->str:
    """Get fundamental financial data from Alpha Vantage.
    
    This tool provides company overview and key financial metrics.

    Arg:
        ticker:Stock symbol

    Returns:
        Formatted string with fundamental data
    """

    try:
        # Get company overview
        params = {
            'function': 'OVERVIEW',
            'symbol': ticker,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(AV_BASE_URL, params=params, timeout=AV_TIMEOUT)
        data = response.json()
        
        if not data or 'Symbol' not in data:
            return f"No fundamental data available for {ticker}"
        
        # Extract key metrics
        name = data.get('Name', 'N/A')
        sector = data.get('Sector', 'N/A')
        pe_ratio = data.get('PERatio', 'N/A')
        peg_ratio = data.get('PEGRatio', 'N/A')
        price_to_book = data.get('PriceToBookRatio', 'N/A')
        debt_to_equity = data.get('DebtToEquity', 'N/A')
        profit_margin = data.get('ProfitMargin', 'N/A')
        roe = data.get('ReturnOnEquityTTM', 'N/A')
        revenue_growth = data.get('QuarterlyRevenueGrowthYOY', 'N/A')
        market_cap = data.get('MarketCapitalization', 'N/A')
        
        # Format market cap
        if market_cap != 'N/A':
            market_cap = f"${int(market_cap):,}"
        
        # Convert percentages
        if profit_margin != 'N/A':
            profit_margin = f"{float(profit_margin)*100:.2f}%"
        if roe != 'N/A':
            roe = f"{float(roe)*100:.2f}%"
        if revenue_growth != 'N/A':
            revenue_growth = f"{float(revenue_growth)*100:.2f}%"
        
        output = f"""
Fundamental Data for {ticker}:
Company: {name}
Sector: {sector}
Market Cap: {market_cap}

Valuation Metrics:
P/E Ratio: {pe_ratio}
PEG Ratio: {peg_ratio}
Price/Book: {price_to_book}

Financial Health:
Debt/Equity: {debt_to_equity}
Profit Margin: {profit_margin}
ROE: {roe}

Growth:
Revenue Growth (QoQ): {revenue_growth}
"""
        return output.strip()
        
    except Exception as e:
        return f"Error fetching fundamentals: {str(e)}"


#tool list
FUNDAMENTAL_TOOLS=[get_fundamentals]