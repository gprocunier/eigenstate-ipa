import importlib.util
import pathlib
import sys
import types
import unittest


def _load_access_path_module():
    module_name = "eigenstate_ipa_test_access_path"
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "plugins"
        / "modules"
        / "access_path.py"
    )
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class NotFound(Exception):
    pass


class FakeCommands:
    def __init__(self):
        self.users = {
            "automation": {
                "uid": ["automation"],
                "krbprincipalname": ["automation@EXAMPLE.COM"],
            },
        }
        self.hbacrules = {
            "automation-ssh": {
                "cn": ["automation-ssh"],
                "ipaenabledflag": ["TRUE"],
                "memberservice_hbacsvc": ["sshd"],
                "memberhost_host": ["app01.example.com"],
                "memberuser_user": ["automation"],
            },
        }
        self.sudorules = {
            "automation-root": {
                "cn": ["automation-root"],
                "ipaenabledflag": ["TRUE"],
                "ipasudorunas_user": ["root"],
                "ipasudoopt": [],
            },
        }
        self.selinuxmaps = {
            "automation-confined": {
                "cn": ["automation-confined"],
                "ipaenabledflag": ["TRUE"],
                "ipaselinuxuser": ["staff_u:s0"],
            },
        }

    def _show(self, store, name):
        if name not in store:
            raise NotFound("not found")
        return {"result": dict(store[name])}

    def user_show(self, name, **kwargs):
        return self._show(self.users, name)

    def hbacrule_show(self, name, **kwargs):
        return self._show(self.hbacrules, name)

    def sudorule_show(self, name, **kwargs):
        return self._show(self.sudorules, name)

    def selinuxusermap_show(self, name, **kwargs):
        return self._show(self.selinuxmaps, name)


class AccessPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_access_path_module()

    def _api(self):
        commands = FakeCommands()
        return types.SimpleNamespace(Command=commands), commands

    def _params(self, **overrides):
        params = {
            "principal": "automation@EXAMPLE.COM",
            "host": "app01.example.com",
            "hbac_service": "sshd",
            "hbac_rule": "automation-ssh",
            "sudo_rule": "automation-root",
            "selinux_map": "automation-confined",
            "expected_selinux_user": "staff_u:s0",
            "expected_runas_user": "root",
        }
        params.update(overrides)
        return params

    def test_all_green_path_is_ready(self):
        api, _commands = self._api()

        result = self.mod.run_access_path(api, self._params())

        self.assertTrue(result["path_ready"])
        self.assertEqual(result["errors"], [])
        self.assertTrue(result["principal"]["exists"])
        self.assertTrue(result["hbac"]["permits_service"])
        self.assertTrue(result["sudo"]["runas_ok"])
        self.assertTrue(result["selinux_map"]["selinuxuser_matches"])

    def test_missing_hbac_rule_blocks_path(self):
        api, commands = self._api()
        del commands.hbacrules["automation-ssh"]

        result = self.mod.run_access_path(api, self._params())

        self.assertFalse(result["path_ready"])
        self.assertIn("HBAC rule does not exist", result["errors"])

    def test_disabled_hbac_rule_blocks_path(self):
        api, commands = self._api()
        commands.hbacrules["automation-ssh"]["ipaenabledflag"] = ["FALSE"]

        result = self.mod.run_access_path(api, self._params())

        self.assertFalse(result["path_ready"])
        self.assertIn("HBAC rule is disabled", result["errors"])

    def test_wrong_hbac_service_blocks_path(self):
        api, commands = self._api()
        commands.hbacrules["automation-ssh"]["memberservice_hbacsvc"] = ["sudo"]

        result = self.mod.run_access_path(api, self._params())

        self.assertFalse(result["path_ready"])
        self.assertIn(
            "HBAC rule does not permit requested service",
            result["errors"],
        )

    def test_missing_sudo_rule_blocks_path(self):
        api, commands = self._api()
        del commands.sudorules["automation-root"]

        result = self.mod.run_access_path(api, self._params())

        self.assertFalse(result["path_ready"])
        self.assertIn("sudo rule does not exist", result["errors"])

    def test_sudo_runas_mismatch_blocks_path(self):
        api, commands = self._api()
        commands.sudorules["automation-root"]["ipasudorunas_user"] = ["app"]

        result = self.mod.run_access_path(api, self._params())

        self.assertFalse(result["path_ready"])
        self.assertIn(
            "sudo rule RunAs target does not match expectation",
            result["errors"],
        )

    def test_missing_selinux_map_blocks_path(self):
        api, commands = self._api()
        del commands.selinuxmaps["automation-confined"]

        result = self.mod.run_access_path(api, self._params())

        self.assertFalse(result["path_ready"])
        self.assertIn("SELinux user map does not exist", result["errors"])

    def test_disabled_selinux_map_blocks_path(self):
        api, commands = self._api()
        commands.selinuxmaps["automation-confined"]["ipaenabledflag"] = ["FALSE"]

        result = self.mod.run_access_path(api, self._params())

        self.assertFalse(result["path_ready"])
        self.assertIn("SELinux user map is disabled", result["errors"])

    def test_selinux_user_mismatch_blocks_path(self):
        api, commands = self._api()
        commands.selinuxmaps["automation-confined"]["ipaselinuxuser"] = [
            "user_u:s0",
        ]

        result = self.mod.run_access_path(api, self._params())

        self.assertFalse(result["path_ready"])
        self.assertIn(
            "SELinux user does not match expectation",
            result["errors"],
        )

    def test_risky_sudo_options_are_warnings(self):
        api, commands = self._api()
        commands.sudorules["automation-root"]["ipasudoopt"] = ["!authenticate"]

        result = self.mod.run_access_path(api, self._params())

        self.assertTrue(result["path_ready"])
        self.assertEqual(result["sudo"]["risky_options"], ["!authenticate"])
        self.assertEqual(
            result["warnings"],
            ["sudo rule contains risky options"],
        )


if __name__ == "__main__":
    unittest.main()
