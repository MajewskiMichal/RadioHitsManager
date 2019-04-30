from unittest import TestCase
from unittest.mock import patch

import json
from app import (
    app,
    validate_title,
    title_and_artist_id_provided,
    artist_id_is_int,
    urlify,
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
        result = self.app.get("/api/v1/hits/Existing-Title")
        print("get_hit_result_data", result.data)

        # assert the response data
        # we assume this record is in db
        self.assertEqual("artist" in json.loads(result.data.decode("utf-8")), True)
        self.assertEqual("hit" in json.loads(result.data.decode("utf-8")), True)
        self.assertEqual(result.status_code, 200)

    def test_get_hit_data_title_not_exists(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get("/api/v1/hits/Not-Existing-Title")
        self.assertEqual(result.data, b'{"error":"This title doesn\'t exist"}\n')
        self.assertEqual(result.status_code, 404)

    def test_create_hit_data_with_bad_json(self):
        # sends HTTP POST request to the application
        # on the specified path
        # artist_id missed in request
        sent = {"title": "artist_id missed"}
        result = self.app.post("/api/v1/hits", json=sent)
        self.assertEqual(
            result.data,
            b'{"error":"please provide json data with (title) and (artist_id)"}\n',
        )

    @patch("app.title_and_artist_id_provided", return_value=True)
    @patch("app.validate_title", return_value=True)
    @patch("app.artist_id_is_int", return_value=True)
    def test_create_hit_data(self, mock_1, mock_2, mock_3):

        result = self.app.post(
            "/api/v1/hits", json={"title": "Some Title", "artist_id": 88}
        )
        print("result_data", result.data)
        # convert to dict to check only title, because id is unique
        self.assertEqual(json.loads(result.data.decode("utf-8"))["title"], "Some Title")
        self.assertEqual(result.status_code, 201)

    def test_update_hit_with_no_data(self):
        result = self.app.put("/api/v1/hits/Existing-Title")
        self.assertEqual(result.data, b'{"error":"JSON has an error"}\n')
        self.assertEqual(result.status_code, 400)

    def test_update_hit_title_doenst_exist(self):
        result = self.app.put("/api/v1/hits/Not-Existing-Title")
        self.assertEqual(result.data, b'{"error":"JSON has an error"}\n')
        self.assertEqual(result.status_code, 400)

    def test_update_bad_title(self):
        result = self.app.put("/api/v1/hits/Existing-Title", json={"title": "&*%"})
        self.assertEqual(
            result.data,
            b'{"error":"title must be a non empty string'
            b' containing only letters ans spaces"}\n',
        )
        self.assertEqual(result.status_code, 400)

    def test_update_hit_bad_artist_id(self):
        result = self.app.put("/api/v1/hits/Existing-Title", json={"artist_id": ""})
        self.assertEqual(result.data, b'{"error":"artist_id must be an integer"}\n')
        self.assertEqual(result.status_code, 400)

    def test_update_hit_no_title_in_db(self):
        result = self.app.put("/api/v1/hits/Not-Existing-Title", json={"artist_id": 12})
        self.assertEqual(result.data, b'{"error":"This title doesn\'t exist"}\n')
        self.assertEqual(result.status_code, 404)

    @patch("app.validate_title", return_value=True)
    @patch("app.artist_id_is_int", return_value=True)
    def test_update_hit_success(self, mock_1, mcok_2):
        # create record to check update
        self.app.post(
            "/api/v1/hits",
            json={"title": "Title-to-update-which-exists", "artist_id": 88},
        )
        result = self.app.put(
            "/api/v1/hits/Title-to-update-which-exists", json={"title": "New Title"}
        )
        print("result_data_for_update", result.data)
        self.assertEqual(json.loads(result.data.decode("utf-8"))["title"], "New Title")
        self.assertEqual(result.status_code, 201)

    def test_delete_hit(self):
        # self.app.post("/api/v1/hits", json={'title': 'Title-to-delete',
        #                                    'artist_id': 77})
        result = self.app.delete("/api/v1/hits/Not-existing-title")
        print("del_result_data", result.data)
        self.assertEqual(result.data, b'{"error":"This title doesn\'t exist"}\n')
        self.assertEqual(result.status_code, 404)

    def title_and_artist_id_provided(self):
        request_json = {"title": "test_title", "artist_id": 1}
        result = title_and_artist_id_provided(request_json)
        self.assertEqual(result, True)

    def test_title_is_not_empty_string(self):
        request_json = {"title": "hello hello"}
        result = validate_title(request_json)
        self.assertEqual(result, True)

    def test_artist_id_is_int(self):
        request_json = {"artist_id": 1}
        result = artist_id_is_int(request_json)
        self.assertEqual(result, True)

    def test_urlify(self):
        result = urlify("test")
        self.assertEqual(result, "test")
