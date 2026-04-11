"""
Test resource-specific recommendations
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import enhance_recommendation

def test_medical_resource_recommendations():
    """Test that medical resource shortages generate specific recommendations"""
    print("\n" + "="*60)
    print("TEST 1: Medical Resource Shortages")
    print("="*60)
    
    # Test critical hospital status
    recommendation = enhance_recommendation(
        base_recommendation="Deploy rescue teams",
        resources=50,
        infrastructure=50,
        priority="HIGH",
        additional_context="",
        medical_resources={
            'hospital_status': 'critical',
            'doctor_availability': 'scarce'
        }
    )
    
    print("\nScenario: Hospital Critical, Doctors Scarce")
    print(f"Recommendation:\n{recommendation}\n")
    
    assert 'MEDICAL INFRASTRUCTURE CRISIS' in recommendation or 'HOSPITAL' in recommendation.upper()
    assert 'MEDICAL PERSONNEL EMERGENCY' in recommendation or 'MEDICAL STAFF' in recommendation.upper()
    print("✓ Medical shortage recommendations generated!")

def test_water_food_recommendations():
    """Test that water and food shortages generate specific recommendations"""
    print("\n" + "="*60)
    print("TEST 2: Water & Food Shortages")
    print("="*60)
    
    recommendation = enhance_recommendation(
        base_recommendation="Deploy rescue teams",
        resources=50,
        infrastructure=50,
        priority="HIGH",
        additional_context="",
        water_food_resources={
            'water_supply': 'critical',
            'food_supply': 'scarce'
        }
    )
    
    print("\nScenario: Water Critical, Food Scarce")
    print(f"Recommendation:\n{recommendation}\n")
    
    assert 'WATER CRISIS' in recommendation or 'WATER' in recommendation.upper()
    assert 'FOOD EMERGENCY' in recommendation or 'FOOD' in recommendation.upper()
    print("✓ Water and food shortage recommendations generated!")

def test_logistics_recommendations():
    """Test that logistics issues generate specific recommendations"""
    print("\n" + "="*60)
    print("TEST 3: Logistics & Communication Issues")
    print("="*60)
    
    recommendation = enhance_recommendation(
        base_recommendation="Deploy rescue teams",
        resources=50,
        infrastructure=50,
        priority="HIGH",
        additional_context="",
        logistics_resources={
            'transport_status': 'collapsed',
            'communication_status': 'limited'
        }
    )
    
    print("\nScenario: Transport Collapsed, Communication Limited")
    print(f"Recommendation:\n{recommendation}\n")
    
    assert 'TRANSPORTATION CRISIS' in recommendation or 'TRANSPORT' in recommendation.upper()
    assert 'COMMUNICATION' in recommendation.upper()
    print("✓ Logistics recommendations generated!")

def test_emergency_resources_recommendations():
    """Test that emergency resource shortages generate specific recommendations"""
    print("\n" + "="*60)
    print("TEST 4: Emergency Response Resource Shortages")
    print("="*60)
    
    recommendation = enhance_recommendation(
        base_recommendation="Deploy rescue teams",
        resources=50,
        infrastructure=50,
        priority="HIGH",
        additional_context="",
        emergency_resources={
            'personnel_availability': 'none',
            'equipment_status': 'limited'
        }
    )
    
    print("\nScenario: No Personnel, Limited Equipment")
    print(f"Recommendation:\n{recommendation}\n")
    
    assert 'PERSONNEL SHORTAGE' in recommendation or 'PERSONNEL' in recommendation.upper()
    assert 'EQUIPMENT SHORTAGE' in recommendation or 'EQUIPMENT' in recommendation.upper()
    print("✓ Emergency resource recommendations generated!")

def test_comprehensive_scenario():
    """Test comprehensive scenario with multiple resource issues"""
    print("\n" + "="*60)
    print("TEST 5: Comprehensive Multi-Resource Shortage")
    print("="*60)
    
    recommendation = enhance_recommendation(
        base_recommendation="Deploy rescue teams",
        resources=50,
        infrastructure=50,
        priority="HIGH",
        additional_context="Gas leak detected",
        medical_resources={
            'hospital_status': 'critical',
            'doctor_availability': 'scarce'
        },
        water_food_resources={
            'water_supply': 'critical',
            'food_supply': 'scarce'
        },
        logistics_resources={
            'transport_status': 'limited',
            'communication_status': 'limited'
        },
        emergency_resources={
            'personnel_availability': 'limited',
            'equipment_status': 'limited'
        }
    )
    
    print("\nScenario: All Resources Critical + Gas Leak")
    print(f"Recommendation:\n{recommendation}\n")
    
    # Should have recommendations for all categories
    assert 'MEDICAL' in recommendation.upper()
    assert 'WATER' in recommendation.upper()
    assert 'FOOD' in recommendation.upper()
    assert 'TRANSPORT' in recommendation.upper() or 'COMMUNICATION' in recommendation.upper()
    assert 'PERSONNEL' in recommendation.upper() or 'EQUIPMENT' in recommendation.upper()
    assert 'HAZMAT' in recommendation.upper() or 'GAS' in recommendation.upper()
    print("✓ Comprehensive recommendations generated for all resource categories!")

def test_adequate_resources():
    """Test that adequate resources don't generate shortage warnings"""
    print("\n" + "="*60)
    print("TEST 6: Adequate Resources (No Shortages)")
    print("="*60)
    
    recommendation = enhance_recommendation(
        base_recommendation="Deploy rescue teams",
        resources=50,
        infrastructure=50,
        priority="MEDIUM",
        additional_context="",
        medical_resources={
            'hospital_status': 'adequate',
            'doctor_availability': 'adequate'
        },
        water_food_resources={
            'water_supply': 'adequate',
            'food_supply': 'adequate'
        },
        logistics_resources={
            'transport_status': 'normal',
            'communication_status': 'normal'
        },
        emergency_resources={
            'personnel_availability': 'adequate',
            'equipment_status': 'adequate'
        }
    )
    
    print("\nScenario: All Resources Adequate")
    print(f"Recommendation:\n{recommendation}\n")
    
    # Should NOT have critical shortage warnings
    assert 'CRISIS' not in recommendation
    assert 'EMERGENCY' not in recommendation or 'EMERGENCY' in 'Deploy rescue teams'
    print("✓ No shortage warnings for adequate resources!")

if __name__ == "__main__":
    print("="*60)
    print("TESTING RESOURCE-SPECIFIC RECOMMENDATIONS")
    print("="*60)
    
    test_medical_resource_recommendations()
    test_water_food_recommendations()
    test_logistics_recommendations()
    test_emergency_resources_recommendations()
    test_comprehensive_scenario()
    test_adequate_resources()
    
    print("\n" + "="*60)
    print("ALL RESOURCE RECOMMENDATION TESTS PASSED! ✓")
    print("="*60)
