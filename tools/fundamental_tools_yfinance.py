"""
Fundamental Analysis Tools using Yahoo Finance (yfinance)

This module provides tools for fetching financial statements and fundamental data
using yfinance - completely FREE with no API key required!
"""

from langchain_core.tools import tool
import yfinance as yf
import pandas as pd


@tool
def get_company_overview(ticker: str) -> str:
    """Get company overview and valuation metrics from Yahoo Finance.

    This tool provides company profile, sector information, and key valuation ratios.
    Completely FREE - no API key required!

    Args:
        ticker: Stock symbol

    Returns:
        str: Formatted string with company overview and valuation metrics
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            return f"No company overview data available for {ticker}"

        # Extract company profile
        name = info.get('longName', 'N/A')
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        description = info.get('longBusinessSummary', 'N/A')
        market_cap = info.get('marketCap', 'N/A')

        # Valuation metrics
        pe_ratio = info.get('trailingPE', 'N/A')
        forward_pe = info.get('forwardPE', 'N/A')
        peg_ratio = info.get('pegRatio', 'N/A')
        price_to_book = info.get('priceToBook', 'N/A')
        price_to_sales = info.get('priceToSalesTrailing12Months', 'N/A')
        ev_to_revenue = info.get('enterpriseToRevenue', 'N/A')
        ev_to_ebitda = info.get('enterpriseToEbitda', 'N/A')

        # Market metrics
        beta = info.get('beta', 'N/A')
        dividend_yield = info.get('dividendYield', 'N/A')
        week_52_high = info.get('fiftyTwoWeekHigh', 'N/A')
        week_52_low = info.get('fiftyTwoWeekLow', 'N/A')
        target_price = info.get('targetMeanPrice', 'N/A')

        # Format market cap
        if market_cap != 'N/A' and market_cap:
            try:
                market_cap = f"${int(market_cap):,}"
            except:
                pass

        # Format dividend yield
        if dividend_yield != 'N/A' and dividend_yield:
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
P/E Ratio (Trailing): {pe_ratio}
P/E Ratio (Forward): {forward_pe}
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
Analyst Target: ${target_price}

Description: {description[:200] if description != 'N/A' else 'N/A'}...
"""
        return output.strip()

    except Exception as e:
        return f"Error fetching company overview for {ticker}: {str(e)}"


@tool
def get_balance_sheet(ticker: str, period: str = 'quarterly') -> str:
    """Get balance sheet data from Yahoo Finance.

    This tool provides financial position including assets, liabilities, and equity.
    Completely FREE - no API key required!

    Args:
        ticker: Stock symbol
        period: 'quarterly' or 'annual' (default: 'quarterly')

    Returns:
        str: Formatted string with balance sheet data for recent periods
    """
    try:
        stock = yf.Ticker(ticker)

        # Get balance sheet
        if period == 'quarterly':
            bs = stock.quarterly_balance_sheet
        else:
            bs = stock.balance_sheet

        if bs.empty:
            return f"No balance sheet data available for {ticker}"

        output = f"Balance Sheet for {ticker} ({period.capitalize()}):\n\n"

        # Transpose so dates are rows
        bs = bs.T

        # Get last 4 periods
        for i, (date, row) in enumerate(bs.head(4).iterrows()):
            fiscal_date = date.strftime('%Y-%m-%d')

            # Assets
            total_assets = row.get('Total Assets', 'N/A')
            current_assets = row.get('Current Assets', 'N/A')
            cash = row.get('Cash And Cash Equivalents', 'N/A')

            # Liabilities
            total_liabilities = row.get('Total Liabilities Net Minority Interest', 'N/A')
            current_liabilities = row.get('Current Liabilities', 'N/A')
            long_term_debt = row.get('Long Term Debt', 'N/A')

            # Equity
            shareholder_equity = row.get('Stockholders Equity', 'N/A')

            # Format numbers
            def format_number(val):
                if val == 'N/A' or pd.isna(val):
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
                    if not pd.isna(current_assets) and not pd.isna(current_liabilities) and current_liabilities != 0:
                        current_ratio = float(current_assets) / float(current_liabilities)
                        output += f"\nCurrent Ratio: {current_ratio:.2f}\n"

                    if not pd.isna(total_liabilities) and not pd.isna(shareholder_equity) and shareholder_equity != 0:
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
    """Get income statement data from Yahoo Finance.

    This tool provides profitability data including revenue, expenses, and net income.
    Completely FREE - no API key required!

    Args:
        ticker: Stock symbol
        period: 'quarterly' or 'annual' (default: 'quarterly')

    Returns:
        str: Formatted string with income statement data for recent periods
    """
    try:
        stock = yf.Ticker(ticker)

        # Get income statement
        if period == 'quarterly':
            inc = stock.quarterly_income_stmt
        else:
            inc = stock.income_stmt

        if inc.empty:
            return f"No income statement data available for {ticker}"

        output = f"Income Statement for {ticker} ({period.capitalize()}):\n\n"

        # Transpose so dates are rows
        inc = inc.T

        # Get last 4 periods
        for i, (date, row) in enumerate(inc.head(4).iterrows()):
            fiscal_date = date.strftime('%Y-%m-%d')

            # Revenue and income
            total_revenue = row.get('Total Revenue', 'N/A')
            gross_profit = row.get('Gross Profit', 'N/A')
            operating_income = row.get('Operating Income', 'N/A')
            ebitda = row.get('EBITDA', 'N/A')
            net_income = row.get('Net Income', 'N/A')

            # Per share metrics (if available)
            eps_basic = row.get('Basic EPS', 'N/A')
            eps_diluted = row.get('Diluted EPS', 'N/A')

            # Expenses
            cost_of_revenue = row.get('Cost Of Revenue', 'N/A')
            operating_expenses = row.get('Operating Expense', 'N/A')
            rd_expenses = row.get('Research And Development', 'N/A')

            # Format numbers
            def format_number(val):
                if val == 'N/A' or pd.isna(val):
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
  EPS (Basic): {eps_basic if not pd.isna(eps_basic) else 'N/A'}
  EPS (Diluted): {eps_diluted if not pd.isna(eps_diluted) else 'N/A'}
