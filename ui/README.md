# Web UI for Trading Agents

This folder contains the web dashboard and related UI components.

## Structure
- `static/` - Frontend files (HTML, JS, CSS)
- `web_app.py` - FastAPI backend server
- `cache_manager.py` - Analysis caching system
- `backtest.py` - Backtesting functionality
- `backtest_analyzer.py` - Backtest analysis tools

## Running the UI

### Option 1: Using the start script (Linux/Mac)
```bash
cd ui
./start_dashboard.sh
```

### Option 2: Direct Python (All platforms)
```bash
cd ui
python web_app.py
```

Then open browser to http://localhost:8000

## Features

- **Interactive Dashboard** - Real-time analysis with progress tracking
- **WebSocket Updates** - Live agent execution updates
- **Analysis History** - View and reload past analyses
- **Dark/Light Mode** - Theme toggle
- **Caching** - Automatic caching of analysis results

## Backend Integration

- **News Analyst**: SZ's sophisticated company-focused version
- **News Tools**: SZ's fixed NewsAPI tools (Windows compatible)
- **Trading Graph**: SZ's optimized settings (30-day lookback, 0.4 threshold)

## Credits

- **UI Base**: MC (mc/feature/news-dashboard-enhancements)
- **Backend Logic**: SZ's news analyst + NewsAPI fixes
- **Organization**: UI files separated for clarity
