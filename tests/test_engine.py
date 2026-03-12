import pytest
import httpx
from fastapi.testclient import TestClient
from api.routes import app

client = TestClient(app)

def test_successful_loan_flow():
    payload = {
        "idempotency_key": "test_happy_001",
        "name": "Alice",
        "age": 30,
        "credit_score": 800
    }

    response = client.post("/trigger/loan_approval", json=payload)
    assert response.status_code == 200
    request_id = response.json()["request_id"]

    import time
    time.sleep(2)

    status_resp = client.get(f"/status/{request_id}")
    assert status_resp.status_code == 200
    assert len(status_resp.json()["history"]) > 0


def test_rejection_flow():
    payload = {
        "idempotency_key": "test_reject_001",
        "name": "Bob",
        "age": 16,
        "credit_score": 800
    }

    response = client.post("/trigger/loan_approval", json=payload)
    request_id = response.json()["request_id"]

    import time
    time.sleep(1)

    status_resp = client.get(f"/status/{request_id}")
    assert "REJECTED" in status_resp.json()["current_status"]