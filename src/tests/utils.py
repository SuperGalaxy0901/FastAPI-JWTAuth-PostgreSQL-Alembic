import random
from app.schemas.user import UserCreate
from app.schemas.magazine import MagazineCreate


def create_user(client, base_username: str, base_email: str, password: str) -> dict:
    unique_id = random.randint(1000, 9999)
    username = f"{base_username}{unique_id}"
    email = f"{base_email.split('@')[0]}{unique_id}@{base_email.split('@')[1]}"
    
    user_data = UserCreate(username=username, email=email, password=password)
    response = client.post("/users/register", json=user_data.model_dump())
    user_id = response.json()["id"]
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    print(f"Created user: {username}, {email}, {password}")
    return dict(username=username, email=email, user_id=user_id)


def login_user(client, username: str, password: str):
    response = client.post("/users/login", json={"username": username, "password": password})
    assert response.status_code == 200, f"Response status code: {response.status_code}, Response body: {response.text}"
    return response.json()["access_token"]


def create_plan(
    client,
    headers,
    title="Monthly",
    description="Monthly subscription plan",
    renewal_period=1,
    discount=0.0,
    tier=1,
):
    response = client.post(
        "/plans/",
        json={
            "title": title,
            "description": description,
            "renewal_period": renewal_period,
            "discount": discount,
            "tier": tier,
        },
        headers=headers,
    )
    assert (
        response.status_code == 200
    ), f"Response status code: {response.status_code}, Response body: {response.text}"
    return response.json()


def create_magazine(client, headers, name_suffix, base_price=100):
    magazine_data = MagazineCreate(
        name=f"Magazine {name_suffix}",
        description=f"Description {name_suffix}",
        base_price=base_price,
    )
    response = client.post(
        "/magazines/", json=magazine_data.model_dump(), headers=headers
    )
    assert (
        response.status_code == 200
    ), f"Response status code: {response.status_code}, Response body: {response.text}"
    print(
        f"Created magazine: Magazine {name_suffix}, Description {name_suffix}, {base_price}"
    )
    return response.json()


def generate_random_plan_name():
    random_words = ["Silver", "Gold", "Platinum", "Diamond", "Titanium"]
    random_suffix = random.randint(1000, 9999)
    return f"{random.choice(random_words)} Plan {random_suffix}"
