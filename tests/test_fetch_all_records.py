import unittest
import json
from app import create_app

class AllRecordsTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_get_all_data_endpoint(self):
        response = self.client.get('/all-records')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()