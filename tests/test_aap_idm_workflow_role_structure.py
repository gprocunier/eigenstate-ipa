import pathlib
import unittest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class AapIdmWorkflowRoleStructureTests(unittest.TestCase):
    def test_required_role_files_exist(self):
        roles = {
            "sealed_artifact_delivery": [
                "tasks/validate.yml",
                "tasks/preflight.yml",
                "tasks/retrieve.yml",
                "tasks/stage.yml",
                "tasks/handoff.yml",
                "tasks/cleanup.yml",
                "tasks/report.yml",
                "templates/handoff-report.json.j2",
                "templates/handoff-report.md.j2",
            ],
            "temporary_access_window": [
                "tasks/validate.yml",
                "tasks/preflight_hbac.yml",
                "tasks/preflight_sudo.yml",
                "tasks/preflight_selinuxmap.yml",
                "tasks/open.yml",
                "tasks/expire.yml",
                "tasks/clear.yml",
                "tasks/report.yml",
                "templates/access-window-report.json.j2",
                "templates/access-window-report.md.j2",
            ],
            "cert_expiry_report": [
                "tasks/validate.yml",
                "tasks/find.yml",
                "tasks/render.yml",
                "templates/cert-expiry-report.json.j2",
                "templates/cert-expiry-report.md.j2",
                "templates/cert-expiry-report.csv.j2",
            ],
        }
        common = [
            "README.md",
            "defaults/main.yml",
            "meta/argument_specs.yml",
            "tasks/main.yml",
        ]

        for role, extra_files in roles.items():
            role_dir = PROJECT_ROOT / "roles" / role
            for relpath in common + extra_files:
                with self.subTest(role=role, relpath=relpath):
                    self.assertTrue((role_dir / relpath).is_file())

    def test_required_aap_idm_workflow_playbooks_and_docs_exist(self):
        required = [
            "playbooks/sealed-artifact-delivery.yml",
            "playbooks/temporary-access-window.yml",
            "playbooks/cert-expiry-report.yml",
            "playbooks/aap-idm-workflow-static-validation.yml",
            "playbooks/aap-idm-workflow-live-smoke.yml",
            "docs/aap-idm-workflow-roles.md",
            "docs/sealed-artifact-delivery-role.md",
            "docs/temporary-access-window-role.md",
            "docs/cert-expiry-report-role.md",
            "docs/aap-idm-workflow-validation-walkthrough.md",
            "aap/job-templates/sealed-artifact-delivery.example.yml",
            "aap/job-templates/temporary-access-window.example.yml",
            "aap/job-templates/cert-expiry-report.example.yml",
            "aap/workflow-templates/eigenstate-idm-operations-workflow.example.yml",
        ]
        for relpath in required:
            with self.subTest(relpath=relpath):
                self.assertTrue((PROJECT_ROOT / relpath).is_file())


if __name__ == "__main__":
    unittest.main()
