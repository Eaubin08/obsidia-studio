import ast
import unittest

from patch_local_unknown_surface import WORDS, patch_source


class UnknownSurfacePatchTests(unittest.TestCase):
    def test_bounded_surface_extension(self):
        source = '_COMMON_SURFACE_WORDS = {"bonjour", "merci"}\n'
        result = patch_source(source)
        ast.parse(result)
        ns = {}
        exec(result, ns)
        words = ns["_COMMON_SURFACE_WORDS"]
        self.assertTrue(set(WORDS).issubset(words))
        self.assertIn("bonjour", words)
        self.assertNotIn("comprendre", words)
        self.assertNotIn("proposer", words)
        self.assertNotIn("agir", words)
        with self.assertRaisesRegex(RuntimeError, "ALREADY_PATCHED"):
            patch_source(result)

    def test_unknown_qualifier_shape_mismatch_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "SOURCE_MISMATCH"):
            patch_source("_COMMON_SURFACE_WORDS = get_words()\n")


if __name__ == "__main__":
    unittest.main()
