from unittest import TestCase
from unittest.mock import patch

import json
from app import (
    app,
    title_is_not_empty_string,
    title_and_artist_id_provided,
    artist_id_is_int,
    urlify
)


class TestEskaApp(TestCase):
    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def test_get_hits_status_code(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get("/api/v1/hits")

        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

    def test_get_hit_data(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get("/api/v1/hits/Betonowy-Las")

        # assert the response data
        # we assume this record is in db
        self.assertEqual(
            result.data, b'{"id":2,"title":"Betonowy Las","title_url":"Betonowy-Las"}\n'
        )

    def test_create_hit_data_with_bad_json(self):
        # sends HTTP POST request to the application
        # on the specified path
        # artist_id missed in request
        sent = json.dumps({"title": "artist_id missed"})
        result = self.app.post("/api/v1/hits", data=sent)
        self.assertEqual(
            result.data,
            b'{"error":"please provide json data with (title) and (artist_id)"}\n',
        )

    @patch('app.title_and_artist_id_provided', return_value=True)
    @patch('app.title_is_not_empty_string', return_value=None)
    def test_create_hit_data(self, mock_1, mock_2):
        result = self.app.post("/api/v1/hits")
        self.assertEqual(result.data, b'{"error":"title must be a non empty string string"}\n')


    def test_update_hit_with_no_data(self):
        result = self.app.put("/api/v1/hits/Betonowy-Las")
        self.assertEqual(
            result.data, b'{"error":"You didn\'t send anything to update"}\n'
        )

    def title_and_artist_id_provided(self):
        request_json = {"title": "test_title", "artist_id": 1}
        result = title_and_artist_id_provided(request_json)
        self.assertEqual(result, True)

    def test_title_is_not_empty_string(self):
        request_json = {"title": "hello hello"}
        result = title_is_not_empty_string(request_json)
        self.assertEqual(result, True)

    def test_artist_id_is_int(self):
        request_json = {"artist_id": 1}
        result = artist_id_is_int(request_json)
        self.assertEqual(result, True)

    def test_urlify(self):
        result = urlify("test")
        self.assertEqual(result, "test")




