/**
 * Trading Agents Dashboard - Frontend JavaScript
 * Handles WebSocket communication, UI updates, and animations
 */

// State
let ws = null;
let currentResults = null;
let currentTab = 'market_analyst';

// DOM Elements
const analyzeBtn = document.getElementById('analyzeBtn');
const tickerInput = document.getElementById('ticker');
const dateInput = document.getElementById('date');
const progressSection = document.getElementById('progressSection');
const progressBar = document.getElementById('progressBar');
const progressPercentage = document.getElementById('progressPercentage');
const progressMessage = document.getElementById('progressMessage');
const resultsSection = document.getElementById('resultsSection');
const decisionSection = document.getElementById('decisionSection');
const agentContent = document.getElementById('agentContent');
const tabList = document.getElementById('tabList');
const tabIndicator = document.getElementById('tabIndicator');
const mouseLight = document.getElementById('mouseLight');
const themeToggle = document.getElementById('themeToggle');
const exportBtn = document.getElementById('exportBtn');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');

// Initialize
function init() {
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
    
    // Event listeners
    analyzeBtn.addEventListener('click', startAnalysis);
    themeToggle.addEventListener('click', toggleTheme);
    exportBtn.addEventListener('click', exportReport);
    newAnalysisBtn.addEventListener('click', resetDashboard);
    
    // Check cache on input change
    tickerInput.addEventListener('input', checkCacheOnInput);
    dateInput.addEventListener('change', checkCacheOnInput);
    
    // Tab switching
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
    
    // Mouse light effect
    document.addEventListener('mousemove', (e) => {
        mouseLight.style.transform = `translate(${e.clientX - 150}px, ${e.clientY - 150}px)`;
    });
    
    // Button ripple effect
    document.querySelectorAll('.btn-primary').forEach(btn => {
        btn.addEventListener('click', createRipple);
    });
    
    // Update tab indicator position
    updateTabIndicator();
    
    // Load history sidebar
    loadHistorySidebar();
}

// Check Cache on Input Change
async function checkCacheOnInput() {
    const ticker = tickerInput.value.trim().toUpperCase();
    const date = dateInput.value;
    
    if (!ticker || !date) {
        hideCacheNotification();
        return;
    }
    
    try {
        const response = await fetch(`/api/cache/check?ticker=${ticker}&date=${date}`);
        const data = await response.json();
        
        if (data.has_cache) {
            showCacheNotification(data.cache_data);
        } else {
            hideCacheNotification();
        }
    } catch (error) {
        console.error('Error checking cache:', error);
        hideCacheNotification();
    }
}

// Show Cache Notification
function showCacheNotification(cacheData) {
    let notification = document.getElementById('cacheNotification');
    
    if (!notification) {
        // Create notification element
        notification = document.createElement('div');
        notification.id = 'cacheNotification';
        notification.className = 'cache-notification';
        
        const inputSection = document.querySelector('.input-section');
        inputSection.appendChild(notification);
    }
    
    const cachedTime = new Date(cacheData.cached_at);
    const timeAgo = getTimeAgo(cachedTime);
    
    notification.innerHTML = `
        <div class="cache-notification-content">
            <span class="cache-icon">💾</span>
            <div class="cache-info">
                <strong>Cached Analysis Available</strong>
                <span>Decision: ${cacheData.decision.toUpperCase()} | Confidence: ${(cacheData.confidence * 100).toFixed(0)}% | ${timeAgo}</span>
            </div>
            <button class="btn-load-cache" onclick="loadCachedAnalysis()">Load Cache</button>
        </div>
    `;
    
    notification.style.display = 'block';
}

// Hide Cache Notification
function hideCacheNotification() {
    const notification = document.getElementById('cacheNotification');
    if (notification) {
        notification.style.display = 'none';
    }
}

