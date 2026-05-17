import importlib.util
import pathlib
import sys
import unittest


def _load_sudo_risk_module():
    module_name = "eigenstate_ipa_test_sudo_risk"
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "plugins"
        / "module_utils"
        / "sudo_risk.py"
    )
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SudoRiskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_sudo_risk_module()

    def _rule(self, **overrides):
        rule = {
            "allow_sudocmds": ["/usr/bin/systemctl restart app.service"],
            "runasusers": ["app"],
            "runasusercategory": None,
        }
        rule.update(overrides)
        return rule

    def test_safe_narrow_command_is_low_risk(self):
        result = self.mod.classify_sudo_rule(self._rule())

        self.assertEqual(result["risk_level"], "low")
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["recommendation"], "monitor")

    def test_shells_are_high_risk(self):
        result = self.mod.classify_sudo_rule(
            self._rule(allow_sudocmds=["/bin/bash"]))

        self.assertEqual(result["risk_level"], "high")
        self.assertEqual(result["findings"][0]["category"], "shell_escape")

    def test_package_managers_are_high_risk(self):
        result = self.mod.classify_sudo_rule(
            self._rule(allow_sudocmds=["/usr/bin/dnf install httpd"]))

        self.assertEqual(result["risk_level"], "high")
        self.assertEqual(result["findings"][0]["category"], "package_manager")

    def test_policy_management_tools_are_high_risk(self):
        result = self.mod.classify_sudo_rule(
            self._rule(allow_sudocmds=["/usr/sbin/semanage fcontext -a"]))

        self.assertEqual(result["risk_level"], "high")
        self.assertEqual(result["findings"][0]["category"], "policy_management")

    def test_idm_tools_are_high_risk(self):
        result = self.mod.classify_sudo_rule(
            self._rule(allow_sudocmds=["/usr/bin/ipa user-add app"]))

        self.assertEqual(result["risk_level"], "high")
        self.assertEqual(result["findings"][0]["category"], "idm_management")

    def test_wildcard_commands_are_high_risk(self):
        result = self.mod.classify_sudo_rule(
            self._rule(allow_sudocmds=["ALL"]))

        self.assertEqual(result["risk_level"], "high")
        self.assertEqual(result["findings"][0]["command"], "ALL")

    def test_unrestricted_runas_is_high_risk(self):
        result = self.mod.classify_sudo_rule(
            self._rule(runasusercategory="all"))

        self.assertEqual(result["risk_level"], "high")
        categories = [item["category"] for item in result["findings"]]
        self.assertIn("unrestricted_runas", categories)

    def test_custom_pattern_override_works(self):
        result = self.mod.classify_sudo_rule(
            self._rule(allow_sudocmds=["/opt/tools/pkgctl update"]),
            custom_patterns={"package_manager": ["/opt/tools/pkgctl"]},
        )

        self.assertEqual(result["risk_level"], "high")
        self.assertEqual(result["findings"][0]["category"], "package_manager")

    def test_categories_can_be_limited(self):
        result = self.mod.classify_sudo_rule(
            self._rule(allow_sudocmds=["/usr/bin/dnf install httpd"]),
            risk_categories=["shell_escape"],
        )

        self.assertEqual(result["risk_level"], "low")
        self.assertEqual(result["findings"], [])

    def test_bad_input_shape_is_unknown(self):
        result = self.mod.classify_sudo_rule("not a dict")

        self.assertEqual(result["risk_level"], "unknown")
        self.assertEqual(result["recommendation"], "review_input_shape")


if __name__ == "__main__":
    unittest.main()
