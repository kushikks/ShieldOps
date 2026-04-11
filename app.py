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

# Store simulation history and learnings
simulation_history = []
learned_patterns = []


def calculate_risk_score(severity, population, resources_available=50, infrastructure_quality=50):
    """
    Calculate risk score based on multiple factors
    
    Args:
        severity: Disaster severity (1-10)
        population: Affected population count
        resources_available: Available resources percentage (0-100)
        infrastructure_quality: Infrastructure quality percentage (0-100)
    
    Returns:
        tuple: (risk_score, reasoning)
    """
    reasoning = []
    
    # Base severity impact (0-50 points)
    severity_impact = severity * 5
    reasoning.append(f"Severity level {severity}/10 contributes {severity_impact} points to base risk")
    
    # Population impact (0-30 points)
    if population < 1000:
        pop_impact = 5
        pop_category = "small"
    elif population < 10000:
        pop_impact = 12
        pop_category = "moderate"
    elif population < 100000:
        pop_impact = 22
        pop_category = "large"
    else:
        pop_impact = 30
        pop_category = "very large"
    
    reasoning.append(f"Affected population of {population:,} ({pop_category} scale) adds {pop_impact} points")
    
    # Resource availability impact (reduces risk by 0-15 points)
    resource_reduction = (resources_available / 100) * 15
    reasoning.append(f"Available resources at {resources_available}% reduce risk by {resource_reduction:.1f} points")
    
    # Infrastructure quality impact (reduces risk by 0-15 points)
    infrastructure_reduction = (infrastructure_quality / 100) * 15
    reasoning.append(f"Infrastructure quality at {infrastructure_quality}% reduces risk by {infrastructure_reduction:.1f} points")
    
    # Calculate final risk score
    risk_score = severity_impact + pop_impact - resource_reduction - infrastructure_reduction
    risk_score = max(0, min(risk_score, 100))  # Clamp between 0-100
    
    reasoning.append(f"Final calculated risk score: {risk_score:.1f}/100")
    
    return risk_score, reasoning


def determine_priority(risk_score):
    """Determine priority level based on risk score"""
    if risk_score >= 70:
        return 'HIGH'
    elif risk_score >= 40:
        return 'MEDIUM'
    else:
        return 'LOW'


