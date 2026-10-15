"""Tests hors réseau du raccord Studio → Brody / routeur Obsidia."""
import os
import unittest
from unittest.mock import patch
import studio_ai


class LocalAIContractTests(unittest.TestCase):
    def test_loopback_only(self):
        self.assertEqual(studio_ai._endpoint({"base_url": "http://127.0.0.1:8000"}),
                         "http://127.0.0.1:8000/api/brody/chat")
        for url in ("https://example.org", "http://example.org",
                    "http://127.0.0.1:8000/v1", "http://user:pass@localhost:8000"):
            with self.subTest(url=url), self.assertRaises(studio_ai.InferenceError):
                studio_ai._endpoint({"base_url": url})

    def test_brody_first(self):
        with patch.object(studio_ai, "_call", return_value={"response": "<POST>Bonjour</POST>", "readonly": True}) as call:
            self.assertEqual(studio_ai.generate("Rédige"), "<POST>Bonjour</POST>")
        data = call.call_args.args[0]
        self.assertEqual(data["message"], "Rédige")
        self.assertTrue(data["allow_provider"])
        self.assertEqual(data["language"], "fr")

    def test_reject_act(self):
        with patch.object(studio_ai, "_call", return_value={"response": "texte", "emits_act": True}):
            with self.assertRaises(studio_ai.InferenceError):
                studio_ai.generate("Rédige")

    def test_default_status_is_configuration_only(self):
        with patch.dict(os.environ, {"OBSIDIA_STUDIO_BRODY_URL": "http://127.0.0.1:8000"}):
            st = studio_ai.status()
            self.assertFalse(st["ready"])
            self.assertEqual(st["provider"], "obsidia_brody")


if __name__ == "__main__":
    unittest.main()
