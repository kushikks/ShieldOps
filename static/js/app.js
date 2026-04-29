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
const learningsSection = document.getElementById('learningsSection');

// Store current simulation data
let currentSimulation = null;

// Update slider value displays
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
    
    // Collect qualitative resource data
    const medicalResources = {
        hospital_status: document.getElementById('hospitalStatus').value,
        doctor_availability: document.getElementById('doctorAvailability').value
    };
    
    const waterFoodResources = {
        water_supply: document.getElementById('waterSupply').value,
        food_supply: document.getElementById('foodSupply').value
    };
    
    const logisticsResources = {
        transport_status: document.getElementById('transportStatus').value,
        communication_status: document.getElementById('communicationStatus').value
    };
    
    const emergencyResources = {
        personnel_availability: document.getElementById('personnelAvailability').value,
        equipment_status: document.getElementById('equipmentStatus').value
    };
    
    const infrastructureQuality = parseInt(document.getElementById('infrastructureQuality').value);
    const additionalContext = document.getElementById('additionalContext').value;
    
    // Disable button and show loading
    const submitBtn = document.getElementById('simulateBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Generating AI Recommendations...';
    
    // Show loading in results panel
    resultsPanel.style.display = 'block';
    document.getElementById('recommendationText').innerHTML = '<div class="loading-container"><div class="spinner-large"></div><p>AI is analyzing the situation and generating recommendations...</p></div>';
    
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
                medical_resources: medicalResources,
                water_food_resources: waterFoodResources,
                logistics_resources: logisticsResources,
                emergency_resources: emergencyResources,
                infrastructure_quality: infrastructureQuality,
                additional_context: additionalContext
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
        document.getElementById('recommendationText').innerHTML = '<p style="color: var(--danger);">Failed to generate recommendations. Please try again.</p>';
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Run Simulation';
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
    const recommendationText = document.getElementById('recommendationText');
    // Convert newlines to HTML breaks for proper formatting
    recommendationText.innerHTML = data.recommendation.replace(/\n/g, '<br>');

    
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
    
    // Display resource breakdown in organized format
    const resourcesElement = document.getElementById('detailResources');
    resourcesElement.innerHTML = ''; // Clear existing content
    
    if (data.medical_resources || data.water_food_resources || data.logistics_resources || data.emergency_resources) {
        const resourceContainer = document.createElement('div');
        resourceContainer.className = 'resource-breakdown';
        
        // Medical Resources
        if (data.medical_resources) {
            const medicalDiv = document.createElement('div');
            medicalDiv.className = 'resource-category';
            medicalDiv.innerHTML = `
                <span class="resource-label">Medical:</span>
                <span class="resource-value ${getResourceClass(data.medical_resources.hospital_status)}">
                    Hospital: ${capitalizeFirst(data.medical_resources.hospital_status)}
                </span>
                <span class="resource-value ${getResourceClass(data.medical_resources.doctor_availability)}">
                    Doctors: ${capitalizeFirst(data.medical_resources.doctor_availability)}
                </span>
            `;
            resourceContainer.appendChild(medicalDiv);
        }
        
        // Water & Food Resources
        if (data.water_food_resources) {
            const suppliesDiv = document.createElement('div');
            suppliesDiv.className = 'resource-category';
            suppliesDiv.innerHTML = `
                <span class="resource-label">Supplies:</span>
                <span class="resource-value ${getResourceClass(data.water_food_resources.water_supply)}">
                    Water: ${capitalizeFirst(data.water_food_resources.water_supply)}
                </span>
                <span class="resource-value ${getResourceClass(data.water_food_resources.food_supply)}">
                    Food: ${capitalizeFirst(data.water_food_resources.food_supply)}
                </span>
            `;
            resourceContainer.appendChild(suppliesDiv);
        }
        
        // Logistics Resources
        if (data.logistics_resources) {
            const logisticsDiv = document.createElement('div');
            logisticsDiv.className = 'resource-category';
            logisticsDiv.innerHTML = `
                <span class="resource-label">Logistics:</span>
                <span class="resource-value ${getResourceClass(data.logistics_resources.transport_status)}">
                    Transport: ${capitalizeFirst(data.logistics_resources.transport_status)}
                </span>
                <span class="resource-value ${getResourceClass(data.logistics_resources.communication_status)}">
                    Comm: ${capitalizeFirst(data.logistics_resources.communication_status)}
                </span>
            `;
            resourceContainer.appendChild(logisticsDiv);
        }
        
        // Emergency Resources
        if (data.emergency_resources) {
            const emergencyDiv = document.createElement('div');
            emergencyDiv.className = 'resource-category';
            emergencyDiv.innerHTML = `
                <span class="resource-label">Emergency:</span>
                <span class="resource-value ${getResourceClass(data.emergency_resources.personnel_availability)}">
                    Personnel: ${capitalizeFirst(data.emergency_resources.personnel_availability)}
                </span>
                <span class="resource-value ${getResourceClass(data.emergency_resources.equipment_status)}">
                    Equipment: ${capitalizeFirst(data.emergency_resources.equipment_status)}
                </span>
            `;
            resourceContainer.appendChild(emergencyDiv);
        }
        
        resourcesElement.appendChild(resourceContainer);
    } else {
        resourcesElement.textContent = 'N/A';
    }
    
    document.getElementById('detailInfrastructure').textContent = getInfrastructureLabel(data.infrastructure_quality);
    
    // Set up re-evaluation selects with current values
    if (data.medical_resources) {
        document.getElementById('newHospitalStatus').value = data.medical_resources.hospital_status;
        document.getElementById('newDoctorAvailability').value = data.medical_resources.doctor_availability;
    }
    if (data.water_food_resources) {
        document.getElementById('newWaterSupply').value = data.water_food_resources.water_supply;
        document.getElementById('newFoodSupply').value = data.water_food_resources.food_supply;
    }
    if (data.logistics_resources) {
        document.getElementById('newTransportStatus').value = data.logistics_resources.transport_status;
        document.getElementById('newCommunicationStatus').value = data.logistics_resources.communication_status;
    }
    if (data.emergency_resources) {
        document.getElementById('newPersonnelAvailability').value = data.emergency_resources.personnel_availability;
        document.getElementById('newEquipmentStatus').value = data.emergency_resources.equipment_status;
    }
    document.getElementById('newInfrastructureQuality').value = data.infrastructure_quality;
    
    // Apply color theme based on priority
    applyTheme(data.priority);
}

