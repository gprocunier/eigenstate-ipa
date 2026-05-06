import pathlib
import unittest


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]


class OpenShiftIdentityRoleStructureTests(unittest.TestCase):
    def test_required_role_files_exist(self):
        roles = {
            "openshift_idm_oidc_validation": [
                "tasks/validate.yml",
                "tasks/render.yml",
                "tasks/report.yml",
                "templates/oauth-oidc.yaml.j2",
                "templates/readiness-report.json.j2",
                "templates/readiness-report.md.j2",
            ],
            "keycloak_idm_federation_validation": [
                "tasks/validate.yml",
                "tasks/report.yml",
                "templates/readiness-report.json.j2",
                "templates/readiness-report.md.j2",
            ],
            "openshift_breakglass_validation": [
                "tasks/validate.yml",
                "tasks/report.yml",
                "templates/readiness-report.json.j2",
                "templates/readiness-report.md.j2",
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

    def test_required_openshift_identity_playbooks_and_docs_exist(self):
        required = [
            "playbooks/render-openshift-oidc-config.yml",
            "playbooks/validate-openshift-idm-groups.yml",
            "playbooks/validate-keycloak-idm-claims.yml",
            "playbooks/validate-openshift-breakglass-path.yml",
            "playbooks/openshift-identity-static-validation.yml",
            "docs/openshift-keycloak-idm-reference.md",
            "docs/openshift-identity-validation-walkthrough.md",
            "docs/openshift-breakglass-validation.md",
            "docs/openshift-ldap-fallback.md",
        ]
        for relpath in required:
            with self.subTest(relpath=relpath):
                self.assertTrue((PROJECT_ROOT / relpath).is_file())


if __name__ == "__main__":
    unittest.main()
