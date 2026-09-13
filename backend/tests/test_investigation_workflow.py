import pytest

def get_token(client, email, role):
    client.post("/api/v1/auth/register", json={"email": email, "name": f"User {role}", "password": "Password123!", "role": role})
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": "Password123!"})
    return login_res.json()["access_token"]

def test_full_investigation_workflow(client):
    analyst_token = get_token(client, "inv_analyst@example.com", "ANALYST")
    cust_token = get_token(client, "inv_cust@example.com", "CUSTOMER")
    admin_token = get_token(client, "inv_admin@example.com", "ADMIN")

    # 1. Get customer and create merchant
    cust_id = client.get("/api/v1/customers/me", headers={"Authorization": f"Bearer {cust_token}"}).json()["id"]
    merch_res = client.post(
        "/api/v1/merchants",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "GlobalCryptoEx", "category": "CRYPTO", "location": "London, UK"}
    )
    merch_id = merch_res.json()["id"]

    # 2. Trigger High Risk Transaction
    tx_res = client.post(
        "/api/v1/transactions",
        headers={"Authorization": f"Bearer {cust_token}"},
        json={
            "customer_id": cust_id,
            "merchant_id": merch_id,
            "amount": 2500.0, # High amount ratio
            "location": "Tokyo, Japan", # Location mismatch
            "device_id": "DEV-SUSPICIOUS-1"
        }
    )
    assert tx_res.status_code == 201
    tx_data = tx_res.json()
    assert tx_data["status"] == "FLAGGED"
    tx_id = tx_data["transaction_id"]

    # 3. Check Alerts list
    alerts_res = client.get("/api/v1/alerts", headers={"Authorization": f"Bearer {analyst_token}"})
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert len(alerts) >= 1
    alert_id = alerts[0]["id"]

    # 4. Submit Investigation Decision (CONFIRMED_FRAUD)
    inv_res = client.post(
        "/api/v1/investigations",
        headers={"Authorization": f"Bearer {analyst_token}"},
        json={
            "transaction_id": tx_id,
            "decision": "CONFIRMED_FRAUD",
            "notes": "Stolen card credentials used from unfamiliar IP & country."
        }
    )
    assert inv_res.status_code == 201
    inv_data = inv_res.json()
    assert inv_data["decision"] == "CONFIRMED_FRAUD"

    # 5. Verify Transaction status is updated to REJECTED
    tx_detail = client.get(f"/api/v1/transactions/{tx_id}", headers={"Authorization": f"Bearer {analyst_token}"}).json()
    assert tx_detail["status"] == "REJECTED"

    # 6. Verify Dashboard stats
    stats_res = client.get("/api/v1/dashboard/statistics", headers={"Authorization": f"Bearer {analyst_token}"})
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["kpis"]["confirmed_fraud"] >= 1

    # 7. Verify Audit logs
    audit_res = client.get("/api/v1/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert audit_res.status_code == 200
    assert len(audit_res.json()) >= 1
