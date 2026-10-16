import unittest
from studio_quality import assess


class EditorialQualityTests(unittest.TestCase):
    def test_rejects_wrong_authority(self):
        wrong = "L'IA doit comprendre, proposer et autoriser les actions."
        self.assertFalse(assess(wrong)["ok"])
        self.assertTrue(any("KX108" in x for x in assess(wrong)["issues"]))

    def test_rejects_false_execution_ban(self):
        bad = "L'IA ne doit jamais exécuter."
        self.assertFalse(assess(bad)["ok"])

    def test_rejects_meta_linkedin_intro(self):
        self.assertFalse(assess("Sur LinkedIn je partage cette idée.")["ok"])

    def test_accepts_coherent_long_form(self):
        body = ("Une proposition n'est pas une autorisation.\n\n"
                + "Brody peut comprendre et proposer, sans autorité d'action. " * 5
                + "\n\nKX108 décide de l'autorisation selon les règles. "
                + "L'exécution, si elle est autorisée, reste contrôlée. " * 5
                + "\n\nLes preuves et receipts rendent la décision traçable.")
        self.assertTrue(assess(body)["ok"])


if __name__ == "__main__":
    unittest.main()
