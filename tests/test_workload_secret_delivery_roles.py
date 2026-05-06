import os
import pathlib
import stat
import subprocess
import tempfile
import unittest
import json

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


class WorkloadSecretDeliveryRoleTests(unittest.TestCase):
    def _run_playbook(self, playbook, output_dir, extra_vars=None):
        merged_vars = {
            "eigenstate_k8s_secret_output_dir": str(output_dir),
            "eigenstate_k8s_tls_output_dir": str(output_dir),
            "eigenstate_keytab_secret_output_dir": str(output_dir),
        }
        merged_vars.update(extra_vars or {})
        with tempfile.TemporaryDirectory() as collections_root:
            command = [
                "ansible-playbook",
                playbook,
                "-e",
                json.dumps(merged_vars),
            ]

            result = subprocess.run(
                command,
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

    def test_review_manifests_redact_payloads_by_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = pathlib.Path(tmpdir)
            sensitive_value = "workload-secret-sensitive-material"
            result = self._run_playbook(
                "playbooks/render-kubernetes-secret-from-idm-vault.yml",
                output_dir,
                {
                    "eigenstate_k8s_secret_data": {
                        "application.conf": sensitive_value,
                    },
                },
            )

            review_path = output_dir / "kubernetes-secret-from-idm-vault.review.yaml"
            payload_path = output_dir / "kubernetes-secret-from-idm-vault.secret.yaml"
            self.assertTrue(review_path.is_file())
            self.assertFalse(payload_path.exists())
            review_doc = yaml.safe_load(review_path.read_text())
            self.assertEqual("Secret", review_doc["kind"])
            self.assertEqual("REDACTED", review_doc["stringData"]["application.conf"])
            self.assertNotIn(sensitive_value, review_path.read_text())
            self.assertNotIn(sensitive_value, result.stdout)
            self.assertNotIn(sensitive_value, result.stderr)

    def test_tls_and_keytab_review_manifests_are_rendered_without_payload_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = pathlib.Path(tmpdir)
            self._run_playbook("playbooks/render-kubernetes-tls-secret-from-idm-cert.yml", output_dir)
            self._run_playbook("playbooks/render-keytab-secret.yml", output_dir)

            tls_review = output_dir / "kubernetes-tls-from-idm-cert.review.yaml"
            keytab_review = output_dir / "keytab-secret.review.yaml"
            self.assertTrue(tls_review.is_file())
            self.assertTrue(keytab_review.is_file())
            self.assertFalse((output_dir / "kubernetes-tls-from-idm-cert.secret.yaml").exists())
            self.assertFalse((output_dir / "keytab-secret.secret.yaml").exists())

            tls_doc = yaml.safe_load(tls_review.read_text())
            keytab_doc = yaml.safe_load(keytab_review.read_text())
            self.assertEqual("kubernetes.io/tls", tls_doc["type"])
            self.assertEqual("REDACTED", tls_doc["stringData"]["tls.key"])
            self.assertEqual("REDACTED", keytab_doc["stringData"]["service.keytab"])

    def test_payload_manifest_is_explicit_and_protected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = pathlib.Path(tmpdir)
            self._run_playbook(
                "playbooks/render-keytab-secret.yml",
                output_dir,
                {"eigenstate_keytab_secret_write_payload_manifest": True},
            )

            payload_path = output_dir / "keytab-secret.secret.yaml"
            self.assertTrue(payload_path.is_file())
            mode = stat.S_IMODE(payload_path.stat().st_mode)
            self.assertEqual(0o600, mode)
            payload_doc = yaml.safe_load(payload_path.read_text())
            self.assertIn("service.keytab", payload_doc["data"])


if __name__ == "__main__":
    unittest.main()