// Helper function to get infrastructure label
function getInfrastructureLabel(value) {
    if (value >= 90) return 'Fully Functional';
    if (value >= 60) return 'Partially Functional';
    if (value >= 40) return 'Moderately Damaged';
    if (value >= 20) return 'Severely Damaged';
    return 'Non-Functional';
}

// Helper function to capitalize first letter
function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Helper function to get resource status class for color coding
function getResourceClass(status) {
    if (!status) return '';
    const statusLower = status.toLowerCase();
    
    // Good status
    if (['adequate', 'normal'].includes(statusLower)) {
        return 'resource-good';
    }
    // Moderate status
    if (['moderate', 'limited'].includes(statusLower)) {
        return 'resource-moderate';
    }
    // Critical status
    if (['critical', 'scarce', 'collapsed', 'none'].includes(statusLower)) {
        return 'resource-critical';
    }
    
    return '';
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
    
    // SOS button handler (for dashboard header)
    const sosButtonHeader = document.getElementById('sosButtonHeader');
    if (sosButtonHeader) {
        sosButtonHeader.addEventListener('click', () => {
            sosButtonHeader.classList.add('sos-active');
            sosButtonHeader.innerHTML = `
                <svg class="sos-icon-small sos-pulse" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                </svg>
                <span>Deploying Help...</span>
            `;
            
            // Show notification
            showNotification('SOS Alert', 'Emergency help is being deployed to your location. Stay safe!', 'warning');
            
            // Reset after 3 seconds
            setTimeout(() => {
                sosButtonHeader.classList.remove('sos-active');
                sosButtonHeader.innerHTML = `
                    <svg class="sos-icon-small" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <span>SOS</span>
                `;
            }, 3000);
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
        
        // Collect updated qualitative data
        const newMedicalResources = {
            hospital_status: document.getElementById('newHospitalStatus').value,
            doctor_availability: document.getElementById('newDoctorAvailability').value
        };
        
        const newWaterFoodResources = {
            water_supply: document.getElementById('newWaterSupply').value,
            food_supply: document.getElementById('newFoodSupply').value
        };
        
        const newLogisticsResources = {
            transport_status: document.getElementById('newTransportStatus').value,
            communication_status: document.getElementById('newCommunicationStatus').value
        };
        
        const newEmergencyResources = {
            personnel_availability: document.getElementById('newPersonnelAvailability').value,
            equipment_status: document.getElementById('newEquipmentStatus').value
        };
        
        const newInfrastructure = parseInt(document.getElementById('newInfrastructureQuality').value);
        const additionalNotes = document.getElementById('additionalNotes').value;
        
        reevaluateBtn.disabled = true;
        reevaluateBtn.innerHTML = '<span class="spinner"></span> Re-evaluating with AI...';
        
        // Show loading in recommendation
        document.getElementById('recommendationText').innerHTML = '<div class="loading-container"><div class="spinner-large"></div><p>AI is re-analyzing with updated information...</p></div>';
        
        try {
            const response = await fetch(`${API_BASE}/api/reevaluate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    original_timestamp: currentSimulation.timestamp,
                    new_findings: {
                        medical_resources: newMedicalResources,
                        water_food_resources: newWaterFoodResources,
                        logistics_resources: newLogisticsResources,
                        emergency_resources: newEmergencyResources,
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
            await loadHistory();
            
        } catch (error) {
            alert('Re-evaluation failed: ' + error.message);
            console.error('Re-evaluation error:', error);
            document.getElementById('recommendationText').innerHTML = '<p style="color: var(--danger);">Failed to re-evaluate. Please try again.</p>';
        } finally {
            reevaluateBtn.disabled = false;
            reevaluateBtn.innerHTML = 'Re-evaluate Risk';
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
