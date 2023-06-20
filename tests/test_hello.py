import unittest
from app import create_app

class HelloTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_hello_endpoint(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()