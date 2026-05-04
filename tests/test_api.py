"""
test_api.py - Proper pytest tests for ShieldOps API endpoints.
Uses Flask's built-in test client — NO live server required.
"""
import sys
import os

# Ensure root is on the path so `app` and `models` can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

# ---------------------------------------------------------------------------
# App factory / fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def client():
    """Create a Flask test client with an in-memory SQLite DB."""
    # Import here so path is set first
    import app as flask_app

    flask_app.app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret',
    })

    with flask_app.app.app_context():
        flask_app.db.create_all()
        yield flask_app.app.test_client()
        flask_app.db.drop_all()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_json_shape(self, client):
        data = response = client.get('/health').get_json()
        assert 'status' in data


# ---------------------------------------------------------------------------
# Simulation endpoint
# ---------------------------------------------------------------------------

class TestSimulationEndpoint:
    """Test /api/simulate with valid and invalid payloads."""

    VALID_PAYLOAD = {
        'disaster_type': 'flood',
        'severity': 7,
        'population': 50000
    }

    def test_valid_simulation_returns_200(self, client):
        resp = client.post('/api/simulate', json=self.VALID_PAYLOAD)
        assert resp.status_code == 200

    def test_simulation_response_has_required_fields(self, client):
        data = client.post('/api/simulate', json=self.VALID_PAYLOAD).get_json()
        for field in ('disaster_type', 'severity', 'population', 'risk_score', 'priority', 'recommendation'):
            assert field in data, f"Missing field: {field}"

    def test_simulation_disaster_type_echoed(self, client):
        data = client.post('/api/simulate', json=self.VALID_PAYLOAD).get_json()
        assert data['disaster_type'] == 'flood'

    def test_risk_score_is_numeric(self, client):
        data = client.post('/api/simulate', json=self.VALID_PAYLOAD).get_json()
        assert isinstance(data['risk_score'], (int, float))
        assert 0 <= data['risk_score'] <= 100

    def test_missing_disaster_type_returns_400(self, client):
        payload = {'severity': 5, 'population': 10000}
        resp = client.post('/api/simulate', json=payload)
        assert resp.status_code == 400

    def test_missing_severity_returns_400(self, client):
        payload = {'disaster_type': 'earthquake', 'population': 10000}
        resp = client.post('/api/simulate', json=payload)
        assert resp.status_code == 400

    def test_missing_population_returns_400(self, client):
        payload = {'disaster_type': 'earthquake', 'severity': 5}
        resp = client.post('/api/simulate', json=payload)
        assert resp.status_code == 400

    def test_severity_out_of_range_returns_400(self, client):
        payload = {'disaster_type': 'flood', 'severity': 15, 'population': 10000}
        resp = client.post('/api/simulate', json=payload)
        assert resp.status_code == 400

    def test_high_severity_produces_higher_risk(self, client):
        low = client.post('/api/simulate', json={
            'disaster_type': 'flood', 'severity': 2, 'population': 50000
        }).get_json()
        high = client.post('/api/simulate', json={
            'disaster_type': 'flood', 'severity': 9, 'population': 50000
        }).get_json()
        assert high['risk_score'] > low['risk_score']


# ---------------------------------------------------------------------------
# History endpoint
# ---------------------------------------------------------------------------

class TestHistoryEndpoint:
    def test_history_returns_200(self, client):
        resp = client.get('/api/history')
        assert resp.status_code == 200

    def test_history_has_count(self, client):
        data = client.get('/api/history').get_json()
        assert 'count' in data
        assert isinstance(data['count'], int)

    def test_history_populates_after_simulation(self, client):
        # Run a sim first
        client.post('/api/simulate', json={
            'disaster_type': 'cyclone', 'severity': 6, 'population': 30000
        })
        data = client.get('/api/history').get_json()
        assert data['count'] >= 1