// Load Cached Analysis
async function loadCachedAnalysis() {
    const ticker = tickerInput.value.trim().toUpperCase();
    const date = dateInput.value;
    
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Loading Cache...';
    
    try {
        const response = await fetch(`/api/cache/load?ticker=${ticker}&date=${date}`);
        const result = await response.json();
        
        if (result.error) {
            alert('Failed to load cache: ' + result.error);
            return;
        }
        
        // Display results immediately
        currentResults = result;
        
        progressSection.style.display = 'none';
        resultsSection.style.display = 'block';
        decisionSection.style.display = 'block';
        
        displayResults(result);
        
        // Show cache indicator
        showCacheIndicator(result.cached_at);
        
    } catch (error) {
        console.error('Error loading cache:', error);
        alert('Failed to load cached analysis');
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Start Analysis';
    }
}

// Show Cache Indicator
function showCacheIndicator(cachedAt) {
    const cachedTime = new Date(cachedAt);
    const timeAgo = getTimeAgo(cachedTime);
    
    // Add indicator to decision section
    const decisionHeader = document.querySelector('.decision-header');
    if (decisionHeader) {
        let indicator = document.getElementById('cacheIndicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'cacheIndicator';
            indicator.className = 'cache-indicator';
            decisionHeader.appendChild(indicator);
        }
        indicator.innerHTML = `💾 Loaded from cache (${timeAgo})`;
        indicator.style.display = 'block';
    }
}

// Load History Sidebar
async function loadHistorySidebar() {
    try {
        const response = await fetch('/api/cache/list');
        const data = await response.json();
        
        const historyList = document.getElementById('historyList');
        if (!historyList) return;
        
        if (data.cached_analyses.length === 0) {
            historyList.innerHTML = '<div class="history-empty">No analysis history yet</div>';
            return;
        }
        
        historyList.innerHTML = data.cached_analyses.map(item => `
            <div class="history-item" onclick="loadHistoryItem('${item.ticker}', '${item.date}')">
                <div class="history-ticker">${item.ticker}</div>
                <div class="history-date">${item.date}</div>
                <div class="history-decision ${item.decision}">${item.decision.toUpperCase()}</div>
                <div class="history-confidence">${(item.confidence * 100).toFixed(0)}%</div>
            </div>
        `).join('');
        
        // Update stats
        const statsDiv = document.getElementById('historyStats');
        if (statsDiv) {
            statsDiv.innerHTML = `
                <div>Total: ${data.stats.total_analyses}</div>
                <div>Size: ${data.stats.cache_size_mb} MB</div>
            `;
        }
        
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Load History Item
function loadHistoryItem(ticker, date) {
    tickerInput.value = ticker;
    dateInput.value = date;
    checkCacheOnInput();
    loadCachedAnalysis();
}

// Get Time Ago String
function getTimeAgo(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
}

// Toggle History Sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('historySidebar');
    const toggle = document.getElementById('sidebarToggle');
    
    if (sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
        toggle.classList.remove('hidden');
    } else {
        sidebar.classList.add('open');
        toggle.classList.add('hidden');
        // Refresh history when opening
        loadHistorySidebar();
    }
}

// Start Analysis
function startAnalysis() {
    const ticker = tickerInput.value.trim().toUpperCase();
    const date = dateInput.value;
    
    if (!ticker) {
        alert('Please enter a stock ticker');
        return;
    }
    
    if (!date) {
        alert('Please select a date');
        return;
    }
    
    // Show progress section
    progressSection.style.display = 'block';
    resultsSection.style.display = 'none';
    decisionSection.style.display = 'none';
    
    // Reset progress
    resetProgress();
    
    // Disable button
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Analyzing...';
    
    // Connect WebSocket
    connectWebSocket(ticker, date);
}

// WebSocket Connection
function connectWebSocket(ticker, date) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        // Send analysis request
        ws.send(JSON.stringify({ ticker, date }));
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        showError('Connection error. Please try again.');
    };
    
    ws.onclose = () => {
        console.log('WebSocket closed');
    };
}

