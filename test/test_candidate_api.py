import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine
from app import models

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Reset database schema for each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_candidate():
    data = {"name": "John Doe", "email": "john@example.com", "phone": "1234567890"}
    response = client.post("/candidates/", json=data)
    assert response.status_code == 200
    candidate = response.json()
    assert candidate["name"] == "John Doe"
    assert candidate["email"] == "john@example.com"
    assert candidate["phone"] == "1234567890"
    assert "id" in candidate

def test_read_candidates():
    # Create a candidate first
    data = {"name": "Alice", "email": "alice@example.com", "phone": "1112223333"}
    client.post("/candidates/", json=data)
    response = client.get("/candidates/")
    assert response.status_code == 200
    candidates = response.json()
    assert isinstance(candidates, list)
    assert len(candidates) >= 1

def test_read_candidate():
    # Create a candidate first
    data = {"name": "Bob", "email": "bob@example.com", "phone": "4445556666"}
    post_resp = client.post("/candidates/", json=data)
    candidate = post_resp.json()
    candidate_id = candidate["id"]

    get_resp = client.get(f"/candidates/{candidate_id}")
    assert get_resp.status_code == 200
    candidate_by_id = get_resp.json()
    assert candidate_by_id["id"] == candidate_id
    assert candidate_by_id["name"] == "Bob"

def test_update_candidate():
    # Create a candidate first
    data = {"name": "Charlie", "email": "charlie@example.com", "phone": "7778889999"}
    post_resp = client.post("/candidates/", json=data)
    candidate = post_resp.json()
    candidate_id = candidate["id"]

    update_data = {"name": "Charles", "email": "charles@example.com", "phone": "7778880000"}
    put_resp = client.put(f"/candidates/{candidate_id}", json=update_data)
    assert put_resp.status_code == 200
    updated_candidate = put_resp.json()
    assert updated_candidate["name"] == "Charles"
    assert updated_candidate["email"] == "charles@example.com"
    assert updated_candidate["phone"] == "7778880000"

def test_delete_candidate():
    # Create a candidate first
    data = {"name": "Daisy", "email": "daisy@example.com", "phone": "0001112222"}
    post_resp = client.post("/candidates/", json=data)
    candidate = post_resp.json()
    candidate_id = candidate["id"]

    delete_resp = client.delete(f"/candidates/{candidate_id}")
    assert delete_resp.status_code == 200
    deleted_candidate = delete_resp.json()
    assert deleted_candidate["id"] == candidate_id

    # Afterwards, fetching should return 404
    get_resp = client.get(f"/candidates/{candidate_id}")
    assert get_resp.status_code == 404
