import json
import os
import unittest
from unittest.mock import patch
from studio_llamacpp import _endpoint, generate_llamacpp, EditorialEngineError


class FakeResponse:
    def __init__(self, data):
        self.data = data
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, limit):
        return json.dumps(self.data).encode("utf-8")


class LlamaCppStudioTests(unittest.TestCase):
    def test_local_only(self):
        self.assertEqual(_endpoint(), "http://127.0.0.1:8080/v1/chat/completions")
        for url in ("http://remote.example:8080", "https://127.0.0.1:8080",
                    "http://127.0.0.1:8080/proxy"):
            with patch.dict(os.environ, {"OBSIDIA_STUDIO_LLAMACPP_URL": url}):
                with self.assertRaises(EditorialEngineError):
                    _endpoint()

    def test_no_empty_subject(self):
        with self.assertRaises(EditorialEngineError):
            generate_llamacpp(" ")

    def test_real_model_content_and_provenance(self):
        response = {"model": "local", "choices": [{"message": {"content": "Post original."}}]}
        with patch("studio_llamacpp.urllib.request.urlopen", return_value=FakeResponse(response)) as call:
            result = generate_llamacpp("Gouvernance cognitive")
        self.assertEqual(result["text"], "Post original.")
        self.assertEqual(result["provenance"]["source"], "STUDIO_LOCAL_LLAMACPP")
        self.assertFalse(result["provenance"]["publication_permitted"])
        req = call.call_args.args[0]
        sent = json.loads(req.data.decode("utf-8"))
        self.assertIn("Gouvernance cognitive", sent["messages"][1]["content"])

    def test_refuse_empty_output(self):
        response = {"model": "local", "choices": [{"message": {"content": ""}}]}
        with patch("studio_llamacpp.urllib.request.urlopen", return_value=FakeResponse(response)):
            with self.assertRaises(EditorialEngineError):
                generate_llamacpp("Sujet")


if __name__ == "__main__":
    unittest.main()
