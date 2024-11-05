import pytest
from .utils import create_user, login_user

def test_create_plan(client, unique_username, unique_email):
    username = create_user(client, unique_username, unique_email, "adminpassword")["username"]
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/plans/", json={
        "title": "Gold Plan",
        "description": "Standard plan which renews every 3 months",
        "renewal_period": 3,
        "tier": 2,
        "discount": 0.05
    }, headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    assert response.json()["title"] == "Gold Plan"
    assert response.json()["description"] == "Standard plan which renews every 3 months"

def test_get_plans(client, unique_username, unique_email):
    username = create_user(client, unique_username, unique_email, "adminpassword")["username"]
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/plans/",
        json={
            "title": "Silver Plan",
            "description": "Standard plan which renews every 3 months",
            "renewal_period": 3,
            "tier": 2,
            "discount": 0.05,
        },
        headers=headers,
    )

    response = client.get("/plans/", headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    plans = response.json()
    assert isinstance(plans, list)
    assert len(plans) > 0

def test_update_plan(client, unique_username, unique_email):
    username = create_user(client, unique_username, unique_email, "adminpassword")["username"]
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/plans/",
        json={
            "title": "Diamond plan",
            "description": "Exclusive plan which renews annually",
            "renewal_period": 12,
            "tier": 4,
            "discount": 0.25,
        },
        headers=headers,
    )
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    plan_id = response.json()["id"]

    response = client.put(
        f"/plans/{plan_id}",
        json={
            "title": "Updated Diamond plan",
            "description": "Updated Exclusive plan which renews annually",
            "renewal_period": 12,
            "tier": 4,
            "discount": 0.25,
        },
        headers=headers,
    )
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    assert response.json()["title"] == "Updated Diamond plan"
    assert (
        response.json()["description"] == "Updated Exclusive plan which renews annually"
    )

def test_delete_plan(client, unique_username, unique_email):
    username = create_user(client, unique_username, unique_email, "adminpassword")["username"]
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/plans/", json={
        "title": "Deleting Plan",
        "description": "Monthly subscription plan",
        "renewal_period": 1,
        "tier": 1,
        "discount": 0.1
    }, headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    plan_id = response.json()["id"]

    response = client.delete(f"/plans/{plan_id}", headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"

    # Verify plan is deleted
    response = client.get(f"/plans/{plan_id}", headers=headers)
    assert response.status_code == 404, f"Response status code: {response.status_code}, Response body: {response.text}"

def test_create_plan_with_zero_renewal_period(client, unique_username, unique_email):
    username = create_user(client, unique_username, unique_email, "adminpassword")["username"]
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/plans/", json={
        "title": "Invalid Plan",
        "description": "Plan with zero renewal period",
        "renewal_period": 0,
        "tier": 1,
        "discount": 0.1
    }, headers=headers)
    assert response.status_code == 422, f"Response status code: {response.status_code}, Response body: {response.text}"
