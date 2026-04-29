"""
Disaster Response Simulation & Decision Intelligence System
Backend API with Flask
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import AI service
from ai_service import get_ai_service

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

# Qualitative to Quantitative Mapping
QUALITATIVE_SCORES = {
    'adequate': 1.0,
    'normal': 1.0,
    'moderate': 0.6,
    'limited': 0.6,
    'critical': 0.3,
    'scarce': 0.3,
    'none': 0.0,
    'collapsed': 0.0
}

# Resource category weights (sum to 1.0)
RESOURCE_WEIGHTS = {
    'medical': 0.35,      # Highest priority
    'water_food': 0.30,   # Critical for survival
    'logistics': 0.20,    # Important for response
    'emergency': 0.15     # Support capability
}


def calculate_resource_score(medical_resources, water_food_resources, logistics_resources, emergency_resources):
    """
    Calculate overall resource score from qualitative inputs
    
    Args:
        medical_resources: dict with 'hospital_status' and 'doctor_availability'
        water_food_resources: dict with 'water_supply' and 'food_supply'
        logistics_resources: dict with 'transport_status' and 'communication_status'
        emergency_resources: dict with 'personnel_availability' and 'equipment_status'
    
    Returns:
        float: Overall resource score (0-100)
    """
    # Calculate category scores (average of indicators)
    medical_score = (
        QUALITATIVE_SCORES.get(medical_resources.get('hospital_status', 'moderate'), 0.6) +
        QUALITATIVE_SCORES.get(medical_resources.get('doctor_availability', 'moderate'), 0.6)
    ) / 2
    
    water_food_score = (
        QUALITATIVE_SCORES.get(water_food_resources.get('water_supply', 'moderate'), 0.6) +
        QUALITATIVE_SCORES.get(water_food_resources.get('food_supply', 'moderate'), 0.6)
    ) / 2
    
    logistics_score = (
        QUALITATIVE_SCORES.get(logistics_resources.get('transport_status', 'moderate'), 0.6) +
        QUALITATIVE_SCORES.get(logistics_resources.get('communication_status', 'moderate'), 0.6)
    ) / 2
    
    emergency_score = (
        QUALITATIVE_SCORES.get(emergency_resources.get('personnel_availability', 'moderate'), 0.6) +
        QUALITATIVE_SCORES.get(emergency_resources.get('equipment_status', 'moderate'), 0.6)
    ) / 2
    
    # Weighted aggregation
    overall_score = (
        RESOURCE_WEIGHTS['medical'] * medical_score +
        RESOURCE_WEIGHTS['water_food'] * water_food_score +
        RESOURCE_WEIGHTS['logistics'] * logistics_score +
        RESOURCE_WEIGHTS['emergency'] * emergency_score
    )
    
    # Convert to 0-100 scale
    return overall_score * 100


def analyze_additional_context_impact(additional_context):
    """
    Analyze additional context and calculate its impact on risk
    
    Returns:
        tuple: (risk_modifier, context_analysis)
        risk_modifier: float (-20 to +20 points to add to risk)
        context_analysis: dict with detected issues
    """
    if not additional_context:
        return 0, {}
    
    context_lower = additional_context.lower()
    risk_modifier = 0
    context_analysis = {
        'medical_issues': [],
        'supply_issues': [],
        'infrastructure_issues': [],
        'security_issues': [],
        'hazmat_issues': [],
        'positive_developments': []
    }
    
    # CRITICAL HAZMAT/Chemical issues (very high impact)
    if any(word in context_lower for word in ['gas leak', 'gas', 'chemical', 'toxic', 'hazmat', 'hazardous', 'explosion', 'fire hazard', 'radiation', 'nuclear']):
        if any(word in context_lower for word in ['leak', 'spill', 'exposure', 'contamination', 'detected', 'reported', 'spreading']):
            risk_modifier += 15
            context_analysis['hazmat_issues'].append('Hazardous material/gas leak detected - immediate evacuation required')
        elif 'gas leak' in context_lower or 'chemical leak' in context_lower or 'toxic' in context_lower:
            risk_modifier += 15
            context_analysis['hazmat_issues'].append('Critical hazmat situation')
    
    # Explosion/Fire (very high impact)
    if any(word in context_lower for word in ['explosion', 'blast', 'exploded', 'detonation']):
        risk_modifier += 12
        context_analysis['hazmat_issues'].append('Explosion reported - secondary hazards likely')
    
    # Fire spreading (high impact)
    if any(word in context_lower for word in ['fire', 'burning', 'flames']):
        if any(word in context_lower for word in ['spreading', 'out of control', 'uncontrolled', 'growing', 'multiple']):
            risk_modifier += 10
            context_analysis['hazmat_issues'].append('Fire spreading rapidly')
    
    # Medical issues (high impact)
    if any(word in context_lower for word in ['doctor', 'medical', 'hospital', 'healthcare', 'ambulance']):
        if any(word in context_lower for word in ['no', 'not', 'unavailable', 'shortage', 'lacking', 'insufficient', 'overwhelmed']):
            risk_modifier += 8
            context_analysis['medical_issues'].append('Medical personnel/facilities unavailable or overwhelmed')
        elif any(word in context_lower for word in ['many', 'casualties', 'injured', 'wounded', 'deaths', 'fatalities']):
            risk_modifier += 10
            context_analysis['medical_issues'].append('High casualty count')
    
    # Disease/Epidemic (high impact)
    if any(word in context_lower for word in ['disease', 'epidemic', 'outbreak', 'infection', 'contagious', 'virus', 'pandemic']):
        risk_modifier += 9
        context_analysis['medical_issues'].append('Disease outbreak or epidemic risk')
    
    # Supply issues (high impact)
    if any(word in context_lower for word in ['water', 'food', 'supplies', 'medicine', 'fuel']):
        if any(word in context_lower for word in ['no', 'not', 'unavailable', 'shortage', 'contaminated', 'insufficient', 'running out', 'depleted']):
            risk_modifier += 7
            context_analysis['supply_issues'].append('Critical supply shortage')
    
    # Infrastructure issues (medium-high impact)
    if any(word in context_lower for word in ['road', 'bridge', 'transport', 'communication', 'power', 'electricity', 'network']):
        if any(word in context_lower for word in ['blocked', 'down', 'failed', 'collapsed', 'damaged', 'outage', 'destroyed']):
            risk_modifier += 6
            context_analysis['infrastructure_issues'].append('Infrastructure failure')
    
    # Building collapse (high impact)
    if any(word in context_lower for word in ['building', 'structure', 'dam', 'levee']):
        if any(word in context_lower for word in ['collapse', 'collapsed', 'collapsing', 'failing', 'breach', 'breached']):
            risk_modifier += 10
            context_analysis['infrastructure_issues'].append('Structural collapse - major hazard')
    
    # Flooding/Water rising (medium-high impact)
    if any(word in context_lower for word in ['flood', 'water', 'river']):
        if any(word in context_lower for word in ['rising', 'increasing', 'overflow', 'overflowing', 'surge']):
            risk_modifier += 7
            context_analysis['infrastructure_issues'].append('Water levels rising rapidly')
    
    # Security issues (medium impact)
    if any(word in context_lower for word in ['looting', 'violence', 'crime', 'riot', 'panic', 'chaos']):
        risk_modifier += 5
        context_analysis['security_issues'].append('Security concerns - civil unrest')
    
    # Weather worsening (medium impact)
    if any(word in context_lower for word in ['weather', 'storm', 'rain', 'wind', 'hurricane', 'tornado', 'cyclone']):
        if any(word in context_lower for word in ['worsening', 'approaching', 'deteriorating', 'intensifying', 'strengthening']):
            risk_modifier += 5
            context_analysis['infrastructure_issues'].append('Weather deteriorating')
    
    # Aftershocks/Secondary disasters (medium impact)
    if any(word in context_lower for word in ['aftershock', 'tremor', 'secondary', 'landslide', 'mudslide']):
        risk_modifier += 6
        context_analysis['infrastructure_issues'].append('Secondary disaster risk')
    
    # Evacuation issues (medium impact)
    if any(word in context_lower for word in ['evacuation', 'evacuate', 'trapped', 'stranded', 'isolated']):
        if any(word in context_lower for word in ['unable', 'cannot', 'impossible', 'blocked', 'cut off']):
            risk_modifier += 7
            context_analysis['infrastructure_issues'].append('Evacuation routes blocked - people trapped')
    
    # Positive developments (reduce risk)
    if any(word in context_lower for word in ['arrived', 'deployed', 'restored', 'cleared', 'operational', 'improved', 'contained', 'controlled', 'stabilized']):
        risk_modifier -= 5
        context_analysis['positive_developments'].append('Situation improving')
    
    # Cap the modifier
    risk_modifier = max(-20, min(20, risk_modifier))
    
    return risk_modifier, context_analysis


def calculate_risk_score(severity, population, resources_available=50, infrastructure_quality=50, 
                         medical_resources=None, water_food_resources=None, logistics_resources=None, 
                         emergency_resources=None, additional_context=""):
    """
    Calculate risk score based on multiple factors including qualitative resources and context
    
    Args:
        severity: Disaster severity (1-10)
        population: Affected population count
        resources_available: Legacy percentage (0-100) - used if qualitative not provided
        infrastructure_quality: Infrastructure quality percentage (0-100)
        medical_resources: dict with qualitative medical resource indicators
        water_food_resources: dict with qualitative water/food indicators
        logistics_resources: dict with qualitative logistics indicators
        emergency_resources: dict with qualitative emergency response indicators
        additional_context: str with additional situation context
    
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
    
    # Calculate resource score (qualitative if provided, else use legacy)
    if medical_resources or water_food_resources or logistics_resources or emergency_resources:
        # Use qualitative model
        med_res = medical_resources or {}
        wf_res = water_food_resources or {}
        log_res = logistics_resources or {}
        emg_res = emergency_resources or {}
        
        calculated_resources = calculate_resource_score(med_res, wf_res, log_res, emg_res)
        resource_reduction = (calculated_resources / 100) * 15
        reasoning.append(f"Qualitative resource assessment at {calculated_resources:.1f}% reduces risk by {resource_reduction:.1f} points")
        
        # Add detailed resource breakdown
        if med_res:
            reasoning.append(f"  - Medical: Hospital {med_res.get('hospital_status', 'N/A')}, Doctors {med_res.get('doctor_availability', 'N/A')}")
        if wf_res:
            reasoning.append(f"  - Supplies: Water {wf_res.get('water_supply', 'N/A')}, Food {wf_res.get('food_supply', 'N/A')}")
        if log_res:
            reasoning.append(f"  - Logistics: Transport {log_res.get('transport_status', 'N/A')}, Communication {log_res.get('communication_status', 'N/A')}")
        if emg_res:
            reasoning.append(f"  - Emergency: Personnel {emg_res.get('personnel_availability', 'N/A')}, Equipment {emg_res.get('equipment_status', 'N/A')}")
    else:
        # Use legacy percentage model
        resource_reduction = (resources_available / 100) * 15
        reasoning.append(f"Available resources at {resources_available}% reduce risk by {resource_reduction:.1f} points")
    
    # Infrastructure quality impact (reduces risk by 0-15 points)
    infrastructure_reduction = (infrastructure_quality / 100) * 15
    reasoning.append(f"Infrastructure quality at {infrastructure_quality}% reduces risk by {infrastructure_reduction:.1f} points")
    
    # Analyze additional context impact
    context_modifier, context_analysis = analyze_additional_context_impact(additional_context)
    if context_modifier != 0:
        if context_modifier > 0:
            reasoning.append(f"Additional context INCREASES risk by {context_modifier:.1f} points:")
        else:
            reasoning.append(f"Additional context DECREASES risk by {abs(context_modifier):.1f} points:")
        
        for category, issues in context_analysis.items():
            if issues:
                for issue in issues:
                    reasoning.append(f"  - {issue}")
    
    # Calculate final risk score
    risk_score = severity_impact + pop_impact - resource_reduction - infrastructure_reduction + context_modifier
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


