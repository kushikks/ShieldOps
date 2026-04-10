"""
Comprehensive test suite for ShieldOps application
Tests functional, scenario, and failure cases
"""

import pytest
import json
from app import app, calculate_risk_score, determine_priority


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_endpoint(self, client):
        """Test health check returns 200 and correct status"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert data['service'] == 'Disaster Response System'


class TestRiskCalculation:
    """Test risk score calculation logic"""
    
    def test_low_risk_scenario(self):
        """Test low severity and low population"""
        risk, reasoning = calculate_risk_score(severity=2, population=500, resources_available=70, infrastructure_quality=70)
        assert risk < 40
        assert determine_priority(risk) == 'LOW'
        assert len(reasoning) > 0
    
    def test_medium_risk_scenario(self):
        """Test medium severity and medium population"""
        risk, reasoning = calculate_risk_score(severity=6, population=50000, resources_available=40, infrastructure_quality=40)
        assert 40 <= risk < 70
        assert determine_priority(risk) == 'MEDIUM'
        assert len(reasoning) > 0
    
    def test_high_risk_scenario(self):
        """Test high severity and high population"""
        risk, reasoning = calculate_risk_score(severity=10, population=200000, resources_available=20, infrastructure_quality=20)
        assert risk >= 70
        assert determine_priority(risk) == 'HIGH'
        assert len(reasoning) > 0
    
    def test_risk_score_cap(self):
        """Test risk score is capped at 100"""
        risk, reasoning = calculate_risk_score(severity=10, population=1000000, resources_available=0, infrastructure_quality=0)
        assert risk <= 100
    
    def test_resources_reduce_risk(self):
        """Test that higher resources reduce risk"""
        risk_low_resources, _ = calculate_risk_score(severity=7, population=50000, resources_available=20, infrastructure_quality=50)
        risk_high_resources, _ = calculate_risk_score(severity=7, population=50000, resources_available=80, infrastructure_quality=50)
        assert risk_high_resources < risk_low_resources
    
    def test_infrastructure_reduces_risk(self):
        """Test that better infrastructure reduces risk"""
        risk_poor_infra, _ = calculate_risk_score(severity=7, population=50000, resources_available=50, infrastructure_quality=20)
        risk_good_infra, _ = calculate_risk_score(severity=7, population=50000, resources_available=50, infrastructure_quality=80)
        assert risk_good_infra < risk_poor_infra


class TestSimulationEndpoint:
    """Test main simulation endpoint"""
    
    def test_valid_flood_simulation(self, client):
        """Test valid flood disaster simulation"""
        payload = {
            'disaster_type': 'flood',
            'severity': 7,
            'population': 50000,
            'resources_available': 50,
            'infrastructure_quality': 50
        }
        
        response = client.post('/api/simulate',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['disaster_type'] == 'flood'
        assert data['severity'] == 7
        assert data['population'] == 50000
        assert 'risk_score' in data
        assert 'priority' in data
        assert 'recommendation' in data
        assert 'reasoning' in data
        assert data['priority'] in ['LOW', 'MEDIUM', 'HIGH']
        assert len(data['reasoning']) > 0
    
    def test_valid_earthquake_simulation(self, client):
        """Test valid earthquake disaster simulation"""
        payload = {
            'disaster_type': 'earthquake',
            'severity': 9,
            'population': 100000
        }
        
        response = client.post('/api/simulate',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['disaster_type'] == 'earthquake'
        assert 'Deploy search and rescue teams' in data['recommendation']
    
    def test_all_disaster_types(self, client):
        """Test all supported disaster types"""
        disaster_types = ['flood', 'earthquake', 'fire', 'cyclone', 
                         'tsunami', 'landslide', 'drought', 'epidemic']
        
        for disaster in disaster_types:
            payload = {
                'disaster_type': disaster,
                'severity': 5,
                'population': 10000
            }
            
            response = client.post('/api/simulate',
                                  data=json.dumps(payload),
                                  content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['disaster_type'] == disaster


class TestInputValidation:
    """Test input validation and error handling"""
    
    def test_missing_data(self, client):
        """Test request with no data"""
        response = client.post('/api/simulate',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_invalid_disaster_type(self, client):
        """Test invalid disaster type"""
        payload = {
            'disaster_type': 'invalid_disaster',
            'severity': 5,
            'population': 10000
        }
        
        response = client.post('/api/simulate',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_severity_out_of_range_low(self, client):
        """Test severity below minimum"""
        payload = {
            'disaster_type': 'flood',
            'severity': 0,
            'population': 10000
        }
        
        response = client.post('/api/simulate',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_severity_out_of_range_high(self, client):
        """Test severity above maximum"""
        payload = {
            'disaster_type': 'flood',
            'severity': 11,
            'population': 10000
        }
        
        response = client.post('/api/simulate',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_negative_population(self, client):
        """Test negative population value"""
        payload = {
            'disaster_type': 'flood',
            'severity': 5,
            'population': -1000
        }
        
        response = client.post('/api/simulate',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 400


class TestHistoryEndpoint:
    """Test history tracking"""
    
    def test_history_endpoint(self, client):
        """Test history endpoint returns data"""
        response = client.get('/api/history')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'history' in data
        assert 'count' in data
        assert isinstance(data['history'], list)
    
    def test_history_after_simulation(self, client):
        """Test history is updated after simulation"""
        # Run a simulation
        payload = {
            'disaster_type': 'fire',
            'severity': 6,
            'population': 25000
        }
        
        client.post('/api/simulate',
                   data=json.dumps(payload),
                   content_type='application/json')
        
        # Check history
        response = client.get('/api/history')
        data = json.loads(response.data)
        
        assert data['count'] > 0
        assert any(item['disaster_type'] == 'fire' for item in data['history'])


class TestDisasterTypesEndpoint:
    """Test disaster types listing"""
    
    def test_get_disaster_types(self, client):
        """Test getting available disaster types"""
        response = client.get('/api/disasters')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'disaster_types' in data
        assert len(data['disaster_types']) > 0
        assert 'flood' in data['disaster_types']
        assert 'earthquake' in data['disaster_types']


class TestDeterministicBehavior:
    """Test that same inputs produce same outputs"""
    
    def test_deterministic_output(self, client):
        """Test same input produces same output"""
        payload = {
            'disaster_type': 'cyclone',
            'severity': 8,
            'population': 75000
        }
        
        # Run simulation twice
        response1 = client.post('/api/simulate',
                               data=json.dumps(payload),
                               content_type='application/json')
        data1 = json.loads(response1.data)
        
        response2 = client.post('/api/simulate',
                               data=json.dumps(payload),
                               content_type='application/json')
        data2 = json.loads(response2.data)
        
        # Results should be identical
        assert data1['risk_score'] == data2['risk_score']
        assert data1['priority'] == data2['priority']
        assert data1['recommendation'] == data2['recommendation']


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_minimum_values(self, client):
        """Test minimum valid values"""
        payload = {
            'disaster_type': 'drought',
            'severity': 1,
            'population': 0
        }
        
        response = client.post('/api/simulate',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['priority'] == 'LOW'
    
    def test_maximum_values(self, client):
        """Test maximum valid values"""
        payload = {
            'disaster_type': 'tsunami',
            'severity': 10,
            'population': 1000000,
            'resources_available': 20,
            'infrastructure_quality': 20
        }
        
        response = client.post('/api/simulate',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['priority'] == 'HIGH'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])



class TestReevaluation:
    """Test re-evaluation functionality"""
    
    def test_reevaluate_with_improved_resources(self, client):
        """Test re-evaluation with improved resources"""
        # Initial simulation
        payload = {
            'disaster_type': 'earthquake',
            'severity': 8,
            'population': 75000,
            'resources_available': 30,
            'infrastructure_quality': 40
        }
        
        response = client.post('/api/simulate',
                              data=json.dumps(payload),
                              content_type='application/json')
        initial_data = json.loads(response.data)
        
        # Re-evaluate with improved resources
        reevaluate_payload = {
            'original_timestamp': initial_data['timestamp'],
            'new_findings': {
                'resources_available': 70,
                'infrastructure_quality': 40,
                'additional_notes': 'Emergency supplies arrived'
            }
        }
        
        response = client.post('/api/reevaluate',
                              data=json.dumps(reevaluate_payload),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'original_simulation' in data
        assert 'updated_assessment' in data
        assert 'changes' in data
        assert data['changes']['risk_change'] < 0  # Risk should decrease
    
    def test_reevaluate_nonexistent_simulation(self, client):
        """Test re-evaluation of non-existent simulation"""
        payload = {
            'original_timestamp': '2024-01-01T00:00:00',
            'new_findings': {
                'resources_available': 70
            }
        }
        
        response = client.post('/api/reevaluate',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 404


class TestLearnings:
    """Test learning and insights functionality"""
    
    def test_learnings_endpoint(self, client):
        """Test learnings endpoint"""
        response = client.get('/api/learnings')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'learnings' in data
        assert 'count' in data
        assert 'insights' in data
    
    def test_learnings_after_reevaluation(self, client):
        """Test that learnings are recorded after re-evaluation"""
        # Initial simulation
        payload = {
            'disaster_type': 'flood',
            'severity': 7,
            'population': 50000,
            'resources_available': 40,
            'infrastructure_quality': 50
        }
        
        response = client.post('/api/simulate',
                              data=json.dumps(payload),
                              content_type='application/json')
        initial_data = json.loads(response.data)
        
        # Re-evaluate
        reevaluate_payload = {
            'original_timestamp': initial_data['timestamp'],
            'new_findings': {
                'resources_available': 80,
                'infrastructure_quality': 70,
                'additional_notes': 'Situation improved'
            }
        }
        
        client.post('/api/reevaluate',
                   data=json.dumps(reevaluate_payload),
                   content_type='application/json')
        
        # Check learnings
        response = client.get('/api/learnings')
        data = json.loads(response.data)
        
        assert data['count'] > 0
