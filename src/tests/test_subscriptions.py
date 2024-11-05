from operator import ge
import pytest
from .utils import create_user, generate_random_plan_name, login_user, create_plan, create_magazine


def test_create_subscription(client, unique_username, unique_email):
    username, email, user_id = create_user(
        client, unique_username, unique_email, "adminpassword"
    ).values()
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}

    name_suffix = "create_sub"
    plan = create_plan(client, headers, title=generate_random_plan_name(), discount=0.1)
    magazine = create_magazine(client, headers, name_suffix, base_price=100)

    response = client.post(
        "/subscriptions/",
        json={
            "user_id": user_id,
            "magazine_id": magazine["id"],
            "plan_id": plan["id"],
            "renewal_date": "2024-12-31",
        },
        headers=headers,
    )
    assert (
        response.status_code == 200
    ), f"Response status code: {response.status_code}, Response body: {response.text}"
    expected_price = 100 * (1 - plan["discount"])
    assert response.json()["price"] == expected_price


def test_get_subscriptions(client, unique_username, unique_email):
    username, email, user_id = create_user(
        client, unique_username, unique_email, "adminpassword"
    ).values()
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}

    name_suffix = "get_sub"
    plan = create_plan(client, headers, title=generate_random_plan_name(), discount=0.25)
    magazine = create_magazine(client, headers, name_suffix, base_price=100)

    client.post(
        "/subscriptions/",
        json={
            "user_id": user_id,
            "magazine_id": magazine["id"],
            "plan_id": plan["id"],
            "renewal_date": "2024-12-31",
        },
        headers=headers,
    )

    response = client.get("/subscriptions/", headers=headers)
    assert (
        response.status_code == 200
    ), f"Response status code: {response.status_code}, Response body: {response.text}"
    subscriptions = response.json()
    assert isinstance(subscriptions, list)
    assert len(subscriptions) > 0


def test_update_subscription(client, unique_username, unique_email):
    username, email, user_id = create_user(
        client, unique_username, unique_email, "adminpassword"
    ).values()
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}

    name_suffix = "update_sub"
    plan = create_plan(client, headers, title=generate_random_plan_name(), discount=0.1)
    magazine = create_magazine(client, headers, name_suffix, base_price=100)

    response = client.post(
        "/subscriptions/",
        json={
            "user_id": user_id,
            "magazine_id": magazine["id"],
            "plan_id": plan["id"],
            "renewal_date": "2024-12-31",
        },
        headers=headers,
    )
    assert (
        response.status_code == 200
    ), f"Response status code: {response.status_code}, Response body: {response.text}"
    subscription_id = response.json()["id"]

    new_plan = create_plan(
        client,
        headers,
        title=generate_random_plan_name(),
        description="Gold subscription plan",
        renewal_period=3,
        discount=0.1,
        tier=2,
    )
    response = client.put(
        f"/subscriptions/{subscription_id}",
        json={
            "user_id": user_id,
            "magazine_id": magazine["id"],
            "plan_id": new_plan["id"],
            "renewal_date": "2025-01-31",
        },
        headers=headers,
    )
    assert (
        response.status_code == 200
    ), f"Response status code: {response.status_code}, Response body: {response.text}"
    expected_price = 100 * (1 - new_plan["discount"])
    assert response.json()["price"] == expected_price


def test_delete_subscription(client, unique_username, unique_email):
    username, email, user_id = create_user(
        client, unique_username, unique_email, "adminpassword"
    ).values()
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}

    plan = create_plan(client, headers, title=generate_random_plan_name(), discount=0.1)
    name_suffix = "delete_sub"
    magazine = create_magazine(client, headers, name_suffix, base_price=100)

    response = client.post(
        "/subscriptions/",
        json={
            "user_id": user_id,
            "magazine_id": magazine["id"],
            "plan_id": plan["id"],
            "renewal_date": "2024-12-31",
        },
        headers=headers,
    )
    assert (
        response.status_code == 200
    ), f"Response status code: {response.status_code}, Response body: {response.text}"
    subscription_id = response.json()["id"]

    response = client.delete(f"/subscriptions/{subscription_id}", headers=headers)
    assert (
        response.status_code == 200
    ), f"Response status code: {response.status_code}, Response body: {response.text}"

    # Verify subscription is marked as inactive
    response = client.get(f"/subscriptions/{subscription_id}", headers=headers)
    assert (
        response.status_code == 200
    ), f"Response status code: {response.status_code}, Response body: {response.text}"
    assert not response.json()[
        "is_active"
    ], f"Subscription is not marked as inactive: {response.json()}"


