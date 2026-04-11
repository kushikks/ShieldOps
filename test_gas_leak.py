"""
Test gas leak and hazmat context detection
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import analyze_additional_context_impact, enhance_recommendation, calculate_risk_score

def test_gas_leak_detection():
    """Test that gas leak is detected and increases risk"""
    # Test gas leak context
    risk_modifier, context_analysis = analyze_additional_context_impact("Gas leak detected in the area")
    
    print(f"Risk Modifier: {risk_modifier}")
    print(f"Context Analysis: {context_analysis}")
    
    assert risk_modifier > 0, "Gas leak should increase risk"
    assert risk_modifier >= 15, f"Gas leak should add at least 15 points, got {risk_modifier}"
    assert len(context_analysis['hazmat_issues']) > 0, "Gas leak should be detected as hazmat issue"
    print("✓ Gas leak detection test passed!")

def test_gas_leak_risk_calculation():
    """Test that gas leak affects risk score calculation"""
    # Calculate risk without context
    risk_no_context, _ = calculate_risk_score(
        severity=7,
        population=50000,
        resources_available=50,
        infrastructure_quality=50,
        additional_context=""
    )
    
    # Calculate risk with gas leak context
    risk_with_gas_leak, reasoning = calculate_risk_score(
        severity=7,
        population=50000,
        resources_available=50,
        infrastructure_quality=50,
        additional_context="Gas leak detected, evacuating area"
    )
    
    print(f"\nRisk without context: {risk_no_context}")
    print(f"Risk with gas leak: {risk_with_gas_leak}")
    print(f"Difference: {risk_with_gas_leak - risk_no_context}")
    print("\nReasoning:")
    for reason in reasoning:
        print(f"  {reason}")
    
    assert risk_with_gas_leak > risk_no_context, "Gas leak should increase risk score"
    assert (risk_with_gas_leak - risk_no_context) >= 15, "Gas leak should add at least 15 points to risk"
    print("✓ Gas leak risk calculation test passed!")

def test_gas_leak_recommendation():
    """Test that gas leak generates specific recommendations"""
    recommendation = enhance_recommendation(
        base_recommendation="Deploy rescue teams",
        resources=50,
        infrastructure=50,
        priority="HIGH",
        additional_context="Gas leak reported in residential area"
    )
    
    print(f"\nRecommendation: {recommendation}")
    
    assert "HAZMAT" in recommendation or "GAS LEAK" in recommendation, "Should mention hazmat or gas leak"
    assert "evacuat" in recommendation.lower(), "Should recommend evacuation"
    print("✓ Gas leak recommendation test passed!")

def test_various_hazmat_scenarios():
    """Test various hazmat scenarios"""
    scenarios = [
        ("Gas leak detected", 15),
        ("Chemical spill reported", 15),
        ("Toxic fumes spreading", 15),
        ("Explosion at factory", 12),
        ("Fire spreading rapidly", 10),
        ("Building collapsed", 10),
        ("Disease outbreak", 9),
        ("Water rising rapidly", 7),
    ]
    
    print("\n" + "="*60)
    print("Testing various hazmat scenarios:")
    print("="*60)
    
    for context, expected_min_impact in scenarios:
        risk_modifier, context_analysis = analyze_additional_context_impact(context)
        print(f"\nContext: '{context}'")
        print(f"  Risk Impact: +{risk_modifier} points (expected: ≥{expected_min_impact})")
        print(f"  Analysis: {context_analysis}")
        
        assert risk_modifier >= expected_min_impact, f"'{context}' should add at least {expected_min_impact} points, got {risk_modifier}"
    
    print("\n✓ All hazmat scenario tests passed!")

if __name__ == "__main__":
    print("="*60)
    print("TESTING GAS LEAK AND HAZMAT CONTEXT DETECTION")
    print("="*60)
    
    test_gas_leak_detection()
    test_gas_leak_risk_calculation()
    test_gas_leak_recommendation()
    test_various_hazmat_scenarios()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✓")
    print("="*60)
