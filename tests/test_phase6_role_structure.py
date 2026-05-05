import pathlib
import unittest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class Phase6RoleStructureTests(unittest.TestCase):
    def test_required_role_files_exist(self):
        roles = [
            "idm_readiness_report",
            "certificate_inventory_report",
            "keytab_rotation_candidates",
            "temporary_access_report",
            "policy_drift_report",
        ]
        required = [
            "README.md",
            "defaults/main.yml",
            "meta/argument_specs.yml",
            "tasks/main.yml",
            "tasks/validate.yml",
            "tasks/render.yml",
            "templates/report.json.j2",
            "templates/report.yaml.j2",
            "templates/report.md.j2",
        ]

        for role in roles:
            role_dir = PROJECT_ROOT / "roles" / role
            for relpath in required:
                with self.subTest(role=role, relpath=relpath):
                    self.assertTrue((role_dir / relpath).is_file())

    def test_required_phase6_playbooks_and_docs_exist(self):
        required = [
            "playbooks/report-idm-readiness.yml",
            "playbooks/report-certificate-inventory.yml",
            "playbooks/report-keytab-rotation-candidates.yml",
            "playbooks/report-temporary-access.yml",
            "playbooks/report-policy-drift.yml",
            "playbooks/phase6-static-validation.yml",
            "docs/reporting-overview.md",
            "docs/readiness-report-schema.md",
            "docs/certificate-inventory-report.md",
            "docs/keytab-rotation-candidate-report.md",
            "docs/temporary-access-report.md",
            "docs/policy-drift-report.md",
        ]
        for relpath in required:
            with self.subTest(relpath=relpath):
                self.assertTrue((PROJECT_ROOT / relpath).is_file())


if __name__ == "__main__":
    unittest.main()
