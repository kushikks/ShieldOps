"""
Disaster Response Simulation & Decision Intelligence System
Backend API with Flask
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Disaster response logic
DISASTER_ACTIONS = {
    'flood': 'Deploy rescue boats, establish evacuation centers, distribute clean water',
    'earthquake': 'Deploy search and rescue teams, set up medical camps, assess structural damage',
    'fire': 'Deploy fire brigades, evacuate affected areas, establish air quality monitoring',
    'cyclone': 'Activate early warning systems, establish shelters, secure infrastructure',
    'tsunami': 'Immediate evacuation to high ground, activate coastal warning systems',
    'landslide': 'Deploy rescue teams, establish safe zones, monitor geological activity',
    'drought': 'Distribute water supplies, implement water conservation, provide agricultural support',
    'epidemic': 'Deploy medical teams, establish quarantine zones, distribute medical supplies'
}

# Store simulation history
simulation_history = []


def calculate_risk_score(severity, population):
    """
    Calculate risk score based on severity and affected population
    Formula: (severity * 10) + (population impact factor)
    """
    # Normalize population to a 0-100 scale
    if population < 1000:
        pop_factor = 10
    elif population < 10000:
        pop_factor = 30
    elif population < 100000:
        pop_factor = 60
    else:
        pop_factor = 90
    
    risk_score = (severity * 10) + (pop_factor * 0.5)
    return min(risk_score, 100)  # Cap at 100


def determine_priority(risk_score):
    """Determine priority level based on risk score"""
    if risk_score >= 70:
        return 'HIGH'
    elif risk_score >= 40:
        return 'MEDIUM'
    else:
        return 'LOW'


@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'Disaster Response System',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/api/simulate', methods=['POST'])
def simulate_disaster():
    """
    Main simulation endpoint
    Expected input: {
        "disaster_type": "flood",
        "severity": 7,
        "population": 50000
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        disaster_type = data.get('disaster_type', '').lower()
        severity = data.get('severity')
        population = data.get('population')
        
        # Validation
        if not disaster_type or disaster_type not in DISASTER_ACTIONS:
            return jsonify({
                'error': 'Invalid disaster type',
                'valid_types': list(DISASTER_ACTIONS.keys())
            }), 400
        
        if severity is None or not (1 <= severity <= 10):
            return jsonify({'error': 'Severity must be between 1 and 10'}), 400
        
        if population is None or population < 0:
            return jsonify({'error': 'Population must be a positive number'}), 400
        
        # Calculate risk and priority
        risk_score = calculate_risk_score(severity, population)
        priority = determine_priority(risk_score)
        recommendation = DISASTER_ACTIONS[disaster_type]
        
        # Create response
        response = {
            'disaster_type': disaster_type,
            'severity': severity,
            'population': population,
            'risk_score': round(risk_score, 2),
            'priority': priority,
            'recommendation': recommendation,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store in history
        simulation_history.append(response)
        if len(simulation_history) > 10:  # Keep only last 10
            simulation_history.pop(0)
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get simulation history"""
    return jsonify({
        'history': simulation_history,
        'count': len(simulation_history)
    }), 200


@app.route('/api/disasters', methods=['GET'])
def get_disaster_types():
    """Get available disaster types"""
    return jsonify({
        'disaster_types': list(DISASTER_ACTIONS.keys())
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