// Handle WebSocket Messages
function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'start':
            console.log('Analysis started:', data);
            break;
            
        case 'progress':
            updateProgress(data);
            break;
            
        case 'complete':
            handleComplete(data.result);
            break;
            
        case 'error':
            showError(data.message);
            break;
    }
}

// Update Progress
function updateProgress(data) {
    const { agent, progress, message } = data;
    
    // Update progress bar
    progressBar.style.width = `${progress}%`;
    progressPercentage.textContent = `${progress}%`;
    
    // Update message
    progressMessage.textContent = message;
    
    // Update agent status
    updateAgentStatus(agent, progress);
    
    // Animate progress percentage
    animateNumber(progressPercentage, progress);
}

// Update Agent Status with Stage Management
function updateAgentStatus(currentAgent, progress) {
    // Update individual agents
    const agents = document.querySelectorAll('.agent-item');
    
    agents.forEach(item => {
        const agentKey = item.dataset.agent;
        const state = item.querySelector('.agent-state');
        
        if (agentKey === currentAgent) {
            item.classList.add('active');
            state.textContent = '⏳';
        } else if (shouldBeComplete(agentKey, currentAgent)) {
            item.classList.remove('active');
            item.classList.add('complete');
            state.textContent = '✅';
        } else {
            item.classList.remove('active');
            state.textContent = '⏳';
        }
    });
    
    // Update stages
    updateStageStatus(currentAgent, progress);
}

// Update Stage Status
function updateStageStatus(currentAgent, progress) {
    const stage1Agents = ['market_analyst', 'fundamentals_analyst', 'news_analyst'];
    const stage2Agents = ['bull_debater', 'bear_debater'];
    const stage3Agents = ['supervisor'];
    
    const stage1 = document.getElementById('stage1');
    const stage2 = document.getElementById('stage2');
    const stage3 = document.getElementById('stage3');
    
    const stage1Status = document.getElementById('stage1Status');
    const stage2Status = document.getElementById('stage2Status');
    const stage3Status = document.getElementById('stage3Status');
    
    // Stage 1
    if (stage1Agents.includes(currentAgent)) {
        stage1.classList.add('active');
        stage1.classList.remove('complete');
        stage1Status.textContent = '⏳';
    } else if (progress > 45) {
        stage1.classList.remove('active');
        stage1.classList.add('complete');
        stage1Status.textContent = '✅';
    }
    
    // Stage 2
    if (stage2Agents.includes(currentAgent)) {
        stage2.classList.add('active');
        stage2.classList.remove('complete');
        stage2Status.textContent = '⏳';
    } else if (progress > 75) {
        stage2.classList.remove('active');
        stage2.classList.add('complete');
        stage2Status.textContent = '✅';
    }
    
    // Stage 3
    if (stage3Agents.includes(currentAgent)) {
        stage3.classList.add('active');
        stage3.classList.remove('complete');
        stage3Status.textContent = '⏳';
    } else if (progress >= 100) {
        stage3.classList.remove('active');
        stage3.classList.add('complete');
        stage3Status.textContent = '✅';
    }
}

// Check if agent should be marked complete
function shouldBeComplete(agentKey, currentAgent) {
    const order = ['market_analyst', 'fundamentals_analyst', 'news_analyst', 
                   'bull_debater', 'bear_debater', 'supervisor'];
    const currentIndex = order.indexOf(currentAgent);
    const agentIndex = order.indexOf(agentKey);
    return agentIndex < currentIndex;
}

// Handle Analysis Complete
function handleComplete(result) {
    currentResults = result;
    
    // Hide progress, show results
    setTimeout(() => {
        progressSection.style.display = 'none';
        resultsSection.style.display = 'block';
        decisionSection.style.display = 'block';
        
        // Display results
        displayResults(result);
        
        // Show fireworks
        triggerFireworks();
        
        // Reset button
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Start Analysis';
    }, 1000);
}

// Display Results
function displayResults(result) {
    // Display final decision
    displayDecision(result);
    
    // Display first tab content
    switchTab('market_analyst');
}

