"""Offline regression tests for cosmetic Studio draft cleanup."""
import unittest

from editorial_cleanup import clean_editorial_draft


class EditorialCleanupTests(unittest.TestCase):
    def test_linkedin_wrapper_literal_newlines_and_commentary(self):
        raw = (
            r'\nVoici une courte publication LinkedIn en français sur la date indiquée : '
            '"Le 15 octobre 2026, en local, la mémoire cognitive est branchée en lecture seule. '
            'Elle observe les événements sans intervenir directement."  '
            r'Cette publication respecte les directives de ne rien inventer ni publier.\n'
        )
        actual = clean_editorial_draft(raw)
        self.assertEqual(
            actual,
            "Le 15 octobre 2026, en local, la mémoire cognitive est branchée en lecture seule. "
            "Elle observe les événements sans intervenir directement.",
        )

    def test_authored_content_is_not_rewritten(self):
        draft = "Nous documentons la méthode.\\n\\nLe prochain audit est prévu."
        self.assertEqual(
            clean_editorial_draft(draft),
            "Nous documentons la méthode.\n\nLe prochain audit est prévu.",
        )

    def test_quoted_user_content_is_preserved_without_wrapper(self):
        text = '"Comprendre" ne veut pas dire "décider".'
        self.assertEqual(clean_editorial_draft(text), text)

    def test_echoed_instruction_not_part_of_post(self):
        raw = ('"Le club a intégré des dossiers et des tâches. #Organisation"  '
               "N'invente aucun fait ou chiffre.")
        self.assertEqual(
            clean_editorial_draft(raw),
            "Le club a intégré des dossiers et des tâches. #Organisation",
        )

    def test_do_not_strip_normal_statement_about_facts(self):
        text = "Nous n'inventons aucun fait ou chiffre dans nos rapports."
        self.assertEqual(clean_editorial_draft(text), text)

    def test_no_fabrication(self):
        self.assertEqual(clean_editorial_draft("   "), "")


if __name__ == "__main__":
    unittest.main()
