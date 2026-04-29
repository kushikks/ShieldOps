"""
Test AI Service functionality
"""

import pytest
from ai_service import AIRecommendationService


def test_ai_service_initialization():
    """Test AI service can be initialized"""
    service = AIRecommendationService()
    assert service is not None


def test_fallback_recommendation():
    """Test fallback recommendations work without API key"""
    service = AIRecommendationService()
    
    recommendation = service.generate_recommendation(
        disaster_type='earthquake',
        severity=8,
        population=50000,
        risk_score=75.5,
        priority='HIGH',
        medical_resources={'hospital_status': 'critical', 'doctor_availability': 'limited'},
        water_food_resources={'water_supply': 'moderate', 'food_supply': 'adequate'},
        logistics_resources={'transport_status': 'limited', 'communication_status': 'moderate'},
        emergency_resources={'personnel_availability': 'moderate', 'equipment_status': 'adequate'},
        infrastructure_quality=50,
        additional_context='Gas leak detected'
    )
    
    assert recommendation is not None
    assert len(recommendation) > 0
    assert 'earthquake' in recommendation.lower() or 'rescue' in recommendation.lower()


def test_prompt_building():
    """Test prompt is built correctly with all context"""
    service = AIRecommendationService()
    
    prompt = service._build_prompt(
        disaster_type='flood',
        severity=7,
        population=10000,
        risk_score=65.0,
        priority='MEDIUM',
        medical_resources={'hospital_status': 'moderate', 'doctor_availability': 'adequate'},
        water_food_resources={'water_supply': 'critical', 'food_supply': 'moderate'},
        logistics_resources={'transport_status': 'limited', 'communication_status': 'normal'},
        emergency_resources={'personnel_availability': 'adequate', 'equipment_status': 'moderate'},
        infrastructure_quality=60,
        additional_context='Rising water levels'
    )
    
    assert 'FLOOD' in prompt
    assert '7/10' in prompt
    assert '10,000' in prompt
    assert '65.0/100' in prompt
    assert 'MEDIUM' in prompt
    assert 'critical' in prompt
    assert 'Rising water levels' in prompt


def test_fallback_includes_warning():
    """Test fallback recommendations include warning message"""
    service = AIRecommendationService()
    
    recommendation = service._generate_fallback('fire', 'HIGH', 'Spreading rapidly')
    
    assert '⚠️' in recommendation or 'AI recommendations unavailable' in recommendation
    assert 'fire' in recommendation.lower() or 'Fire' in recommendation


def test_different_disaster_types():
    """Test fallback works for all disaster types"""
    service = AIRecommendationService()
    
    disaster_types = ['flood', 'earthquake', 'fire', 'cyclone', 'tsunami', 'landslide', 'drought', 'epidemic']
    
    for disaster_type in disaster_types:
        recommendation = service._generate_fallback(disaster_type, 'MEDIUM', '')
        assert recommendation is not None
        assert len(recommendation) > 0


def test_priority_affects_fallback():
    """Test priority level affects fallback recommendations"""
    service = AIRecommendationService()
    
    high_rec = service._generate_fallback('flood', 'HIGH', '')
    medium_rec = service._generate_fallback('flood', 'MEDIUM', '')
    low_rec = service._generate_fallback('flood', 'LOW', '')
    
    assert 'URGENT' in high_rec or 'immediate' in high_rec.lower()
    assert high_rec != medium_rec
    assert medium_rec != low_rec


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
