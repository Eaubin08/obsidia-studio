import unittest

from editorial_intent import explanatory_editorial_request
from patch_local_os_trad import OLD, NEW, patch_source


class EditorialIntentTests(unittest.TestCase):
    def test_request_contains_readonly_explanatory_question(self):
        text = explanatory_editorial_request(
            "Pourquoi une IA doit comprendre avant d'agir ?", "LinkedIn"
        )
        self.assertIn("Comment expliquer", text)
        self.assertIn("avant d'agir", text)
        self.assertIn("brouillon consultatif", text)

    def test_no_subject(self):
        with self.assertRaises(ValueError):
            explanatory_editorial_request("  ")

    def test_patch_is_strict_and_compiles(self):
        sample = "import re\n\ndef check(low, flags, _action_negation=False):\n" + OLD + "    return flags\n"
        patched = patch_source(sample)
        self.assertEqual(patched.count(NEW), 1)
        space = {}
        exec(compile(patched, "<test-patch>", "exec"), space)
        def flagged(x):
            return "action_request" in space["check"](x.lower(), [])
        self.assertFalse(flagged("Pourquoi une IA doit vérifier avant d'agir ?"))
        self.assertFalse(flagged("Comment comprendre sans agir ?"))
        self.assertTrue(flagged("Agir maintenant."))
        self.assertTrue(flagged("Exécute cette action maintenant."))
        self.assertTrue(flagged("Lance le paiement."))
        self.assertTrue(flagged("Write memory."))
        self.assertFalse(flagged("Une explication sur la gouvernance cognitive."))

    def test_incompatible_patch_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "SOURCE_MISMATCH"):
            patch_source("x = 1\n")


if __name__ == "__main__":
    unittest.main()
