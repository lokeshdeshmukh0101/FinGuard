import pytest

def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new_user@example.com",
            "name": "New User",
            "password": "Password123!",
            "role": "CUSTOMER"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new_user@example.com"
    assert data["role"] == "CUSTOMER"

def test_login_success_and_invalid(client):
    # 1. Register user
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": "login_user@example.com", "name": "Login User", "password": "SecretPassword123!", "role": "ANALYST"}
    )
    assert reg_res.status_code == 201

    # 2. Login with wrong password
    bad_res = client.post(
        "/api/v1/auth/login",
        json={"email": "login_user@example.com", "password": "WrongPassword!"}
    )
    assert bad_res.status_code == 401

    # 3. Login with correct password
    good_res = client.post(
        "/api/v1/auth/login",
        json={"email": "login_user@example.com", "password": "SecretPassword123!"}
    )
    assert good_res.status_code == 200
    token_data = good_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 4. Fetch /me profile with token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "login_user@example.com"
    assert me_data["role"] == "ANALYST"
