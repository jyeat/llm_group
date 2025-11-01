from langchain_core.tools import tool
import requests
from config import ALPHA_VANTAGE_API_KEY, AV_BASE_URL, AV_TIMEOUT


@tool
def get_company_overview(ticker: str) -> str:
    """Get company overview and valuation metrics from Alpha Vantage.

    This tool provides company profile, sector information, and key valuation ratios.

    Args:
        ticker: Stock symbol

    Returns:
        Formatted string with company overview and valuation metrics
    """
    try:
        params = {
            'function': 'OVERVIEW',
            'symbol': ticker,
            'apikey': ALPHA_VANTAGE_API_KEY
        }

        response = requests.get(AV_BASE_URL, params=params, timeout=AV_TIMEOUT)
        data = response.json()

        if not data or 'Symbol' not in data:
            return f"No company overview data available for {ticker}"

        # Extract company profile
        name = data.get('Name', 'N/A')
        sector = data.get('Sector', 'N/A')
        industry = data.get('Industry', 'N/A')
        description = data.get('Description', 'N/A')
        market_cap = data.get('MarketCapitalization', 'N/A')

        # Valuation metrics
        pe_ratio = data.get('PERatio', 'N/A')
        peg_ratio = data.get('PEGRatio', 'N/A')
        price_to_book = data.get('PriceToBookRatio', 'N/A')
        price_to_sales = data.get('PriceToSalesRatioTTM', 'N/A')
        ev_to_revenue = data.get('EVToRevenue', 'N/A')
        ev_to_ebitda = data.get('EVToEBITDA', 'N/A')

        # Market metrics
        beta = data.get('Beta', 'N/A')
        dividend_yield = data.get('DividendYield', 'N/A')
        week_52_high = data.get('52WeekHigh', 'N/A')
        week_52_low = data.get('52WeekLow', 'N/A')
        analyst_target = data.get('AnalystTargetPrice', 'N/A')

        # Format market cap
        if market_cap != 'N/A':
            try:
                market_cap = f"${int(market_cap):,}"
            except:
                pass

        # Convert percentages
        if dividend_yield != 'N/A':
            try:
                dividend_yield = f"{float(dividend_yield)*100:.2f}%"
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
EV/Revenue: {ev_to_revenue}
EV/EBITDA: {ev_to_ebitda}

Market Metrics:
Beta: {beta}
Dividend Yield: {dividend_yield}
52-Week High: ${week_52_high}
52-Week Low: ${week_52_low}
Analyst Target: ${analyst_target}

