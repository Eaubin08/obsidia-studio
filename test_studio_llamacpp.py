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
        good_post = (
            "Une proposition ne suffit pas pour autoriser une action.\n\n"
            "Brody contribue a l analyse du contexte, sans pouvoir decider. "
            "Une suggestion peut etre utile et pourtant rester incomplete.\n\n"
            "KX108 examine les conditions et rend une decision selon les regles. "
            "Le passage de la proposition a l autorisation exige donc un controle explicite.\n\n"
            "Un composant distinct peut ensuite executer dans les limites accordees. "
            "Si le cadre ne permet pas l action, cette derniere reste suspendue.\n\n"
            "Les receipts et preuves rendent chaque etape retraçable pour une revue humaine."
        )
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
        good = (
            "Proposer une action ne signifie pas avoir le droit de la realiser.\n\n"
            "Brody fournit des hypotheses consultatives sur la situation. "
            "Il peut signaler une incertitude sans transformer son avis en ordre.\n\n"
            "KX108 tranche selon des contraintes connues et refuse si elles manquent. "
            "L autorisation est differente du texte produit par le modele.\n\n"
            "Seul un executant distinct, soumis au perimetre valide, peut agir. "
            "Cette separation diminue le risque de confusion des responsabilites.\n\n"
            "Une trace de preuve accompagne le resultat pour permettre son audit."
        )
        bad = {"model": "local", "choices": [{"message": {"content": "Trop bref."}}]}
        corrected = {"model": "local", "choices": [{"message": {"content": good}}]}
        with patch("studio_llamacpp.urllib.request.urlopen",
                   side_effect=[FakeResponse(bad), FakeResponse(corrected)]) as call:
            result = generate_llamacpp("Gouvernance des actions")
        self.assertEqual(result["text"], good.strip())
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
