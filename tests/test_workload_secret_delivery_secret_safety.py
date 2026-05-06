import pathlib
import unittest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


WORKLOAD_SECRET_DELIVERY_DOCS = [
    PROJECT_ROOT / "docs" / "workload-secret-delivery-controls.md",
    PROJECT_ROOT / "docs" / "kubernetes-secret-from-idm-vault.md",
    PROJECT_ROOT / "docs" / "kubernetes-tls-from-idm-cert.md",
    PROJECT_ROOT / "docs" / "keytab-delivery-to-workloads.md",
]

WORKLOAD_SECRET_DELIVERY_ROLES = [
    PROJECT_ROOT / "roles" / "kubernetes_secret_from_idm_vault",
    PROJECT_ROOT / "roles" / "kubernetes_tls_from_idm_cert",
    PROJECT_ROOT / "roles" / "keytab_secret_render",
]

WORKLOAD_SECRET_DELIVERY_PLAYBOOKS = [
    PROJECT_ROOT / "playbooks" / "render-kubernetes-secret-from-idm-vault.yml",
    PROJECT_ROOT / "playbooks" / "render-kubernetes-tls-secret-from-idm-cert.yml",
    PROJECT_ROOT / "playbooks" / "render-keytab-secret.yml",
    PROJECT_ROOT / "playbooks" / "workload-secret-delivery-static-validation.yml",
]


class WorkloadSecretDeliverySecretSafetyTests(unittest.TestCase):
    def test_workload_secret_delivery_public_content_is_neutral(self):
        forbidden = ["seller", "sales", "presales", "sales motion"]
        failures = []
        for path in WORKLOAD_SECRET_DELIVERY_DOCS:
            text = path.read_text().lower()
            for marker in forbidden:
                if marker in text:
                    failures.append(f"{path}: {marker}")
        self.assertEqual([], failures)

    def test_workload_secret_delivery_examples_do_not_embed_real_secret_markers(self):
        paths = [
            *WORKLOAD_SECRET_DELIVERY_DOCS,
            *WORKLOAD_SECRET_DELIVERY_PLAYBOOKS,
        ]
        for role_dir in WORKLOAD_SECRET_DELIVERY_ROLES:
            paths.extend(path for path in role_dir.rglob("*") if path.is_file())

        forbidden = [
            "changeme",
            "adminpass",
            "token:",
            "client_secret:",
            "-----begin private key-----",
            "-----begin rsa private key-----",
            "-----begin openssh private key-----",
        ]
        failures = []
        for path in paths:
            text = path.read_text().lower()
            for marker in forbidden:
                if marker in text:
                    failures.append(f"{path}: {marker}")
        self.assertEqual([], failures)

    def test_secret_bearing_task_files_use_no_log(self):
        secret_markers = [
            "eigenstate_k8s_secret_data",
            "eigenstate_k8s_secret_vault_record",
            "eigenstate_k8s_tls_certificate",
            "eigenstate_k8s_tls_private_key",
            "eigenstate_keytab_secret_keytab_b64",
            "kubeconfig",
        ]
        failures = []
        for role_dir in WORKLOAD_SECRET_DELIVERY_ROLES:
            for path in (role_dir / "tasks").glob("*.yml"):
                text = path.read_text()
                if any(marker in text for marker in secret_markers):
                    if "no_log:" not in text:
                        failures.append(str(path))
        self.assertEqual([], failures)


if __name__ == "__main__":
    unittest.main()
