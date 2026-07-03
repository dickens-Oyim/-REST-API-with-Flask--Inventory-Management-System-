import argparse
import json
import urllib.error
import urllib.parse
import urllib.request

from flask import Flask, jsonify, request

app = Flask(__name__)

inventory = []


def _next_id():
    return max((item["id"] for item in inventory), default=0) + 1


def fetch_product_details(name=None, barcode=None):
    """Fetch product data from OpenFoodFacts using either a barcode or a name."""
    if barcode:
        url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    elif name:
        query = urllib.parse.quote(name)
        url = (
            "https://world.openfoodfacts.org/cgi/search.pl?"
            f"search_terms={query}&search_simple=1&json=1"
            "&fields=product_name,code,brands,categories,ingredients_text"
        )
    else:
        return None

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.load(response)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return {
            "name": name or barcode,
            "barcode": barcode,
            "source": "offline-fallback",
            "message": "Product lookup could not reach the external API.",
        }

    if barcode:
        product = data.get("product", {})
        return {
            "name": product.get("product_name") or product.get("product_name_en") or name,
            "barcode": product.get("code") or barcode,
            "brands": product.get("brands"),
            "categories": product.get("categories"),
            "ingredients": product.get("ingredients_text"),
        }

    products = data.get("products") or []
    if not products:
        return None

    first_product = products[0]
    return {
        "name": first_product.get("product_name") or name,
        "barcode": first_product.get("code"),
        "brands": first_product.get("brands"),
        "categories": first_product.get("categories"),
        "ingredients": first_product.get("ingredients_text"),
    }


@app.get("/inventory")
def list_inventory():
    return jsonify(inventory)


@app.get("/inventory/<int:item_id>")
def get_item(item_id):
    item = next((entry for entry in inventory if entry["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)


@app.post("/inventory")
def create_item():
    data = request.get_json(silent=True) or {}
    required_fields = ["name", "price", "quantity"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    item = {
        "id": _next_id(),
        "name": data["name"],
        "price": float(data["price"]),
        "quantity": int(data["quantity"]),
        "category": data.get("category"),
        "barcode": data.get("barcode"),
    }
    inventory.append(item)
    return jsonify(item), 201


@app.patch("/inventory/<int:item_id>")
def update_item(item_id):
    item = next((entry for entry in inventory if entry["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True) or {}
    for field in ["name", "price", "quantity", "category", "barcode"]:
        if field in data:
            if field == "price":
                item[field] = float(data[field])
            elif field == "quantity":
                item[field] = int(data[field])
            else:
                item[field] = data[field]

    return jsonify(item)


@app.delete("/inventory/<int:item_id>")
def delete_item(item_id):
    item = next((entry for entry in inventory if entry["id"] == item_id), None)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return jsonify({"message": "Item deleted successfully"})


@app.get("/external-product")
def external_product():
    name = request.args.get("name")
    barcode = request.args.get("barcode")
    if not name and not barcode:
        return jsonify({"error": "Provide either a barcode or a name"}), 400

    product = fetch_product_details(name=name, barcode=barcode)
    if product is None:
        return jsonify({"error": "No product found"}), 404
    return jsonify(product)


def run_cli():
    print("Inventory Management CLI")
    print("Commands: list, add, update, delete, exit")
    while True:
        command = input("Enter command: ").strip().lower()
        if command == "exit":
            print("Goodbye!")
            break
        if command == "list":
            print(json.dumps(inventory, indent=2))
        elif command == "add":
            name = input("Name: ").strip()
            price = float(input("Price: ").strip())
            quantity = int(input("Quantity: ").strip())
            create_item_data = {
                "name": name,
                "price": price,
                "quantity": quantity,
            }
            inventory.append(
                {
                    "id": _next_id(),
                    "name": create_item_data["name"],
                    "price": create_item_data["price"],
                    "quantity": create_item_data["quantity"],
                }
            )
            print("Item added")
        elif command == "update":
            item_id = int(input("Item id: ").strip())
            item = next((entry for entry in inventory if entry["id"] == item_id), None)
            if item is None:
                print("Item not found")
                continue
            new_quantity = input("New quantity (leave blank to keep): ").strip()
            if new_quantity:
                item["quantity"] = int(new_quantity)
            new_price = input("New price (leave blank to keep): ").strip()
            if new_price:
                item["price"] = float(new_price)
            print("Item updated")
        elif command == "delete":
            item_id = int(input("Item id: ").strip())
            item = next((entry for entry in inventory if entry["id"] == item_id), None)
            if item is None:
                print("Item not found")
                continue
            inventory.remove(item)
            print("Item deleted")
        else:
            print("Unknown command")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inventory management API")
    parser.add_argument("--cli", action="store_true", help="Run the interactive CLI")
    args = parser.parse_args()
    if args.cli:
        run_cli()
    else:
        app.run(debug=True)
