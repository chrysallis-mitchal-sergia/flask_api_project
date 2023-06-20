import unittest
from app import create_app

class LookupTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_lookup_endpoint(self):
        response = self.client.get('/lookup')
        self.assertEqual(response.status_code, 400)

        response = self.client.get('/lookup?ipAddress=1.1.1.1')


if __name__ == '__main__':
    unittest.main()