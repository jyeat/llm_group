# LangSmith Integration Guide

This guide shows you how to integrate LangSmith for monitoring, debugging, and tracing your Trading Agents system.

## 📊 What is LangSmith?

LangSmith is a platform for debugging, testing, and monitoring LLM applications. It provides:

- **Real-time Tracing**: See each agent's execution step-by-step
- **Performance Monitoring**: Track latency, token usage, and costs
- **Debugging Tools**: Identify errors and bottlenecks in your agent workflows
- **Analytics**: Understand how your agents are performing over time

## 🚀 Quick Start (5 minutes)

### Step 1: Create LangSmith Account

1. Go to [https://smith.langchain.com/](https://smith.langchain.com/)
2. Click **"Sign Up"**
3. Sign up with your email or GitHub account
4. Verify your email
5. You'll get a **FREE account** with generous limits

### Step 2: Get Your API Key

1. After logging in, click your **profile icon** (top right)
2. Go to **Settings** → **API Keys**
3. Click **"Create API Key"**
4. Name it: `TradingAgents` or similar
5. **Copy the API key** (you won't see it again!)

### Step 3: Create a Project

1. In LangSmith dashboard, click **"Projects"** in the sidebar
2. Click **"New Project"**
3. Name it: `trading-agents`
4. Click **"Create"**

### Step 4: Update Your `.env` File

Add these lines to your `.env` file (or copy from `.env.example`):

```bash
# LangSmith Configuration (OPTIONAL - for tracing and monitoring)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=lsv2_pt_xxxxxxxxxxxxxxxxxxxxxxxx
LANGCHAIN_PROJECT=trading-agents
```

**Replace** `lsv2_pt_xxxxxxxxxxxxxxxxxxxxxxxx` with your actual API key from Step 2.

### Step 5: Install LangSmith Package

```bash
cd "c:\Users\tongj\Documents\04 SMU Masters\CS614- Gen AI and LLM\Group_Assignment\simplified_tradingagents"
pip install langsmith
```

### Step 6: Run Your Analysis

That's it! Now run your analysis normally:

**CLI:**
```bash
python main.py --ticker NVDA
```

**Web UI:**
```bash
python ui/web_app.py
```

LangSmith will automatically trace all agent executions!

## 📈 View Your Traces

After running an analysis:

1. Go to [https://smith.langchain.com/](https://smith.langchain.com/)
2. Click **"Projects"** → **"trading-agents"**
3. You'll see all your analysis runs with:
   - Total execution time
   - Number of LLM calls
   - Token usage
   - Cost estimates
   - Success/failure status

4. Click on any run to see:
   - **Timeline view**: Visual representation of agent execution
   - **Tree view**: Hierarchical view of all steps
   - **Logs**: Detailed input/output for each agent
   - **Metadata**: Ticker, date, decision, confidence

## 🔍 What Gets Traced?

LangSmith automatically traces:

### 1. **News Analyst Agent**
- NewsAPI requests
- Article filtering and ranking
- Sentiment analysis
- Output: Selected news articles with sentiment

### 2. **Market Analyst Agent**
- Technical indicator calculations
- Price action analysis
- Volume analysis
- Output: Market sentiment and confidence

### 3. **Fundamental Analyst Agent**
- Financial data retrieval
- Ratio calculations (P/E, debt-to-equity, etc.)
- Valuation analysis
- Output: Financial health assessment

### 4. **Bull Agent**
- Bullish argument construction
- Risk/reward analysis
- Output: Bull thesis and conviction score

### 5. **Bear Agent**
- Bearish argument construction
- Downside analysis
- Output: Bear thesis and conviction score

### 6. **Supervisor Agent**
- Final decision synthesis
- Risk-tiered recommendations
- Output: Trading decision with confidence

## 📊 Example Trace View

When you click on a run in LangSmith, you'll see something like:

```
Run: NVDA Analysis (2025-11-01)
Duration: 45.2s
Status: ✅ Success
Cost: $0.08

Timeline:
├─ 📰 News Analyst (8.3s) ✅
│  ├─ NewsAPI Fetch (2.1s)
│  ├─ Article Filtering (0.8s)
│  └─ Sentiment Analysis (5.4s)
│
├─ 📊 Market Analyst (12.1s) ✅
│  ├─ Fetch Price Data (3.2s)
│  ├─ Calculate Indicators (2.9s)
│  └─ Technical Analysis (6.0s)
│
├─ 💰 Fundamental Analyst (15.7s) ✅
│  ├─ Fetch Financial Data (4.1s)
│  ├─ Calculate Ratios (2.3s)
│  └─ Valuation Analysis (9.3s)
│
├─ 🐂 Bull Agent (4.2s) ✅
│  └─ Build Bull Case (4.2s)
│
├─ 🐻 Bear Agent (3.8s) ✅
│  └─ Build Bear Case (3.8s)
│
└─ 👔 Supervisor (1.1s) ✅
   └─ Final Decision (1.1s)

Result: BUY (Confidence: 78%)
```

## 🛠️ Advanced Features

### Filter by Decision Type

In LangSmith, you can filter runs by:
- Decision: BUY, SELL, HOLD
- Ticker symbol
- Date range
- Execution time
- Success/failure

### Compare Runs

Select multiple runs to compare:
- Performance differences
- Decision consistency
- Token usage
- Latency

### Set Up Alerts

Get notified when:
- Analysis fails
- Execution time exceeds threshold
- Token costs are too high

### Export Data

Export traces as:
- JSON for analysis
- CSV for spreadsheets
- Share links with team members

## 🔒 Security & Privacy

- **API Key**: Keep your `LANGCHAIN_API_KEY` secret (don't commit to git)
- **Data**: LangSmith stores traces in the cloud (read their privacy policy)
- **Opt-out**: Set `LANGCHAIN_TRACING_V2=false` to disable tracing anytime

## 🆓 Free Tier Limits

LangSmith free tier includes:
- **5,000 traces/month** (plenty for development)
- **14-day data retention**
- **Unlimited projects**
- **Full feature access**

For more, see: [LangSmith Pricing](https://www.langchain.com/pricing)

## 🐛 Troubleshooting

### Issue: No traces showing up

**Solution:**
1. Verify API key is correct in `.env`
2. Check `LANGCHAIN_TRACING_V2=true` is set
3. Make sure you installed `langsmith`: `pip install langsmith`
4. Check console output for "✅ LangSmith tracing enabled"

### Issue: "API key invalid" error

**Solution:**
1. Go to LangSmith → Settings → API Keys
2. Create a new API key
3. Update `.env` with the new key
4. Restart your application

### Issue: Traces delayed

**Solution:**
- Traces may take 10-30 seconds to appear in dashboard
- Refresh the page
- Check your internet connection

### Issue: Don't want to use LangSmith

**Solution:**
Simply don't add `LANGCHAIN_API_KEY` to your `.env` file. The system will run normally without tracing.

You'll see this message:
```
⚠️  LangSmith API key not found. Tracing disabled.
```

## 📚 Additional Resources

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangSmith Tutorial Videos](https://www.youtube.com/@LangChain)
- [LangChain Discord Community](https://discord.gg/langchain)

## 💡 Pro Tips

1. **Use descriptive project names**: Create separate projects for dev/staging/production
2. **Add metadata**: The system automatically adds ticker, date, and decision to traces
3. **Monitor costs**: Track token usage to optimize your prompts
4. **Debug faster**: Use the timeline view to identify slow agents
5. **Share insights**: Send trace URLs to teammates for collaboration

## 🎯 What's Next?

After setting up LangSmith:

1. Run a few analyses and explore the traces
2. Identify bottlenecks (which agents take longest?)
3. Optimize prompts to reduce token usage
4. Set up monitoring for production deployments
5. Use insights to improve your trading strategy

---

**Need Help?**

- Check [LangSmith Docs](https://docs.smith.langchain.com/)
- Ask in [LangChain Discord](https://discord.gg/langchain)
- Open an issue in this repository

Happy Tracing! 📊
