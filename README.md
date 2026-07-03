# Inventory Management API

This project implements a small Flask REST API for inventory management. It supports:

- Creating, reading, updating, and deleting inventory items
- Looking up product details from the OpenFoodFacts API by name or barcode
- A simple interactive CLI for managing items
- Unit tests covering the core API behavior

## Run the API

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
2. Start the Flask app:
   ```bash
   python flask_apis/app.py
   ```
3. Visit the API at http://127.0.0.1:5000/inventory

## Example requests

- List inventory: `GET /inventory`
- Create item: `POST /inventory`
- Update item: `PATCH /inventory/<id>`
- Delete item: `DELETE /inventory/<id>`
- Fetch product details: `GET /external-product?name=banana`

## Run tests

```bash
python -m unittest discover -s tests -v
```

## CLI usage

```bash
python flask_apis/app.py --cli
```
# Python-REST-API-with-Flask--Inventory-Management-System-
