from flask import Flask, jsonify, request

import openfoodfacts_client as off
import store

app = Flask(__name__)
store.reset_store()


@app.route("/")
def index():
    return jsonify({
        "message": "FoodFast Inventory API",
        "endpoints": {
            "inventory": "/inventory",
            "external_barcode": "/external/product/<barcode>",
            "external_search": "/external/search?name=<query>",
            "import_from_api": "POST /inventory/from-api",
        },
    })


@app.route("/inventory", methods=["GET"])
def list_inventory():
    return jsonify(store.get_all())


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    item = store.get_by_id(item_id)
    if item is None:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return jsonify(item)


@app.route("/inventory", methods=["POST"])
def create_inventory_item():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    if not data.get("product_name"):
        return jsonify({"error": "product_name is required"}), 400
    item = store.add_item(data)
    return jsonify(item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_inventory_item(item_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400
    item = store.update_item(item_id, data)
    if item is None:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return jsonify(item)


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    if not store.delete_item(item_id):
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return "", 204


@app.route("/external/product/<barcode>", methods=["GET"])
def external_product(barcode):
    try:
        product = off.fetch_by_barcode(barcode)
    except Exception as exc:
        return jsonify({"error": f"External API request failed: {exc}"}), 502
    if product is None:
        return jsonify({"error": f"No product found for barcode {barcode}"}), 404
    return jsonify({"status": 1, "product": product})


@app.route("/external/search", methods=["GET"])
def external_search():
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"error": "Query parameter 'name' is required"}), 400
    try:
        products = off.search_by_name(name)
    except Exception as exc:
        return jsonify({"error": f"External API request failed: {exc}"}), 502
    return jsonify({"count": len(products), "products": products})


@app.route("/inventory/from-api", methods=["POST"])
def import_from_api():
    """Fetch product from OpenFoodFacts and add it to inventory."""
    data = request.get_json(silent=True) or {}
    barcode = data.get("barcode", "").strip()
    name = data.get("name", "").strip()
    price = data.get("price", 0)
    stock = data.get("stock", 0)

    if not barcode and not name:
        return jsonify({"error": "Provide 'barcode' or 'name'"}), 400

    try:
        if barcode:
            product = off.fetch_by_barcode(barcode)
            if product is None:
                return jsonify({"error": f"No product found for barcode {barcode}"}), 404
        else:
            results = off.search_by_name(name, page_size=1)
            if not results:
                return jsonify({"error": f"No products found for '{name}'"}), 404
            product = results[0]
    except Exception as exc:
        return jsonify({"error": f"External API request failed: {exc}"}), 502

    product["price"] = price
    product["stock"] = stock
    item = store.add_item(product)
    return jsonify(item), 201


if __name__ == "__main__":
    app.run(debug=True)