// Display Decision
function displayDecision(result) {
    const { decision, confidence, rationale } = result;
    
    const decisionBadge = document.getElementById('decisionBadge');
    const decisionAction = document.getElementById('decisionAction');
    const confidenceValue = document.getElementById('confidenceValue');
    const confidenceCircle = document.getElementById('confidenceCircle');
    const decisionRationale = document.getElementById('decisionRationale');
    
    // Set decision
    decisionAction.textContent = decision.toUpperCase();
    decisionBadge.className = `decision-badge ${decision.toLowerCase()}`;
    
    // Animate confidence
    const confidencePercent = Math.round(confidence * 100);
    animateNumber(confidenceValue, confidencePercent, '%');
    
    // Animate confidence ring
    const circumference = 283;
    const offset = circumference - (circumference * confidence);
    confidenceCircle.style.strokeDashoffset = offset;
    
    // Set rationale
    decisionRationale.textContent = rationale || 'Analysis complete.';
}

// Switch Tab
function switchTab(tabKey) {
    currentTab = tabKey;
    
    // Update active tab
    document.querySelectorAll('.tab').forEach(tab => {
        if (tab.dataset.tab === tabKey) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Update indicator
    updateTabIndicator();
    
    // Display content
    displayTabContent(tabKey);
}

// Update Tab Indicator
function updateTabIndicator() {
    const activeTab = document.querySelector('.tab.active');
    if (activeTab) {
        const { offsetLeft, offsetWidth } = activeTab;
        tabIndicator.style.left = `${offsetLeft}px`;
        tabIndicator.style.width = `${offsetWidth}px`;
    }
}

// Display Tab Content
function displayTabContent(tabKey) {
    if (!currentResults || !currentResults.agents) {
        agentContent.innerHTML = '<div class="content-loading"><p>No data available</p></div>';
        return;
    }
    
    const agentData = currentResults.agents[tabKey] || {};
    
    // Build content HTML
    let html = '<div class="agent-data">';
    
    // Title
    const titles = {
        'market_analyst': 'Market Analysis',
        'fundamentals_analyst': 'Fundamental Analysis',
        'news_analyst': 'News Analysis',
        'bull_debater': 'Bullish Case',
        'bear_debater': 'Bearish Case',
        'supervisor': 'Final Recommendation'
    };
    
    html += `<h2 style="margin-bottom: 20px; color: var(--accent-blue);">${titles[tabKey]}</h2>`;
    
    // Display data based on agent type
    if (tabKey === 'market_analyst') {
        html += buildMarketAnalystContent(agentData);
    } else if (tabKey === 'fundamentals_analyst') {
        html += buildFundamentalsContent(agentData);
    } else if (tabKey === 'news_analyst') {
        html += buildNewsContent(agentData);
    } else if (tabKey === 'bull_debater') {
        html += buildBullContent(agentData);
    } else if (tabKey === 'bear_debater') {
        html += buildBearContent(agentData);
    } else if (tabKey === 'supervisor') {
        html += buildSupervisorContent(agentData);
    }
    
    html += '</div>';
    
    agentContent.innerHTML = html;
}

// Build Market Analyst Content
function buildMarketAnalystContent(data) {
    let html = '';
    
    if (data.market_sentiment) {
        html += `<div class="data-section">
            <h3>Market Sentiment</h3>
            <div class="data-grid">
                <div class="data-item">
                    <div class="data-label">Sentiment</div>
                    <div class="data-value ${getSentimentClass(data.market_sentiment)}">${data.market_sentiment}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Confidence</div>
                    <div class="data-value">${formatPercent(data.confidence_score)}</div>
                </div>
            </div>
        </div>`;
    }
    
    if (data.analysis_summary) {
        html += `<div class="data-section">
            <h3>Summary</h3>
            <p style="color: var(--text-secondary); line-height: 1.8;">${data.analysis_summary}</p>
        </div>`;
    }
    
    // Technical indicators
    if (data.technical_indicators) {
        html += buildDataSection('Technical Indicators', data.technical_indicators);
    }
    
    return html || '<p>No market analysis data available.</p>';
}

// Build Fundamentals Content
function buildFundamentalsContent(data) {
    let html = '';
    
    if (data.fundamental_rating) {
        html += `<div class="data-section">
            <h3>Fundamental Rating</h3>
            <div class="data-grid">
                <div class="data-item">
                    <div class="data-label">Rating</div>
                    <div class="data-value">${data.fundamental_rating}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Confidence</div>
                    <div class="data-value">${formatPercent(data.confidence_score)}</div>
                </div>
            </div>
        </div>`;
    }
    
    if (data.analysis_summary) {
        html += `<div class="data-section">
            <h3>Summary</h3>
            <p style="color: var(--text-secondary); line-height: 1.8;">${data.analysis_summary}</p>
        </div>`;
    }
    
    // Financial health
    if (data.financial_health) {
        html += buildDataSection('Financial Health', data.financial_health);
    }
    
    // Valuation
    if (data.valuation) {
        html += buildDataSection('Valuation', data.valuation);
    }
    
    return html || '<p>No fundamental analysis data available.</p>';
}

// Build News Content
function buildNewsContent(data) {
    let html = '';
    
    // Overall Sentiment
    if (data.overall_sentiment) {
        html += `<div class="data-section">
            <h3>Overall Sentiment</h3>
            <div class="data-grid">
                <div class="data-item">
                    <div class="data-label">Sentiment</div>
                    <div class="data-value ${getSentimentClass(data.overall_sentiment)}">${data.overall_sentiment}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Confidence</div>
                    <div class="data-value">${formatPercent(data.confidence_score)}</div>
                </div>
            </div>
        </div>`;
    }
    
    // Analysis Summary
    if (data.analysis_summary) {
        html += `<div class="data-section">
            <h3>Summary</h3>
            <p style="color: var(--text-secondary); line-height: 1.8;">${data.analysis_summary}</p>
        </div>`;
    }
    
    // Sentiment Breakdown
    if (data.sentiment_breakdown) {
        html += `<div class="data-section">
            <h3>Sentiment Breakdown</h3>
            <div class="data-grid">
                <div class="data-item">
                    <div class="data-label">Company News</div>
                    <div class="data-value ${getSentimentClass(data.sentiment_breakdown.company_sentiment)}">${data.sentiment_breakdown.company_sentiment}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Industry News</div>
                    <div class="data-value ${getSentimentClass(data.sentiment_breakdown.industry_sentiment)}">${data.sentiment_breakdown.industry_sentiment}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Macro News</div>
                    <div class="data-value ${getSentimentClass(data.sentiment_breakdown.macro_sentiment)}">${data.sentiment_breakdown.macro_sentiment}</div>
                </div>
            </div>
        </div>`;
    }
    
    // Key Themes
    if (data.key_themes && data.key_themes.length > 0) {
        html += `<div class="data-section">
            <h3>Key Themes</h3>
            <ul style="color: var(--text-secondary); line-height: 1.8;">
                ${data.key_themes.map(theme => `<li>${theme}</li>`).join('')}
            </ul>
        </div>`;
    }
    
    // Highlighted Articles (with direct links to sources)
    if (data.highlighted_articles && data.highlighted_articles.length > 0) {
        html += `<div class="data-section">
            <h3>📰 Top News Articles (Click to Read Full Article)</h3>
            <div style="display: flex; flex-direction: column; gap: 15px;">`;

        data.highlighted_articles.forEach(article => {
            const sentimentColor = article.sentiment === 'bullish' ? 'var(--accent-green)' :
                                  article.sentiment === 'bearish' ? 'var(--accent-red)' :
                                  'var(--accent-yellow)';

            const impactBadge = article.impact_scope === 'company' ? '🏢 Company' :
                               article.impact_scope === 'macro' ? '🌍 Macro' :
                               '📊 Industry';

            const relevancePercent = (article.relevance_score * 100).toFixed(0);

            html += `
                <div style="padding: 15px; background: rgba(255,255,255,0.02); border-radius: 8px; border-left: 3px solid ${sentimentColor};">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
                        <div class="data-value ${getSentimentClass(article.sentiment)}" style="font-size: 0.85em;">${article.sentiment}</div>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            <span style="color: var(--text-muted); font-size: 0.8em;">${impactBadge}</span>
                            <span style="color: var(--accent-blue); font-size: 0.8em;">Relevance: ${relevancePercent}%</span>
                        </div>
                    </div>
                    <a href="${article.url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
                        <h4 style="color: var(--accent-blue); margin: 8px 0; font-size: 1em; cursor: pointer; transition: color 0.2s;"
                            onmouseover="this.style.color='var(--accent-yellow)'"
                            onmouseout="this.style.color='var(--accent-blue)'">
                            ${article.title} 🔗
                        </h4>
                    </a>
                    <p style="color: var(--text-secondary); font-size: 0.9em; line-height: 1.6; margin: 8px 0;">${article.summary}</p>
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-top: 8px;">
                        <div style="color: var(--text-muted); font-size: 0.8em;">
                            📅 ${new Date(article.published_at).toLocaleDateString()} |
                            📰 ${article.source}
                        </div>
                        ${article.tags && article.tags.length > 0 ? `
                            <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                                ${article.tags.slice(0, 3).map(tag => `
                                    <span style="background: rgba(59, 130, 246, 0.1); color: var(--accent-blue); padding: 2px 8px; border-radius: 4px; font-size: 0.75em;">
                                        ${tag}
                                    </span>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>`;
        });

        html += `</div></div>`;
    }

    // Legacy format support (old selected_news format)
    else if (data.selected_news && data.selected_news.length > 0) {
        html += `<div class="data-section">
            <h3>Top News Articles</h3>
            <div style="display: flex; flex-direction: column; gap: 15px;">`;

        data.selected_news.forEach(news => {
            const impactColor = news.impact === 'high' ? 'var(--accent-red)' :
                               news.impact === 'medium' ? 'var(--accent-yellow)' :
                               'var(--text-secondary)';

            html += `
                <div style="padding: 15px; background: rgba(255,255,255,0.02); border-radius: 8px; border-left: 3px solid ${impactColor};">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <div class="data-value ${getSentimentClass(news.sentiment)}" style="font-size: 0.85em;">${news.sentiment}</div>
                        <div style="color: ${impactColor}; font-size: 0.85em; text-transform: uppercase;">${news.impact} Impact</div>
                    </div>
                    <h4 style="color: var(--text-primary); margin: 8px 0; font-size: 1em;">${news.headline}</h4>
                    <p style="color: var(--text-secondary); font-size: 0.9em; line-height: 1.6; margin: 8px 0;">${news.summary}</p>
                    <div style="color: var(--text-muted); font-size: 0.8em; margin-top: 8px;">Source: ${news.source}</div>
                </div>`;
        });

        html += `</div></div>`;
    }
    
    // Risk Factors
    if (data.risk_factors && data.risk_factors.length > 0) {
        html += `<div class="data-section">
            <h3>Risk Factors</h3>
            <ul style="color: var(--accent-red); line-height: 1.8;">
                ${data.risk_factors.map(risk => `<li>${risk}</li>`).join('')}
            </ul>
        </div>`;
    }
    
    return html || '<p>No news analysis data available.</p>';
}

// Build Bull Content
function buildBullContent(data) {
    let html = '';
    
    if (data.conviction_score) {
        html += `<div class="data-section">
            <h3>Bull Conviction</h3>
            <div class="data-grid">
                <div class="data-item">
                    <div class="data-label">Conviction</div>
                    <div class="data-value text-success">${formatPercent(data.conviction_score)}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Recommended Action</div>
                    <div class="data-value">${data.recommended_action || 'N/A'}</div>
                </div>
            </div>
        </div>`;
    }
    
    if (data.thesis_summary) {
        html += `<div class="data-section">
            <h3>Thesis Summary</h3>
            <p style="color: var(--text-secondary); line-height: 1.8;">${data.thesis_summary}</p>
        </div>`;
    }
    
    if (data.key_strengths) {
        html += buildListSection('Key Strengths', data.key_strengths);
    }
    
    return html || '<p>No bull case data available.</p>';
}

// Build Bear Content
function buildBearContent(data) {
    let html = '';
    
    if (data.conviction_score) {
        html += `<div class="data-section">
            <h3>Bear Conviction</h3>
            <div class="data-grid">
                <div class="data-item">
                    <div class="data-label">Conviction</div>
                    <div class="data-value text-danger">${formatPercent(data.conviction_score)}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Recommended Action</div>
                    <div class="data-value">${data.recommended_action || 'N/A'}</div>
                </div>
            </div>
        </div>`;
    }
    
    if (data.thesis_summary) {
        html += `<div class="data-section">
            <h3>Thesis Summary</h3>
            <p style="color: var(--text-secondary); line-height: 1.8;">${data.thesis_summary}</p>
        </div>`;
    }
    
    if (data.key_risks) {
        html += buildListSection('Key Risks', data.key_risks);
    }
    
    return html || '<p>No bear case data available.</p>';
}

// Build Supervisor Content
function buildSupervisorContent(data) {
    let html = '';
    
    // Risk-tiered recommendations
    if (data.low_risk_recommendation) {
        html += buildRiskRecommendation('Low Risk', data.low_risk_recommendation, '🛡️');
    }
    
    if (data.medium_risk_recommendation) {
        html += buildRiskRecommendation('Medium Risk', data.medium_risk_recommendation, '⚖️');
    }
    
    if (data.high_risk_recommendation) {
        html += buildRiskRecommendation('High Risk', data.high_risk_recommendation, '🚀');
    }
    
    // Case strengths
    if (data.bull_case_strength !== undefined && data.bear_case_strength !== undefined) {
        html += `<div class="data-section">
            <h3>Case Strength Comparison</h3>
            <div class="data-grid">
                <div class="data-item">
                    <div class="data-label">Bull Case Strength</div>
                    <div class="data-value text-success">${data.bull_case_strength}/10</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Bear Case Strength</div>
                    <div class="data-value text-danger">${data.bear_case_strength}/10</div>
                </div>
            </div>
        </div>`;
    }
    
    return html || '<p>No supervisor decision data available.</p>';
}

// Build Risk Recommendation
function buildRiskRecommendation(title, data, icon) {
    return `<div class="data-section">
        <h3>${icon} ${title}</h3>
        <div class="data-grid">
            <div class="data-item">
                <div class="data-label">Action</div>
                <div class="data-value">${data.action || 'N/A'}</div>
            </div>
            <div class="data-item">
                <div class="data-label">Position Size</div>
                <div class="data-value">${data.position_size || 'N/A'}</div>
            </div>
            <div class="data-item">
                <div class="data-label">Entry Strategy</div>
                <div class="data-value">${data.entry_strategy || 'N/A'}</div>
            </div>
            ${data.stop_loss ? `<div class="data-item">
                <div class="data-label">Stop Loss</div>
                <div class="data-value">${data.stop_loss}</div>
            </div>` : ''}
        </div>
        <p style="color: var(--text-secondary); margin-top: 10px; line-height: 1.8;">${data.rationale || ''}</p>
    </div>`;
}

// Build Data Section
function buildDataSection(title, data) {
    let html = `<div class="data-section"><h3>${title}</h3><div class="data-grid">`;
    
    for (const [key, value] of Object.entries(data)) {
        const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        html += `<div class="data-item">
            <div class="data-label">${label}</div>
            <div class="data-value">${formatValue(value)}</div>
        </div>`;
    }
    
    html += '</div></div>';
    return html;
}

// Build List Section
function buildListSection(title, items) {
    if (!Array.isArray(items) || items.length === 0) return '';
    
    let html = `<div class="data-section"><h3>${title}</h3><ul style="color: var(--text-secondary); line-height: 1.8;">`;
    items.forEach(item => {
        html += `<li>${item}</li>`;
    });
    html += '</ul></div>';
    return html;
}

// Utility Functions
function formatValue(value) {
    if (typeof value === 'number') {
        return value.toFixed(2);
    }
    return value;
}

function formatPercent(value) {
    if (typeof value === 'number') {
        return `${(value * 100).toFixed(1)}%`;
    }
    return value;
}

function getSentimentClass(sentiment) {
    const s = sentiment.toLowerCase();
    if (s.includes('bullish') || s.includes('positive')) return 'text-success';
    if (s.includes('bearish') || s.includes('negative')) return 'text-danger';
    return 'text-warning';
}

// Animate Number
function animateNumber(element, target, suffix = '') {
    const duration = 1000;
    const start = 0;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const current = Math.floor(start + (target - start) * progress);
        
        element.textContent = current + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// Reset Progress
function resetProgress() {
    progressBar.style.width = '0%';
    progressPercentage.textContent = '0%';
    progressMessage.textContent = 'Initializing...';
    
    // Reset agents
    document.querySelectorAll('.agent-item').forEach(item => {
        item.classList.remove('active', 'complete');
        item.querySelector('.agent-state').textContent = '⏳';
    });
    
    // Reset stages
    document.querySelectorAll('.workflow-stage').forEach(stage => {
        stage.classList.remove('active', 'complete');
    });
    
    // Reset stage statuses
    ['stage1Status', 'stage2Status', 'stage3Status'].forEach(id => {
        const elem = document.getElementById(id);
        if (elem) elem.textContent = '⏳';
    });
}

// Reset Dashboard
function resetDashboard() {
    progressSection.style.display = 'none';
    resultsSection.style.display = 'none';
    decisionSection.style.display = 'none';
    currentResults = null;
}

// Trigger Fireworks
function triggerFireworks() {
    const fireworks = document.getElementById('fireworks');
    
    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            createFirework(fireworks);
        }, i * 300);
    }
}

function createFirework(container) {
    const x = Math.random() * window.innerWidth;
    const y = Math.random() * window.innerHeight * 0.5;
    
    for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.className = 'firework';
        
        const angle = (Math.PI * 2 * i) / 30;
        const velocity = 50 + Math.random() * 50;
        const tx = Math.cos(angle) * velocity;
        const ty = Math.sin(angle) * velocity;
        
        particle.style.left = x + 'px';
        particle.style.top = y + 'px';
        particle.style.background = `hsl(${Math.random() * 360}, 100%, 50%)`;
        particle.style.setProperty('--tx', tx + 'px');
        particle.style.setProperty('--ty', ty + 'px');
        
        container.appendChild(particle);
        
        setTimeout(() => particle.remove(), 1000);
    }
}

// Create Ripple Effect
function createRipple(e) {
    const button = e.currentTarget;
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('btn-ripple');
    
    button.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
}

// Toggle Theme
function toggleTheme() {
    document.body.classList.toggle('light-theme');
    const icon = document.querySelector('.theme-icon');
    icon.textContent = document.body.classList.contains('light-theme') ? '☀️' : '🌙';
}

// Export Report
function exportReport() {
    if (!currentResults) {
        alert('No analysis results to export');
        return;
    }
    
    const dataStr = JSON.stringify(currentResults, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analysis_${currentResults.ticker}_${currentResults.date}.json`;
    link.click();
    URL.revokeObjectURL(url);
}

// Show Error
function showError(message) {
    alert(`Error: ${message}`);
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = 'Start Analysis';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);