def enhance_recommendation(base_recommendation, resources, infrastructure, priority, additional_context=""):
    """
    Enhance recommendation based on available resources, infrastructure, and context
    Intelligently parses additional context to provide specific actionable recommendations
    """
    enhanced = base_recommendation
    recommendations = []
    
    # Resource-based enhancements
    if resources < 30:
        recommendations.append("CRITICAL: Immediate external aid required due to low resource availability.")
    elif resources < 50:
        recommendations.append("WARNING: Request additional resources from neighboring regions.")
    elif resources > 70:
        recommendations.append("GOOD: Adequate resources available for effective response.")
    
    # Infrastructure-based enhancements
    if infrastructure < 30:
        recommendations.append("CRITICAL: Infrastructure severely compromised, prioritize structural assessments and alternative routes.")
    elif infrastructure < 50:
        recommendations.append("CAUTION: Monitor infrastructure stability closely, prepare backup systems.")
    elif infrastructure > 70:
        recommendations.append("GOOD: Infrastructure intact, enables efficient emergency operations.")
    
    # Priority and resource combination
    if priority == 'HIGH' and resources > 70 and infrastructure > 70:
        recommendations.append("ADVANTAGE: Strong resources and infrastructure enable rapid response despite high severity.")
    elif priority == 'HIGH' and (resources < 40 or infrastructure < 40):
        recommendations.append("URGENT: High priority with limited capacity - escalate to national/international level immediately.")
    
    # Intelligent context parsing and specific recommendations
    if additional_context:
        context_lower = additional_context.lower()
        
        # Medical/Healthcare related
        if any(word in context_lower for word in ['doctor', 'doctors', 'medical', 'hospital', 'healthcare', 'physician', 'nurse', 'paramedic']):
            if any(word in context_lower for word in ['no', 'not', 'unavailable', 'shortage', 'lacking', 'insufficient', 'limited']):
                recommendations.append("MEDICAL CRISIS: Deploy mobile medical units immediately. Request medical personnel from neighboring regions. Establish triage centers with available staff. Coordinate with military medical corps.")
            elif any(word in context_lower for word in ['arrived', 'available', 'deployed', 'present']):
                recommendations.append("MEDICAL SUPPORT: Optimize medical resource distribution. Establish treatment protocols. Set up field hospitals in strategic locations.")
        
        # Food/Water related
        elif any(word in context_lower for word in ['food', 'water', 'supplies', 'rations', 'drinking', 'nutrition']):
            if any(word in context_lower for word in ['no', 'not', 'unavailable', 'shortage', 'lacking', 'insufficient', 'contaminated']):
                recommendations.append("SUPPLY EMERGENCY: Activate emergency food/water distribution. Deploy water purification units. Coordinate with humanitarian organizations. Establish distribution centers.")
            elif any(word in context_lower for word in ['arrived', 'available', 'sufficient']):
                recommendations.append("SUPPLY MANAGEMENT: Organize systematic distribution. Monitor consumption rates. Prevent hoarding. Maintain supply chain.")
        
        # Communication related
        elif any(word in context_lower for word in ['communication', 'phone', 'network', 'internet', 'radio', 'signal']):
            if any(word in context_lower for word in ['down', 'failed', 'no', 'not', 'unavailable', 'disrupted']):
                recommendations.append("COMMUNICATION BREAKDOWN: Deploy satellite phones. Establish radio communication network. Use runners for critical messages. Set up information centers at key locations.")
            elif any(word in context_lower for word in ['restored', 'working', 'operational']):
                recommendations.append("COMMUNICATION ACTIVE: Broadcast emergency information. Coordinate response teams via established channels. Maintain communication logs.")
        
        # Transportation/Roads related
        elif any(word in context_lower for word in ['road', 'roads', 'transport', 'vehicle', 'access', 'route']):
            if any(word in context_lower for word in ['blocked', 'collapsed', 'damaged', 'impassable', 'destroyed']):
                recommendations.append("ACCESS RESTRICTED: Deploy helicopters for critical transport. Clear priority routes immediately. Establish alternative access points. Use boats/amphibious vehicles if applicable.")
            elif any(word in context_lower for word in ['cleared', 'open', 'accessible', 'restored']):
                recommendations.append("ACCESS RESTORED: Prioritize evacuation routes. Transport critical supplies. Establish traffic control. Monitor route conditions.")
        
        # Shelter related
        elif any(word in context_lower for word in ['shelter', 'housing', 'accommodation', 'homeless', 'displaced']):
            if any(word in context_lower for word in ['no', 'not', 'insufficient', 'lacking', 'overcrowded']):
                recommendations.append("SHELTER CRISIS: Establish emergency shelters immediately. Deploy tents and temporary structures. Coordinate with schools/community centers. Ensure basic amenities.")
            elif any(word in context_lower for word in ['available', 'established', 'ready']):
                recommendations.append("SHELTER AVAILABLE: Organize systematic allocation. Maintain hygiene standards. Provide security. Monitor capacity.")
        
        # Power/Electricity related
        elif any(word in context_lower for word in ['power', 'electricity', 'generator', 'energy']):
            if any(word in context_lower for word in ['no', 'not', 'outage', 'failed', 'down']):
                recommendations.append("POWER OUTAGE: Deploy emergency generators for critical facilities. Prioritize hospitals and communication centers. Arrange fuel supply. Use solar/battery backup.")
            elif any(word in context_lower for word in ['restored', 'working', 'available']):
                recommendations.append("POWER RESTORED: Prioritize critical infrastructure. Monitor grid stability. Prepare backup systems.")
        
        # Personnel/Workforce related
        elif any(word in context_lower for word in ['personnel', 'staff', 'workers', 'volunteers', 'team', 'manpower']):
            if any(word in context_lower for word in ['no', 'not', 'shortage', 'insufficient', 'lacking']):
                recommendations.append("PERSONNEL SHORTAGE: Request additional response teams. Mobilize volunteers. Coordinate with NGOs. Establish training for local volunteers. Prioritize critical roles.")
            elif any(word in context_lower for word in ['arrived', 'available', 'deployed']):
                recommendations.append("PERSONNEL DEPLOYED: Organize teams efficiently. Assign clear responsibilities. Establish shift rotations. Maintain coordination.")
        
        # Security related
        elif any(word in context_lower for word in ['security', 'looting', 'crime', 'violence', 'safety']):
            if any(word in context_lower for word in ['issue', 'problem', 'concern', 'threat']):
                recommendations.append("SECURITY CONCERN: Deploy security forces. Establish curfew if necessary. Protect supply distribution points. Ensure responder safety. Coordinate with law enforcement.")
            elif any(word in context_lower for word in ['stable', 'controlled', 'secure']):
                recommendations.append("SECURITY MAINTAINED: Continue monitoring. Maintain visible presence. Protect critical infrastructure.")
        
        # Weather related
        elif any(word in context_lower for word in ['weather', 'rain', 'storm', 'wind', 'forecast']):
            if any(word in context_lower for word in ['worsening', 'deteriorating', 'incoming', 'approaching']):
                recommendations.append("WEATHER ALERT: Accelerate evacuation if needed. Secure temporary structures. Prepare for secondary impacts. Monitor weather updates continuously.")
            elif any(word in context_lower for word in ['improving', 'clearing', 'stable']):
                recommendations.append("WEATHER IMPROVING: Proceed with outdoor operations. Assess damage safely. Plan recovery operations.")
        
        # Casualties/Injuries related
        elif any(word in context_lower for word in ['casualties', 'injured', 'wounded', 'victims', 'deaths']):
            if any(word in context_lower for word in ['many', 'numerous', 'high', 'increasing', 'rising']):
                recommendations.append("MASS CASUALTY EVENT: Activate mass casualty protocols. Establish triage system. Request additional medical support. Set up morgue facilities. Coordinate with forensic teams.")
            else:
                recommendations.append("CASUALTY MANAGEMENT: Maintain medical records. Provide psychological support. Coordinate with families. Ensure proper care.")
        
        # General positive developments
        elif any(word in context_lower for word in ['arrived', 'deployed', 'improved', 'cleared', 'restored', 'reinforced', 'operational']):
            recommendations.append(f"SITUATION UPDATE: {additional_context} - Continue monitoring and optimize resource deployment based on improved conditions.")
        
        # General negative developments
        elif any(word in context_lower for word in ['worsened', 'collapsed', 'blocked', 'damaged', 'failed', 'deteriorated', 'critical']):
            recommendations.append(f"SITUATION ALERT: {additional_context} - Immediately adjust response strategy. Reassess priorities. Request additional support.")
        
        # Neutral/General context
        else:
            recommendations.append(f"CONTEXT NOTE: {additional_context} - Evaluate impact and adjust response accordingly.")
    
    # Combine all recommendations
    if recommendations:
        enhanced += " | " + " | ".join(recommendations)
    
    return enhanced


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
        "population": 50000,
        "resources_available": 50,  // optional, 0-100
        "infrastructure_quality": 50  // optional, 0-100
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
        resources_available = data.get('resources_available', 50)
        infrastructure_quality = data.get('infrastructure_quality', 50)
        
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
        
        if not (0 <= resources_available <= 100):
            return jsonify({'error': 'Resources available must be between 0 and 100'}), 400
        
        if not (0 <= infrastructure_quality <= 100):
            return jsonify({'error': 'Infrastructure quality must be between 0 and 100'}), 400
        
        # Calculate risk and priority with reasoning
        risk_score, reasoning = calculate_risk_score(
            severity, population, resources_available, infrastructure_quality
        )
        priority = determine_priority(risk_score)
        recommendation = DISASTER_ACTIONS[disaster_type]
        
        # Enhance recommendation based on resources
        enhanced_recommendation = enhance_recommendation(
            recommendation, resources_available, infrastructure_quality, priority
        )
        
        # Create response
        response = {
            'disaster_type': disaster_type,
            'severity': severity,
            'population': population,
            'resources_available': resources_available,
            'infrastructure_quality': infrastructure_quality,
            'risk_score': round(risk_score, 2),
            'priority': priority,
            'recommendation': enhanced_recommendation,
            'reasoning': reasoning,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store in history
        simulation_history.append(response)
        if len(simulation_history) > 20:  # Keep last 20
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


@app.route('/api/reevaluate', methods=['POST'])
def reevaluate_disaster():
    """
    Re-evaluate an existing disaster with updated information
    Expected input: {
        "original_timestamp": "2024-01-15T10:30:00",
        "new_findings": {
            "resources_available": 70,
            "infrastructure_quality": 40,
            "additional_notes": "Emergency supplies arrived"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        original_timestamp = data.get('original_timestamp')
        new_findings = data.get('new_findings', {})
        
        # Find original simulation
        original = None
        for sim in simulation_history:
            if sim['timestamp'] == original_timestamp:
                original = sim
                break
        
        if not original:
            return jsonify({'error': 'Original simulation not found'}), 404
        
        # Extract updated values
        new_resources = new_findings.get('resources_available', original.get('resources_available', 50))
        new_infrastructure = new_findings.get('infrastructure_quality', original.get('infrastructure_quality', 50))
        additional_notes = new_findings.get('additional_notes', '')
        
        # Recalculate risk with new information
        new_risk_score, new_reasoning = calculate_risk_score(
            original['severity'],
            original['population'],
            new_resources,
            new_infrastructure
        )
        new_priority = determine_priority(new_risk_score)
        
        # Enhanced recommendation with context
        base_recommendation = DISASTER_ACTIONS[original['disaster_type']]
        new_recommendation = enhance_recommendation(
            base_recommendation, new_resources, new_infrastructure, new_priority, additional_notes
        )
        
        # Calculate changes
        old_risk = original['risk_score']
        risk_change = new_risk_score - old_risk
        risk_change_percent = (risk_change / old_risk * 100) if old_risk > 0 else 0
        
        # Store learning
        learning = {
            'disaster_type': original['disaster_type'],
            'original_risk': old_risk,
            'new_risk': new_risk_score,
            'risk_change': risk_change,
            'factors_changed': {
                'resources': new_resources - original.get('resources_available', 50),
                'infrastructure': new_infrastructure - original.get('infrastructure_quality', 50)
            },
            'notes': additional_notes,
            'timestamp': datetime.utcnow().isoformat()
        }
        learned_patterns.append(learning)
        
        # Create response
        response = {
            'original_simulation': original,
            'updated_assessment': {
                'disaster_type': original['disaster_type'],
                'severity': original['severity'],
                'population': original['population'],
                'resources_available': new_resources,
                'infrastructure_quality': new_infrastructure,
                'risk_score': round(new_risk_score, 2),
                'priority': new_priority,
                'recommendation': new_recommendation,
                'reasoning': new_reasoning,
                'timestamp': datetime.utcnow().isoformat()  # NEW timestamp for this assessment
            },
            'changes': {
                'risk_change': round(risk_change, 2),
                'risk_change_percent': round(risk_change_percent, 2),
                'priority_changed': original['priority'] != new_priority,
                'old_priority': original['priority'],
                'new_priority': new_priority,
                'resources_change': new_resources - original.get('resources_available', 50),
                'infrastructure_change': new_infrastructure - original.get('infrastructure_quality', 50)
            },
            'additional_notes': additional_notes,
            'learning_recorded': True
        }
        
        # IMPORTANT: Add the updated assessment to history so it can be re-evaluated again
        updated_sim = response['updated_assessment'].copy()
        simulation_history.append(updated_sim)
        if len(simulation_history) > 20:
            simulation_history.pop(0)
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/learnings', methods=['GET'])
def get_learnings():
    """Get learned patterns from re-evaluations"""
    return jsonify({
        'learnings': learned_patterns,
        'count': len(learned_patterns),
        'insights': generate_insights()
    }), 200


def generate_insights():
    """Generate insights from learned patterns"""
    if not learned_patterns:
        return []
    
    insights = []
    
    # Analyze resource impact
    resource_improvements = [l for l in learned_patterns if l['factors_changed']['resources'] > 0]
    if resource_improvements:
        avg_risk_reduction = sum(l['risk_change'] for l in resource_improvements) / len(resource_improvements)
        if avg_risk_reduction < 0:
            insights.append(f"Increasing resources typically reduces risk by {abs(avg_risk_reduction):.1f} points on average")
    
    # Analyze infrastructure impact
    infra_improvements = [l for l in learned_patterns if l['factors_changed']['infrastructure'] > 0]
    if infra_improvements:
        avg_risk_reduction = sum(l['risk_change'] for l in infra_improvements) / len(infra_improvements)
        if avg_risk_reduction < 0:
            insights.append(f"Improving infrastructure typically reduces risk by {abs(avg_risk_reduction):.1f} points on average")
    
    # Disaster-specific insights
    disaster_types = {}
    for learning in learned_patterns:
        dtype = learning['disaster_type']
        if dtype not in disaster_types:
            disaster_types[dtype] = []
        disaster_types[dtype].append(learning)
    
    for dtype, learnings in disaster_types.items():
        avg_change = sum(l['risk_change'] for l in learnings) / len(learnings)
        insights.append(f"{dtype.capitalize()}: Average risk change after intervention is {avg_change:+.1f} points")
    
    return insights


@app.route('/api/disasters', methods=['GET'])
def get_disaster_types():
    """Get available disaster types"""
    return jsonify({
        'disaster_types': list(DISASTER_ACTIONS.keys())
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
