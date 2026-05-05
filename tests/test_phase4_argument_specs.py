import pathlib
import unittest

import yaml


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class Phase4ArgumentSpecTests(unittest.TestCase):
    def _load_spec(self, role):
        path = PROJECT_ROOT / "roles" / role / "meta" / "argument_specs.yml"
        return yaml.safe_load(path.read_text())

    def test_argument_specs_have_main_and_required_options(self):
        expected = {
            "openshift_idm_oidc_validation": [
                "eigenstate_oidc_issuer_url",
                "eigenstate_oidc_client_id",
                "eigenstate_oidc_client_secret_name",
                "eigenstate_oidc_expected_groups",
                "eigenstate_oidc_idm_known_groups",
            ],
            "keycloak_idm_federation_validation": [
                "eigenstate_keycloak_realm",
                "eigenstate_keycloak_idm_provider_alias",
                "eigenstate_keycloak_expected_groups",
                "eigenstate_keycloak_expected_mappers",
            ],
            "openshift_breakglass_validation": [
                "eigenstate_breakglass_expected_groups",
                "eigenstate_breakglass_known_idm_groups",
                "eigenstate_breakglass_expected_rbac_bindings",
                "eigenstate_breakglass_required_controls",
            ],
        }

        for role, option_names in expected.items():
            with self.subTest(role=role):
                data = self._load_spec(role)
                self.assertIn("argument_specs", data)
                self.assertIn("main", data["argument_specs"])
                options = data["argument_specs"]["main"]["options"]
                for name in option_names:
                    self.assertIn(name, options)

    def test_report_format_choices_are_validation_only(self):
        report_options = {
            "openshift_idm_oidc_validation": "eigenstate_oidc_report_formats",
            "keycloak_idm_federation_validation": "eigenstate_keycloak_report_formats",
            "openshift_breakglass_validation": "eigenstate_breakglass_report_formats",
        }

        for role, option_name in report_options.items():
            options = self._load_spec(role)["argument_specs"]["main"]["options"]
            with self.subTest(role=role):
                self.assertEqual(options[option_name]["default"], ["json", "md"])


if __name__ == "__main__":
    unittest.main()
