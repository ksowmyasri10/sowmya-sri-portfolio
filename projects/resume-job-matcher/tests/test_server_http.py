from __future__ import annotations

import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from server import RequestHandler


class LocalApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), RequestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def post(self, path, payload, headers=None):
        request_headers = {"Content-Type": "application/json"}
        request_headers.update(headers or {})
        request = Request(
            self.base + path,
            data=json.dumps(payload).encode(),
            headers=request_headers,
            method="POST",
        )
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, json.loads(response.read())
        except HTTPError as error:
            return error.code, json.loads(error.read())

    def test_health_endpoint_confirms_local_mode(self):
        with urlopen(self.base + "/api/health", timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertTrue(json.loads(response.read())["local_only"])

    def test_match_endpoint_returns_transparent_overlap(self):
        status, result = self.post(
            "/api/match",
            {"resume_text": "Python and scikit-learn", "job_text": "Python, SQL"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(result["score"], 50)
        self.assertEqual([skill["name"] for skill in result["missing"]], ["SQL"])

    def test_match_endpoint_rejects_empty_resume(self):
        status, result = self.post(
            "/api/match",
            {"resume_text": "  ", "job_text": "Python"},
        )
        self.assertEqual(status, 400)
        self.assertIn("Resume", result["error"])

    def test_rejects_cross_origin_upload_or_match_requests(self):
        status, result = self.post(
            "/api/match",
            {"resume_text": "Python", "job_text": "Python"},
            {"Origin": "https://example.com"},
        )
        self.assertEqual(status, 403)
        self.assertIn("Cross-origin", result["error"])

    def test_rejects_non_json_post(self):
        request = Request(
            self.base + "/api/match",
            data=b"resume_text=python",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with self.assertRaises(HTTPError) as raised:
            urlopen(request, timeout=3)
        self.assertEqual(raised.exception.code, 415)


if __name__ == "__main__":
    unittest.main()
