"""Client for the OpenFoodFacts public API."""

import requests

BASE_URL = "https://world.openfoodfacts.org"
TIMEOUT = 10


def _extract_product(raw: dict) -> dict | None:
    if raw.get("status") != 1 or not raw.get("product"):
        return None
    product = raw["product"]
    return {
        "product_name": product.get("product_name", ""),
        "brands": product.get("brands", ""),
        "barcode": product.get("code", product.get("_id", "")),
        "ingredients_text": product.get("ingredients_text", ""),
        "quantity": product.get("quantity", ""),
        "categories": product.get("categories", ""),
    }


def fetch_by_barcode(barcode: str) -> dict | None:
    """Fetch a single product by barcode from OpenFoodFacts."""
    url = f"{BASE_URL}/api/v0/product/{barcode}.json"
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return _extract_product(response.json())


def search_by_name(name: str, page_size: int = 5) -> list[dict]:
    """Search products by name; returns a list of normalized product dicts."""
    url = f"{BASE_URL}/cgi/search.pl"
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": page_size,
    }
    response = requests.get(url, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    products = []
    for hit in data.get("products", []):
        products.append({
            "product_name": hit.get("product_name", ""),
            "brands": hit.get("brands", ""),
            "barcode": hit.get("code", hit.get("_id", "")),
            "ingredients_text": hit.get("ingredients_text", ""),
            "quantity": hit.get("quantity", ""),
            "categories": hit.get("categories", ""),
        })
    return products
