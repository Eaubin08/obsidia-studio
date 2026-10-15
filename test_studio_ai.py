"""Tests autonomes de l'adaptateur IA, sans serveur Qwen ni appel réseau."""
import os
import unittest
from unittest.mock import patch
import studio_ai


class LocalAIContractTests(unittest.TestCase):
    def test_loopback_only(self):
        good = {"base_url": "http://127.0.0.1:8080/v1"}
        self.assertEqual(studio_ai._endpoint(good), "http://127.0.0.1:8080/v1/chat/completions")
        for url in ("https://example.org/v1", "http://example.org/v1",
                    "http://127.0.0.1:8080/other", "http://user:pass@localhost:8080/v1"):
            with self.subTest(url=url), self.assertRaises(studio_ai.InferenceError):
                studio_ai._endpoint({"base_url": url})

    def test_does_not_call_nonlocal_provider(self):
        with patch.dict(os.environ, {"OBSIDIA_STUDIO_AI_PROVIDER": "claude"}, clear=False):
            with self.assertRaises(studio_ai.InferenceError):
                studio_ai.generate("test")

    def test_default_status_is_configuration_only(self):
        with patch.dict(os.environ, {"OBSIDIA_STUDIO_AI_URL": "http://127.0.0.1:8080/v1"}, clear=False):
            self.assertFalse(studio_ai.status()["ready"])


if __name__ == "__main__":
    unittest.main()
