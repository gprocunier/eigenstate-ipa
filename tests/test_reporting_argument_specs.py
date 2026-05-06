import pathlib
import unittest

import yaml


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReportingArgumentSpecTests(unittest.TestCase):
    def _load_spec(self, role):
        path = PROJECT_ROOT / "roles" / role / "meta" / "argument_specs.yml"
        return yaml.safe_load(path.read_text())

    def test_argument_specs_have_main_and_required_options(self):
        expected = {
            "idm_readiness_report": [
                "eigenstate_idm_readiness_report_output_dir",
                "eigenstate_idm_readiness_report_formats",
                "eigenstate_idm_readiness_report_checks",
            ],
            "certificate_inventory_report": [
                "eigenstate_certificate_inventory_report_output_dir",
                "eigenstate_certificate_inventory_report_formats",
                "eigenstate_certificate_inventory_report_certificates",
            ],
            "keytab_rotation_candidates": [
                "eigenstate_keytab_rotation_candidates_output_dir",
                "eigenstate_keytab_rotation_candidates_formats",
                "eigenstate_keytab_rotation_candidates_records",
            ],
            "temporary_access_report": [
                "eigenstate_temporary_access_report_output_dir",
                "eigenstate_temporary_access_report_formats",
                "eigenstate_temporary_access_report_windows",
            ],
            "policy_drift_report": [
                "eigenstate_policy_drift_report_output_dir",
                "eigenstate_policy_drift_report_formats",
                "eigenstate_policy_drift_report_findings",
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

    def test_all_reporting_roles_support_json_yaml_markdown_by_default(self):
        format_options = {
            "idm_readiness_report": "eigenstate_idm_readiness_report_formats",
            "certificate_inventory_report": "eigenstate_certificate_inventory_report_formats",
            "keytab_rotation_candidates": "eigenstate_keytab_rotation_candidates_formats",
            "temporary_access_report": "eigenstate_temporary_access_report_formats",
            "policy_drift_report": "eigenstate_policy_drift_report_formats",
        }

        for role, option_name in format_options.items():
            options = self._load_spec(role)["argument_specs"]["main"]["options"]
            with self.subTest(role=role):
                self.assertEqual(options[option_name]["default"], ["json", "yaml", "md"])


if __name__ == "__main__":
    unittest.main()
