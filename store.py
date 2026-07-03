"""In-memory inventory storage simulating a product database."""

_inventory: list[dict] = []
_next_id = 1

SEED_DATA = [
    {
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "barcode": "025293001301",
        "ingredients_text": "Filtered water, almonds, cane sugar, sea salt, locust bean gum, sunflower lecithin, gellan gum.",
        "quantity": "1.89 L",
        "categories": "Plant-based beverages, Plant-based milk alternatives",
        "price": 4.99,
        "stock": 42,
    },
    {
        "product_name": "Whole Grain Oats",
        "brands": "Quaker",
        "barcode": "030000413004",
        "ingredients_text": "100% whole grain rolled oats.",
        "quantity": "510 g",
        "categories": "Breakfast cereals, Cereals and potatoes",
        "price": 3.49,
        "stock": 85,
    },
    {
        "product_name": "Dark Chocolate Bar",
        "brands": "Lindt",
        "barcode": "037466007738",
        "ingredients_text": "Sugar, cocoa mass, cocoa butter, vanilla.",
        "quantity": "100 g",
        "categories": "Snacks, Sweet snacks, Chocolate candies",
        "price": 2.99,
        "stock": 30,
    },
]


def reset_store(seed: bool = True) -> None:
    """Reset inventory; used by tests and app startup."""
    global _inventory, _next_id
    _inventory = []
    _next_id = 1
    if seed:
        for item in SEED_DATA:
            add_item(item)


def _find_index(item_id: int) -> int | None:
    for i, item in enumerate(_inventory):
        if item["id"] == item_id:
            return i
    return None


def get_all() -> list[dict]:
    return list(_inventory)


def get_by_id(item_id: int) -> dict | None:
    for item in _inventory:
        if item["id"] == item_id:
            return dict(item)
    return None


def add_item(data: dict) -> dict:
    global _next_id
    item = {
        "id": _next_id,
        "product_name": data.get("product_name", ""),
        "brands": data.get("brands", ""),
        "barcode": data.get("barcode", ""),
        "ingredients_text": data.get("ingredients_text", ""),
        "quantity": data.get("quantity", ""),
        "categories": data.get("categories", ""),
        "price": float(data.get("price", 0)),
        "stock": int(data.get("stock", 0)),
    }
    _next_id += 1
    _inventory.append(item)
    return dict(item)


def update_item(item_id: int, data: dict) -> dict | None:
    index = _find_index(item_id)
    if index is None:
        return None
    item = _inventory[index]
    allowed = {"product_name", "brands", "barcode", "ingredients_text",
               "quantity", "categories", "price", "stock"}
    for key, value in data.items():
        if key in allowed:
            if key in ("price",):
                item[key] = float(value)
            elif key in ("stock",):
                item[key] = int(value)
            else:
                item[key] = value
    return dict(item)


def delete_item(item_id: int) -> bool:
    index = _find_index(item_id)
    if index is None:
        return False
    _inventory.pop(index)
    return True
