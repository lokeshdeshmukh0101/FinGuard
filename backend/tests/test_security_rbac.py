import pytest

def get_token(client, email, role):
    client.post("/api/v1/auth/register", json={"email": email, "name": f"User {role}", "password": "Password123!", "role": role})
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    return login_res.json()["access_token"]

def test_customer_cannot_access_analyst_alerts(client):
    cust_token = get_token(client, "cust_sec@example.com", "CUSTOMER")
    
    # Customer attempts to view alerts queue
    res = client.get("/api/v1/alerts", headers={"Authorization": f"Bearer {cust_token}"})
    assert res.status_code == 403
    assert "not authorized" in res.json()["detail"]

def test_customer_cannot_submit_investigation(client):
    cust_token = get_token(client, "cust_sec2@example.com", "CUSTOMER")
    
    res = client.post(
        "/api/v1/investigations",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={"transaction_id": "tx-fake", "decision": "CONFIRMED_FRAUD", "notes": "Hacked"}
    )
    assert res.status_code == 403

def test_invalid_token_rejected(client):
    res = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid_garbage_token"})
    assert res.status_code == 401

def test_negative_amount_validation(client):
    cust_token = get_token(client, "cust_sec3@example.com", "CUSTOMER")
    cust_profile = client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {cust_token}"}).json()
    
    # Submit transaction with negative amount (-50.00)
    res = client.post(
        "/api/v1/transactions",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={
            "customer_id": cust_profile["id"],
            "merchant_id": "merch-fake",
            "amount": -50.0,
            "location": "New York, USA",
            "device_id": "DEV-1"
        }
    )
    assert res.status_code == 422 # Pydantic Validation Error
