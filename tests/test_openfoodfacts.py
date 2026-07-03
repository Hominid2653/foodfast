from unittest.mock import MagicMock, patch

import openfoodfacts_client as off


MOCK_PRODUCT_RESPONSE = {
    "status": 1,
    "product": {
        "product_name": "Test Cereal",
        "brands": "TestBrand",
        "code": "1234567890123",
        "ingredients_text": "Wheat, sugar",
        "quantity": "500 g",
        "categories": "Cereals",
    },
}

MOCK_SEARCH_RESPONSE = {
    "products": [
        {
            "product_name": "Search Result",
            "brands": "BrandX",
            "code": "9876543210987",
            "ingredients_text": "Water",
            "quantity": "1 L",
            "categories": "Beverages",
        }
    ]
}


@patch("openfoodfacts_client.requests.get")
def test_fetch_by_barcode_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_PRODUCT_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = off.fetch_by_barcode("1234567890123")
    assert result["product_name"] == "Test Cereal"
    assert result["barcode"] == "1234567890123"


@patch("openfoodfacts_client.requests.get")
def test_fetch_by_barcode_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": 0, "product": None}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    assert off.fetch_by_barcode("000") is None


@patch("openfoodfacts_client.requests.get")
def test_search_by_name(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_SEARCH_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    results = off.search_by_name("water")
    assert len(results) == 1
    assert results[0]["product_name"] == "Search Result"


def test_external_product_route(client):
    with patch("app.off.fetch_by_barcode") as mock_fetch:
        mock_fetch.return_value = {
            "product_name": "API Product",
            "brands": "API Brand",
            "barcode": "111",
            "ingredients_text": "",
            "quantity": "",
            "categories": "",
        }
        response = client.get("/external/product/111")
        assert response.status_code == 200
        assert response.get_json()["product"]["product_name"] == "API Product"


def test_import_from_api(client):
    with patch("app.off.fetch_by_barcode") as mock_fetch:
        mock_fetch.return_value = {
            "product_name": "Imported Item",
            "brands": "Import Co",
            "barcode": "555",
            "ingredients_text": "Stuff",
            "quantity": "1 kg",
            "categories": "Food",
        }
        response = client.post(
            "/inventory/from-api",
            json={"barcode": "555", "price": 9.99, "stock": 5},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["product_name"] == "Imported Item"
        assert data["price"] == 9.99
        assert data["stock"] == 5
