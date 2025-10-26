"""
Fundamental Analysis Tools using Financial Modeling Prep (FMP) API

This module provides tools for fetching financial statements and fundamental data
using FMP instead of Alpha Vantage. FMP offers 250 API calls/day on free tier.
"""

from langchain_core.tools import tool
import requests
from config import FMP_API_KEY, FMP_BASE_URL, FMP_TIMEOUT


@tool
def get_company_overview(ticker: str) -> str:
    """Get company overview and valuation metrics from FMP.

    This tool provides company profile, sector information, and key valuation ratios.

    Args:
        ticker: Stock symbol

    Returns:
        str: Formatted string with company overview and valuation metrics
    """
    try:
        # Get company profile
        url_profile = f"{FMP_BASE_URL}/profile/{ticker}"
        params = {"apikey": FMP_API_KEY}

        response = requests.get(url_profile, params=params, timeout=FMP_TIMEOUT)
        data = response.json()

        if not data or (isinstance(data, list) and len(data) == 0):
            return f"No company overview data available for {ticker}"

        # FMP returns list with one item
        profile = data[0] if isinstance(data, list) else data

        # Extract company profile
        name = profile.get('companyName', 'N/A')
        sector = profile.get('sector', 'N/A')
        industry = profile.get('industry', 'N/A')
        description = profile.get('description', 'N/A')
        market_cap = profile.get('mktCap', 'N/A')

        # Valuation metrics (some from profile, some need ratios endpoint)
        pe_ratio = profile.get('pe', 'N/A')
        price_to_book = profile.get('priceToBook', 'N/A')
        beta = profile.get('beta', 'N/A')
        dividend_yield = profile.get('lastDiv', 'N/A')
        week_52_high = profile.get('range', 'N/A')  # Returns range string

        # Get additional ratios
        url_ratios = f"{FMP_BASE_URL}/ratios-ttm/{ticker}"
        response_ratios = requests.get(url_ratios, params=params, timeout=FMP_TIMEOUT)
        ratios_data = response_ratios.json()

        peg_ratio = 'N/A'
        price_to_sales = 'N/A'
        if ratios_data and isinstance(ratios_data, list) and len(ratios_data) > 0:
            ratios = ratios_data[0]
            peg_ratio = ratios.get('pegRatioTTM', 'N/A')
            price_to_sales = ratios.get('priceToSalesRatioTTM', 'N/A')

        # Format market cap
        if market_cap != 'N/A' and market_cap:
            try:
                market_cap = f"${int(market_cap):,}"
            except:
                pass

        # Format dividend yield
        if dividend_yield != 'N/A' and dividend_yield:
            try:
                dividend_yield = f"{float(dividend_yield):.2f}%"
            except:
                pass

        output = f"""
Company Overview for {ticker}:

Company Profile:
Name: {name}
Sector: {sector}
Industry: {industry}
Market Cap: {market_cap}

Valuation Metrics:
P/E Ratio: {pe_ratio}
PEG Ratio: {peg_ratio}
Price/Book: {price_to_book}
Price/Sales (TTM): {price_to_sales}

Market Metrics:
Beta: {beta}
Dividend Yield: {dividend_yield}
52-Week Range: {week_52_high}

Description: {description[:200]}...
"""
        return output.strip()

    except Exception as e:
        return f"Error fetching company overview for {ticker}: {str(e)}"


@tool
def get_balance_sheet(ticker: str, period: str = 'quarter') -> str:
    """Get balance sheet data from FMP.

    This tool provides financial position including assets, liabilities, and equity.

    Args:
        ticker: Stock symbol
        period: 'quarter' or 'annual' (default: 'quarter')

    Returns:
        str: Formatted string with balance sheet data for recent periods
    """
    try:
        url = f"{FMP_BASE_URL}/balance-sheet-statement/{ticker}"
        params = {
            "period": period,
            "limit": 4,  # Get last 4 periods
            "apikey": FMP_API_KEY
        }

        response = requests.get(url, params=params, timeout=FMP_TIMEOUT)
        data = response.json()

        if not data or not isinstance(data, list):
            return f"No balance sheet data available for {ticker}"

        output = f"Balance Sheet for {ticker} ({period.capitalize()}):\n\n"

        for i, report in enumerate(data):
            fiscal_date = report.get('date', 'N/A')

            # Assets
            total_assets = report.get('totalAssets', 'N/A')
            current_assets = report.get('totalCurrentAssets', 'N/A')
            cash = report.get('cashAndCashEquivalents', 'N/A')

            # Liabilities
            total_liabilities = report.get('totalLiabilities', 'N/A')
            current_liabilities = report.get('totalCurrentLiabilities', 'N/A')
            long_term_debt = report.get('longTermDebt', 'N/A')

            # Equity
            shareholder_equity = report.get('totalStockholdersEquity', 'N/A')

            # Format numbers
            def format_number(val):
                if val == 'N/A' or val is None:
                    return 'N/A'
                try:
                    return f"${int(val):,}"
                except:
                    return val

            output += f"""
Period Ending: {fiscal_date}
---
Assets:
  Total Assets: {format_number(total_assets)}
  Current Assets: {format_number(current_assets)}
  Cash & Equivalents: {format_number(cash)}

Liabilities:
  Total Liabilities: {format_number(total_liabilities)}
  Current Liabilities: {format_number(current_liabilities)}
  Long-term Debt: {format_number(long_term_debt)}

Equity:
  Shareholder Equity: {format_number(shareholder_equity)}
"""

            # Calculate key ratios for most recent period
            if i == 0:
                try:
                    if current_assets != 'N/A' and current_liabilities != 'N/A' and current_liabilities != 0:
                        current_ratio = float(current_assets) / float(current_liabilities)
                        output += f"\nCurrent Ratio: {current_ratio:.2f}\n"

                    if total_liabilities != 'N/A' and shareholder_equity != 'N/A' and shareholder_equity != 0:
                        debt_to_equity = float(total_liabilities) / float(shareholder_equity)
                        output += f"Debt-to-Equity: {debt_to_equity:.2f}\n"
                except:
                    pass

            output += "\n"

        return output.strip()

    except Exception as e:
        return f"Error fetching balance sheet for {ticker}: {str(e)}"


