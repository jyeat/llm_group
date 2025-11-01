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
# Use .resolve() to get absolute paths for proper import resolution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trading_graph import create_trading_graph

# Import cache_manager from same directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cache_manager import cache_manager

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


def calculate_progress_from_node(node_name: str) -> int:
    """
    Calculate progress percentage based on which agent node has completed.

    Agent pipeline order:
    news_analyst (0-20%) → market_analyst (20-35%) → fundamentals_analyst (35-50%)
    → bull_debater (50-65%) → bear_debater (65-80%) → supervisor (80-100%)
    """
    progress_map = {
        "news_analyst": 20,
        "market_analyst": 35,
        "fundamentals_analyst": 50,
        "bull_debater": 65,
        "bear_debater": 80,
        "supervisor": 95
    }
    return progress_map.get(node_name, 0)


async def run_analysis_with_progress(
    ticker: str, 
    date: str, 
    websocket: WebSocket
) -> Dict[str, Any]:
    """
    Run trading analysis and send REAL progress updates via WebSocket.
    Uses LangGraph's streaming API to track actual agent completion.
    """

    # Initialize graph
    await websocket.send_json({
        "type": "progress",
        "agent": "initializing",
        "progress": 0,
        "message": "Initializing trading agents..."
    })
    
    graph = create_trading_graph(debug=True)

    # Create initial state for the graph
    initial_state = {
        "ticker": ticker,
        "date": date,
        "messages": [],
        "lookback_days": 30,
        "relevance_threshold": 0.4,
        "max_company_articles": 20,
        "max_macro_articles": 30,
        "max_kept_articles": 50,
        "news_analysis": "",
        "market_analysis": "",
        "fundamental_analysis": "",
        "bull_argument": "",
        "bear_argument": "",
        "decision": "neutral",
        "rationale": "",
        "confidence": 0.0,
        "supervisor_decision": ""
    }

    await websocket.send_json({
        "type": "progress",
        "agent": "initializing",
        "progress": 5,
        "message": "Starting analysis pipeline..."
    })

    # Run analysis with real-time progress tracking via streaming
    # This uses LangGraph's .stream() to get updates as each agent completes

    # Shared state for tracking progress across thread
    progress_state = {"final_state": None, "current_node": None}

    def run_graph_stream():
        """Run the graph with streaming (regular function for to_thread)"""
        accumulated_state = dict(initial_state)  # Start with initial state
        final_output = None

        for output in graph.graph.stream(initial_state):
            # Update shared state for progress tracking
            if output:
                node_name = list(output.keys())[0]
                node_state = output[node_name]

                # Accumulate all state updates
                accumulated_state.update(node_state)

                # Track progress
                progress_state["current_node"] = node_name
                progress_state["final_state"] = output
                final_output = output

        # Return the accumulated state, not just the last node's output
        return accumulated_state

    # Run graph streaming in background with timeout
    try:
        stream_task = asyncio.create_task(
            asyncio.to_thread(run_graph_stream)
        )

        # Monitor for completion with timeout
        last_progress = 5
        last_node = None
        start_time = asyncio.get_event_loop().time()

        while not stream_task.done():
            # Check timeout (5 minutes = 300 seconds)
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > 300:
                stream_task.cancel()
                raise asyncio.TimeoutError()

            # Send progress update every 2 seconds
            await asyncio.sleep(2)

            # Check if a new node has completed
            current_node = progress_state.get("current_node")
            if current_node and current_node != last_node:
                progress = calculate_progress_from_node(current_node)
                if progress > last_progress:
                    await websocket.send_json({
                        "type": "progress",
                        "agent": current_node,
                        "progress": progress,
                        "message": f"Completed {current_node.replace('_', ' ').title()}..."
                    })
                    last_progress = progress
                    last_node = current_node

        # Get final result
        result = await stream_task

    except asyncio.TimeoutError:
        error_msg = "Analysis timed out after 5 minutes. This may be due to: (1) Too many news articles being processed, (2) Slow API responses from Google Gemini, or (3) NewsAPI rate limits. Try analyzing again with a different ticker or reduce the number of articles."
        await websocket.send_json({
            "type": "error",
            "message": error_msg
        })
        print(f"[WebSocket] Analysis timeout for {ticker} on {date}")
        raise

    # result is now the accumulated state from all agents
    # No need to extract - it's already the full state dict

    # Debug: Print what we got
    print(f"[WebSocket] Final result keys: {list(result.keys()) if result else 'None'}")
    if result:
        print(f"[WebSocket] Has market_analysis: {'market_analysis' in result}")
        print(f"[WebSocket] Has news_analysis: {'news_analysis' in result}")
        print(f"[WebSocket] Has fundamental_analysis: {'fundamental_analysis' in result}")
        print(f"[WebSocket] Has bull_argument: {'bull_argument' in result}")
        print(f"[WebSocket] Has bear_argument: {'bear_argument' in result}")

    # Send final progress
    await websocket.send_json({
        "type": "progress",
        "agent": "complete",
        "progress": 100,
        "message": "Analysis complete!"
    })

    # Parse and structure the results
    structured_result = {
        "ticker": result.get("ticker") if result else ticker,
        "date": result.get("date") if result else date,
        "decision": result.get("decision") if result else "neutral",
        "confidence": result.get("confidence") if result else 0.0,
        "rationale": result.get("rationale") if result else "",
        "agents": {
            "market_analyst": parse_json_safe(result.get("market_analysis", "{}")) if result else {},
            "fundamentals_analyst": parse_json_safe(result.get("fundamental_analysis", "{}")) if result else {},
            "news_analyst": parse_json_safe(result.get("news_analysis", "{}")) if result else {},
            "bull_debater": parse_json_safe(result.get("bull_argument", "{}")) if result else {},
            "bear_debater": parse_json_safe(result.get("bear_argument", "{}")) if result else {},
            "supervisor": parse_json_safe(result.get("supervisor_decision", "{}")) if result else {}
        },
        "from_cache": False
    }
    
    # Save to cache - save the full result state, not the structured_result
    # The cache expects the raw state with all analysis fields
    if result:
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

