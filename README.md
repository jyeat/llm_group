# MC-SZ Integration Branch

## Overview

This branch (`mc-sz-integration`) combines:
- **SZ's sophisticated news analyst** (base) - Advanced news filtering, relevance scoring, universal ticker support
- **MC's web UI** (organized in `ui/` folder) - Real-time web dashboard with WebSocket progress updates

## Branch History

This branch was created from `sz-integration` which contains:
1. SZ's news analyst with company-focused filtering and deduplication
2. NewsAPI.org integration (free, 100 requests/day, 30-day history)
3. All compatibility fixes for Windows and universal ticker support
4. MC's web UI added in organized folder structure

## Key Features

### News Analysis (SZ's Implementation)
- **Universal Ticker Support**: Works with ANY ticker symbol (not just AAPL, NVDA, AMD, TSLA)
- **Smart Relevance Filtering**:
  - Ticker match score: 0.70 (increased from 0.55)
  - Relevance threshold: 0.4 (lowered from 0.6)
  - Company name matching with aliases
  - Industry/sector keyword matching
- **NewsAPI.org Integration**:
  - Primary source (free, 100 requests/day)
  - 30-day history limit (with automatic capping)
  - yfinance as fallback
- **Windows Compatible**: Fixed datetime handling for Windows systems
- **Deduplication**: Removes duplicate articles by content hash
- **Source Normalization**: Handles both dict and string source formats

### Web Dashboard (MC's Implementation)
- **Real-time Analysis**: WebSocket-based progress updates
- **Interactive UI**: Modern responsive design with theme toggle
- **Analysis History**: Sidebar with cached results
- **Cache Management**: Save/load/delete analysis results
- **Visual Progress**: Agent-by-agent progress tracking

## Project Structure

```
simplified_tradingagents/
├── agent/
│   ├── news_analyst.py              # SZ's sophisticated news analyst
│   ├── market_analyst_v2.py         # Technical analysis agent
│   ├── fundamentals_analyst_v2.py   # Financial analysis agent
│   ├── bull_debater_v2.py           # Bull case builder
│   ├── bear_debater_v2.py           # Bear case builder
│   └── supervisor_v2.py             # Risk-tiered recommendations
├── tools/
│   ├── news_tools_newsapi.py        # NewsAPI integration (primary)
│   ├── analyst_tools_fmp.py         # Technical indicators (FMP)
│   ├── fundamental_tools_fmp.py     # Financial data (FMP)
│   └── ...
├── ui/                              # MC's Web Dashboard (organized)
│   ├── static/
│   │   ├── dashboard.html           # Main UI
│   │   ├── app.js                   # Frontend logic
│   │   └── styles.css               # Styling
│   ├── web_app.py                   # FastAPI server
│   ├── cache_manager.py             # Analysis caching
│   ├── backtest.py                  # Backtesting utilities
│   ├── start_dashboard.sh           # Startup script
│   └── README.md                    # UI documentation
├── config.py                        # Configuration (API keys, etc.)
├── state.py                         # Shared state schema
├── trading_graph.py                 # LangGraph workflow
├── main.py                          # CLI interface
├── .env                             # Environment variables (API keys)
├── .env.example                     # Environment template
└── NEWSAPI_SETUP_GUIDE.md          # NewsAPI setup instructions

```

## Setup Instructions

### 1. Environment Setup

```bash
# Create .env file with your API keys
cp .env.example .env

# Edit .env and add:
# - GOOGLE_GENAI_API_KEY (for LLM)
# - NEWSAPI_KEY (for news - get free at https://newsapi.org/register)
# - FMP_API_KEY (optional - for financial data)
# - ALPHA_VANTAGE_API_KEY (optional - backup)
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- langchain-core
- langchain-google-genai
- langgraph
- pydantic
- requests
- yfinance
- pandas
- fastapi
- uvicorn
- python-dotenv

### 3. Run Analysis (CLI)

```bash
# Basic usage
python main.py

# Analyze specific ticker
python main.py --ticker MSFT

# With debug output
python main.py --ticker NVDA --debug

# With detailed JSON results
python main.py --ticker AAPL --detailed
```

### 4. Run Web Dashboard

```bash
# Start the web server
cd ui
python web_app.py

