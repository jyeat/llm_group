"""
FastAPI Web Server for Trading Agents Dashboard

Provides a web interface for running trading analysis with real-time progress updates.
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import sys

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Add parent directory to path for imports (ui/ folder is one level down)
sys.path.insert(0, str(Path(__file__).parent.parent))

from trading_graph import create_trading_graph
from ui.cache_manager import cache_manager

app = FastAPI(title="Trading Agents Dashboard")

# Serve static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


class AnalysisProgress:
    """Track analysis progress for real-time updates"""
    def __init__(self):
        self.current_agent = ""
        self.progress = 0
        self.status = "idle"
        self.results = {}
    
    def update(self, agent: str, progress: int, status: str = "running"):
        self.current_agent = agent
        self.progress = progress
        self.status = status
    
    def set_result(self, agent: str, result: Any):
        self.results[agent] = result


# Global progress tracker
progress_tracker = AnalysisProgress()


@app.get("/")
async def read_root():
    """Serve the main dashboard HTML page"""
    html_file = Path(__file__).parent / "templates" / "dashboard.html"
    if html_file.exists():
        return FileResponse(html_file)
    
    # Fallback: inline HTML if file doesn't exist yet
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading Agents Dashboard</title>
    </head>
    <body>
        <h1>Trading Agents Dashboard</h1>
        <p>Loading...</p>
        <script>window.location.href = '/static/dashboard.html';</script>
    </body>
    </html>
    """)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time analysis updates"""
    await websocket.accept()
    
    try:
        while True:
            # Receive analysis request
            data = await websocket.receive_json()
            ticker = data.get("ticker", "AAPL")
            date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
            
            # Send acknowledgment
            await websocket.send_json({
                "type": "start",
                "ticker": ticker,
                "date": date
            })
            
            # Run analysis with progress updates
            try:
                result = await run_analysis_with_progress(
                    ticker, date, websocket
                )
                
                # Send completion
                await websocket.send_json({
                    "type": "complete",
                    "result": result
                })
                
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        print("Client disconnected")


async def run_analysis_with_progress(
    ticker: str, 
    date: str, 
    websocket: WebSocket
) -> Dict[str, Any]:
    """
    Run trading analysis and send progress updates via WebSocket
    """
    
    # Agent progression
    agents = [
        ("market_analyst", "Market Analyst", 15),
        ("fundamentals_analyst", "Fundamentals Analyst", 30),
        ("news_analyst", "News Analyst", 45),
        ("bull_debater", "Bull Debater", 60),
        ("bear_debater", "Bear Debater", 75),
        ("supervisor", "Supervisor", 90)
    ]
    
    # Initialize graph
    await websocket.send_json({
        "type": "progress",
        "agent": "initializing",
        "progress": 0,
        "message": "Initializing trading agents..."
    })
    
    graph = create_trading_graph(debug=False)
    
    # Simulate progress for each agent
    # In production, you'd hook into the actual graph execution
    current_progress = 5
    
    await websocket.send_json({
        "type": "progress",
        "agent": "initializing",
        "progress": current_progress,
        "message": "Starting analysis pipeline..."
    })
    
    # Run the actual analysis in background
    # We'll simulate progress while it runs
    analysis_task = asyncio.create_task(
        asyncio.to_thread(graph.analyze, ticker, date)
    )
    
    # Simulate progress updates
    for agent_key, agent_name, target_progress in agents:
        await websocket.send_json({
            "type": "progress",
            "agent": agent_key,
            "progress": current_progress,
            "message": f"Running {agent_name}..."
        })
        
        # Wait a bit and update progress
        while current_progress < target_progress:
            await asyncio.sleep(0.5)
            current_progress += 2
            
            await websocket.send_json({
                "type": "progress",
                "agent": agent_key,
                "progress": min(current_progress, target_progress),
                "message": f"Analyzing with {agent_name}..."
            })
    
    # Wait for actual analysis to complete
    result = await analysis_task
    
    # Send final progress
    await websocket.send_json({
        "type": "progress",
        "agent": "complete",
        "progress": 100,
        "message": "Analysis complete!"
    })
    
    # Parse and structure the results
    structured_result = {
        "ticker": result.get("ticker"),
        "date": result.get("date"),
        "decision": result.get("decision"),
        "confidence": result.get("confidence"),
        "rationale": result.get("rationale"),
        "agents": {
            "market_analyst": parse_json_safe(result.get("market_analysis", "{}")),
            "fundamentals_analyst": parse_json_safe(result.get("fundamental_analysis", "{}")),
            "news_analyst": parse_json_safe(result.get("news_analysis", "{}")),
            "bull_debater": parse_json_safe(result.get("bull_argument", "{}")),
            "bear_debater": parse_json_safe(result.get("bear_argument", "{}")),
            "supervisor": parse_json_safe(result.get("supervisor_decision", "{}"))
        },
        "from_cache": False
    }
    
    # Save to cache
    cache_manager.save_cache(ticker, date, result)
    
    return structured_result


def parse_json_safe(json_str: str) -> Dict[str, Any]:
    """Safely parse JSON string, return empty dict on failure"""
    try:
        if isinstance(json_str, dict):
            return json_str
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return {}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "trading-agents-dashboard"}


@app.get("/api/cache/check")
async def check_cache(ticker: str, date: str):
    """Check if cache exists for a given ticker and date"""
    has_cache = cache_manager.has_cache(ticker, date)
    cache_data = None
    
    if has_cache:
        # Get cache metadata from index
        cache_key = f"{ticker}_{date}"
        cache_info = cache_manager.index.get(cache_key, {})
        cache_data = {
            "exists": True,
            "ticker": ticker,
            "date": date,
            "cached_at": cache_info.get("cached_at"),
            "decision": cache_info.get("decision"),
            "confidence": cache_info.get("confidence")
        }
    
    return {
        "has_cache": has_cache,
        "cache_data": cache_data
    }


@app.get("/api/cache/load")
async def load_cache(ticker: str, date: str):
    """Load cached analysis result"""
    result = cache_manager.get_cache(ticker, date)
    
    if result is None:
        return {"error": "Cache not found", "ticker": ticker, "date": date}
    
    # Structure the result similar to live analysis
    structured_result = {
        "ticker": result.get("ticker"),
        "date": result.get("date"),
        "decision": result.get("decision"),
        "confidence": result.get("confidence"),
        "rationale": result.get("rationale"),
        "from_cache": True,
        "cached_at": result.get("cached_at"),
        "agents": {
            "market_analyst": parse_json_safe(result.get("market_analysis", "{}")),
            "fundamentals_analyst": parse_json_safe(result.get("fundamental_analysis", "{}")),
            "news_analyst": parse_json_safe(result.get("news_analysis", "{}")),
            "bull_debater": parse_json_safe(result.get("bull_argument", "{}")),
            "bear_debater": parse_json_safe(result.get("bear_argument", "{}")),
            "supervisor": parse_json_safe(result.get("supervisor_decision", "{}"))
        }
    }
    
    return structured_result


@app.get("/api/cache/list")
async def list_cache():
    """Get list of all cached analyses"""
    cached_list = cache_manager.get_all_cached()
    stats = cache_manager.get_cache_stats()
    
    return {
        "cached_analyses": cached_list,
        "stats": stats
    }


@app.delete("/api/cache/delete")
async def delete_cache(ticker: str, date: str):
    """Delete a specific cache entry"""
    success = cache_manager.delete_cache(ticker, date)
    return {
        "success": success,
        "ticker": ticker,
        "date": date
    }


@app.delete("/api/cache/clear")
async def clear_all_cache():
    """Clear all cached analyses"""
    success = cache_manager.clear_all_cache()
    return {
        "success": success,
        "message": "All cache cleared" if success else "Failed to clear cache"
    }


def main():
    """Start the web server"""
    print("=" * 80)
    print("🚀 Trading Agents Dashboard Starting...")
    print("=" * 80)
    print("\n📊 Dashboard URL: http://localhost:8000")
    print("🔌 WebSocket URL: ws://localhost:8000/ws")
    print("❤️  Health Check: http://localhost:8000/health")
    print("\n⏹️  Press Ctrl+C to stop the server\n")
    print("=" * 80)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()

