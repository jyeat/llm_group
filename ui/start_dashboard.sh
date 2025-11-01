#!/bin/bash
# Start the Trading Agents Dashboard

cd "$(dirname "$0")"
echo "Starting Trading Agents Dashboard..."
echo "Open http://localhost:8000 in your browser"
python web_app.py
