// ShieldOps Frontend Application
const API_BASE = window.location.origin;

// DOM Elements
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const simulationForm = document.getElementById('simulationForm');
const severitySlider = document.getElementById('severity');
const severityValue = document.getElementById('severityValue');
const resourcesSlider = document.getElementById('resources');
const resourcesValue = document.getElementById('resourcesValue');
const infrastructureSlider = document.getElementById('infrastructure');
const infrastructureValue = document.getElementById('infrastructureValue');
const resultsPanel = document.getElementById('resultsPanel');
const insightsPanel = document.getElementById('insightsPanel');
const historySection = document.getElementById('historySection');
const learningsSection = document.getElementById('learningsSection');

// Store current simulation data
let currentSimulation = null;

// Update slider value displays
severitySlider.addEventListener('input', (e) => {
    severityValue.textContent = e.target.value;
});

resourcesSlider.addEventListener('input', (e) => {
    resourcesValue.textContent = e.target.value;
});

infrastructureSlider.addEventListener('input', (e) => {
    infrastructureValue.textContent = e.target.value;
});

// Update new resources/infrastructure sliders
const newResourcesSlider = document.getElementById('newResources');
const newResourcesValue = document.getElementById('newResourcesValue');
const newInfrastructureSlider = document.getElementById('newInfrastructure');
const newInfrastructureValue = document.getElementById('newInfrastructureValue');

if (newResourcesSlider) {
    newResourcesSlider.addEventListener('input', (e) => {
        newResourcesValue.textContent = e.target.value;
    });
}

if (newInfrastructureSlider) {
    newInfrastructureSlider.addEventListener('input', (e) => {
        newInfrastructureValue.textContent = e.target.value;
    });
}

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
    const resources = parseInt(document.getElementById('resources').value);
    const infrastructure = parseInt(document.getElementById('infrastructure').value);
    
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
                population: population,
                resources_available: resources,
                infrastructure_quality: infrastructure
            })
        });
        
        if (!response.ok) {
            throw new Error('Simulation failed');
        }
        
        const data = await response.json();
        currentSimulation = data;
        displayResults(data);
        await loadHistory();
        await loadLearnings();
        
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
    
    // Display reasoning
    if (data.reasoning) {
        const reasoningList = document.getElementById('reasoningList');
        reasoningList.innerHTML = '';
        data.reasoning.forEach(reason => {
            const item = document.createElement('div');
            item.className = 'reasoning-item';
            item.textContent = reason;
            reasoningList.appendChild(item);
        });
    }
    
    // Update gauge
    updateGauge(data.risk_score);
    
    // Update details
    document.getElementById('detailType').textContent = data.disaster_type.charAt(0).toUpperCase() + data.disaster_type.slice(1);
    document.getElementById('detailSeverity').textContent = data.severity + '/10';
    document.getElementById('detailPopulation').textContent = data.population.toLocaleString();
    document.getElementById('detailResources').textContent = data.resources_available + '%';
    document.getElementById('detailInfrastructure').textContent = data.infrastructure_quality + '%';
    
    // Set up re-evaluation sliders with current values
    if (newResourcesSlider) {
        newResourcesSlider.value = data.resources_available;
        newResourcesValue.textContent = data.resources_available;
    }
    if (newInfrastructureSlider) {
        newInfrastructureSlider.value = data.infrastructure_quality;
        newInfrastructureValue.textContent = data.infrastructure_quality;
    }
    
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
    loadLearnings();
    
    // Load theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
    
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-theme');
            const isDark = document.body.classList.contains('dark-theme');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        });
    }
    
    // Refresh health check every 30 seconds
    setInterval(checkHealth, 30000);
});


// Handle re-evaluation
const reevaluateBtn = document.getElementById('reevaluateBtn');
if (reevaluateBtn) {
    reevaluateBtn.addEventListener('click', async () => {
        if (!currentSimulation) {
            alert('No simulation to re-evaluate');
            return;
        }
        
        const newResources = parseInt(newResourcesSlider.value);
        const newInfrastructure = parseInt(newInfrastructureSlider.value);
        const additionalNotes = document.getElementById('additionalNotes').value;
        
        reevaluateBtn.disabled = true;
        reevaluateBtn.textContent = 'Re-evaluating...';
        
        try {
            const response = await fetch(`${API_BASE}/api/reevaluate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    original_timestamp: currentSimulation.timestamp,
                    new_findings: {
                        resources_available: newResources,
                        infrastructure_quality: newInfrastructure,
                        additional_notes: additionalNotes
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error('Re-evaluation failed');
            }
            
            const data = await response.json();
            displayReevaluationResults(data);
            await loadLearnings();
            
        } catch (error) {
            alert('Re-evaluation failed: ' + error.message);
            console.error('Re-evaluation error:', error);
        } finally {
            reevaluateBtn.disabled = false;
            reevaluateBtn.textContent = 'Re-evaluate Risk';
        }
    });
}

// Display re-evaluation results
function displayReevaluationResults(data) {
    const updated = data.updated_assessment;
    const changes = data.changes;
    
    // CRITICAL: Update current simulation with the NEW timestamp from updated assessment
    // This allows unlimited re-evaluations
    currentSimulation = {
        ...updated,
        timestamp: updated.timestamp  // Use the new timestamp
    };
    
    // Display updated results
    displayResults(updated);
    
    // Show change notification with better formatting
    let changeMessage = `Risk changed by ${changes.risk_change > 0 ? '+' : ''}${changes.risk_change.toFixed(1)} points (${changes.risk_change_percent > 0 ? '+' : ''}${changes.risk_change_percent.toFixed(1)}%)`;
    
    if (changes.priority_changed) {
        changeMessage += `\nPriority: ${changes.old_priority} → ${changes.new_priority}`;
    }
    
    if (data.additional_notes) {
        changeMessage += `\n\nNotes: ${data.additional_notes}`;
    }
    
    // Show notification
    showNotification('Re-evaluation Complete', changeMessage, changes.risk_change < 0 ? 'success' : 'warning');
}

// Load learnings and insights
async function loadLearnings() {
    try {
        const response = await fetch(`${API_BASE}/api/learnings`);
        const data = await response.json();
        
        if (data.insights && data.insights.length > 0) {
            learningsSection.style.display = 'block';
            displayLearnings(data.insights);
        }
    } catch (error) {
        console.error('Failed to load learnings:', error);
    }
}

// Display learnings
function displayLearnings(insights) {
    const insightsContainer = document.getElementById('insightsContainer');
    insightsContainer.innerHTML = '';
    
    insights.forEach(insight => {
        const insightItem = document.createElement('div');
        insightItem.className = 'insight-item';
        insightItem.textContent = insight;
        insightsContainer.appendChild(insightItem);
    });
}


// Show notification
function showNotification(title, message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-header">
            <strong>${title}</strong>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
        <div class="notification-body">${message.replace(/\n/g, '<br>')}</div>
    `;
    
    // Add to page
    let container = document.getElementById('notificationContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notificationContainer';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}