"""

            # Calculate margins for most recent period
            if i == 0:
                try:
                    if not pd.isna(gross_profit) and not pd.isna(total_revenue) and total_revenue != 0:
                        gross_margin = (float(gross_profit) / float(total_revenue)) * 100
                        output += f"\nGross Margin: {gross_margin:.2f}%\n"

                    if not pd.isna(operating_income) and not pd.isna(total_revenue) and total_revenue != 0:
                        operating_margin = (float(operating_income) / float(total_revenue)) * 100
                        output += f"Operating Margin: {operating_margin:.2f}%\n"

                    if not pd.isna(net_income) and not pd.isna(total_revenue) and total_revenue != 0:
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
    """Get cash flow statement data from Yahoo Finance.

    This tool provides cash flow from operating, investing, and financing activities.
    Completely FREE - no API key required!

    Args:
        ticker: Stock symbol
        period: 'quarterly' or 'annual' (default: 'quarterly')

    Returns:
        str: Formatted string with cash flow data for recent periods
    """
    try:
        stock = yf.Ticker(ticker)

        # Get cash flow statement
        if period == 'quarterly':
            cf = stock.quarterly_cashflow
        else:
            cf = stock.cashflow

        if cf.empty:
            return f"No cash flow data available for {ticker}"

        output = f"Cash Flow Statement for {ticker} ({period.capitalize()}):\n\n"

        # Transpose so dates are rows
        cf = cf.T

        # Get last 4 periods
        for i, (date, row) in enumerate(cf.head(4).iterrows()):
            fiscal_date = date.strftime('%Y-%m-%d')

            # Operating activities
            operating_cashflow = row.get('Operating Cash Flow', 'N/A')

            # Investing activities
            capex = row.get('Capital Expenditure', 'N/A')
            cashflow_from_investment = row.get('Investing Cash Flow', 'N/A')

            # Financing activities
            cashflow_from_financing = row.get('Financing Cash Flow', 'N/A')
            dividend_payout = row.get('Cash Dividends Paid', 'N/A')

            # Net change
            net_change_in_cash = row.get('End Cash Position', 'N/A')
            free_cashflow = row.get('Free Cash Flow', 'N/A')

            # Format numbers
            def format_number(val):
                if val == 'N/A' or pd.isna(val):
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
  End Cash Position: {format_number(net_change_in_cash)}
  Free Cash Flow: {format_number(free_cashflow)}
"""

            output += "\n"

        return output.strip()

    except Exception as e:
        return f"Error fetching cash flow for {ticker}: {str(e)}"


@tool
def get_earnings(ticker: str) -> str:
    """Get earnings history and EPS data from Yahoo Finance.

    This tool provides quarterly and annual earnings, including EPS data.
    Completely FREE - no API key required!

    Args:
        ticker: Stock symbol

    Returns:
        str: Formatted string with earnings history
    """
    try:
        stock = yf.Ticker(ticker)

        output = f"Earnings Data for {ticker}:\n\n"

        # Get earnings history
        earnings_history = stock.earnings_history

        if not earnings_history.empty:
            output += "Recent Earnings (Last 4 Quarters):\n"
            output += "---\n"

            for idx, row in earnings_history.head(4).iterrows():
                quarter = row.get('Quarter', 'N/A')
                eps_actual = row.get('EPS Actual', 'N/A')
                eps_estimate = row.get('EPS Estimate', 'N/A')
                surprise_pct = row.get('Surprise(%)', 'N/A')

                output += f"\nQuarter: {quarter}\n"
                output += f"Actual EPS: {eps_actual}\n"
                output += f"Estimated EPS: {eps_estimate}\n"

                if surprise_pct != 'N/A' and not pd.isna(surprise_pct):
                    beat_miss = "Beat" if surprise_pct > 0 else "Miss" if surprise_pct < 0 else "Met"
                    output += f"Surprise: {surprise_pct:.1f}% - {beat_miss}\n"

        # Get annual earnings
        earnings_yearly = stock.earnings

        if earnings_yearly is not None and not earnings_yearly.empty:
            output += "\n\nAnnual Earnings:\n"
            output += "---\n"

            for year, row in earnings_yearly.tail(5).iterrows():
                revenue = row.get('Revenue', 'N/A')
                earnings = row.get('Earnings', 'N/A')

                output += f"\nYear: {year}\n"
                output += f"Revenue: ${int(revenue):,}" if revenue != 'N/A' and not pd.isna(revenue) else "Revenue: N/A"
                output += f"\nEarnings: ${int(earnings):,}" if earnings != 'N/A' and not pd.isna(earnings) else "\nEarnings: N/A"
                output += "\n"

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
