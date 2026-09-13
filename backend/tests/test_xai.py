import pytest

def get_auth_token(client, email="xai_user@example.com", role="ANALYST"):
    reg_res = client.post("/api/v1/auth/register", json={"email": email, "name": "XAI User", "password": "Password123!", "role": role})
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    return login_res.json()["access_token"]

def test_xai_explanation_endpoint(client):
    admin_token = get_auth_token(client, "xai_admin@example.com", "ADMIN")
    cust_token = get_auth_token(client, "xai_cust@example.com", "CUSTOMER")
    
    cust_profile = client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {cust_token}"}).json()
    cust_id = cust_profile["id"]

    merchant_res = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "JewelryLux", "category": "JEWELRY", "location": "Paris, France"}
    )
    assert merchant_res.status_code == 201
    merch_id = merchant_res.json()["id"]

    tx_res = client.post(
        "/api/v1/transactions",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={
            "customer_id": cust_id,
            "merchant_id": merch_id,
            "amount": 1500.0,
            "location": "Paris, France",
            "device_id": "DEV-XAI-1"
        }
    )
    assert tx_res.status_code == 201
    tx_id = tx_res.json()["transaction_id"]

    # Call /risk/{tx_id} endpoint
    risk_res = client.get(f"/api/v1/risk/{tx_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert risk_res.status_code == 200
    data = risk_res.json()

    assert data["transaction_id"] == tx_id
    assert "contributing_factors" in data
    assert len(data["contributing_factors"]) >= 1
    assert "final_risk_score" in data
    assert "model_probability" in data
