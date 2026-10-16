import unittest
from studio_quality import assess

class GeneratedOutputSafetyTests(unittest.TestCase):
    def test_request_label_is_not_a_post(self):
        self.assertFalse(assess("RESEAU : LinkedIn\nUn texte. " + "Suite. " * 100)["ok"])

    def test_hybrid_fragment_is_detected(self):
        self.assertFalse(assess("Une question par herself. " + "Texte. " * 100)["ok"])

if __name__ == "__main__":
    unittest.main()
