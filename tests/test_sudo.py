import importlib.util
import pathlib
import sys
import types
import unittest

from unittest import mock


def _load_sudo_module():
    module_name = "eigenstate_ipa_test_sudo"
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "plugins" / "lookup" / "sudo.py"
    )

    import ansible.errors  # noqa: F401
    import ansible.plugins.lookup  # noqa: F401
    import ansible.utils.display  # noqa: F401
    import ansible.module_utils.common.text.converters  # noqa: F401

    fake_not_found = type("NotFound", (Exception,), {})
    fake_auth_error = type("AuthorizationError", (Exception,), {})

    fake_api = types.SimpleNamespace(
        isdone=lambda phase: True,
        bootstrap=lambda **kwargs: None,
        finalize=lambda: None,
        Backend=types.SimpleNamespace(
            rpcclient=types.SimpleNamespace(
                isconnected=lambda: True,
                connect=lambda ccache=None: None,
                disconnect=lambda: None,
            )
        ),
        Command=types.SimpleNamespace(
            sudorule_show=lambda name, **kwargs: {
                "result": {
                    "cn": [name],
                    "ipaenabledflag": ["TRUE"],
                    "memberuser_user": ["svc-deploy"],
                    "memberuser_group": ["ops"],
                    "memberhost_host": ["app01.example.com"],
                    "memberhost_hostgroup": ["app-servers"],
                    "memberallowcmd_sudocmd": ["/usr/bin/systemctl"],
                    "memberallowcmd_sudocmdgroup": ["system-ops"],
                    "memberdenycmd_sudocmd": ["/usr/bin/su"],
                    "memberdenycmd_sudocmdgroup": [],
                    "ipasudoopt": ["!authenticate"],
                    "ipasudorunas_user": ["root"],
                    "ipasudorunas_group": ["wheel"],
                    "sudoorder": [10],
                    "description": ["Ops maintenance sudo rule"],
                }
            },
            sudorule_find=lambda criteria, **kwargs: {
                "result": [
                    {
                        "cn": ["ops-maintenance"],
                        "ipaenabledflag": ["TRUE"],
                        "memberuser_user": ["svc-deploy"],
                        "memberallowcmd_sudocmd": ["/usr/bin/systemctl"],
                        "description": ["Ops maintenance sudo rule"],
                    },
                    {
                        "cn": ["breakglass"],
                        "ipaenabledflag": ["FALSE"],
                        "usercategory": ["all"],
                        "hostcategory": ["all"],
                        "cmdcategory": ["all"],
                        "description": ["Emergency access"],
                    },
                ],
                "count": 2,
            },
            sudocmd_show=lambda name, **kwargs: {
                "result": {
                    "sudocmd": [name],
                    "description": ["Command description"],
                }
            },
            sudocmd_find=lambda criteria, **kwargs: {
                "result": [
                    {
                        "sudocmd": ["/usr/bin/systemctl"],
                        "description": ["Command description"],
                    },
                    {
                        "sudocmd": ["/usr/bin/journalctl"],
                        "description": None,
                    },
                ],
                "count": 2,
            },
            sudocmdgroup_show=lambda name, **kwargs: {
                "result": {
                    "cn": [name],
                    "member_sudocmd": ["/usr/bin/systemctl", "/usr/bin/journalctl"],
                    "description": ["System operations commands"],
                }
            },
            sudocmdgroup_find=lambda criteria, **kwargs: {
                "result": [
                    {
                        "cn": ["system-ops"],
                        "member_sudocmd": ["/usr/bin/systemctl"],
                        "description": ["System operations commands"],
                    }
                ],
                "count": 1,
            },
        ),
    )

    fake_errors = types.SimpleNamespace(
        NotFound=fake_not_found,
        AuthorizationError=fake_auth_error,
    )

    fake_ipalib = types.ModuleType("ipalib")
    fake_ipalib.api = fake_api
    fake_ipalib.errors = fake_errors

    fake_install = types.ModuleType("ipalib.install")
    fake_install_kinit = types.ModuleType("ipalib.install.kinit")
    fake_install_kinit.kinit_password = (
        lambda principal, password, ccache_path: None
    )
    fake_ipalib_kinit = types.ModuleType("ipalib.kinit")
    fake_ipalib_kinit.kinit_password = (
        lambda principal, password, ccache_path: None
    )

    with mock.patch.dict(
        sys.modules,
        {
            "ipalib": fake_ipalib,
            "ipalib.errors": fake_errors,
            "ipalib.install": fake_install,
            "ipalib.install.kinit": fake_install_kinit,
            "ipalib.kinit": fake_ipalib_kinit,
        },
        clear=False,
    ):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module, fake_errors


class SudoLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod, cls.fake_errors = _load_sudo_module()

    def _make_lookup(self, options):
        lookup = self.mod.LookupModule()
        defaults = {
            "operation": "show",
            "sudo_object": "rule",
            "result_format": "record",
            "ipaadmin_principal": "admin",
            "criteria": None,
        }

        def set_options(var_options=None, direct=None):
            if var_options:
                options.update(var_options)
            if direct:
                options.update(direct)

        lookup.set_options = set_options
        lookup.get_option = lambda key: options.get(key, defaults.get(key))
        lookup._ensure_ipalib = lambda: None
        lookup._resolve_verify = lambda verify: verify or "/etc/ipa/ca.crt"
        lookup._connect = lambda *args, **kwargs: None
        lookup._cleanup_ccache = lambda: None
        return lookup

    def test_show_rule_returns_expected_fields(self):
        lookup = self._make_lookup({
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        })

        result = lookup.run(["ops-maintenance"], variables={})

        self.assertEqual(len(result), 1)
        rec = result[0]
        self.assertEqual(rec["name"], "ops-maintenance")
        self.assertEqual(rec["object_type"], "rule")
        self.assertTrue(rec["exists"])
        self.assertTrue(rec["enabled"])
        self.assertEqual(rec["users"], ["svc-deploy"])
        self.assertEqual(rec["groups"], ["ops"])
        self.assertEqual(rec["allow_sudocmds"], ["/usr/bin/systemctl"])
        self.assertEqual(rec["runasusers"], ["root"])
        self.assertEqual(rec["order"], 10)

    def test_rule_record_without_enabled_flag_returns_record(self):
        lookup = self._make_lookup({})
        rec = lookup._rule_record("legacy-rule", {"cn": ["legacy-rule"]})

        self.assertEqual(rec["name"], "legacy-rule")
        self.assertEqual(rec["object_type"], "rule")
        self.assertTrue(rec["exists"])
        self.assertIsNone(rec["enabled"])

    def test_show_missing_rule_returns_exists_false(self):
        lookup = self._make_lookup({
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        })
        not_found = self.fake_errors.NotFound
        original = self.mod._ipa_api.Command.sudorule_show

        def raising_show(name, **kwargs):
            raise not_found("not found")

        self.mod._ipa_api.Command.sudorule_show = raising_show
        try:
            result = lookup.run(["missing-rule"], variables={})
        finally:
            self.mod._ipa_api.Command.sudorule_show = original

        rec = result[0]
        self.assertFalse(rec["exists"])
        self.assertIsNone(rec["enabled"])
        self.assertEqual(rec["allow_sudocmds"], [])

    def test_find_rules_and_map_record(self):
        lookup = self._make_lookup({
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "find",
            "sudo_object": "rule",
            "result_format": "map_record",
        })

        result = lookup.run([], variables={})

        rec_map = result[0]
        self.assertIn("ops-maintenance", rec_map)
        self.assertIn("breakglass", rec_map)
        self.assertFalse(rec_map["breakglass"]["enabled"])
        self.assertEqual(rec_map["breakglass"]["usercategory"], "all")

    def test_show_command(self):
        lookup = self._make_lookup({
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "sudo_object": "command",
        })

        result = lookup.run(["/usr/bin/systemctl"], variables={})

        rec = result[0]
        self.assertEqual(rec["object_type"], "command")
        self.assertEqual(rec["name"], "/usr/bin/systemctl")
        self.assertEqual(rec["command"], "/usr/bin/systemctl")
        self.assertEqual(rec["description"], "Command description")

    def test_find_command_groups(self):
        lookup = self._make_lookup({
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "find",
            "sudo_object": "commandgroup",
        })

        result = lookup.run([], variables={})

        self.assertEqual(len(result), 1)
        rec = result[0]
        self.assertEqual(rec["object_type"], "commandgroup")
        self.assertEqual(rec["name"], "system-ops")
        self.assertEqual(rec["commands"], ["/usr/bin/systemctl"])

    def test_unknown_operation_raises(self):
        lookup = self._make_lookup({
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "delete",
        })

        with self.assertRaisesRegex(Exception, "Unknown operation"):
            lookup.run(["ops-maintenance"], variables={})


if __name__ == "__main__":
    unittest.main()
