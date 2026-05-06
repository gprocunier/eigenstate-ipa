import json
import os
import pathlib
import subprocess
import tempfile
import unittest

import yaml


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _collection_env(collections_root):
    collection_dir = (
        pathlib.Path(collections_root)
        / "ansible_collections"
        / "eigenstate"
    )
    collection_dir.mkdir(parents=True)
    (collection_dir / "ipa").symlink_to(PROJECT_ROOT)
    return {
        **os.environ,
        "ANSIBLE_COLLECTIONS_PATH": str(collections_root),
        "ANSIBLE_LOCALHOST_WARNING": "false",
    }


class ReportingRoleTests(unittest.TestCase):
    def _run_playbook(self, playbook, output_dir):
        extra_vars = {
            "eigenstate_idm_readiness_report_output_dir": str(output_dir),
            "eigenstate_certificate_inventory_report_output_dir": str(output_dir),
            "eigenstate_keytab_rotation_candidates_output_dir": str(output_dir),
            "eigenstate_temporary_access_report_output_dir": str(output_dir),
            "eigenstate_policy_drift_report_output_dir": str(output_dir),
        }
        with tempfile.TemporaryDirectory() as collections_root:
            result = subprocess.run(
                [
                    "ansible-playbook",
                    playbook,
                    "-e",
                    json.dumps(extra_vars),
                ],
                cwd=PROJECT_ROOT,
                env=_collection_env(collections_root),
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def test_static_validation_renders_all_report_formats(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = pathlib.Path(tmpdir)
            self._run_playbook("playbooks/reporting-static-validation.yml", output_dir)

            expected = [
                "idm-readiness-report",
                "certificate-inventory-report",
                "keytab-rotation-candidates",
                "temporary-access-report",
                "policy-drift-report",
            ]
            for basename in expected:
                with self.subTest(basename=basename):
                    self.assertTrue((output_dir / f"{basename}.json").is_file())
                    self.assertTrue((output_dir / f"{basename}.yaml").is_file())
                    self.assertTrue((output_dir / f"{basename}.md").is_file())

    def test_json_reports_have_stable_schemas_and_read_only_boundary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = pathlib.Path(tmpdir)
            self._run_playbook("playbooks/reporting-static-validation.yml", output_dir)

            expected_schemas = {
                "idm-readiness-report.json": "eigenstate.ipa/idm_readiness_report/v1",
                "certificate-inventory-report.json": "eigenstate.ipa/certificate_inventory_report/v1",
                "keytab-rotation-candidates.json": "eigenstate.ipa/keytab_rotation_candidates/v1",
                "temporary-access-report.json": "eigenstate.ipa/temporary_access_report/v1",
                "policy-drift-report.json": "eigenstate.ipa/policy_drift_report/v1",
            }
            for filename, schema in expected_schemas.items():
                with self.subTest(filename=filename):
                    report = json.loads((output_dir / filename).read_text())
                    self.assertEqual(schema, report["schema"])
                    self.assertEqual("1.0", report["schema_version"])
                    self.assertTrue(report["read_only"])
                    self.assertIn("summary", report)

    def test_yaml_reports_match_json_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = pathlib.Path(tmpdir)
            self._run_playbook("playbooks/reporting-static-validation.yml", output_dir)

            for json_path in output_dir.glob("*.json"):
                yaml_path = output_dir / f"{json_path.stem}.yaml"
                with self.subTest(report=json_path.name):
                    json_report = json.loads(json_path.read_text())
                    yaml_report = yaml.safe_load(yaml_path.read_text())
                    self.assertEqual(json_report["schema"], yaml_report["schema"])
                    self.assertEqual(json_report["role"], yaml_report["role"])


if __name__ == "__main__":
    unittest.main()
