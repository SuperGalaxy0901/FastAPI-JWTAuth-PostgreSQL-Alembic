import pytest
from .utils import create_user, login_user, create_plan, create_magazine

def test_create_magazine(client, unique_username, unique_email):
    username = create_user(client, unique_username, unique_email, "adminpassword")["username"]
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    
    name_suffix = "create"
    response = create_magazine(client, headers, name_suffix)
    assert response["name"] == f"Magazine {name_suffix}"

def test_get_magazines(client, unique_username, unique_email):
    username = create_user(client, unique_username, unique_email, "adminpassword")["username"]
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    
    name_suffix = "get"
    create_magazine(client, headers, name_suffix)

    response = client.get("/magazines/", headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    magazines = response.json()
    assert isinstance(magazines, list)
    assert len(magazines) > 0

def test_update_magazine(client, unique_username, unique_email):
    username = create_user(client, unique_username, unique_email, "adminpassword")["username"]
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    
    name_suffix = "update"
    magazine = create_magazine(client, headers, name_suffix)

    response = client.put(f"/magazines/{magazine['id']}", json={
        "name": f"Updated Tech Weekly {name_suffix}",
        "description": "An updated weekly tech magazine",
        "base_price": 6.0,
        "discount_quarterly": 0.15,
        "discount_half_yearly": 0.25,
        "discount_annual": 0.35
    }, headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    assert response.json()["name"] == f"Updated Tech Weekly {name_suffix}"

def test_delete_magazine(client, unique_username, unique_email):
    username = create_user(client, unique_username, unique_email, "adminpassword")["username"]
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}
    
    name_suffix = "delete"
    magazine = create_magazine(client, headers, name_suffix)

    response = client.delete(f"/magazines/{magazine['id']}", headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"

    # Verify magazine is deleted
    response = client.get(f"/magazines/{magazine['id']}", headers=headers)
    assert response.status_code == 404, f"Response status code: {response.status_code}, Response body: {response.text}"
