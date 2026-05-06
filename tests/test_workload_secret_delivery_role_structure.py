import pathlib
import unittest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class WorkloadSecretDeliveryRoleStructureTests(unittest.TestCase):
    def test_required_role_files_exist(self):
        roles = {
            "kubernetes_secret_from_idm_vault": [
                "tasks/validate.yml",
                "tasks/retrieve.yml",
                "tasks/render.yml",
                "tasks/apply.yml",
                "templates/secret-review.yaml.j2",
                "templates/secret-payload.yaml.j2",
            ],
            "kubernetes_tls_from_idm_cert": [
                "tasks/validate.yml",
                "tasks/render.yml",
                "tasks/apply.yml",
                "templates/tls-secret-review.yaml.j2",
                "templates/tls-secret-payload.yaml.j2",
            ],
            "keytab_secret_render": [
                "tasks/validate.yml",
                "tasks/render.yml",
                "tasks/apply.yml",
                "templates/keytab-secret-review.yaml.j2",
                "templates/keytab-secret-payload.yaml.j2",
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

    def test_required_workload_secret_delivery_playbooks_and_docs_exist(self):
        required = [
            "playbooks/render-kubernetes-secret-from-idm-vault.yml",
            "playbooks/render-kubernetes-tls-secret-from-idm-cert.yml",
            "playbooks/render-keytab-secret.yml",
            "playbooks/workload-secret-delivery-static-validation.yml",
            "docs/workload-secret-delivery-controls.md",
            "docs/kubernetes-secret-from-idm-vault.md",
            "docs/kubernetes-tls-from-idm-cert.md",
            "docs/keytab-delivery-to-workloads.md",
        ]
        for relpath in required:
            with self.subTest(relpath=relpath):
                self.assertTrue((PROJECT_ROOT / relpath).is_file())


if __name__ == "__main__":
    unittest.main()
