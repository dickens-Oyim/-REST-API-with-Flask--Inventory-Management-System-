import unittest
from unittest.mock import patch

from flask_apis.app import app, inventory


class InventoryApiTests(unittest.TestCase):
    def setUp(self):
        inventory.clear()
        self.client = app.test_client()

    def test_get_inventory_returns_empty_list(self):
        response = self.client.get('/inventory')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_create_and_read_inventory_item(self):
        payload = {'name': 'Keyboard', 'price': 25.5, 'quantity': 10}
        create_response = self.client.post('/inventory', json=payload)
        self.assertEqual(create_response.status_code, 201)

        created_item = create_response.get_json()
        self.assertEqual(created_item['name'], 'Keyboard')
        self.assertEqual(created_item['price'], 25.5)
        self.assertEqual(created_item['quantity'], 10)

        list_response = self.client.get('/inventory')
        self.assertEqual(len(list_response.get_json()), 1)

    def test_update_inventory_item(self):
        self.client.post('/inventory', json={'name': 'Mouse', 'price': 15.0, 'quantity': 4})

        update_response = self.client.patch('/inventory/1', json={'quantity': 7, 'price': 18.0})
        self.assertEqual(update_response.status_code, 200)

        updated_item = update_response.get_json()
        self.assertEqual(updated_item['quantity'], 7)
        self.assertEqual(updated_item['price'], 18.0)

    def test_delete_inventory_item(self):
        self.client.post('/inventory', json={'name': 'Monitor', 'price': 150.0, 'quantity': 2})

        delete_response = self.client.delete('/inventory/1')
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.get_json()['message'], 'Item deleted successfully')

        get_response = self.client.get('/inventory')
        self.assertEqual(get_response.get_json(), [])

    @patch('flask_apis.app.fetch_product_details')
    def test_external_product_route_uses_helper(self, mock_fetch):
        mock_fetch.return_value = {'name': 'Sample Product', 'barcode': '1234567890123'}

        response = self.client.get('/external-product?name=Sample%20Product')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['name'], 'Sample Product')


if __name__ == '__main__':
    unittest.main()
