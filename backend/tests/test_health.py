from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_success():
    response = client.get('/health')
    assert response.status_code == 200
    payload = response.json()
    assert payload['service'] == 'lenny-growth-assistant'
    assert payload['status'] in {'ok', 'degraded'}
    assert payload.get('database') in {'connected', 'unavailable', None}
