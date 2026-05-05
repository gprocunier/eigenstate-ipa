import os
import pathlib
import subprocess
import tempfile
import unittest

import yaml


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class AapExecutionEnvironmentRoleTests(unittest.TestCase):
    def test_render_playbook_creates_expected_build_context(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = pathlib.Path(tmpdir) / "eigenstate-idm-ee"
            result = subprocess.run(
                [
                    "ansible-playbook",
                    "playbooks/aap-ee-render.yml",
                    "-e",
                    f"eigenstate_ee_output_dir={output_dir}",
                ],
                cwd=PROJECT_ROOT,
                env={**os.environ, "ANSIBLE_LOCALHOST_WARNING": "false"},
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(
                result.returncode,
                0,
                msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
            )

            expected_files = [
                "execution-environment.yml",
                "requirements.yml",
                "bindep.txt",
                "python-requirements.txt",
                "README.md",
                "ansible.cfg.example",
            ]
            for filename in expected_files:
                self.assertTrue((output_dir / filename).is_file(), filename)

            ee_definition = yaml.safe_load(
                (output_dir / "execution-environment.yml").read_text()
            )
            requirements = yaml.safe_load((output_dir / "requirements.yml").read_text())

            self.assertEqual(ee_definition["version"], 3)
            collection_names = {
                item["name"] for item in requirements.get("collections", [])
            }
            self.assertIn("eigenstate.ipa", collection_names)

            bindep = (output_dir / "bindep.txt").read_text()
            for package in (
                "ipa-client",
                "krb5-workstation",
                "python3-ipalib",
                "python3-ipaclient",
            ):
                self.assertIn(package, bindep)

            rendered_text = "\n".join(
                (output_dir / filename).read_text() for filename in expected_files
            ).lower()
            forbidden_markers = [
                "changeme",
                "password=",
                "token=",
                "secret=",
                "-----begin private key-----",
            ]
            for marker in forbidden_markers:
                self.assertNotIn(marker, rendered_text)


if __name__ == "__main__":
    unittest.main()