Description: {description[:200]}...
"""
        return output.strip()

    except Exception as e:
        return f"Error fetching company overview for {ticker}: {str(e)}"


@tool
def get_balance_sheet(ticker: str, period: str = 'quarterly') -> str:
    """Get balance sheet data from Alpha Vantage.

    This tool provides financial position including assets, liabilities, and equity.

    Args:
        ticker: Stock symbol
        period: 'quarterly' or 'annual' (default: 'quarterly')

    Returns:
        Formatted string with balance sheet data for recent periods
    """
    try:
        params = {
            'function': 'BALANCE_SHEET',
            'symbol': ticker,
            'apikey': ALPHA_VANTAGE_API_KEY
        }

        response = requests.get(AV_BASE_URL, params=params, timeout=AV_TIMEOUT)
        data = response.json()

        # Select quarterly or annual reports
        report_key = 'quarterlyReports' if period == 'quarterly' else 'annualReports'

        if report_key not in data or not data[report_key]:
            return f"No balance sheet data available for {ticker}"

        reports = data[report_key][:4]  # Get last 4 periods

        output = f"Balance Sheet for {ticker} ({period.capitalize()}):\n\n"

        for i, report in enumerate(reports):
            fiscal_date = report.get('fiscalDateEnding', 'N/A')

            # Assets
            total_assets = report.get('totalAssets', 'N/A')
            current_assets = report.get('totalCurrentAssets', 'N/A')
            cash = report.get('cashAndCashEquivalentsAtCarryingValue', 'N/A')

            # Liabilities
            total_liabilities = report.get('totalLiabilities', 'N/A')
            current_liabilities = report.get('totalCurrentLiabilities', 'N/A')
            long_term_debt = report.get('longTermDebt', 'N/A')

            # Equity
            shareholder_equity = report.get('totalShareholderEquity', 'N/A')

            # Format numbers
            def format_number(val):
                if val == 'N/A':
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
                    if current_assets != 'N/A' and current_liabilities != 'N/A':
                        current_ratio = float(current_assets) / float(current_liabilities)
                        output += f"\nCurrent Ratio: {current_ratio:.2f}\n"

                    if total_liabilities != 'N/A' and shareholder_equity != 'N/A':
                        debt_to_equity = float(total_liabilities) / float(shareholder_equity)
                        output += f"Debt-to-Equity: {debt_to_equity:.2f}\n"
                except:
                    pass

            output += "\n"

        return output.strip()

    except Exception as e:
        return f"Error fetching balance sheet for {ticker}: {str(e)}"


@tool
def get_income_statement(ticker: str, period: str = 'quarterly') -> str:
    """Get income statement data from Alpha Vantage.

    This tool provides profitability data including revenue, expenses, and net income.

    Args:
        ticker: Stock symbol
        period: 'quarterly' or 'annual' (default: 'quarterly')

    Returns:
        Formatted string with income statement data for recent periods
    """
    try:
        params = {
            'function': 'INCOME_STATEMENT',
            'symbol': ticker,
            'apikey': ALPHA_VANTAGE_API_KEY
        }

        response = requests.get(AV_BASE_URL, params=params, timeout=AV_TIMEOUT)
        data = response.json()

        # Select quarterly or annual reports
        report_key = 'quarterlyReports' if period == 'quarterly' else 'annualReports'

        if report_key not in data or not data[report_key]:
            return f"No income statement data available for {ticker}"

        reports = data[report_key][:4]  # Get last 4 periods

        output = f"Income Statement for {ticker} ({period.capitalize()}):\n\n"

        for i, report in enumerate(reports):
            fiscal_date = report.get('fiscalDateEnding', 'N/A')

            # Revenue and income
            total_revenue = report.get('totalRevenue', 'N/A')
            gross_profit = report.get('grossProfit', 'N/A')
            operating_income = report.get('operatingIncome', 'N/A')
            ebit = report.get('ebit', 'N/A')
            ebitda = report.get('ebitda', 'N/A')
            net_income = report.get('netIncome', 'N/A')

            # Per share metrics
            eps = report.get('reportedEPS', 'N/A')

            # Expenses
            cost_of_revenue = report.get('costOfRevenue', 'N/A')
            operating_expenses = report.get('operatingExpenses', 'N/A')
            rd_expenses = report.get('researchAndDevelopment', 'N/A')

            # Format numbers
            def format_number(val):
                if val == 'N/A':
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
  EBIT: {format_number(ebit)}
  EBITDA: {format_number(ebitda)}

Bottom Line:
  Net Income: {format_number(net_income)}
  EPS: {eps}
"""

            # Calculate margins for most recent period
            if i == 0:
                try:
                    if gross_profit != 'N/A' and total_revenue != 'N/A':
                        gross_margin = (float(gross_profit) / float(total_revenue)) * 100
                        output += f"\nGross Margin: {gross_margin:.2f}%\n"

                    if operating_income != 'N/A' and total_revenue != 'N/A':
                        operating_margin = (float(operating_income) / float(total_revenue)) * 100
                        output += f"Operating Margin: {operating_margin:.2f}%\n"

                    if net_income != 'N/A' and total_revenue != 'N/A':
                        net_margin = (float(net_income) / float(total_revenue)) * 100
                        output += f"Net Margin: {net_margin:.2f}%\n"
                except:
                    pass

            output += "\n"

        return output.strip()

    except Exception as e:
        return f"Error fetching income statement for {ticker}: {str(e)}"


