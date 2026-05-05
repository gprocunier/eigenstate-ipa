import pathlib
import unittest

import yaml


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


SECRET_MARKERS = [
    "eigenstate.ipa.vault",
    "eigenstate.ipa.keytab",
    "vault_password",
    "private_key",
    "enroll_pass",
    "otp",
    "keytab_b64",
    "sealed_bundle",
    "sealed_artifact",
    "eigenstate_sealed_record",
]


def _task_documents(path):
    data = yaml.safe_load(path.read_text())
    if not data:
        return []
    if isinstance(data, list):
        return data
    return [data]


class Phase2SecretSafetyTests(unittest.TestCase):
    def test_secret_bearing_role_tasks_use_no_log(self):
        task_paths = []
        for role in (
            "sealed_artifact_delivery",
            "temporary_access_window",
            "cert_expiry_report",
        ):
            task_paths.extend((PROJECT_ROOT / "roles" / role / "tasks").glob("*.yml"))

        failures = []
        for path in sorted(task_paths):
            for task in _task_documents(path):
                if not isinstance(task, dict):
                    continue
                task_text = yaml.safe_dump(task, sort_keys=True).lower()
                if not any(marker.lower() in task_text for marker in SECRET_MARKERS):
                    continue
                operation = task_text.replace('"', "'")
                metadata_only = (
                    "operation='show'" in operation or "operation: show" in operation
                ) and "value" not in operation
                if metadata_only and "eigenstate_sealed_record" not in operation:
                    continue
                no_log = task.get("no_log")
                if no_log is None:
                    failures.append(f"{path}: {task.get('name', '<unnamed>')}")

        self.assertEqual([], failures)

    def test_neutral_phase2_docs_do_not_use_sales_framing(self):
        docs = [
            PROJECT_ROOT / "docs" / "aap-golden-path-roles.md",
            PROJECT_ROOT / "docs" / "sealed-artifact-delivery-role.md",
            PROJECT_ROOT / "docs" / "temporary-access-window-role.md",
            PROJECT_ROOT / "docs" / "cert-expiry-report-role.md",
            PROJECT_ROOT / "docs" / "phase2-validation-walkthrough.md",
        ]
        forbidden = ["seller", "sales", "presales", "sales motion"]
        failures = []
        for path in docs:
            text = path.read_text().lower()
            for marker in forbidden:
                if marker in text:
                    failures.append(f"{path}: {marker}")
        self.assertEqual([], failures)


if __name__ == "__main__":
    unittest.main()