# Or use the startup script (Linux/Mac/WSL)
bash start_dashboard.sh
```

Then open: http://localhost:8000

## Configuration

### News Analysis Parameters (trading_graph.py)

```python
initial_state = {
    "lookback_days": 30,           # NewsAPI free tier max
    "relevance_threshold": 0.4,    # Lower = more inclusive (supports ANY ticker)
    # ...
}
```

### NewsAPI Limits
- **Free Tier**: 100 requests/day
- **History**: 30 days maximum
- **Fallback**: yfinance (unlimited, no API key required)

## Key Improvements in This Branch

### From SZ's Work:
1. ✅ **NewsAPI Integration**: Free alternative to Alpha Vantage
2. ✅ **Universal Ticker Support**: Works with any ticker, not just 4 predefined ones
3. ✅ **Smart Filtering**: Increased ticker match score (0.70), lowered threshold (0.4)
4. ✅ **Windows Compatible**: Fixed datetime handling for Windows systems
5. ✅ **30-Day Cap**: Automatic capping with warnings for NewsAPI free tier
6. ✅ **Source Normalization**: Handles both dict and string formats
7. ✅ **API Priority**: NewsAPI first, yfinance fallback (not reversed)

### From MC's Work:
8. ✅ **Web Dashboard**: Real-time WebSocket-based UI
9. ✅ **Cache System**: Save/load/delete analysis results
10. ✅ **Progress Tracking**: Visual agent-by-agent progress
11. ✅ **Organized Structure**: All UI files in separate `ui/` folder

## Testing

### Test News Analysis
```bash
# Should work with ANY ticker now
python main.py --ticker MSFT --debug
python main.py --ticker GOOGL --debug
python main.py --ticker JPM --debug
```

### Test Web Dashboard
```bash
cd ui
python web_app.py

# Test with different tickers in browser
# http://localhost:8000
```

## Troubleshooting

### "No news found for [TICKER]"
1. Check if NewsAPI key is set in `.env`
2. Verify ticker symbol is correct
3. Check NewsAPI daily limit (100 requests)
4. Try with `--debug` flag to see detailed logs

### "ModuleNotFoundError: No module named 'simplified_tradingagents'"
- Fixed! All absolute imports changed to relative imports
- Restart Python interpreter if issue persists

### Windows datetime errors
- Fixed! Now uses 1970 timestamp for missing dates
- Articles with missing dates sorted to bottom

### Source field dict error
- Fixed! `get_source_name()` handles both dict and string formats

## Commit History

```
b2ad9cb Fix absolute imports to relative imports for UI compatibility
18e6393 Add MC's web UI in organized ui/ folder
8f1ee4e Fix source field handling: Support both string and dict formats
5e19032 Fix Windows datetime error: Use 1970 timestamp for missing dates
c204f48 Fix relevance filtering to support ANY ticker, not just predefined ones
ac5d3d5 Fix NewsAPI integration: Priority and 30-day cap
e4ca8ac Replace Alpha Vantage with NewsAPI.org (free tier)
9bce8c1 Merge sz/szgan: Integrate SZ's news analyst
```

## Next Steps (Phase 2 - Optional)

User requested future enhancements:
1. Add "Model Explanation" section to dashboard
2. Create interactive workflow diagram (agent pipeline visualization)
3. Add agent comparison UI (bull vs bear strength)
4. Enhance progress tracking with live agent outputs
5. Add educational tooltips about each agent's role

## Contributors

- **SZ**: Sophisticated news analyst, NewsAPI integration, compatibility fixes
- **MC**: Web dashboard, caching system, real-time progress UI

## API Documentation

### FastAPI Endpoints (ui/web_app.py)

- `GET /` - Dashboard homepage
- `WebSocket /ws` - Real-time analysis with progress updates
- `GET /health` - Health check
- `GET /api/cache/check?ticker=AAPL&date=2025-01-01` - Check cache existence
- `GET /api/cache/load?ticker=AAPL&date=2025-01-01` - Load cached result
- `GET /api/cache/list` - List all cached analyses
- `DELETE /api/cache/delete?ticker=AAPL&date=2025-01-01` - Delete cache entry
- `DELETE /api/cache/clear` - Clear all cache

## License

[Your license here]
