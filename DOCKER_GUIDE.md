# Docker Deployment Guide for Simplified Trading Agents

This guide explains how to run the Simplified Trading Agents system using Docker.

---

## 📦 **What's Included**

- **Dockerfile**: Multi-stage build for optimized image size (~300MB)
- **docker-compose.yml**: Orchestration for web UI and CLI services
- **.dockerignore**: Optimized build context
- **docker-run.sh**: Convenient wrapper script for common operations

---

## 🚀 **Quick Start**

### **1. Prerequisites**

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)
- API keys (Google Gemini, NewsAPI)

### **2. Setup Environment**

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use any text editor
```

Required keys in `.env`:
```bash
GOOGLE_GENAI_API_KEY=your_gemini_key_here
NEWSAPI_KEY=your_newsapi_key_here
```

### **3. Build and Run**

#### **Option A: Using the Helper Script (Recommended)**

```bash
# Make script executable (Linux/Mac)
chmod +x docker-run.sh

# Build the image
./docker-run.sh build

# Start the web UI
./docker-run.sh start

# Access at http://localhost:8000
```

#### **Option B: Using Docker Compose Directly**

```bash
# Build the image
docker-compose build

# Start the web UI
docker-compose up -d trading-agents-ui

# Access at http://localhost:8000
```

---

## 📋 **Available Commands**

### **Using docker-run.sh**

```bash
# Build Docker image
./docker-run.sh build

# Start web UI (background)
./docker-run.sh start

# Stop all services
./docker-run.sh stop

# Restart services
./docker-run.sh restart

# View logs (follow mode)
./docker-run.sh logs

# Check service status
./docker-run.sh status

# Run CLI analysis
./docker-run.sh cli NVDA
./docker-run.sh cli MSFT 2025-11-01

# Verify setup
./docker-run.sh verify

# Clean up everything
./docker-run.sh clean

# Show help
./docker-run.sh help
```

### **Using Docker Compose Directly**

```bash
# Start web UI
docker-compose up -d trading-agents-ui

# View logs
docker-compose logs -f trading-agents-ui

# Stop services
docker-compose down

# Run CLI analysis
docker-compose run --rm trading-agents-cli python main.py --ticker NVDA

# Check status
docker-compose ps
```

---

## 🌐 **Web UI Access**

Once started, access the dashboard at:

**URL**: http://localhost:8000

Features:
- Real-time analysis with progress tracking
- WebSocket-based live updates
- Analysis caching
- Interactive charts and visualizations

---

## 💻 **CLI Usage**

### **Analyze a Stock**

```bash
# Using helper script
./docker-run.sh cli NVDA

# Using docker-compose
docker-compose run --rm trading-agents-cli \
    python main.py --ticker NVDA

# Specific date
./docker-run.sh cli AAPL 2025-11-01

# With debug output
docker-compose run --rm trading-agents-cli \
    python main.py --ticker TSLA --debug
```

### **View Analysis Results**

Results are saved to `./analysis/` directory (persisted via volume mount).

```bash
# List analysis files
ls -lh analysis/

# View specific analysis
cat analysis/analysis_NVDA_2025-11-01.json | jq .
```

---

## 🗂️ **Data Persistence**

The following directories are mounted as volumes for persistence:

```yaml
volumes:
  - ./ui/analysis_cache:/app/ui/analysis_cache  # Web UI cache
  - ./analysis:/app/analysis                     # CLI results
```

This means:
- ✅ Analysis results persist after container restarts
- ✅ Cache is shared between container and host
- ✅ You can access files from both inside and outside the container

---

## 🔧 **Configuration**

### **Environment Variables**

Set in `.env` file:

```bash
# Required
GOOGLE_GENAI_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here

# Optional
FMP_API_KEY=your_fmp_key  # Financial Modeling Prep
ALPHA_VANTAGE_API_KEY=your_av_key  # Alpha Vantage
```

### **Port Mapping**

Default: `8000:8000` (host:container)

To use a different port:

```bash
# Edit docker-compose.yml
ports:
  - "8080:8000"  # Now access at http://localhost:8080
```

Or use environment variable:

```bash
# Set port
export HOST_PORT=8080

# Run with custom port
docker-compose up -d
```

---

## 🏥 **Health Checks**

The container includes health checks:

```bash
# Check container health
docker ps

# Manual health check
docker exec simplified-trading-agents \
    python -c "import requests; print(requests.get('http://localhost:8000/health').json())"
```

Health check endpoint: `http://localhost:8000/health`

---

## 📊 **Monitoring**

### **View Logs**

```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f trading-agents-ui
```

### **Resource Usage**

```bash
# Show resource stats
docker stats simplified-trading-agents

# Container details
docker inspect simplified-trading-agents
```

---

## 🛠️ **Troubleshooting**

### **Container Won't Start**

```bash
# Check logs
docker-compose logs trading-agents-ui

# Verify .env file exists
ls -la .env

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

### **API Connection Issues**

```bash
# Verify environment variables
docker-compose run --rm trading-agents-ui env | grep API

# Test inside container
docker exec -it simplified-trading-agents \
    python verify_setup.py
