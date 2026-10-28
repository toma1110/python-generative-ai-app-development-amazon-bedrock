"""Implementation tests for the local Section 04 teaching API."""

import json
from http.server import HTTPServer
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from main import NOTES, NotesHandler


class NotesApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), NotesHandler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=2)
        cls.server.server_close()

    def setUp(self):
        NOTES.clear()
        NOTES["123"] = {"id": "123", "title": "調査メモ", "body": "API応答を確認する"}
        import main

        main.NEXT_ID = 124

    def read_response(self, request):
        try:
            response = urlopen(request, timeout=2)
        except HTTPError as error:
            response = error
        with response:
            return response.code, response.headers, response.read()

    def test_get_returns_json_representation_and_compact_query(self):
        code, headers, body = self.read_response(Request(self.base_url + "/notes/123"))
        self.assertEqual(code, 200)
        self.assertEqual(headers["Content-Type"], "application/json; charset=utf-8")
        self.assertEqual(json.loads(body), NOTES["123"])

        code, _, body = self.read_response(Request(self.base_url + "/notes/123?view=compact"))
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body), {"id": "123", "title": "調査メモ"})

    def test_missing_note_returns_404_with_error_details(self):
        code, _, body = self.read_response(Request(self.base_url + "/notes/999"))
        self.assertEqual(code, 404)
        self.assertEqual(json.loads(body), {"error": "note_not_found", "id": "999"})

    def test_post_creates_note_that_can_be_read(self):
        request = Request(
            self.base_url + "/notes",
            data='{"title":"追加メモ","body":"POSTで作成"}'.encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        code, _, body = self.read_response(request)
        created = {"id": "124", "title": "追加メモ", "body": "POSTで作成"}
        self.assertEqual(code, 201)
        self.assertEqual(json.loads(body), created)

        code, _, body = self.read_response(Request(self.base_url + "/notes/124"))
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body), created)

    def test_invalid_json_and_missing_or_blank_title_return_400(self):
        bodies = [b"{", '{"body":"本文だけ"}'.encode("utf-8"), b'{"title":"   "}']
        for body in bodies:
            with self.subTest(body=body):
                request = Request(
                    self.base_url + "/notes",
                    data=body,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                code, _, response_body = self.read_response(request)
                self.assertEqual(code, 400)
                self.assertIn("error", json.loads(response_body))

    def test_unknown_route_returns_404_and_unsupported_method_returns_405(self):
        code, _, body = self.read_response(Request(self.base_url + "/unknown"))
        self.assertEqual(code, 404)
        self.assertEqual(json.loads(body), {"error": "route_not_found"})

        request = Request(self.base_url + "/notes/123", method="PUT")
        code, headers, body = self.read_response(request)
        self.assertEqual(code, 405)
        self.assertEqual(headers["Allow"], "GET, POST")
        self.assertEqual(json.loads(body), {"error": "method_not_allowed"})


if __name__ == "__main__":
    unittest.main()