def enhance_recommendation(base_recommendation, resources, infrastructure, priority, additional_context="", 
                         medical_resources=None, water_food_resources=None, logistics_resources=None, emergency_resources=None):
    """
    Enhance recommendation based on available resources, infrastructure, and context
    Intelligently parses additional context to provide specific actionable recommendations
    """
    enhanced = base_recommendation
    recommendations = []
    
    # Calculate actual resource score if qualitative data provided
    if medical_resources or water_food_resources or logistics_resources or emergency_resources:
        med_res = medical_resources or {}
        wf_res = water_food_resources or {}
        log_res = logistics_resources or {}
        emg_res = emergency_resources or {}
        resources = calculate_resource_score(med_res, wf_res, log_res, emg_res)
    
    # SPECIFIC RESOURCE CATEGORY RECOMMENDATIONS
    # Analyze each resource category and provide targeted recommendations
    
    # Medical Resources Analysis
    if medical_resources:
        hospital_status = medical_resources.get('hospital_status', 'moderate')
        doctor_availability = medical_resources.get('doctor_availability', 'moderate')
        
        if hospital_status in ['critical', 'collapsed']:
            recommendations.append("MEDICAL INFRASTRUCTURE CRISIS: Hospitals severely compromised. Deploy mobile field hospitals immediately. Establish emergency medical stations. Request medical infrastructure support from neighboring regions. Set up triage centers in stable buildings.")
        elif hospital_status == 'limited':
            recommendations.append("HOSPITAL CAPACITY WARNING: Hospital capacity limited. Prepare overflow facilities. Coordinate with private medical facilities. Establish patient transfer protocols to less affected areas.")
        
        if doctor_availability in ['scarce', 'none']:
            recommendations.append("MEDICAL PERSONNEL EMERGENCY: Critical shortage of medical staff. Request immediate deployment of medical teams from neighboring regions. Mobilize military medical corps. Coordinate with medical volunteer organizations. Establish telemedicine support if communication available.")
        elif doctor_availability == 'limited':
            recommendations.append("MEDICAL STAFFING CONCERN: Medical personnel shortage. Request additional doctors and nurses. Extend shifts with proper rest protocols. Prioritize critical cases. Train paramedics for expanded roles.")
    
    # Water & Food Resources Analysis
    if water_food_resources:
        water_supply = water_food_resources.get('water_supply', 'moderate')
        food_supply = water_food_resources.get('food_supply', 'moderate')
        
        if water_supply in ['critical', 'none']:
            recommendations.append("WATER CRISIS: Critical water shortage. Deploy emergency water tankers immediately. Establish water distribution points. Deploy water purification units. Coordinate with bottled water suppliers. Implement water rationing protocols. Check for contamination sources.")
        elif water_supply == 'moderate':
            recommendations.append("WATER SUPPLY CONCERN: Water supply limited. Monitor consumption rates. Prepare backup water sources. Deploy additional purification capacity. Establish conservation guidelines.")
        
        if food_supply in ['scarce', 'none']:
            recommendations.append("FOOD EMERGENCY: Critical food shortage. Activate emergency food distribution immediately. Coordinate with food banks and humanitarian organizations. Deploy mobile kitchens. Establish community feeding centers. Request food aid from national reserves. Prioritize vulnerable populations (children, elderly, medical patients).")
        elif food_supply == 'moderate':
            recommendations.append("FOOD SUPPLY CONCERN: Food supplies limited. Organize systematic distribution. Monitor inventory levels. Coordinate with local suppliers. Prevent hoarding. Establish rationing if needed.")
    
    # Logistics & Communication Resources Analysis
    if logistics_resources:
        transport_status = logistics_resources.get('transport_status', 'moderate')
        communication_status = logistics_resources.get('communication_status', 'moderate')
        
        if transport_status in ['collapsed', 'limited']:
            recommendations.append("TRANSPORTATION CRISIS: Transport infrastructure severely compromised. Deploy helicopters for critical transport. Establish alternative routes immediately. Use boats/amphibious vehicles if applicable. Clear priority access routes. Coordinate with military for heavy equipment. Establish supply drop zones for aerial delivery.")
        elif transport_status == 'moderate':
            recommendations.append("TRANSPORT CONCERN: Transportation partially disrupted. Prioritize emergency vehicle access. Establish traffic control points. Monitor route conditions continuously. Prepare alternative routes.")
        
        if communication_status in ['collapsed', 'limited']:
            recommendations.append("COMMUNICATION BREAKDOWN: Communication systems severely disrupted. Deploy satellite phones immediately. Establish radio communication network. Use runners/messengers for critical information. Set up information centers at key locations. Deploy mobile communication units. Coordinate with amateur radio operators.")
        elif communication_status == 'moderate':
            recommendations.append("COMMUNICATION CONCERN: Communication systems intermittent. Establish backup communication channels. Deploy additional equipment. Prioritize emergency communications. Maintain communication logs.")
    
    # Emergency Response Resources Analysis
    if emergency_resources:
        personnel_availability = emergency_resources.get('personnel_availability', 'moderate')
        equipment_status = emergency_resources.get('equipment_status', 'moderate')
        
        if personnel_availability in ['limited', 'none']:
            recommendations.append("PERSONNEL SHORTAGE: Emergency response personnel critically low. Request immediate deployment of additional response teams. Mobilize reserves and volunteers. Coordinate with neighboring jurisdictions for mutual aid. Establish volunteer training programs. Prioritize critical operations. Implement shift rotation to prevent burnout.")
        elif personnel_availability == 'moderate':
            recommendations.append("PERSONNEL CONCERN: Response personnel stretched. Request additional teams. Organize efficient shift rotations. Prioritize high-impact operations. Prepare for extended operations.")
        
        if equipment_status in ['limited', 'none']:
            recommendations.append("EQUIPMENT SHORTAGE: Critical shortage of emergency equipment. Request immediate equipment deployment from regional stockpiles. Coordinate equipment sharing with neighboring areas. Prioritize essential equipment for life-saving operations. Establish equipment maintenance protocols. Request military equipment support if available.")
        elif equipment_status == 'moderate':
            recommendations.append("EQUIPMENT CONCERN: Emergency equipment limited. Monitor equipment status. Establish maintenance priorities. Request backup equipment. Optimize equipment utilization.")
    
    # Resource-based enhancements (overall)
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
        
        # CRITICAL: Gas Leak / Hazmat / Chemical (HIGHEST PRIORITY)
        if any(word in context_lower for word in ['gas leak', 'gas', 'chemical', 'toxic', 'hazmat', 'hazardous']):
            if any(word in context_lower for word in ['leak', 'spill', 'exposure', 'contamination', 'detected', 'reported']):
                recommendations.append("CRITICAL HAZMAT EMERGENCY: Immediate evacuation of affected area. Deploy hazmat teams with protective equipment. Establish exclusion zone. Shut off gas/chemical sources. Evacuate downwind areas. Request specialized hazmat response units. Set up decontamination stations. Monitor air quality continuously.")
            elif 'gas leak' in context_lower:
                recommendations.append("GAS LEAK EMERGENCY: Evacuate immediate area. No open flames or electrical switches. Shut off gas supply. Ventilate area if safe. Deploy gas detection equipment. Establish safety perimeter. Request utility company emergency response.")
        
        # Explosion / Fire spreading
        elif any(word in context_lower for word in ['explosion', 'blast', 'exploded']):
            recommendations.append("EXPLOSION RESPONSE: Secure perimeter immediately. Search for secondary devices/hazards. Evacuate surrounding buildings. Deploy bomb squad if intentional. Establish triage for blast injuries. Check for structural damage. Assess for gas leaks or fire hazards.")
        
        elif any(word in context_lower for word in ['fire', 'burning', 'flames']):
            if any(word in context_lower for word in ['spreading', 'out of control', 'uncontrolled', 'growing']):
                recommendations.append("FIRE EMERGENCY: Deploy additional fire brigades immediately. Establish firebreaks. Evacuate threatened areas. Protect critical infrastructure. Request mutual aid from neighboring departments. Monitor wind direction. Prepare for spot fires.")
        
        # Building collapse / Structural failure
        elif any(word in context_lower for word in ['building', 'structure', 'dam', 'levee']):
            if any(word in context_lower for word in ['collapse', 'collapsed', 'collapsing', 'failing', 'breach']):
                recommendations.append("STRUCTURAL COLLAPSE: Deploy urban search and rescue teams immediately. Establish collapse zone perimeter. Evacuate adjacent structures. Use specialized equipment for victim location. Shore up unstable structures. Coordinate with structural engineers. Prepare for secondary collapses.")
        
        # Flooding / Rising water
        elif any(word in context_lower for word in ['flood', 'water']):
            if any(word in context_lower for word in ['rising', 'increasing', 'overflow', 'surge']):
                recommendations.append("FLOOD ALERT: Evacuate low-lying areas immediately. Deploy water rescue teams. Establish evacuation routes to higher ground. Monitor water levels continuously. Prepare for infrastructure failure. Secure hazardous materials. Cut power to flooded areas.")
        
        # Disease outbreak / Epidemic
        elif any(word in context_lower for word in ['disease', 'epidemic', 'outbreak', 'infection', 'contagious']):
            recommendations.append("EPIDEMIC RESPONSE: Establish quarantine zones immediately. Deploy medical teams with PPE. Set up isolation facilities. Implement contact tracing. Distribute medical supplies and vaccines if available. Coordinate with health authorities. Establish public health messaging.")
        
        # Evacuation blocked / People trapped
        elif any(word in context_lower for word in ['trapped', 'stranded', 'isolated', 'evacuation']):
            if any(word in context_lower for word in ['unable', 'cannot', 'impossible', 'blocked', 'cut off']):
                recommendations.append("EVACUATION CRISIS: Deploy helicopters for aerial rescue. Establish alternative evacuation routes. Use boats/amphibious vehicles if applicable. Drop supplies to isolated areas. Establish communication with trapped populations. Prioritize medical evacuations.")
        
        # Medical/Healthcare related
        elif any(word in context_lower for word in ['doctor', 'doctors', 'medical', 'hospital', 'healthcare', 'physician', 'nurse', 'paramedic']):
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
def root():
    """Redirect to login page"""
    from flask import redirect, url_for
    return redirect(url_for('login'))


