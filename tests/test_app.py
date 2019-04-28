from unittest import TestCase
from app import app, get_hits


class TestEskaApp(TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def test_get_hits_status_code(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/api/v1/hits')

        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

    def test_get_hit_data(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/api/v1/hits/Betonowy-Las')


        # assert the response data
        self.assertEqual(result.data,
                         b'{"id":1,"title":"Betonowy Las","title_url":"Betonowy-Las"}\n')





