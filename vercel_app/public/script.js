const API_URL = '/api/analyze';

// DOM Elements
const symbolInput = document.getElementById('symbolInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const dashboard = document.getElementById('dashboard');
const statusSection = document.getElementById('statusSection');
const statusText = document.getElementById('statusText');
const progressFill = document.getElementById('progressFill');

// Config
const thresholdInput = document.getElementById('threshold');
const thresholdVal = document.getElementById('thresholdVal');
const maxRoundsInput = document.getElementById('maxRounds');
const maxRoundsVal = document.getElementById('maxRoundsVal');

// Event Listeners
analyzeBtn.addEventListener('click', startAnalysis);
thresholdInput.addEventListener('input', (e) => thresholdVal.textContent = e.target.value);
maxRoundsInput.addEventListener('input', (e) => maxRoundsVal.textContent = e.target.value);

function toggleConfig() {
    const panel = document.getElementById('configPanel');
    panel.classList.toggle('hidden');
}

async function startAnalysis() {
    const symbol = symbolInput.value.trim();
    if (!symbol || symbol.length < 6) {
        alert('Please enter a valid 6-digit stock symbol');
        return;
    }

    // Reset UI
    dashboard.classList.remove('hidden');
    document.querySelector('.hero').style.marginTop = '2rem';
    analyzeBtn.disabled = true;
    analyzeBtn.querySelector('.btn-text').textContent = 'ANALYZING...';

    resetCards();

    statusSection.classList.remove('hidden');
    updateStatus('🚀 INITIALIZING ENHANCED MULTI-AGENT SYSTEM...', 5);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                symbol: symbol,
                debate_threshold: parseFloat(thresholdInput.value),
                max_rounds: parseInt(maxRoundsInput.value),
                api_key: document.getElementById('apiKey').value || null
            })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line

            for (const line of lines) {
                if (line.trim()) {
                    try {
                        const data = JSON.parse(line);
                        handleStreamData(data);
                    } catch (e) {
                        console.error('Error parsing JSON:', e, line);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Fetch error:', error);
        updateStatus('❌ SYSTEM ERROR: CONNECTION LOST', 0);
        alert('Error: ' + error.message + '\n\nPlease ensure the server is running at http://localhost:8000');
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.querySelector('.btn-text').textContent = 'INITIALIZE';
    }
}

function handleStreamData(data) {
    console.log('Stream:', data);

    switch (data.type) {
        case 'status':
            updateStatus(data.message.toUpperCase());
            updateProgress(data.step, data.layer);
            break;

        case 'layer_start':
            updateStatus(`${data.message}`, null);
            break;

        case 'agent_output':
            updateAgentCard(data.role, data.data, data.layer);
            break;

        case 'debate_triggered':
            showDebateTrigger(data.data);
            break;

        case 'risk_assessment':
            updateRiskCards(data.data);
            break;

        case 'final_result':
            showFinalResult(data.data);
            break;

        case 'error':
            alert('❌ Error: ' + data.message);
            console.error('Server error:', data);
            break;
    }
}

function updateStatus(text, progress = null) {
    statusText.innerHTML = text;
    if (progress !== null) {
        progressFill.style.width = `${progress}%`;
    }
}

function updateProgress(step, layer) {
    // Enhanced progress tracking for 4 layers
    const progressMap = {
        'init': 5,
        'initialized': 10,
        // Layer 1 (10-35%)
        'fundamentals_analyst': 15,
        'sentiment_analyst': 20,
        'news_analyst': 25,
        'technical_analyst': 30,
        // Layer 2 (35-55%)
        'researcher_debate': 45,
        // Layer 3 (55-75%)
        'trader': 65,
        // Layer 4 (75-95%)
        'risk_assessment': 80,
        'portfolio_manager': 90,
        'complete': 100
    };

    if (progressMap[step]) {
        progressFill.style.width = `${progressMap[step]}%`;
    } else if (layer) {
        // Layer-based progress
        const layerProgress = { 1: 15, 2: 40, 3: 65, 4: 85 };
        if (layerProgress[layer]) {
            progressFill.style.width = `${layerProgress[layer]}%`;
        }
    }
}

function updateAgentCard(role, data, layer) {
    const cardId = `card-${role}`;
    const textId = `text-${role}`;
    const scoreId = `score-${role}`;

    const textEl = document.getElementById(textId);
    const card = document.getElementById(cardId);

    if (textEl) {
        // Use marked to parse markdown
        textEl.innerHTML = marked.parse(data.content || 'Processing...');

        // Remove loader if present
        if (card) {
            const loader = card.querySelector('.loader-line');
            if (loader) loader.style.display = 'none';

            // Add animation
            card.style.animation = 'pulse 0.3s';
            setTimeout(() => card.style.animation = '', 300);
        }
    }

    const scoreEl = document.getElementById(scoreId);
    if (scoreEl && data.score !== undefined) {
        scoreEl.textContent = data.score.toFixed(1);

        // Color coding
        const score = data.score;
        if (score >= 7) scoreEl.style.color = '#4ade80';
        else if (score >= 5) scoreEl.style.color = '#fbbf24';
        else scoreEl.style.color = '#f87171';
    }

    // Handle trader recommendation
    if (role === 'trader' && data.recommendation) {
        const recEl = document.getElementById('trader-recommendation');
        if (recEl) {
            recEl.textContent = data.recommendation;
            recEl.className = `score-value text-${getColorForVerdict(data.recommendation)}`;
        }
    }
}

function updateRiskCards(riskData) {
    // Update risk assessment cards
    const risks = {
        'aggressive': riskData.aggressive,
        'neutral': riskData.neutral,
        'conservative': riskData.conservative
    };

    for (const [type, content] of Object.entries(risks)) {
        const textEl = document.getElementById(`text-risk-${type}`);
        if (textEl) {
            // Extract key points from content
            const summary = extractRiskSummary(content);
            textEl.textContent = summary;
        }
    }
}

function extractRiskSummary(content) {
    // Extract first 200 chars or first complete sentence
    if (!content) return 'Processing...';
    const lines = content.split('\n').filter(l => l.trim());
    return lines.slice(0, 3).join(' ').substring(0, 200) + (content.length > 200 ? '...' : '');
}

function showDebateTrigger(data) {
    const section = document.getElementById('debateSection');
    const info = document.getElementById('debateInfo');
    section.classList.remove('hidden');
    info.textContent = `Score Difference: ${data.score_diff.toFixed(1)} | ${data.message}`;
}

function showFinalResult(data) {
    const card = document.getElementById('finalResult');
    card.classList.remove('hidden');

    // Animate transition
    card.style.opacity = '0';
    setTimeout(() => card.style.opacity = '1', 100);

    document.getElementById('finalVerdict').textContent = data.recommendation;
    document.getElementById('finalVerdict').className = `verdict text-${getColorForVerdict(data.recommendation)}`;

    document.getElementById('confidenceLevel').textContent = `${data.confidence.toUpperCase()} CONFIDENCE`;
    document.getElementById('confidenceLevel').className = `confidence-badge badge-${data.confidence.toLowerCase()}`;

    // Extract description from content
    const desc = extractDescription(data.content);
    document.getElementById('finalDesc').textContent = desc;

    // Update scores
    if (data.scores) {
        document.getElementById('fundamentalsScore').textContent = data.scores.fundamentals?.toFixed(1) || '-';
        document.getElementById('technicalScore').textContent = data.scores.technical?.toFixed(1) || '-';

        const bullBear = `${data.scores.bullish?.toFixed(1) || '-'} / ${data.scores.bearish?.toFixed(1) || '-'}`;
        document.getElementById('consensusScore').textContent = bullBear;
    }

    // Update position suggestions
    if (data.position_suggestions) {
        document.getElementById('aggressivePos').textContent = data.position_suggestions['激进型'] || data.position_suggestions['Aggressive'] || '-';
        document.getElementById('neutralPos').textContent = data.position_suggestions['稳健型'] || data.position_suggestions['Neutral'] || '-';
        document.getElementById('conservativePos').textContent = data.position_suggestions['保守型'] || data.position_suggestions['Conservative'] || '-';
    }

    // Scroll to result
    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function extractDescription(content) {
    if (!content) return 'Comprehensive analysis complete.';
    // Extract first meaningful paragraph
    const lines = content.split('\n').filter(l => l.trim() && !l.startsWith('#'));
    return lines.slice(0, 2).join(' ').substring(0, 150) + '...';
}

function getColorForVerdict(verdict) {
    const v = verdict.toLowerCase();
    if (v.includes('买入') || v.includes('buy')) return 'green';
    if (v.includes('卖出') || v.includes('sell')) return 'red';
    return 'blue'; // Hold
}

function resetCards() {
    // Reset all agent cards
    const roles = [
        'fundamentals_analyst',
        'sentiment_analyst',
        'news_analyst',
        'technical_analyst',
        'bullish_researcher',
        'bearish_researcher',
        'trader'
    ];

    roles.forEach(role => {
        const textEl = document.getElementById(`text-${role}`);
        if (textEl) textEl.textContent = 'Waiting for initialization...';

        const scoreEl = document.getElementById(`score-${role}`);
        if (scoreEl) scoreEl.textContent = '--';

        // Show loader for layer 1 agents
        if (role.includes('analyst')) {
            const card = document.getElementById(`card-${role}`);
            if (card) {
                let loader = card.querySelector('.loader-line');
                if (!loader) {
                    loader = document.createElement('div');
                    loader.className = 'loader-line';
                    card.querySelector('.agent-content').prepend(loader);
                } else {
                    loader.style.display = 'block';
                }
            }
        }
    });

    // Reset risk cards
    ['aggressive', 'neutral', 'conservative'].forEach(type => {
        const el = document.getElementById(`text-risk-${type}`);
        if (el) el.textContent = 'Waiting...';
    });

    // Reset final result and debate
    document.getElementById('finalResult').classList.add('hidden');
    document.getElementById('debateSection').classList.add('hidden');

    // Reset progress
    progressFill.style.width = '0%';
}
