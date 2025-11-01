#!/bin/bash
# Docker Run Script for Simplified Trading Agents
# This script provides easy commands to run the trading agents system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_error ".env file not found!"
        echo ""
        echo "Please create a .env file with your API keys:"
        echo "  cp .env.example .env"
        echo "  # Then edit .env and add your keys"
        echo ""
        exit 1
    fi
    print_success ".env file found"
}

# Build Docker image
build() {
    print_header "Building Docker Image"
    docker-compose build
    print_success "Docker image built successfully"
}

# Start web UI
start_ui() {
    print_header "Starting Web UI"
    check_env
    docker-compose up -d trading-agents-ui
    echo ""
    print_success "Web UI started successfully!"
    echo ""
    echo "Access the dashboard at: ${GREEN}http://localhost:8000${NC}"
    echo ""
    echo "View logs with: ${BLUE}./docker-run.sh logs${NC}"
    echo "Stop with: ${BLUE}./docker-run.sh stop${NC}"
}

# Run CLI analysis
run_cli() {
    print_header "Running CLI Analysis"
    check_env

    TICKER=${1:-NVDA}
    DATE=${2:-$(date +%Y-%m-%d)}

    echo "Analyzing: ${GREEN}${TICKER}${NC} on ${GREEN}${DATE}${NC}"
    echo ""

    docker-compose run --rm \
        -e TICKER=${TICKER} \
        trading-agents-cli \
        python main.py --ticker ${TICKER} --date ${DATE}
}

# View logs
logs() {
    if [ -z "$1" ]; then
        docker-compose logs -f trading-agents-ui
    else
        docker-compose logs -f $1
    fi
}

# Stop all services
stop() {
    print_header "Stopping Services"
    docker-compose down
    print_success "All services stopped"
}

# Restart services
restart() {
    print_header "Restarting Services"
    docker-compose restart
    print_success "Services restarted"
}

# Show status
status() {
    print_header "Service Status"
    docker-compose ps
}

# Clean up everything
clean() {
    print_header "Cleaning Up Docker Resources"
    print_warning "This will remove containers, networks, and images"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        docker-compose rm -f
        print_success "Cleanup complete"
    else
        print_warning "Cleanup cancelled"
    fi
}

# Verify setup
verify() {
    print_header "Verifying Setup"
    check_env
    docker-compose run --rm trading-agents-ui python verify_setup.py
}

# Show help
show_help() {
    cat << EOF
${BLUE}Simplified Trading Agents - Docker Commands${NC}

Usage: ./docker-run.sh [command] [options]

${GREEN}Commands:${NC}
  build         Build Docker image
  start         Start web UI (http://localhost:8000)
  stop          Stop all services
  restart       Restart all services
  status        Show service status
  logs [svc]    View logs (optionally specify service)

  cli [TICKER] [DATE]
                Run CLI analysis (default: NVDA, today)
                Examples:
                  ./docker-run.sh cli MSFT
                  ./docker-run.sh cli AAPL 2025-11-01

  verify        Run setup verification
  clean         Remove all Docker resources
  help          Show this help message

${GREEN}Examples:${NC}
  ./docker-run.sh build                    # Build the image
  ./docker-run.sh start                    # Start web UI
  ./docker-run.sh cli NVDA                 # Analyze NVDA
  ./docker-run.sh cli TSLA 2025-10-15      # Analyze TSLA on specific date
  ./docker-run.sh logs                     # View web UI logs
  ./docker-run.sh stop                     # Stop everything

${YELLOW}First Time Setup:${NC}
  1. cp .env.example .env
  2. Edit .env and add your API keys
  3. ./docker-run.sh build
  4. ./docker-run.sh start
  5. Open http://localhost:8000

EOF
}

# Main command router
case "${1:-help}" in
    build)
        build
        ;;
    start|up)
        start_ui
        ;;
    stop|down)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs $2
        ;;
    cli|analyze)
        run_cli $2 $3
        ;;
    status|ps)
        status
        ;;
    clean)
        clean
        ;;
    verify)
        verify
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
