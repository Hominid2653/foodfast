def test_list_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 3
    assert data[0]["product_name"] == "Organic Almond Milk"


def test_get_single_item(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["brands"] == "Silk"


def test_get_missing_item(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404


def test_create_item(client):
    payload = {
        "product_name": "Green Tea",
        "brands": "Lipton",
        "price": 5.99,
        "stock": 20,
    }
    response = client.post("/inventory", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 4
    assert data["product_name"] == "Green Tea"

    listed = client.get("/inventory").get_json()
    assert len(listed) == 4


def test_create_item_missing_name(client):
    response = client.post("/inventory", json={"price": 1.0})
    assert response.status_code == 400


def test_update_item(client):
    response = client.patch("/inventory/1", json={"price": 6.50, "stock": 10})
    assert response.status_code == 200
    data = response.get_json()
    assert data["price"] == 6.50
    assert data["stock"] == 10


def test_update_missing_item(client):
    response = client.patch("/inventory/999", json={"price": 1.0})
    assert response.status_code == 404


def test_delete_item(client):
    response = client.delete("/inventory/2")
    assert response.status_code == 204
    assert client.get("/inventory/2").status_code == 404
    assert len(client.get("/inventory").get_json()) == 2


def test_delete_missing_item(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404
