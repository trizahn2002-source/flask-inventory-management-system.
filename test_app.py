# Test suite for Flask inventory API endpoints
import pytest
from unittest.mock import patch, Mock
from app import app, inventory


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_inventory():
    # Reset inventory before each test so tests don't interfere with each other
    inventory.clear()
    inventory.extend([
        {"id": 1, "name": "Organic Almond Milk", "brand": "Silk", "price": 3.99, "stock": 20},
        {"id": 2, "name": "Peanut Butter", "brand": "Jif", "price": 4.99, "stock": 15},
    ])
    yield


def test_get_all_items(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["name"] == "Organic Almond Milk"


def test_get_single_item_found(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Organic Almond Milk"


def test_get_single_item_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_add_item(client):
    payload = {"name": "Bread", "brand": "Wonder", "price": 2.5, "stock": 10}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Bread"
    assert data["id"] == 3  # next_id after 2 existing items


def test_add_item_missing_name(client):
    response = client.post("/inventory", json={"brand": "Wonder"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_update_item(client):
    response = client.patch("/inventory/1", json={"price": 5.99})
    assert response.status_code == 200
    assert response.get_json()["price"] == 5.99


def test_update_item_not_found(client):
    response = client.patch("/inventory/999", json={"price": 5.99})
    assert response.status_code == 404


def test_delete_item(client):
    response = client.delete("/inventory/1")
    assert response.status_code == 200
    # confirm it's actually gone
    check = client.get("/inventory/1")
    assert check.status_code == 404


def test_delete_item_not_found(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404


@patch("app.requests.get")
def test_fetch_from_openfoodfacts_success(mock_get, client):
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {
        "products": [{"product_name": "Oat Milk", "brands": "Oatly"}]
    }
    mock_get.return_value = mock_response

    response = client.post("/inventory/fetch", json={"query": "oat milk"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Oat Milk"
    assert data["brand"] == "Oatly"


@patch("app.requests.get")
def test_fetch_from_openfoodfacts_no_results(mock_get, client):
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json.return_value = {"products": []}
    mock_get.return_value = mock_response

    response = client.post("/inventory/fetch", json={"query": "nonexistent item xyz"})
    assert response.status_code == 404


@patch("app.requests.get")
def test_fetch_from_openfoodfacts_api_failure(mock_get, client):
    mock_get.side_effect = Exception("Connection timed out")

    response = client.post("/inventory/fetch", json={"query": "milk"})
    assert response.status_code == 502


def test_fetch_missing_query(client):
    response = client.post("/inventory/fetch", json={})
    assert response.status_code == 400  # will fail until you fix the 500 -> 400 bug