import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Verifica que el endpoint de salud /health retorne 200 y el estado esperado."""
    response = client.get('/health')
    assert response.status_code == 200
    assert b"HEALTH OK" in response.data

def test_home_page(client):
    """Verifica que la página principal renderice correctamente."""
    response = client.get('/')
    assert response.status_code == 200

def test_predict_api_valid_payload(client):
    """Verifica que el endpoint REST /predict_api reciba un JSON y devuelva la predicción."""
    payload = {
        'age': 35,
        'sex': 'male',
        'bmi': 26.5,
        'children': 2,
        'smoker': 'no',
        'region': 'northeast'
    }
    response = client.post('/predict_api', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert 'output' in data
    assert isinstance(data['output'], (int, float))
    assert data['output'] > 0
