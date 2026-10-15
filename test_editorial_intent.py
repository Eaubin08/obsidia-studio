import unittest

from editorial_intent import explanatory_editorial_request


class EditorialIntentTests(unittest.TestCase):
    def test_request_contains_readonly_explanatory_question(self):
        text = explanatory_editorial_request(
            "Pourquoi une IA doit comprendre avant d'agir ?", "LinkedIn"
        )
        self.assertEqual(text, "Pourquoi une IA doit comprendre avant d'agir ?")
        self.assertNotIn("brouillon consultatif", text)

    def test_non_question_topic_is_made_explicit(self):
        text = explanatory_editorial_request("La gouvernance cognitive", "LinkedIn")
        self.assertEqual(text, "La gouvernance cognitive")

    def test_no_subject(self):
        with self.assertRaises(ValueError):
            explanatory_editorial_request("  ")



if __name__ == "__main__":
    unittest.main()
