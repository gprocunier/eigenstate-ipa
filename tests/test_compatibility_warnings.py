import pathlib
import unittest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class CompatibilityWarningsTests(unittest.TestCase):
    def test_keytab_lookup_keeps_rotation_warning(self):
        text = (PROJECT_ROOT / "plugins" / "lookup" / "keytab.py").read_text()
        self.assertIn("retrieve_mode='generate' will", text)
        self.assertIn("immediately invalidated", text)

    def test_migration_docs_cover_lookup_overlap(self):
        path = PROJECT_ROOT / "docs" / "mutation-surface-migration.md"
        if not path.exists():
            self.skipTest("migration docs not added yet")
        text = path.read_text().lower()
        self.assertIn("existing lookups remain supported", text)
        self.assertIn("keytab_manage", text)
        self.assertIn("cert_request", text)


if __name__ == "__main__":
    unittest.main()