```

### **Port Already in Use**

```bash
# Find what's using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
docker-compose down
# Edit docker-compose.yml ports to 8080:8000
docker-compose up -d
```

### **Permission Errors**

```bash
# Fix ownership of analysis directories
sudo chown -R $USER:$USER analysis ui/analysis_cache

# Or run as root (not recommended)
docker-compose run --user root trading-agents-ui bash
```

---

## 🔄 **Updates and Rebuilds**

### **Update Code**

```bash
# Pull latest changes
git pull origin mc-sz-integration

# Rebuild image
docker-compose build

# Restart services
docker-compose up -d
```

### **Clean Rebuild**

```bash
# Stop and remove everything
docker-compose down -v

# Remove old images
docker image prune -a

# Rebuild from scratch
docker-compose build --no-cache

# Start fresh
docker-compose up -d
```

---

## 🚢 **Deployment**

### **Production Deployment**

#### **1. Add Production Environment**

Create `.env.production`:

```bash
GOOGLE_GENAI_API_KEY=prod_key_here
NEWSAPI_KEY=prod_key_here
```

#### **2. Use Production Compose File**

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  trading-agents-ui:
    image: your-registry/trading-agents:latest
    restart: always
    env_file:
      - .env.production
    ports:
      - "80:8000"
    healthcheck:
      interval: 60s
      timeout: 15s
      retries: 5
```

#### **3. Deploy**

```bash
# Build and tag for production
docker build -t your-registry/trading-agents:latest .

# Push to registry
docker push your-registry/trading-agents:latest

# Deploy on server
docker-compose -f docker-compose.prod.yml up -d
```

### **Cloud Deployment**

#### **AWS EC2**

```bash
# SSH to EC2 instance
ssh -i key.pem ec2-user@your-instance

# Clone repo
git clone your-repo

# Setup and run
cd simplified_tradingagents
cp .env.example .env
# Edit .env
docker-compose up -d

# Access via: http://your-ec2-ip:8000
```

#### **Google Cloud Run**

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT-ID/trading-agents

# Deploy
gcloud run deploy trading-agents \
    --image gcr.io/PROJECT-ID/trading-agents \
    --port 8000 \
    --set-env-vars GOOGLE_GENAI_API_KEY=xxx,NEWSAPI_KEY=xxx
```

#### **Heroku**

```bash
# Login and create app
heroku login
heroku create your-app-name

# Set buildpack
heroku stack:set container

# Set environment variables
heroku config:set GOOGLE_GENAI_API_KEY=xxx
heroku config:set NEWSAPI_KEY=xxx

# Deploy
git push heroku mc-sz-integration:main
```

---

## 🔒 **Security Best Practices**

1. **Never commit .env file**
   ```bash
   # Verify .env is in .gitignore
   git check-ignore .env
   ```

2. **Use secrets management in production**
   ```bash
   # Docker Swarm
   docker secret create genai_key /path/to/key

   # Kubernetes
   kubectl create secret generic api-keys \
       --from-literal=GOOGLE_GENAI_API_KEY=xxx
   ```

3. **Run as non-root user** (already configured in Dockerfile)

4. **Use HTTPS in production** (add reverse proxy like Nginx)

---

## 📦 **Image Details**

### **Size**

- **Final image**: ~300MB (multi-stage build)
- **Base**: python:3.11-slim
- **Includes**: All dependencies + application code

### **Tags**

```bash
# Local development
simplified-trading-agents:latest

# Production
your-registry/trading-agents:v1.0.0
your-registry/trading-agents:latest
```

### **Build Args**

To customize build:

```dockerfile
# Example: different Python version
docker build --build-arg PYTHON_VERSION=3.10 -t trading-agents .
```

---

## 🧪 **Testing**

```bash
# Run setup verification
docker-compose run --rm trading-agents-ui python verify_setup.py

# Test web UI endpoint
curl http://localhost:8000/health

# Test analysis
docker-compose run --rm trading-agents-cli \
    python main.py --ticker AAPL --debug
```

---

## 📚 **Additional Resources**

- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Main README](README_MC_SZ_INTEGRATION.md)
- [NewsAPI Setup](NEWSAPI_SETUP_GUIDE.md)

---

## 💡 **Tips**

1. **Faster Builds**: Use `.dockerignore` to exclude unnecessary files
2. **Layer Caching**: Place frequently changing files (code) after dependencies
3. **Volume Mounts**: Use volumes for data persistence
4. **Health Checks**: Monitor container health automatically
5. **Resource Limits**: Set memory/CPU limits in production

```yaml
# Example resource limits
services:
  trading-agents-ui:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

---

## 🐛 **Common Issues**

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Change port in docker-compose.yml |
| No API keys | Check .env file exists and has correct keys |
| Import errors | Rebuild image: `docker-compose build --no-cache` |
| Permission denied | Check file ownership: `ls -la analysis/` |
| Container crashes | Check logs: `docker-compose logs` |
| Slow analysis | Reduce news article limits in trading_graph.py |

---

**Ready to Deploy! 🚀**

For questions or issues, check the main documentation or create an issue on GitHub.
