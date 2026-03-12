import pytest
from fastapi.testclient import TestClient
from api.routes import app

client = TestClient(app)

def test_idempotency():
    payload = {
        "idempotency_key": "unique_key_123",
        "name": "Charlie",
        "age": 35,
        "credit_score": 700
    }

    resp1 = client.post("/trigger/loan_approval", json=payload)
    id1 = resp1.json()["request_id"]

    resp2 = client.post("/trigger/loan_approval", json=payload)
    id2 = resp2.json()["request_id"]

    assert id1 == id2
    assert resp2.json()["message"] == "Request already exists"


def test_invalid_input_intake():
    payload = {"name": "No Key"}
    response = client.post("/trigger/loan_approval", json=payload)
    assert response.status_code == 400