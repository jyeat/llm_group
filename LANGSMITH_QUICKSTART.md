# LangSmith Quick Start - 5 Minutes ⏱️

## What You'll Get

After 5 minutes, you'll be able to:
- ✅ See real-time traces of every agent execution
- ✅ Monitor performance and token usage
- ✅ Debug issues faster with detailed logs
- ✅ Track costs and optimize prompts

## Step-by-Step Instructions

### 1️⃣ Sign Up (2 minutes)

```
1. Go to: https://smith.langchain.com/
2. Click "Sign Up"
3. Use your email or GitHub account
4. Verify email
5. Done! ✅
```

### 2️⃣ Get API Key (1 minute)

```
1. Click profile icon (top right)
2. Settings → API Keys
3. "Create API Key"
4. Name: TradingAgents
5. Copy the key (starts with lsv2_pt_...)
```

### 3️⃣ Add to .env File (1 minute)

Open your `.env` file and add these 4 lines:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=lsv2_pt_YOUR_KEY_HERE
LANGCHAIN_PROJECT=trading-agents
```

**Replace `lsv2_pt_YOUR_KEY_HERE` with your actual key!**

### 4️⃣ Install Package (30 seconds)

```bash
pip install langsmith
```

### 5️⃣ Run Analysis (30 seconds)

```bash
python main.py --ticker NVDA
```

You should see:
```
✅ LangSmith tracing enabled
   Project: trading-agents
   Dashboard: https://smith.langchain.com/...
```

### 6️⃣ View Traces

```
1. Go to: https://smith.langchain.com/
2. Click "Projects" → "trading-agents"
3. See your traces! 🎉
```

## What You'll See in LangSmith

### Dashboard View
```
┌─────────────────────────────────────────────────────┐
│  Trading Agents Project                             │
├─────────────────────────────────────────────────────┤
│  Run: NVDA Analysis - 2025-11-01                    │
│  Status: ✅ Success                                  │
│  Duration: 45.2s                                     │
│  Cost: $0.08                                         │
│  Decision: BUY (78% confidence)                      │
└─────────────────────────────────────────────────────┘
```

### Trace Timeline
```
📰 News Analyst      ████████░░░░░░░░ 8.3s  ✅
📊 Market Analyst    ░░░░░░░░████████████░░░ 12.1s ✅
💰 Fundamental       ░░░░░░░░░░░░████████████████ 15.7s ✅
🐂 Bull Agent        ░░░░░░░░░░░░░░░░░░░░████ 4.2s ✅
🐻 Bear Agent        ░░░░░░░░░░░░░░░░░░░░░░██ 3.8s ✅
👔 Supervisor        ░░░░░░░░░░░░░░░░░░░░░░░█ 1.1s ✅
```

Click any agent to see:
- Input messages
- LLM prompts
- Raw outputs
- Token counts
- Latency breakdown

## Example Trace Details

When you click "News Analyst", you'll see:

**Input:**
```json
{
  "ticker": "NVDA",
  "date": "2025-11-01",
  "lookback_days": 30
}
```

**LLM Calls:**
```
1. Gemini 2.5 Flash - Sentiment Analysis
   Tokens: 1,234 input, 567 output
   Cost: $0.002
   Duration: 2.1s
```

**Output:**
```json
{
  "overall_sentiment": "bullish",
  "confidence_score": 0.82,
  "highlighted_articles": [...]
}
```

## Benefits for Your Project

### 🐛 Debugging
- See exactly where errors occur
- Inspect agent inputs/outputs
- Identify slow steps

### 📊 Performance Monitoring
- Track execution time per agent
- Monitor token usage
- Estimate costs

### 🎓 Learning
- Understand agent workflows
- See how prompts affect outputs
- Learn from successful runs

### 📈 Optimization
- Find bottlenecks
- Reduce unnecessary API calls
- Optimize prompts for cost

## Free Tier Details

✅ **5,000 traces/month** - More than enough for development
✅ **14-day retention** - Keep recent data
✅ **Unlimited projects** - Separate dev/staging/prod
✅ **Full features** - All tools available

## Optional: Disable Tracing

Don't want tracing? No problem! Just don't add the API key to `.env`.

Or set:
```bash
LANGCHAIN_TRACING_V2=false
```

The system works perfectly without LangSmith.

## Need Help?

- **Full Guide:** [LANGSMITH_SETUP.md](LANGSMITH_SETUP.md)
- **LangSmith Docs:** https://docs.smith.langchain.com/
- **Discord:** https://discord.gg/langchain

---

**That's it! You're ready to monitor your trading agents. 🚀**

Now run your analysis and check out the traces in LangSmith!