@tool
def get_income_statement(ticker: str, period: str = 'quarter') -> str:
    """Get income statement data from FMP.

    This tool provides profitability data including revenue, expenses, and net income.

    Args:
        ticker: Stock symbol
        period: 'quarter' or 'annual' (default: 'quarter')

    Returns:
        str: Formatted string with income statement data for recent periods
    """
    try:
        url = f"{FMP_BASE_URL}/income-statement/{ticker}"
        params = {
            "period": period,
            "limit": 4,  # Get last 4 periods
            "apikey": FMP_API_KEY
        }

        response = requests.get(url, params=params, timeout=FMP_TIMEOUT)
        data = response.json()

        if not data or not isinstance(data, list):
            return f"No income statement data available for {ticker}"

        output = f"Income Statement for {ticker} ({period.capitalize()}):\n\n"

        for i, report in enumerate(data):
            fiscal_date = report.get('date', 'N/A')

            # Revenue and income
            total_revenue = report.get('revenue', 'N/A')
            gross_profit = report.get('grossProfit', 'N/A')
            operating_income = report.get('operatingIncome', 'N/A')
            ebitda = report.get('ebitda', 'N/A')
            net_income = report.get('netIncome', 'N/A')

            # Per share metrics
            eps = report.get('eps', 'N/A')
            eps_diluted = report.get('epsdiluted', 'N/A')

            # Expenses
            cost_of_revenue = report.get('costOfRevenue', 'N/A')
            operating_expenses = report.get('operatingExpenses', 'N/A')
            rd_expenses = report.get('researchAndDevelopmentExpenses', 'N/A')

            # Format numbers
            def format_number(val):
                if val == 'N/A' or val is None:
                    return 'N/A'
                try:
                    return f"${int(val):,}"
                except:
                    return val

            output += f"""
Period Ending: {fiscal_date}
---
Revenue:
  Total Revenue: {format_number(total_revenue)}
  Cost of Revenue: {format_number(cost_of_revenue)}
  Gross Profit: {format_number(gross_profit)}

Operating Performance:
  Operating Expenses: {format_number(operating_expenses)}
  R&D Expenses: {format_number(rd_expenses)}
  Operating Income: {format_number(operating_income)}
  EBITDA: {format_number(ebitda)}

Bottom Line:
  Net Income: {format_number(net_income)}
  EPS (Basic): {eps}
  EPS (Diluted): {eps_diluted}
"""

            # Calculate margins for most recent period
            if i == 0:
                try:
                    if gross_profit != 'N/A' and total_revenue != 'N/A' and total_revenue != 0:
                        gross_margin = (float(gross_profit) / float(total_revenue)) * 100
                        output += f"\nGross Margin: {gross_margin:.2f}%\n"

                    if operating_income != 'N/A' and total_revenue != 'N/A' and total_revenue != 0:
                        operating_margin = (float(operating_income) / float(total_revenue)) * 100
                        output += f"Operating Margin: {operating_margin:.2f}%\n"

                    if net_income != 'N/A' and total_revenue != 'N/A' and total_revenue != 0:
                        net_margin = (float(net_income) / float(total_revenue)) * 100
                        output += f"Net Margin: {net_margin:.2f}%\n"
                except:
                    pass

            output += "\n"

        return output.strip()

    except Exception as e:
        return f"Error fetching income statement for {ticker}: {str(e)}"


