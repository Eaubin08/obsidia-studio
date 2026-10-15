import unittest

from editorial_intent import explanatory_editorial_request
from patch_local_os_trad import patch_source


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
        sample = (
            "import re\n"
            "def _risk_flags(text):\n"
            "    low = text.lower()\n"
            "    flags = []\n"
            "    if 'agir' in low:\n"
            "        flags.append('action_request')\n"
            "    return flags\n"
        )
        patched = patch_source(sample)
        self.assertIn("_studio_explanatory_action_filter(text, flags)", patched)
        namespace = {}
        exec(compile(patched, "<test-patch>", "exec"), namespace)
        def flagged(text):
            return "action_request" in namespace["_risk_flags"](text)
        self.assertFalse(flagged("Pourquoi une IA doit vérifier avant d'agir ?"))
        self.assertTrue(flagged("Agir maintenant."))
        self.assertTrue(flagged("Pourquoi une IA agit ? Publie maintenant et agir."))
        self.assertTrue(flagged("Pourquoi agir ? Exécute le virement."))
        self.assertFalse(flagged("Comment expliquer l'importance d'agir ?"))
        with self.assertRaisesRegex(RuntimeError, "ALREADY_PATCHED"):
            patch_source(patched)

    def test_incompatible_patch_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "SOURCE_MISMATCH"):
            patch_source("x = 1\n")


if __name__ == "__main__":
    unittest.main()
