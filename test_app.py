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
        risk = calculate_risk_score(severity=2, population=500)
        assert risk < 40
        assert determine_priority(risk) == 'LOW'
    
    def test_medium_risk_scenario(self):
        """Test medium severity and medium population"""
        risk = calculate_risk_score(severity=5, population=5000)
        assert 40 <= risk < 70
        assert determine_priority(risk) == 'MEDIUM'
    
    def test_high_risk_scenario(self):
        """Test high severity and high population"""
        risk = calculate_risk_score(severity=9, population=200000)
        assert risk >= 70
        assert determine_priority(risk) == 'HIGH'
    
    def test_risk_score_cap(self):
        """Test risk score is capped at 100"""
        risk = calculate_risk_score(severity=10, population=1000000)
        assert risk <= 100


class TestSimulationEndpoint:
    """Test main simulation endpoint"""
    
    def test_valid_flood_simulation(self, client):
        """Test valid flood disaster simulation"""
        payload = {
            'disaster_type': 'flood',
            'severity': 7,
            'population': 50000
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
        assert data['priority'] in ['LOW', 'MEDIUM', 'HIGH']
    
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
            'population': 1000000
        }
        
        response = client.post('/api/simulate',
                              data=json.dumps(payload),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['priority'] == 'HIGH'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
