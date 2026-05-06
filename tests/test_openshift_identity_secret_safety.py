import pathlib
import unittest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class OpenShiftIdentitySecretSafetyTests(unittest.TestCase):
    def test_openshift_identity_public_content_is_neutral(self):
        paths = [
            PROJECT_ROOT / "docs" / "openshift-keycloak-idm-reference.md",
            PROJECT_ROOT / "docs" / "openshift-identity-validation-walkthrough.md",
            PROJECT_ROOT / "docs" / "openshift-breakglass-validation.md",
            PROJECT_ROOT / "docs" / "openshift-ldap-fallback.md",
        ]
        forbidden = ["seller", "sales", "presales", "sales motion"]
        failures = []
        for path in paths:
            text = path.read_text().lower()
            for marker in forbidden:
                if marker in text:
                    failures.append(f"{path}: {marker}")
        self.assertEqual([], failures)

    def test_openshift_identity_examples_do_not_embed_secret_values(self):
        paths = [
            *(
                PROJECT_ROOT / "roles" / "openshift_idm_oidc_validation"
            ).rglob("*"),
            *(
                PROJECT_ROOT / "roles" / "keycloak_idm_federation_validation"
            ).rglob("*"),
            *(
                PROJECT_ROOT / "roles" / "openshift_breakglass_validation"
            ).rglob("*"),
            PROJECT_ROOT / "playbooks" / "render-openshift-oidc-config.yml",
            PROJECT_ROOT / "playbooks" / "validate-openshift-idm-groups.yml",
            PROJECT_ROOT / "playbooks" / "validate-keycloak-idm-claims.yml",
            PROJECT_ROOT / "playbooks" / "validate-openshift-breakglass-path.yml",
        ]
        forbidden = [
            "changeme",
            "adminpass",
            "password:",
            "token:",
            "client_secret:",
            "-----begin private key-----",
        ]
        failures = []
        for path in paths:
            if not path.is_file():
                continue
            text = path.read_text().lower()
            for marker in forbidden:
                if marker in text:
                    failures.append(f"{path}: {marker}")
        self.assertEqual([], failures)


if __name__ == "__main__":
    unittest.main()
