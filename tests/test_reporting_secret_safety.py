import pathlib
import unittest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReportingSecretSafetyTests(unittest.TestCase):
    def test_reporting_public_content_is_neutral(self):
        paths = [
            PROJECT_ROOT / "docs" / "reporting-overview.md",
            PROJECT_ROOT / "docs" / "readiness-report-schema.md",
            PROJECT_ROOT / "docs" / "certificate-inventory-report.md",
            PROJECT_ROOT / "docs" / "keytab-rotation-candidate-report.md",
            PROJECT_ROOT / "docs" / "temporary-access-report.md",
            PROJECT_ROOT / "docs" / "policy-drift-report.md",
        ]
        forbidden = ["seller", "sales", "presales", "sales motion"]
        failures = []
        for path in paths:
            text = path.read_text().lower()
            for marker in forbidden:
                if marker in text:
                    failures.append(f"{path}: {marker}")
        self.assertEqual([], failures)

    def test_reporting_files_do_not_embed_secret_payloads(self):
        paths = [
            *(PROJECT_ROOT / "roles" / "idm_readiness_report").rglob("*"),
            *(PROJECT_ROOT / "roles" / "certificate_inventory_report").rglob("*"),
            *(PROJECT_ROOT / "roles" / "keytab_rotation_candidates").rglob("*"),
            *(PROJECT_ROOT / "roles" / "temporary_access_report").rglob("*"),
            *(PROJECT_ROOT / "roles" / "policy_drift_report").rglob("*"),
            PROJECT_ROOT / "playbooks" / "report-idm-readiness.yml",
            PROJECT_ROOT / "playbooks" / "report-certificate-inventory.yml",
            PROJECT_ROOT / "playbooks" / "report-keytab-rotation-candidates.yml",
            PROJECT_ROOT / "playbooks" / "report-temporary-access.yml",
            PROJECT_ROOT / "playbooks" / "report-policy-drift.yml",
            PROJECT_ROOT / "playbooks" / "reporting-static-validation.yml",
        ]
        forbidden = [
            "adminpass",
            "password:",
            "token:",
            "secret:",
            "private_key:",
            "-----begin private key-----",
            "keytab_b64:",
        ]
        failures = []
        for path in paths:
            if not path.is_file():
                continue
            text = path.read_text().lower()
            for marker in forbidden:
                if marker in text:
                    failures.append(f"{path}: {marker}")
        self.assertEqual([], failures)


if __name__ == "__main__":
    unittest.main()
