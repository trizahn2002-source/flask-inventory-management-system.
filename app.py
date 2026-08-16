from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

##Mock database - each item has a unique id
inventory = [
    {"id": 1, "name": "Organic Almond Milk", "brand": "Silk", "price": 3.99, "stock": 20},
    {"id": 2, "name": "Peanut Butter", "brand": "Jif", "price": 4.99, "stock": 15},
]

next_id = 3


@app.route('/inventory', methods=['GET'])
def get_all_items():
    return jsonify(inventory), 200


@app.route('/inventory/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((i for i in inventory if i["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route('/inventory', methods=['POST'])
def add_item():
    global next_id
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Missing required field: name"}), 400

    new_item = {
        "id": next_id,
        "name": data.get("name"),
        "brand": data.get("brand", ""),
        "price": data.get("price", 0),
        "stock": data.get("stock", 0),
    }
    inventory.append(new_item)
    next_id += 1
    return jsonify(new_item), 201


@app.route('/inventory/<int:item_id>', methods=['PATCH'])
def update_item(item_id):
    item = next((i for i in inventory if i["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    for key in ["name", "brand", "price", "stock"]:
        if key in data:
            item[key] = data[key]

    return jsonify(item), 200


@app.route('/inventory/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global inventory
    item = next((i for i in inventory if i["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory = [i for i in inventory if i["id"] != item_id]
    return jsonify({"message": f"Item {item_id} deleted"}), 200

@app.route('/inventory/fetch', methods=['POST'])
def fetch_from_openfoodfacts():
    global next_id
    data = request.get_json(silent=True)
    query = data.get("query") if data else None

    if not query:
        return jsonify({"error": "Missing 'query' (product name or barcode)"}), 400

    url = "https://world.openfoodfacts.org/api/v2/search"
    params = {
          "search_terms": query,
          "page_size": 1,
          "fields": "product_name,brands",
 }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("products", [])
    except Exception as e:
        return jsonify({"error": f"Failed to reach OpenFoodFacts API: {str(e)}"}), 502

    if not results:
        return jsonify({"error": f"No product found for '{query}'"}), 404

    product = results[0]
    new_item = {
        "id": next_id,
        "name": product.get("product_name") or query,
        "brand": product.get("brands", ""),
        "price": 0,
        "stock": 0,
    }
    inventory.append(new_item)
    next_id += 1
    return jsonify(new_item), 201


if __name__ == '__main__':
    app.run(debug=True, port=5001)