@app.route('/login')
def login():
    """Serve the login page"""
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    """Serve the main dashboard"""
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
        "resources_available": 50,  // optional legacy
        "infrastructure_quality": 50,  // optional
        "medical_resources": {  // optional qualitative
            "hospital_status": "moderate",
            "doctor_availability": "limited"
        },
        "water_food_resources": {  // optional qualitative
            "water_supply": "adequate",
            "food_supply": "moderate"
        },
        "logistics_resources": {  // optional qualitative
            "transport_status": "critical",
            "communication_status": "moderate"
        },
        "emergency_resources": {  // optional qualitative
            "personnel_availability": "moderate",
            "equipment_status": "adequate"
        },
        "additional_context": "No doctors available"  // optional
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
        
        # Qualitative resource inputs
        medical_resources = data.get('medical_resources')
        water_food_resources = data.get('water_food_resources')
        logistics_resources = data.get('logistics_resources')
        emergency_resources = data.get('emergency_resources')
        additional_context = data.get('additional_context', '')
        
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
            severity, population, resources_available, infrastructure_quality,
            medical_resources, water_food_resources, logistics_resources, emergency_resources,
            additional_context
        )
        priority = determine_priority(risk_score)
        
        # Generate AI-powered recommendation
        ai_service = get_ai_service()
        recommendation = ai_service.generate_recommendation(
            disaster_type=disaster_type,
            severity=severity,
            population=population,
            risk_score=risk_score,
            priority=priority,
            medical_resources=medical_resources,
            water_food_resources=water_food_resources,
            logistics_resources=logistics_resources,
            emergency_resources=emergency_resources,
            infrastructure_quality=infrastructure_quality,
            additional_context=additional_context
        )
        
        # Create response
        response = {
            'disaster_type': disaster_type,
            'severity': severity,
            'population': population,
            'resources_available': resources_available,
            'infrastructure_quality': infrastructure_quality,
            'medical_resources': medical_resources,
            'water_food_resources': water_food_resources,
            'logistics_resources': logistics_resources,
            'emergency_resources': emergency_resources,
            'additional_context': additional_context,
            'risk_score': round(risk_score, 2),
            'priority': priority,
            'recommendation': recommendation,  # AI-generated
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
        
        # Qualitative resource updates
        new_medical = new_findings.get('medical_resources', original.get('medical_resources'))
        new_water_food = new_findings.get('water_food_resources', original.get('water_food_resources'))
        new_logistics = new_findings.get('logistics_resources', original.get('logistics_resources'))
        new_emergency = new_findings.get('emergency_resources', original.get('emergency_resources'))
        
        # Recalculate risk with new information AND context impact
        new_risk_score, new_reasoning = calculate_risk_score(
            original['severity'],
            original['population'],
            new_resources,
            new_infrastructure,
            new_medical,
            new_water_food,
            new_logistics,
            new_emergency,
            additional_notes  # Context now affects risk calculation
        )
        new_priority = determine_priority(new_risk_score)
        
        # Generate AI-powered recommendation with updated context
        ai_service = get_ai_service()
        new_recommendation = ai_service.generate_recommendation(
            disaster_type=original['disaster_type'],
            severity=original['severity'],
            population=original['population'],
            risk_score=new_risk_score,
            priority=new_priority,
            medical_resources=new_medical,
            water_food_resources=new_water_food,
            logistics_resources=new_logistics,
            emergency_resources=new_emergency,
            infrastructure_quality=new_infrastructure,
            additional_context=additional_notes
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
                'medical_resources': new_medical,
                'water_food_resources': new_water_food,
                'logistics_resources': new_logistics,
                'emergency_resources': new_emergency,
                'additional_context': additional_notes,
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


@app.route('/api/resource-options', methods=['GET'])
def get_resource_options():
    """Get qualitative resource options and their descriptions"""
    return jsonify({
        'options': {
            'adequate': {'score': 1.0, 'description': 'Fully operational and sufficient'},
            'normal': {'score': 1.0, 'description': 'Normal operating capacity'},
            'moderate': {'score': 0.6, 'description': 'Partially available, some limitations'},
            'limited': {'score': 0.6, 'description': 'Significantly constrained'},
            'critical': {'score': 0.3, 'description': 'Severely limited, barely functional'},
            'scarce': {'score': 0.3, 'description': 'Extremely limited availability'},
            'none': {'score': 0.0, 'description': 'Completely unavailable'},
            'collapsed': {'score': 0.0, 'description': 'Total system failure'}
        },
        'categories': {
            'medical': {
                'weight': 0.35,
                'indicators': ['hospital_status', 'doctor_availability']
            },
            'water_food': {
                'weight': 0.30,
                'indicators': ['water_supply', 'food_supply']
            },
            'logistics': {
                'weight': 0.20,
                'indicators': ['transport_status', 'communication_status']
            },
            'emergency': {
                'weight': 0.15,
                'indicators': ['personnel_availability', 'equipment_status']
            }
        }
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
