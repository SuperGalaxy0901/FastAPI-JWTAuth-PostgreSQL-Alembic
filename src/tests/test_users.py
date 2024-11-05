import pytest
from .utils import create_user, login_user
from app.core.jwt import create_access_token
from datetime import timedelta

def test_register_user(client, unique_username, unique_email):
    response = client.post("/users/register", json={
        "username": unique_username,
        "email": unique_email,
        "password": "testpassword"
    })
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"

def test_login_user(client, unique_username, unique_email):
    username = create_user(client, unique_username, unique_email, "loginpassword")["username"]
    response = client.post("/users/login", json={
        "username": username,
        "password": "loginpassword"
    })
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"


def test_reset_password(client, unique_username, unique_email):
    username, email, _ = create_user(client, unique_username, unique_email, "testpassword").values()
    token = login_user(client, username, "testpassword")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/users/reset-password", params={"email": email}, headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"


def test_user_deactivation(client, unique_username, unique_email):
    username = create_user(client, unique_username, unique_email, "deactivatepassword")["username"]
    token = login_user(client, username, "deactivatepassword")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete(f"/users/deactivate/{username}", headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"

    # Verify user is deactivated
    response = client.get(f"/users/{username}", headers=headers)
    assert response.status_code == 404, f"Response status code: {response.status_code}, Response body: {response.text}"


def test_token_refresh(client, unique_username, unique_email):
    username = create_user(client, unique_username, unique_email, "refreshpassword")["username"]
    login_response = client.post("/users/login", json={
        "username": username,
        "password": "refreshpassword"
    })
    assert login_response.status_code == 200, f"Response status code: {login_response.status_code}, Response body: {login_response.text}"
    refresh_token = login_response.json()["refresh_token"]
    headers = {"Authorization": f"Bearer {refresh_token}"}

    response = client.post("/users/token/refresh", headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    assert "access_token" in response.json(), "Access token not found in response"
    assert "refresh_token" in response.json(), "Refresh token not found in response"


def test_token_expiry(client, unique_username, unique_email):
    username = create_user(client, unique_username, unique_email, "expirypassword")["username"]
    token = create_access_token({"sub": username}, expires_delta=timedelta(seconds=2))
    headers = {"Authorization": f"Bearer {token}"}

    # Verify token works initially
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"

    # Wait for token to expire
    import time
    time.sleep(3)

    # Verify token has expired
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 401, f"Response status code: {response.status_code}, Response body: {response.text}"