@tool
def get_cash_flow(ticker: str, period: str = 'quarterly') -> str:
    """Get cash flow statement data from Alpha Vantage.

    This tool provides cash flow from operating, investing, and financing activities.

    Args:
        ticker: Stock symbol
        period: 'quarterly' or 'annual' (default: 'quarterly')

    Returns:
        Formatted string with cash flow data for recent periods
    """
    try:
        params = {
            'function': 'CASH_FLOW',
            'symbol': ticker,
            'apikey': ALPHA_VANTAGE_API_KEY
        }

        response = requests.get(AV_BASE_URL, params=params, timeout=AV_TIMEOUT)
        data = response.json()

        # Select quarterly or annual reports
        report_key = 'quarterlyReports' if period == 'quarterly' else 'annualReports'

        if report_key not in data or not data[report_key]:
            return f"No cash flow data available for {ticker}"

        reports = data[report_key][:4]  # Get last 4 periods

        output = f"Cash Flow Statement for {ticker} ({period.capitalize()}):\n\n"

        for i, report in enumerate(reports):
            fiscal_date = report.get('fiscalDateEnding', 'N/A')

            # Operating activities
            operating_cashflow = report.get('operatingCashflow', 'N/A')

            # Investing activities
            capex = report.get('capitalExpenditures', 'N/A')
            cashflow_from_investment = report.get('cashflowFromInvestment', 'N/A')

            # Financing activities
            cashflow_from_financing = report.get('cashflowFromFinancing', 'N/A')
            dividend_payout = report.get('dividendPayout', 'N/A')

            # Net change
            net_change_in_cash = report.get('changeInCashAndCashEquivalents', 'N/A')

            # Format numbers
            def format_number(val):
                if val == 'N/A':
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

Net Change:
  Change in Cash: {format_number(net_change_in_cash)}
"""

            # Calculate free cash flow for most recent period
            if i == 0:
                try:
                    if operating_cashflow != 'N/A' and capex != 'N/A':
                        # CapEx is typically negative, so we add it
                        free_cashflow = float(operating_cashflow) + float(capex)
                        output += f"\nFree Cash Flow: ${int(free_cashflow):,}\n"
                except:
                    pass

            output += "\n"

        return output.strip()

    except Exception as e:
        return f"Error fetching cash flow for {ticker}: {str(e)}"


@tool
def get_earnings(ticker: str) -> str:
    """Get earnings history and EPS data from Alpha Vantage.

    This tool provides quarterly and annual earnings, including EPS surprises.

    Args:
        ticker: Stock symbol

    Returns:
        Formatted string with earnings history and surprises
    """
    try:
        params = {
            'function': 'EARNINGS',
            'symbol': ticker,
            'apikey': ALPHA_VANTAGE_API_KEY
        }

        response = requests.get(AV_BASE_URL, params=params, timeout=AV_TIMEOUT)
        data = response.json()

        output = f"Earnings Data for {ticker}:\n\n"

        # Quarterly earnings
        if 'quarterlyEarnings' in data and data['quarterlyEarnings']:
            quarterly = data['quarterlyEarnings'][:8]  # Last 8 quarters (2 years)

            output += "Quarterly Earnings (Last 8 Quarters):\n"
            output += "---\n"

            for q in quarterly:
                fiscal_date = q.get('fiscalDateEnding', 'N/A')
                reported_date = q.get('reportedDate', 'N/A')
                reported_eps = q.get('reportedEPS', 'N/A')
                estimated_eps = q.get('estimatedEPS', 'N/A')
                surprise = q.get('surprise', 'N/A')
                surprise_pct = q.get('surprisePercentage', 'N/A')

                output += f"\nFiscal Quarter Ending: {fiscal_date}\n"
                output += f"Reported Date: {reported_date}\n"
                output += f"Reported EPS: {reported_eps}\n"
                output += f"Estimated EPS: {estimated_eps}\n"

                if surprise != 'N/A' and surprise_pct != 'N/A':
                    try:
                        surprise_val = float(surprise)
                        surprise_pct_val = float(surprise_pct)
                        beat_miss = "Beat" if surprise_val > 0 else "Miss" if surprise_val < 0 else "Met"
                        output += f"Surprise: ${surprise_val:.2f} ({surprise_pct_val:.1f}%) - {beat_miss}\n"
                    except:
                        output += f"Surprise: {surprise}\n"

        # Annual earnings
        if 'annualEarnings' in data and data['annualEarnings']:
            annual = data['annualEarnings'][:5]  # Last 5 years

            output += "\n\nAnnual Earnings (Last 5 Years):\n"
            output += "---\n"

            for a in annual:
                fiscal_date = a.get('fiscalDateEnding', 'N/A')
                reported_eps = a.get('reportedEPS', 'N/A')

                output += f"\nFiscal Year Ending: {fiscal_date}\n"
                output += f"Annual EPS: {reported_eps}\n"

        if 'quarterlyEarnings' not in data and 'annualEarnings' not in data:
            return f"No earnings data available for {ticker}"

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
