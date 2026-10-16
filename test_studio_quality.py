import unittest
from studio_quality import assess


class EditorialQualityTests(unittest.TestCase):
    def test_detects_repeated_post_and_heading(self):
        block = "Comprendre puis proposer et verifier avant toute autorisation. " * 3
        repeated = "### Pourquoi gouverner une IA\n" + block * 3
        issues = assess(repeated)["issues"]
        self.assertTrue(any("Repetition" in issue for issue in issues))
        self.assertTrue(any("Markdown" in issue for issue in issues))

    def test_rejects_wrong_authority(self):
        wrong = "L'IA doit comprendre, proposer et autoriser les actions."
        self.assertFalse(assess(wrong)["ok"])
        self.assertTrue(any("KX108" in x for x in assess(wrong)["issues"]))

    def test_flags_kx108_consultative_misrepresentation(self):
        text = "KX108 reste consultatif et tranche." + " Fin." * 100
        self.assertTrue(any("KX108" in i for i in assess(text)["issues"]))

    def test_rejects_false_execution_ban(self):
        bad = "L'IA ne doit jamais exécuter."
        self.assertFalse(assess(bad)["ok"])

    def test_rejects_meta_linkedin_intro(self):
        self.assertFalse(assess("Sur LinkedIn je partage cette idée.")["ok"])

    def test_accepts_coherent_long_form(self):
        body = (
            "Une proposition ne constitue pas une autorisation.\n\n"
            "Brody participe au travail de comprehension mais son analyse reste consultative. "
            "Une incertitude doit etre conservee plutot que masquee dans une recommandation.\n\n"
            "KX108 tranche dans le cadre des regles applicables et peut suspendre la demande. "
            "Ce controle precede toute tentative d application pratique.\n\n"
            "Un executant distinct intervient seulement quand le perimetre a ete autorise. "
            "Les limites operationnelles sont alors explicites et verifiables.\n\n"
            "Une preuve ou un receipt documente ensuite ce qui s est produit. "
            "Cela permet de revoir la chaine de decisions sans confondre chaque responsabilite."
        )
        self.assertTrue(assess(body)["ok"])


if __name__ == "__main__":
    unittest.main()