@tool
def get_cash_flow(ticker: str, period: str = 'quarter') -> str:
    """Get cash flow statement data from FMP.

    This tool provides cash flow from operating, investing, and financing activities.

    Args:
        ticker: Stock symbol
        period: 'quarter' or 'annual' (default: 'quarter')

    Returns:
        str: Formatted string with cash flow data for recent periods
    """
    try:
        url = f"{FMP_BASE_URL}/cash-flow-statement/{ticker}"
        params = {
            "period": period,
            "limit": 4,  # Get last 4 periods
            "apikey": FMP_API_KEY
        }

        response = requests.get(url, params=params, timeout=FMP_TIMEOUT)
        data = response.json()

        if not data or not isinstance(data, list):
            return f"No cash flow data available for {ticker}"

        output = f"Cash Flow Statement for {ticker} ({period.capitalize()}):\n\n"

        for i, report in enumerate(data):
            fiscal_date = report.get('date', 'N/A')

            # Operating activities
            operating_cashflow = report.get('operatingCashFlow', 'N/A')

            # Investing activities
            capex = report.get('capitalExpenditure', 'N/A')
            cashflow_from_investment = report.get('netCashUsedForInvestingActivites', 'N/A')

            # Financing activities
            cashflow_from_financing = report.get('netCashUsedProvidedByFinancingActivities', 'N/A')
            dividend_payout = report.get('dividendsPaid', 'N/A')

            # Net change
            net_change_in_cash = report.get('netChangeInCash', 'N/A')
            free_cashflow = report.get('freeCashFlow', 'N/A')

            # Format numbers
            def format_number(val):
                if val == 'N/A' or val is None:
                    return 'N/A'
                try:
                    return f"${int(val):,}"
                except:
                    return val

            output += f"""
Period Ending: {fiscal_date}
---
Operating Activities:
  Operating Cash Flow: {format_number(operating_cashflow)}

Investing Activities:
  Cash Flow from Investment: {format_number(cashflow_from_investment)}
  Capital Expenditures: {format_number(capex)}

Financing Activities:
  Cash Flow from Financing: {format_number(cashflow_from_financing)}
  Dividend Payout: {format_number(dividend_payout)}

Net Change & Free Cash Flow:
  Change in Cash: {format_number(net_change_in_cash)}
  Free Cash Flow: {format_number(free_cashflow)}
"""

            output += "\n"

        return output.strip()

    except Exception as e:
        return f"Error fetching cash flow for {ticker}: {str(e)}"


@tool
def get_earnings(ticker: str) -> str:
    """Get earnings history and EPS data from FMP.

    This tool provides quarterly and annual earnings, including EPS surprises.

    Args:
        ticker: Stock symbol

    Returns:
        str: Formatted string with earnings history and surprises
    """
    try:
        output = f"Earnings Data for {ticker}:\n\n"

        # Get earnings surprises (quarterly)
        url_surprises = f"{FMP_BASE_URL}/earnings-surprises/{ticker}"
        params = {"apikey": FMP_API_KEY}

        response = requests.get(url_surprises, params=params, timeout=FMP_TIMEOUT)
        data = response.json()

        if data and isinstance(data, list):
            quarterly = data[:8]  # Last 8 quarters

            output += "Quarterly Earnings (Last 8 Quarters):\n"
            output += "---\n"

            for q in quarterly:
                date = q.get('date', 'N/A')
                actual_eps = q.get('actualEarningResult', 'N/A')
                estimated_eps = q.get('estimatedEarning', 'N/A')

                output += f"\nQuarter Ending: {date}\n"
                output += f"Actual EPS: {actual_eps}\n"
                output += f"Estimated EPS: {estimated_eps}\n"

                if actual_eps != 'N/A' and estimated_eps != 'N/A':
                    try:
                        actual = float(actual_eps)
                        estimated = float(estimated_eps)
                        surprise = actual - estimated
                        surprise_pct = (surprise / abs(estimated)) * 100 if estimated != 0 else 0
                        beat_miss = "Beat" if surprise > 0 else "Miss" if surprise < 0 else "Met"
                        output += f"Surprise: ${surprise:.2f} ({surprise_pct:.1f}%) - {beat_miss}\n"
                    except:
                        pass

        # Get historical earnings (annual)
        url_earnings = f"{FMP_BASE_URL}/income-statement/{ticker}"
        params_annual = {
            "period": "annual",
            "limit": 5,
            "apikey": FMP_API_KEY
        }

        response_annual = requests.get(url_earnings, params=params_annual, timeout=FMP_TIMEOUT)
        data_annual = response_annual.json()

        if data_annual and isinstance(data_annual, list):
            output += "\n\nAnnual Earnings (Last 5 Years):\n"
            output += "---\n"

            for a in data_annual:
                fiscal_date = a.get('date', 'N/A')
                eps = a.get('eps', 'N/A')

                output += f"\nFiscal Year Ending: {fiscal_date}\n"
                output += f"Annual EPS: {eps}\n"

        return output.strip()

    except Exception as e:
        return f"Error fetching earnings for {ticker}: {str(e)}"


# Tool list for export
FUNDAMENTAL_TOOLS = [
    get_company_overview,
    get_balance_sheet,
    get_income_statement,
    get_cash_flow,
    get_earnings
]
