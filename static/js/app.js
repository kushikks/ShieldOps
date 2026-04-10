// ShieldOps Frontend Application
const API_BASE = window.location.origin;

// DOM Elements
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const simulationForm = document.getElementById('simulationForm');
const severitySlider = document.getElementById('severity');
const severityValue = document.getElementById('severityValue');
const resultsPanel = document.getElementById('resultsPanel');
const insightsPanel = document.getElementById('insightsPanel');
const historySection = document.getElementById('historySection');

// Update severity value display
severitySlider.addEventListener('input', (e) => {
    severityValue.textContent = e.target.value;
});

// Check system health on load
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            statusDot.classList.add('active');
            statusDot.classList.remove('inactive');
            statusText.textContent = 'System Active';
        } else {
            throw new Error('System unhealthy');
        }
    } catch (error) {
        statusDot.classList.add('inactive');
        statusDot.classList.remove('active');
        statusText.textContent = 'System Down';
        console.error('Health check failed:', error);
    }
}

// Handle form submission
simulationForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const disasterType = document.getElementById('disasterType').value;
    const severity = parseInt(document.getElementById('severity').value);
    const population = parseInt(document.getElementById('population').value);
    
    // Disable button during request
    const submitBtn = document.getElementById('simulateBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Simulating...';
    
    try {
        const response = await fetch(`${API_BASE}/api/simulate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                disaster_type: disasterType,
                severity: severity,
                population: population
            })
        });
        
        if (!response.ok) {
            throw new Error('Simulation failed');
        }
        
        const data = await response.json();
        displayResults(data);
        await loadHistory();
        
    } catch (error) {
        alert('Simulation failed: ' + error.message);
        console.error('Simulation error:', error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Run Simulation';
    }
});

// Display simulation results
function displayResults(data) {
    // Show panels
    resultsPanel.style.display = 'block';
    insightsPanel.style.display = 'block';
    
    // Update risk score
    document.getElementById('riskScore').textContent = data.risk_score.toFixed(1);
    
    // Update risk meter
    const riskMeterFill = document.getElementById('riskMeterFill');
    riskMeterFill.style.width = data.risk_score + '%';
    
    // Update priority badge
    const priorityBadge = document.getElementById('priorityBadge');
    priorityBadge.textContent = data.priority;
    priorityBadge.className = 'priority-badge ' + data.priority.toLowerCase();
    
    // Update recommendation
    document.getElementById('recommendationText').textContent = data.recommendation;
    
    // Update gauge
    updateGauge(data.risk_score);
    
    // Update details
    document.getElementById('detailType').textContent = data.disaster_type.charAt(0).toUpperCase() + data.disaster_type.slice(1);
    document.getElementById('detailSeverity').textContent = data.severity + '/10';
    document.getElementById('detailPopulation').textContent = data.population.toLocaleString();
    
    // Apply color theme based on priority
    applyTheme(data.priority);
}

// Update gauge visualization
function updateGauge(riskScore) {
    const gaugeFill = document.getElementById('gaugeFill');
    const gaugeText = document.getElementById('gaugeText');
    
    // Calculate stroke-dashoffset (251.2 is the path length)
    const offset = 251.2 - (251.2 * riskScore / 100);
    gaugeFill.style.strokeDashoffset = offset;
    
    // Update color based on risk
    let color;
    if (riskScore >= 70) {
        color = '#f44336';
    } else if (riskScore >= 40) {
        color = '#FFC107';
    } else {
        color = '#4CAF50';
    }
    gaugeFill.style.stroke = color;
    
    // Update text
    gaugeText.textContent = Math.round(riskScore) + '%';
}

// Apply theme based on priority
function applyTheme(priority) {
    const resultsPanel = document.getElementById('resultsPanel');
    
    // Remove existing theme classes
    resultsPanel.classList.remove('theme-low', 'theme-medium', 'theme-high');
    
    // Add new theme class
    resultsPanel.classList.add('theme-' + priority.toLowerCase());
}

// Load simulation history
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/api/history`);
        const data = await response.json();
        
        if (data.history && data.history.length > 0) {
            historySection.style.display = 'block';
            displayHistory(data.history);
        }
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// Display history items
function displayHistory(history) {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '';
    
    // Reverse to show newest first
    const reversedHistory = [...history].reverse();
    
    reversedHistory.forEach(item => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        historyItem.innerHTML = `
            <div class="history-item-header">
                <span class="history-disaster">${item.disaster_type}</span>
                <span class="history-priority ${item.priority.toLowerCase()}">${item.priority}</span>
            </div>
            <div class="history-risk">Risk: ${item.risk_score.toFixed(1)}</div>
        `;
        
        historyList.appendChild(historyItem);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    loadHistory();
    
    // Refresh health check every 30 seconds
    setInterval(checkHealth, 30000);
});
