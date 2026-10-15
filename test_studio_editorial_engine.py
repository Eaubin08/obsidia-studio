"""Tests offline du moteur editorial possede par Studio."""
import json
import os
import unittest
from unittest.mock import patch
from studio_editorial_engine import generate_editorial, EditorialEngineError, _endpoint


class _Response:
    def __init__(self, data):
        self.data = data
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, limit):
        return json.dumps(self.data).encode("utf-8")


class StudioEditorialEngineTests(unittest.TestCase):
    def test_loopback_only(self):
        with patch.dict(os.environ, {"OBSIDIA_STUDIO_OLLAMA_URL": "http://127.0.0.1:11434"}):
            self.assertEqual(_endpoint(), "http://127.0.0.1:11434/api/chat")
        for url in ("http://example.com", "https://127.0.0.1:11434",
                    "http://localhost:11434/v1", "http://x:y@localhost:11434"):
            with self.subTest(url=url), patch.dict(os.environ, {"OBSIDIA_STUDIO_OLLAMA_URL": url}):
                with self.assertRaises(EditorialEngineError):
                    _endpoint()

    def test_requires_explicit_model(self):
        with patch.dict(os.environ, {"OBSIDIA_STUDIO_OLLAMA_MODEL": ""}):
            with self.assertRaises(EditorialEngineError):
                generate_editorial("Sujet")

    def test_produces_real_unapproved_model_draft(self):
        env = {"OBSIDIA_STUDIO_OLLAMA_MODEL": "test-model",
               "OBSIDIA_STUDIO_OLLAMA_URL": "http://127.0.0.1:11434"}
        response = {"model": "test-model", "message": {"content": "Un vrai brouillon original."}}
        with patch.dict(os.environ, env):
            with patch("studio_editorial_engine.urllib.request.urlopen",
                       return_value=_Response(response)) as mocked:
                result = generate_editorial("Sujet de test")
        self.assertEqual(result["text"], "Un vrai brouillon original.")
        self.assertEqual(result["provenance"]["source"], "STUDIO_LOCAL_OLLAMA")
        self.assertFalse(result["provenance"]["publication_permitted"])
        self.assertFalse(result["provenance"]["brody_post_model_synthesis_proven"])
        request = mocked.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["model"], "test-model")
        self.assertIn("Sujet de test", payload["messages"][1]["content"])

    def test_rejects_empty_or_unidentified_output(self):
        with patch.dict(os.environ, {"OBSIDIA_STUDIO_OLLAMA_MODEL": "test-model"}):
            for response in (
                {"model": "wrong-model", "message": {"content": "Texte"}},
                {"model": "test-model", "message": {"content": " "}},
                {"model": "test-model", "message": {"content": "Synthese readonly depuis source-pack"}},
            ):
                with self.subTest(response=response):
                    with patch("studio_editorial_engine.urllib.request.urlopen",
                               return_value=_Response(response)):
                        with self.assertRaises(EditorialEngineError):
                            generate_editorial("Sujet")


if __name__ == "__main__":
    unittest.main()
