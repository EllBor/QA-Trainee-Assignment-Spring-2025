import requests
import pytest
import uuid

BASE_URL_V1 = "https://qa-internship.avito.com/api/1"
BASE_URL_V2 = "https://qa-internship.avito.com/api/2"

@pytest.fixture
def valid_item():
    return {
        "sellerID": 123456,
        "name": "Test Item",
        "price": 999,
        "statistics": {
            "views": 0,
            "likes": 0,
            "contacts": 0
        }
    }

@pytest.fixture
def created_item(valid_item):
    response = requests.post(f"{BASE_URL_V1}/item", json=valid_item)
    assert response.status_code == 200
    return response.json()["status"].split(" - ")[-1]

# TC_001
def test_create_valid_item(valid_item):
    response = requests.post(f"{BASE_URL_V1}/item", json=valid_item)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"].startswith("Сохранили объявление - ")

# TC_002
def test_create_item_missing_required_fields():
    response = requests.post(f"{BASE_URL_V1}/item", json={"statistics": {"views": 0}})
    assert response.status_code == 200
    data = response.json()
    assert data["status"].startswith("Сохранили объявление - ")

# TC_003
def test_create_item_empty_body():
    response = requests.post(f"{BASE_URL_V1}/item", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["status"].startswith("Сохранили объявление - ")

# TC_004
def test_get_existing_item_by_id(created_item):
    response = requests.get(f"{BASE_URL_V1}/item/{created_item}")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list), f"Expected list, got {type(data)}"
    assert len(data) == 1, f"Expected one item, got {len(data)}"

    item = data[0] 
    assert item["id"] == created_item

    required_keys = ["name", "price", "sellerId", "statistics", "createdAt"]
    assert all(k in item for k in required_keys), f"Missing key(s) in response: {item}"

# TC_005
def test_get_nonexistent_item():
    fake_id = str(uuid.uuid4())
    response = requests.get(f"{BASE_URL_V1}/item/{fake_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "404"
    assert "item" in data["result"]["message"]

# TC_006
def test_get_item_without_id():
    response = requests.get(f"{BASE_URL_V1}/item/")
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 400
    assert "route /api/1/item/ not found" in data["message"]

# TC_007
def test_get_items_by_seller():
    response = requests.get(f"{BASE_URL_V1}/123456/item")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# TC_008
def test_get_items_invalid_seller():
    response = requests.get(f"{BASE_URL_V1}/059331500900910192000000/item")
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "400"
    assert "передан некорректный идентификатор продавца" in data["result"]["message"]

# TC_009
def test_get_statistic_v1(created_item):
    response = requests.get(f"{BASE_URL_V1}/statistic/{created_item}")
    assert response.status_code == 200
    data = response.json()
    for item in data:
        assert all(k in item for k in ["contacts", "likes", "viewCount"]), f"Missing key in item: {item}"


# TC_010
def test_get_statistic_nonexistent():
    response = requests.get(f"{BASE_URL_V1}/statistic/{uuid.uuid4()}")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "404"
    assert "statistic" in data["result"]["message"]

# TC_011
def test_get_statistic_without_id():
    response = requests.get(f"{BASE_URL_V1}/statistic/")
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == 400
    assert "route /api/1/statistic/ not found" in data["message"]

# TC_012
def test_get_item_null_id():
    response = requests.get(f"{BASE_URL_V1}/item/null")
    assert response.status_code == 400
    data = response.json()
    assert "ID айтема не UUID" in data["result"]["message"]

# TC_013
def test_get_stat_null_id():
    response = requests.get(f"{BASE_URL_V1}/statistic/null")
    assert response.status_code == 400
    data = response.json()
    assert "передан некорректный идентификатор объявления" in data["result"]["message"]

# TC_014
def test_get_items_null_seller():
    response = requests.get(f"{BASE_URL_V1}/null/item")
    assert response.status_code == 400
    data = response.json()
    assert "передан некорректный идентификатор продавца" in data["result"]["message"]

# TC_015
def test_get_statistic_v2(created_item):
    response = requests.get(f"{BASE_URL_V2}/statistic/{created_item}")
    assert response.status_code == 200
    data = response.json()
    for item in data:
        assert all(k in item for k in ["contacts", "likes", "viewCount"]), f"Missing key in item: {item}"

# TC_016
def test_get_statistic_nonexistent_v2():
    response = requests.get(f"{BASE_URL_V2}/statistic/{uuid.uuid4()}")
    assert response.status_code == 200
    data = response.json()

# TC_017
def test_get_statistic_null_v2():
    response = requests.get(f"{BASE_URL_V2}/statistic/null")
    assert response.status_code == 200

# TC_018
def test_delete_item(created_item):
    response = requests.delete(f"{BASE_URL_V2}/item/{created_item}")
    assert response.status_code == 200

# TC_019
def test_delete_nonexistent():
    fake_id = str(uuid.uuid4())
    response = requests.delete(f"{BASE_URL_V2}/item/{fake_id}")
    assert response.status_code == 404
    data = response.json()
    assert "result" in data
    assert "status" in data
    assert isinstance(data["result"], dict)
    assert "message" in data["result"]
    assert "messages" in data["result"]
    assert isinstance(data["result"]["message"], str)


# TC_020
def test_delete_null_id():
    response = requests.delete(f"{BASE_URL_V2}/item/null")
    assert response.status_code == 400
    data = response.json()
    assert "переданный id айтема некорректный" in data["result"]["message"]
