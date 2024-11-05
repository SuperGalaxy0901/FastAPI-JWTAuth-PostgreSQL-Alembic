import pytest
import random
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from .utils import create_user, login_user

# Define a SQLite URL for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create the engine and session for the test database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override for the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Apply the override to the FastAPI app
app.dependency_overrides[get_db] = override_get_db

# Create the database tables
Base.metadata.create_all(bind=engine)

# Fixture for the test client
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def unique_email():
    return f"user{random.randint(1000, 9999)}@example.com"

@pytest.fixture(scope="function")
def unique_username():
    return f"user{random.randint(1000, 9999)}"

@pytest.fixture(scope="function")
def admin_user(client, unique_username, unique_email):
    create_user(client, unique_username, unique_email, "adminpassword")
    token = login_user(client, unique_username, "adminpassword")
    return token

@pytest.fixture(scope="function")
def create_plans(client, admin_user):
    headers = {"Authorization": f"Bearer {admin_user}"}
    plans = [
        {"title": "Monthly", "description": "Monthly subscription plan", "renewal_period": 1},
        {"title": "Quarterly", "description": "Quarterly subscription plan", "renewal_period": 3},
        {"title": "Half-Yearly", "description": "Half-yearly subscription plan", "renewal_period": 6},
        {"title": "Annual", "description": "Annual subscription plan", "renewal_period": 12}
    ]
    created_plans = []
    for plan in plans:
        response = client.post("/plans/", json=plan, headers=headers)
        assert response.status_code == 200
        created_plans.append(response.json())
    return created_plans

@pytest.fixture(scope="function")
def create_magazine(client, admin_user):
    headers = {"Authorization": f"Bearer {admin_user}"}
    response = client.post("/magazines/", json={
        "name": "Tech Monthly",
        "description": "A magazine about the latest in tech.",
        "base_price": 10.0,
        "discount_quarterly": 0.05,
        "discount_half_yearly": 0.1,
        "discount_annual": 0.15
    }, headers=headers)
    assert response.status_code == 200
    return response.json()

@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    # Remove the test database file after the tests are completed
    if os.path.exists("test.db"):
        os.remove("test.db")
        print("Test database file removed.")
