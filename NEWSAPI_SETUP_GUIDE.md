# NewsAPI Setup Guide

The `sz-integration` branch now uses **NewsAPI** for news data instead of Alpha Vantage, which is a free alternative with better availability.

## Why NewsAPI?

- **100% FREE** - No credit card required
- **100 requests per day** on free tier
- **1 month** of historical news data
- **Easy to use** - Simple REST API
- **Good coverage** - Major news sources worldwide

## How to Get Your Free NewsAPI Key

### Step 1: Sign Up
1. Go to https://newsapi.org/register
2. Fill in your details:
   - Name
   - Email
   - Password
3. **No credit card required**
4. Click "Submit"

### Step 2: Get Your API Key
1. After registration, you'll be redirected to your account page
2. Copy your API key (looks like: `1234567890abcdef1234567890abcdef`)
3. Keep this key safe - you'll need it in the next step

### Step 3: Add to .env File
1. Open the `.env` file in the `simplified_tradingagents` folder
2. Find the line: `NEWSAPI_KEY=your_newsapi_key_here`
3. Replace `your_newsapi_key_here` with your actual API key
4. Save the file

Example:
```bash
NEWSAPI_KEY=1234567890abcdef1234567890abcdef
```

## What Changed in sz-integration Branch?

### New Files:
- `tools/news_tools_newsapi.py` - NewsAPI integration (replaces Alpha Vantage)
- `.env.example` - Template with all API keys needed

### Modified Files:
- `.env` - Added NEWSAPI_KEY field
- `agent/news_analyst.py` - Now imports from `news_tools_newsapi` instead of `news_tools`

### Features:
- **Primary**: Uses yfinance (free, unlimited) for stock-specific news
- **Fallback**: Uses NewsAPI when yfinance doesn't have data
- **Same interface**: Works exactly like the original Alpha Vantage version

## Testing the Setup

After adding your NewsAPI key, test it:

```bash
# Make sure you're on sz-integration branch
git branch --show-current  # Should show: sz-integration

# Run the trading agent
python main.py --ticker AAPL

# Or with debug mode
python main.py --ticker AAPL --debug
```

## Free Tier Limitations

NewsAPI free tier has some limits:
- **100 requests/day** - Plan your testing accordingly
- **1 month lookback** - Can't access news older than 30 days
- **Attributed sources** - Must attribute NewsAPI in any public use

## Alternative: Use yfinance Only

If you don't want to sign up for NewsAPI, the code will automatically fall back to **yfinance** which is:
- **Completely free**
- **No API key needed**
- **Unlimited requests**
- **Stock-specific news only** (no general market news)

To use yfinance only, just leave `NEWSAPI_KEY` empty in `.env`:
```bash
NEWSAPI_KEY=
```

## Troubleshooting

### Error: "NEWSAPI_KEY not configured"
- Make sure you added your API key to `.env`
- Check there are no extra spaces or quotes
- Restart your terminal/IDE after editing `.env`

### Error: "NewsAPI error: apiKeyInvalid"
- Your API key might be incorrect
- Double-check you copied it correctly from newsapi.org
- Try regenerating your key on the NewsAPI website

### No news found
- NewsAPI free tier only has 1 month of history
- Try using a more recent date
- Check if the ticker is a valid stock symbol
- The code will fall back to yfinance automatically

## Need Help?

- NewsAPI Documentation: https://newsapi.org/docs
- NewsAPI Support: support@newsapi.org
- Check your API usage: https://newsapi.org/account

## Original Alpha Vantage Version

If you need to use Alpha Vantage instead, the original files are still available:
- `tools/news_tools.py` - Original Alpha Vantage implementation
- Just change the import in `agent/news_analyst.py` back to `news_tools`
