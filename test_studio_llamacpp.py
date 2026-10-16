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
        good_post = ("Une proposition ne suffit pas pour agir.\n\n" + "Brody analyse et propose. " * 8 + "\n\n" + "KX108 autorise selon des regles explicites. " * 6 + "\n\n" + "L executant agit uniquement dans le perimetre autorise. " * 3 + "\n\nLes receipts permettent une verification.")
        response = {"model": "local", "choices": [{"message": {"content": good_post}}]}
        with patch("studio_llamacpp.urllib.request.urlopen", return_value=FakeResponse(response)) as call:
            result = generate_llamacpp("Gouvernance cognitive")
        self.assertEqual(result["text"], good_post)
        self.assertEqual(result["provenance"]["source"], "STUDIO_LOCAL_LLAMACPP")
        self.assertFalse(result["provenance"]["publication_permitted"])
        req = call.call_args.args[0]
        sent = json.loads(req.data.decode("utf-8"))
        self.assertIn("Gouvernance cognitive", sent["messages"][1]["content"])

    def test_single_revision_rescues_short_draft(self):
        good = ("Une proposition n est pas une autorisation.\n\n"
                + "Brody formule des propositions, sans autoriser. " * 7
                + "\n\nKX108 decide du droit d agir dans un cadre formel. " * 6
                + "\n\nUn executant controle applique seulement l autorisation accordee. " * 3)
        bad = {"model": "local", "choices": [{"message": {"content": "Trop bref."}}]}
        corrected = {"model": "local", "choices": [{"message": {"content": good}}]}
        with patch("studio_llamacpp.urllib.request.urlopen",
                   side_effect=[FakeResponse(bad), FakeResponse(corrected)]) as call:
            result = generate_llamacpp("Gouvernance des actions")
        self.assertEqual(result["text"], good)
        self.assertEqual(call.call_count, 2)

    def test_refuses_after_one_unsuccessful_revision(self):
        bad = {"model": "local", "choices": [{"message": {"content": "Trop bref."}}]}
        with patch("studio_llamacpp.urllib.request.urlopen",
                   side_effect=[FakeResponse(bad), FakeResponse(bad)]) as call:
            with self.assertRaises(EditorialEngineError):
                generate_llamacpp("Gouvernance des actions")
        self.assertEqual(call.call_count, 2)

    def test_refuse_empty_output(self):
        response = {"model": "local", "choices": [{"message": {"content": ""}}]}
        with patch("studio_llamacpp.urllib.request.urlopen", return_value=FakeResponse(response)):
            with self.assertRaises(EditorialEngineError):
                generate_llamacpp("Sujet")


if __name__ == "__main__":
    unittest.main()
