import pathlib
import unittest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class CompatibilityWarningsTests(unittest.TestCase):
    def test_keytab_lookup_keeps_rotation_warning(self):
        text = (PROJECT_ROOT / "plugins" / "lookup" / "keytab.py").read_text()
        self.assertIn("retrieve_mode='generate' will", text)
        self.assertIn("immediately invalidated", text)

    def test_side_effecting_lookup_docs_cover_overlap(self):
        path = PROJECT_ROOT / "docs" / "how-to" / "migrate-side-effecting-lookups.md"
        text = path.read_text().lower()
        self.assertIn("lookups should be read-focused", text)
        self.assertIn("keytab_manage", text)
        self.assertIn("cert_request", text)


if __name__ == "__main__":
    unittest.main()
