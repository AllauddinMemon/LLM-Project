from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_health():
    res = client.get('/healthz')
    assert res.status_code == 200
    assert res.json()['status'] == 'ok'

def test_chat_shape():
    # Smoke test for the endpoint shape; assumes graph can run in test env
    payload = {"query": "Which courses cover Python and data visualization?"}
    res = client.post('/chat', json=payload)
    assert res.status_code == 200
    body = res.json()
    assert 'answer' in body
    assert 'source_tool' in body
