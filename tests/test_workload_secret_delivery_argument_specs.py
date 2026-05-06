import pathlib
import unittest

import yaml


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class WorkloadSecretDeliveryArgumentSpecTests(unittest.TestCase):
    def _spec_options(self, role):
        spec_path = PROJECT_ROOT / "roles" / role / "meta" / "argument_specs.yml"
        spec = yaml.safe_load(spec_path.read_text())
        return spec["argument_specs"]["main"]["options"]

    def test_secret_bearing_options_are_no_log(self):
        expected = {
            "kubernetes_secret_from_idm_vault": [
                "eigenstate_k8s_secret_data",
                "eigenstate_k8s_secret_kerberos_keytab",
                "eigenstate_k8s_secret_ipaadmin_password",
                "eigenstate_k8s_secret_kubeconfig",
            ],
            "kubernetes_tls_from_idm_cert": [
                "eigenstate_k8s_tls_certificate",
                "eigenstate_k8s_tls_private_key",
                "eigenstate_k8s_tls_ca_certificate",
                "eigenstate_k8s_tls_kubeconfig",
            ],
            "keytab_secret_render": [
                "eigenstate_keytab_secret_keytab_b64",
                "eigenstate_keytab_secret_kubeconfig",
            ],
        }
        for role, options in expected.items():
            spec_options = self._spec_options(role)
            for option in options:
                with self.subTest(role=role, option=option):
                    self.assertTrue(spec_options[option].get("no_log"))

    def test_apply_defaults_are_safe(self):
        expectations = {
            "kubernetes_secret_from_idm_vault": (
                "eigenstate_k8s_secret_render_only",
                "eigenstate_k8s_secret_apply",
                "eigenstate_k8s_secret_write_payload_manifest",
            ),
            "kubernetes_tls_from_idm_cert": (
                "eigenstate_k8s_tls_render_only",
                "eigenstate_k8s_tls_apply",
                "eigenstate_k8s_tls_write_payload_manifest",
            ),
            "keytab_secret_render": (
                "eigenstate_keytab_secret_render_only",
                "eigenstate_keytab_secret_apply",
                "eigenstate_keytab_secret_write_payload_manifest",
            ),
        }
        for role, option_names in expectations.items():
            defaults_path = PROJECT_ROOT / "roles" / role / "defaults" / "main.yml"
            defaults = yaml.safe_load(defaults_path.read_text())
            render_only, apply, payload = option_names
            with self.subTest(role=role):
                self.assertTrue(defaults[render_only])
                self.assertFalse(defaults[apply])
                self.assertFalse(defaults[payload])


if __name__ == "__main__":
    unittest.main()
