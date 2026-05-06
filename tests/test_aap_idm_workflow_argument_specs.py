import pathlib
import unittest

import yaml


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class AapIdmWorkflowArgumentSpecTests(unittest.TestCase):
    def _load_spec(self, role):
        path = PROJECT_ROOT / "roles" / role / "meta" / "argument_specs.yml"
        return yaml.safe_load(path.read_text())

    def test_argument_specs_have_main_and_state_choices(self):
        expected = {
            "sealed_artifact_delivery": (
                "eigenstate_sealed_state",
                ["preflight", "staged", "handed_off", "absent"],
                ["eigenstate_sealed_vault_name", "eigenstate_sealed_server"],
            ),
            "temporary_access_window": (
                "eigenstate_taw_state",
                ["preflight", "open", "expire", "clear"],
                ["eigenstate_taw_username", "eigenstate_taw_server"],
            ),
            "cert_expiry_report": (
                "eigenstate_cert_report_state",
                ["present"],
                ["eigenstate_cert_report_server"],
            ),
        }

        for role, (state_var, choices, required_vars) in expected.items():
            with self.subTest(role=role):
                data = self._load_spec(role)
                self.assertIn("argument_specs", data)
                self.assertIn("main", data["argument_specs"])
                options = data["argument_specs"]["main"]["options"]
                self.assertIn(state_var, options)
                self.assertEqual(options[state_var]["choices"], choices)
                for var in required_vars:
                    self.assertIn(var, options)
                    self.assertTrue(options[var].get("required", False))

    def test_secret_auth_options_are_marked_no_log(self):
        secret_options = {
            "sealed_artifact_delivery": ["eigenstate_sealed_ipaadmin_password"],
            "temporary_access_window": ["eigenstate_taw_ipaadmin_password"],
            "cert_expiry_report": ["eigenstate_cert_report_ipaadmin_password"],
        }
        for role, names in secret_options.items():
            options = self._load_spec(role)["argument_specs"]["main"]["options"]
            for name in names:
                with self.subTest(role=role, name=name):
                    self.assertTrue(options[name].get("no_log", False))


if __name__ == "__main__":
    unittest.main()
