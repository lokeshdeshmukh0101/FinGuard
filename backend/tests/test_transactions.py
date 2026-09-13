import pytest
from app.models.domain import User, Customer, Merchant, UserRole
from app.core.security import get_password_hash

def get_auth_token(client, email="cust_tx@example.com", role="CUSTOMER"):
    reg_res = client.post("/api/v1/auth/register", json={"email": email, "name": "Auth User", "password": "Password123!", "role": role})
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    return login_res.json()["access_token"]

def test_process_normal_transaction(client):
    token = get_auth_token(client, "normal_cust@example.com", "CUSTOMER")
    
    # Create customer and merchant via register & db session or APIs
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    user_id = me_res.json()["id"]

    cust_profile = client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {token}"}).json()
    cust_id = cust_profile["id"]

    # Create merchant as admin
    admin_token = get_auth_token(client, "admin_tx@example.com", "ADMIN")
    merchant_res = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "TechStore", "category": "ELECTRONICS", "location": "New York, USA"}
    )
    merch_id = merchant_res.json()["id"]

    res = client.post(
        "/api/v1/transactions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "customer_id": cust_id,
            "merchant_id": merch_id,
            "amount": 85.0,
            "location": "New York, USA",
            "device_id": "DEV-001"
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "APPROVED"
    assert data["risk_level"] == "LOW"
    assert data["risk_score"] < 40

def test_process_high_risk_transaction(client):
    token = get_auth_token(client, "high_risk_cust@example.com", "CUSTOMER")
    cust_profile = client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {token}"}).json()
    cust_id = cust_profile["id"]

    admin_token = get_auth_token(client, "admin_tx2@example.com", "ADMIN")
    merchant_res = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "CryptoExchange", "category": "CRYPTO", "location": "London, UK"}
    )
    merch_id = merchant_res.json()["id"]

    res = client.post(
        "/api/v1/transactions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "customer_id": cust_id,
            "merchant_id": merch_id,
            "amount": 1200.0, # High amount
            "location": "Tokyo, Japan", # Unusual location
            "device_id": "DEV-999"
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "FLAGGED"
    assert data["risk_level"] == "HIGH"
    assert data["risk_score"] >= 70
    assert len(data["reasons"]) >= 2