def test_price_greater_than_zero(client, unique_username, unique_email):
    username, email, user_id = create_user(
        client, unique_username, unique_email, "adminpassword"
    ).values()
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a magazine with a base price of 100
    name_suffix = "price_gt_zero"
    magazine = create_magazine(client, headers, name_suffix, base_price=100)

    # Create a plan with a discount that would make the price zero or negative
    bad_plan = create_plan(
        client,
        headers,
        title="Bad Plan",
        description="Bad subscription plan",
        renewal_period=1,
        discount=1.0,
        tier=5,
    )  # 100% discount

    response = client.post(
        "/subscriptions/",
        json={
            "user_id": user_id,
            "magazine_id": magazine["id"],
            "plan_id": bad_plan["id"],
            "renewal_date": "2024-12-31",
        },
        headers=headers,
    )
    assert (
        response.status_code == 422
    ), f"Response status code: {response.status_code}, Response body: {response.text}"
    assert (
        response.json()["detail"] == "Price must be greater than zero"
    ), f"Unexpected error message: {response.json()}"


def test_price_calculation(client, unique_username, unique_email):
    username, email, user_id = create_user(
        client, unique_username, unique_email, "adminpassword"
    ).values()
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a magazine with a base price of 100
    name_suffix = "price_calc"
    magazine = create_magazine(client, headers, name_suffix, base_price=100)

    # Create different plans with varying discounts
    silver_plan = create_plan(
        client,
        headers,
        title=generate_random_plan_name(),
        description="Silver subscription plan",
        renewal_period=1,
        discount=0.0,
        tier=1,
    )
    gold_plan = create_plan(
        client,
        headers,
        title=generate_random_plan_name(),
        description="Gold subscription plan",
        renewal_period=3,
        discount=0.1,
        tier=2,
    )  # 10% discount
    platinum_plan = create_plan(
        client,
        headers,
        title=generate_random_plan_name(),
        description="Platinum subscription plan",
        renewal_period=6,
        discount=0.15,
        tier=3,
    )  # 15% discount
    diamond_plan = create_plan(
        client,
        headers,
        title=generate_random_plan_name(),
        description="Diamond subscription plan",
        renewal_period=12,
        discount=0.25,
        tier=4,
    )  # 25% discount

    # Create subscriptions for each plan and check the calculated price
    response = client.post(
        "/subscriptions/",
        json={
            "user_id": user_id,
            "magazine_id": magazine["id"],
            "plan_id": silver_plan["id"],
            "renewal_date": "2024-12-31",
        },
        headers=headers,
    )
    assert (
        response.status_code == 200
    ), f"Response status code: {response.status_code}, Response body: {response.text}"
    assert response.json()["price"] == 100 * (1 - silver_plan["discount"])

    response = client.post(
        "/subscriptions/",
        json={
            "user_id": user_id,
            "magazine_id": magazine["id"],
            "plan_id": gold_plan["id"],
            "renewal_date": "2024-12-31",
        },
        headers=headers,
    )
    assert (
        response.status_code == 200
    ), f"Response status code: {response.status_code}, Response body: {response.text}"
    assert response.json()["price"] == 100 * (1 - gold_plan["discount"])

    response = client.post(
        "/subscriptions/",
        json={
            "user_id": user_id,
            "magazine_id": magazine["id"],
            "plan_id": platinum_plan["id"],
            "renewal_date": "2024-12-31",
        },
        headers=headers,
    )
    assert (
        response.status_code == 200
    ), f"Response status code: {response.status_code}, Response body: {response.text}"
    assert response.json()["price"] == 100 * (1 - platinum_plan["discount"])

    response = client.post(
        "/subscriptions/",
        json={
            "user_id": user_id,
            "magazine_id": magazine["id"],
            "plan_id": diamond_plan["id"],
            "renewal_date": "2024-12-31",
        },
        headers=headers,
    )
    assert (
        response.status_code == 200
    ), f"Response status code: {response.status_code}, Response body: {response.text}"
    assert response.json()["price"] == 100 * (1 - diamond_plan["discount"])


def test_unique_subscription_constraint(client, unique_username, unique_email):
    # Create a user and login
    username, _, user_id = create_user(client, unique_username, unique_email, "adminpassword").values()
    token = login_user(client, username, "adminpassword")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a plan and magazine
    name_suffix = "unique_sub"
    plan = create_plan(client, headers, title=generate_random_plan_name())
    magazine = create_magazine(client, headers, name_suffix)

    # Create the first subscription
    response = client.post("/subscriptions/", json={
        "user_id": user_id,  # Assuming the created user ID is 1
        "magazine_id": magazine["id"],
        "plan_id": plan["id"],
        "renewal_date": "2024-12-31"
    }, headers=headers)
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    
    # Attempt to create a duplicate subscription
    response = client.post("/subscriptions/", json={
        "user_id": user_id,  # Assuming the created user ID is 1
        "magazine_id": magazine["id"],
        "plan_id": plan["id"],
        "renewal_date": "2024-12-31"
    }, headers=headers)
    
    # Assert that the second subscription creation attempt fails
    assert response.status_code == 422, f"Response status code: {response.status_code}, Response body: {response.text}"
    assert "already exists" in response.text, "Expected error message for duplicate subscription not found"
