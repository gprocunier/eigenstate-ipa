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


class OpenShiftIdentityValidationRoleTests(unittest.TestCase):
    def _run_playbook(self, playbook, output_dir):
        with tempfile.TemporaryDirectory() as collections_root:
            result = subprocess.run(
                [
                    "ansible-playbook",
                    playbook,
                    "-e",
                    f"eigenstate_oidc_output_dir={output_dir}",
                    "-e",
                    f"eigenstate_keycloak_output_dir={output_dir}",
                    "-e",
                    f"eigenstate_breakglass_output_dir={output_dir}",
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

    def test_render_openshift_oidc_config_outputs_safe_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = pathlib.Path(tmpdir)
            self._run_playbook("playbooks/render-openshift-oidc-config.yml", output_dir)

            oauth_path = output_dir / "openshift-idm-oidc.oauth.yaml"
            report_path = output_dir / "openshift-idm-oidc.json"
            self.assertTrue(oauth_path.is_file())
            self.assertTrue(report_path.is_file())

            oauth_doc = yaml.safe_load(oauth_path.read_text())
            report = json.loads(report_path.read_text())
            self.assertEqual(oauth_doc["kind"], "OAuth")
            self.assertEqual(report["role"], "openshift_idm_oidc_validation")
            self.assertTrue(report["passed"])

            rendered_text = "\n".join(
                path.read_text().lower() for path in output_dir.iterdir()
            )
            forbidden = ["changeme", "password:", "token:", "-----begin private key-----"]
            for marker in forbidden:
                self.assertNotIn(marker, rendered_text)

    def test_keycloak_and_breakglass_validation_reports_pass(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = pathlib.Path(tmpdir)
            self._run_playbook("playbooks/validate-keycloak-idm-claims.yml", output_dir)
            self._run_playbook(
                "playbooks/validate-openshift-breakglass-path.yml",
                output_dir,
            )

            keycloak = json.loads(
                (output_dir / "keycloak-idm-federation.json").read_text()
            )
            breakglass = json.loads(
                (output_dir / "openshift-breakglass.json").read_text()
            )
            self.assertTrue(keycloak["passed"])
            self.assertTrue(breakglass["passed"])
            self.assertEqual([], keycloak["missing_groups"])
            self.assertEqual([], breakglass["missing_controls"])


if __name__ == "__main__":
    unittest.main()
