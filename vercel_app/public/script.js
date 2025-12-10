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
        alert('Please enter a valid stock symbol');
        return;
    }

    // Reset UI
    dashboard.classList.remove('hidden');
    document.querySelector('.hero').style.marginTop = '2rem';
    analyzeBtn.disabled = true;
    analyzeBtn.querySelector('.btn-text').textContent = 'ANALYZING...';
    
    // Reset cards
    resetCards();
    
    statusSection.classList.remove('hidden');
    updateStatus('INITIALIZING NEURAL NETWORKS...', 5);

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
                        console.error('Error parsing JSON:', e);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Fetch error:', error);
        updateStatus('SYSTEM ERROR: CONNECTION LOST', 0);
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
            updateProgress(data.step);
            break;

        case 'agent_output':
            updateAgentCard(data.role, data.data);
            break;

        case 'debate_result':
            showDebate(data.data.rounds);
            break;

        case 'final_result':
            showFinalResult(data.data);
            break;
            
        case 'error':
            alert('Error: ' + data.message);
            break;
    }
}

function updateStatus(text, progress = null) {
    statusText.textContent = text;
    // Animation effect for text change could be added here
}

function updateProgress(step) {
    const steps = {
        'init': 5,
        'data_analyst': 20,
        'news_researcher': 40,
        'reviewers': 60,
        'debate_start': 75,
        'complete': 100
    };
    
    if (steps[step]) {
        progressFill.style.width = `${steps[step]}%`;
    }
    
    // If it's a debate round, increment slowly
    if (String(step).startsWith('debate_round')) {
        progressFill.style.width = '85%';
    }
}

function updateAgentCard(role, data) {
    const cardId = `card-${role}`;
    const textId = `text-${role}`;
    const scoreId = `score-${role}`;
    
    // Handle Reviewers special aggregation logic if needed, 
    // but here we map directly since backend sends distinct roles
    
    const textEl = document.getElementById(textId);
    if (textEl) {
        // Use marked to parse markdown
        textEl.innerHTML = marked.parse(data.content);
        
        // Remove loader if present
        const card = document.getElementById(cardId);
        const loader = card.querySelector('.loader-line');
        if (loader) loader.style.display = 'none';
    }
    
    const scoreEl = document.getElementById(scoreId);
    if (scoreEl && data.score !== undefined) {
        scoreEl.textContent = data.score.toFixed(1);
    }
}

function showDebate(rounds) {
    const section = document.getElementById('debateSection');
    const container = document.getElementById('debateContainer');
    section.classList.remove('hidden');
    container.innerHTML = '';
    
    rounds.forEach(round => {
        // Moderator context
        const modItem = document.createElement('div');
        modItem.className = 'debate-item moderator';
        modItem.innerHTML = `<strong>MODERATOR (ROUND ${round.round}):</strong><br>${round.moderator}`;
        container.appendChild(modItem);
        
        // Bull
        const bullItem = document.createElement('div');
        bullItem.className = 'debate-item bull';
        bullItem.innerHTML = `<strong>BULL ARGUMENT:</strong><br>${round.bull}`;
        container.appendChild(bullItem);
        
        // Bear
        const bearItem = document.createElement('div');
        bearItem.className = 'debate-item bear';
        bearItem.innerHTML = `<strong>BEAR ARGUMENT:</strong><br>${round.bear}`;
        container.appendChild(bearItem);
    });
}

function showFinalResult(data) {
    const card = document.getElementById('finalResult');
    card.classList.remove('hidden');
    
    // Animate transition
    card.style.opacity = '0';
    setTimeout(() => card.style.opacity = '1', 100);
    
    document.getElementById('finalVerdict').textContent = data.recommendation;
    document.getElementById('finalVerdict').className = `verdict text-${getColorForVerdict(data.recommendation)}`;
    
    document.getElementById('confidenceLevel').textContent = `${data.confidence} CONFIDENCE`;
    document.getElementById('finalDesc').textContent = data.brief;
    
    document.getElementById('finalDataScore').textContent = data.scores.data_analyst_score?.toFixed(1) || '-';
    
    const diff = data.scores.score_diff;
    document.getElementById('finalConsensus').textContent = diff < 2 ? 'HIGH' : (diff < 4 ? 'MODERATE' : 'LOW');
}

function getColorForVerdict(verdict) {
    if (verdict.includes('买入') || verdict.includes('Buy')) return 'green';
    if (verdict.includes('卖出') || verdict.includes('Sell')) return 'red';
    return 'blue'; // Hold
}

function resetCards() {
    ['data_analyst', 'news_researcher', 'bull_reviewer', 'bear_reviewer'].forEach(role => {
        document.getElementById(`text-${role}`).textContent = 'Waiting for process...';
        const scoreEl = document.getElementById(`score-${role}`);
        if (scoreEl) scoreEl.textContent = '--';
        
        // Show loader
        const card = document.getElementById(`card-${role}`);
        if (!card.querySelector('.loader-line')) {
            const loader = document.createElement('div');
            loader.className = 'loader-line';
            card.querySelector('.agent-content').prepend(loader);
        } else {
             card.querySelector('.loader-line').style.display = 'block';
        }
    });
    
    document.getElementById('finalResult').classList.add('hidden');
    document.getElementById('debateSection').classList.add('hidden');
}
