import importlib.util
import pathlib
import sys
import types
import unittest

from unittest import mock


def _load_hbacrule_module():
    module_name = "eigenstate_ipa_test_hbacrule"
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "plugins" / "lookup" / "hbacrule.py"
    )

    # Pre-import ansible so mock.patch.dict preserves it across the context
    # manager exit (rather than removing it, which breaks re-import on Py 3.14).
    import ansible.errors  # noqa: F401
    import ansible.plugins.lookup  # noqa: F401
    import ansible.utils.display  # noqa: F401
    import ansible.module_utils.common.text.converters  # noqa: F401

    fake_not_found = type("NotFound", (Exception,), {})
    fake_auth_error = type("AuthorizationError", (Exception,), {})

    def _default_rule_result(name):
        return {
            "result": {
                "cn": [name],
                "ipaenabledflag": ["TRUE"],
                "usercategory": None,
                "hostcategory": None,
                "servicecategory": None,
                "memberuser_user": ["automation-svc"],
                "memberuser_group": ["ops-deploy"],
                "memberhost_host": ["app01.example.com"],
                "memberhost_hostgroup": ["app-servers"],
                "memberservice_hbacsvc": ["sshd"],
                "memberservice_hbacsvcgroup": [],
                "description": ["Ops deploy access rule"],
            }
        }

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
            hbacrule_show=lambda name, **kwargs: _default_rule_result(name),
            hbacrule_find=lambda criteria, **kwargs: {
                "result": [
                    {
                        "cn": ["ops-deploy"],
                        "ipaenabledflag": ["TRUE"],
                        "usercategory": None,
                        "hostcategory": None,
                        "servicecategory": None,
                        "memberuser_user": ["automation-svc"],
                        "memberuser_group": [],
                        "memberhost_host": [],
                        "memberhost_hostgroup": ["app-servers"],
                        "memberservice_hbacsvc": ["sshd"],
                        "memberservice_hbacsvcgroup": [],
                        "description": None,
                    },
                    {
                        "cn": ["allow_all"],
                        "ipaenabledflag": ["TRUE"],
                        "usercategory": ["all"],
                        "hostcategory": ["all"],
                        "servicecategory": ["all"],
                        "memberuser_user": [],
                        "memberuser_group": [],
                        "memberhost_host": [],
                        "memberhost_hostgroup": [],
                        "memberservice_hbacsvc": [],
                        "memberservice_hbacsvcgroup": [],
                        "description": ["Allow all access"],
                    },
                ],
                "count": 2,
            },
            hbactest=lambda user, targethost, service, **kwargs: {
                "result": {
                    "matched": ["ops-deploy"],
                    "notmatched": ["ops-patch"],
                    "error": [],
                    "value": True,
                }
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
        spec = importlib.util.spec_from_file_location(
            module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module, fake_errors


class HBACRuleLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod, cls.fake_errors = _load_hbacrule_module()

    def _make_lookup(self, options):
        lookup = self.mod.LookupModule()
        defaults = {
            "operation": "show",
            "result_format": "record",
            "ipaadmin_principal": "admin",
            "criteria": None,
            "targethost": None,
            "service": None,
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

    # ------------------------------------------------------------------
    # show — basic record structure
    # ------------------------------------------------------------------

    def test_show_returns_record_with_expected_fields(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)

        result = lookup.run(["ops-deploy"], variables={})

        self.assertEqual(len(result), 1)
        rec = result[0]
        self.assertEqual(rec["name"], "ops-deploy")
        self.assertTrue(rec["exists"])
        self.assertTrue(rec["enabled"])
        self.assertIsNone(rec["usercategory"])
        self.assertIsNone(rec["hostcategory"])
        self.assertIsNone(rec["servicecategory"])
        self.assertIn("automation-svc", rec["users"])
        self.assertIn("ops-deploy", rec["groups"])
        self.assertIn("app01.example.com", rec["hosts"])
        self.assertIn("app-servers", rec["hostgroups"])
        self.assertIn("sshd", rec["services"])
        self.assertEqual(rec["servicegroups"], [])
        self.assertEqual(rec["description"], "Ops deploy access rule")

    def test_show_not_found_returns_exists_false(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)
        not_found = self.fake_errors.NotFound

        original = self.mod._ipa_api.Command.hbacrule_show

        def raising_show(name, **kwargs):
            raise not_found("not found")

        self.mod._ipa_api.Command.hbacrule_show = raising_show
        try:
            result = lookup.run(["missing-rule"], variables={})
        finally:
            self.mod._ipa_api.Command.hbacrule_show = original

        rec = result[0]
        self.assertFalse(rec["exists"])
        self.assertEqual(rec["name"], "missing-rule")
        self.assertIsNone(rec["enabled"])
        self.assertEqual(rec["users"], [])
        self.assertEqual(rec["services"], [])

    # ------------------------------------------------------------------
    # show — all-category rule
    # ------------------------------------------------------------------

    def test_show_allow_all_categories(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)
        original = self.mod._ipa_api.Command.hbacrule_show

        def all_cats_show(name, **kwargs):
            return {
                "result": {
                    "cn": [name],
                    "ipaenabledflag": ["TRUE"],
                    "usercategory": ["all"],
                    "hostcategory": ["all"],
                    "servicecategory": ["all"],
                    "memberuser_user": [],
                    "memberuser_group": [],
                    "memberhost_host": [],
                    "memberhost_hostgroup": [],
                    "memberservice_hbacsvc": [],
                    "memberservice_hbacsvcgroup": [],
                    "description": None,
                }
            }

        self.mod._ipa_api.Command.hbacrule_show = all_cats_show
        try:
            result = lookup.run(["allow_all"], variables={})
        finally:
            self.mod._ipa_api.Command.hbacrule_show = original

        rec = result[0]
        self.assertEqual(rec["usercategory"], "all")
        self.assertEqual(rec["hostcategory"], "all")
        self.assertEqual(rec["servicecategory"], "all")

    # ------------------------------------------------------------------
    # show — multiple terms
    # ------------------------------------------------------------------

    def test_show_multiple_terms_returns_multiple_records(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)

        result = lookup.run(["ops-deploy", "ops-patch"], variables={})

        self.assertEqual(len(result), 2)

    # ------------------------------------------------------------------
    # find operation
    # ------------------------------------------------------------------

    def test_find_returns_all_rules(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "find",
        }
        lookup = self._make_lookup(options)

        result = lookup.run([], variables={})

        self.assertEqual(len(result), 2)
        names = [r["name"] for r in result]
        self.assertIn("ops-deploy", names)
        self.assertIn("allow_all", names)

    def test_find_allow_all_has_categories(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "find",
        }
        lookup = self._make_lookup(options)

        result = lookup.run([], variables={})

        allow_all = next(r for r in result if r["name"] == "allow_all")
        self.assertEqual(allow_all["usercategory"], "all")
        self.assertEqual(allow_all["servicecategory"], "all")

    # ------------------------------------------------------------------
    # result_format=map_record
    # ------------------------------------------------------------------

    def test_map_record_format_keys_by_name(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "find",
            "result_format": "map_record",
        }
        lookup = self._make_lookup(options)

        result = lookup.run([], variables={})

        self.assertEqual(len(result), 1)
        keyed = result[0]
        self.assertIn("ops-deploy", keyed)
        self.assertIn("allow_all", keyed)
        self.assertIn("sshd", keyed["ops-deploy"]["services"])

    # ------------------------------------------------------------------
    # test operation — access granted
    # ------------------------------------------------------------------

    def test_test_access_granted(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "test",
            "targethost": "app01.example.com",
            "service": "sshd",
        }
        lookup = self._make_lookup(options)

        result = lookup.run(["automation-svc"], variables={})

        self.assertEqual(len(result), 1)
        rec = result[0]
        self.assertEqual(rec["user"], "automation-svc")
        self.assertEqual(rec["targethost"], "app01.example.com")
        self.assertEqual(rec["service"], "sshd")
        self.assertFalse(rec["denied"])
        self.assertIn("ops-deploy", rec["matched"])
        self.assertIn("ops-patch", rec["notmatched"])

    def test_test_access_granted_top_level_result(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "test",
            "targethost": "app01.example.com",
            "service": "sshd",
        }
        lookup = self._make_lookup(options)
        original = self.mod._ipa_api.Command.hbactest

        def top_level_hbactest(user, targethost, service, **kwargs):
            return {
                "matched": ["ops-deploy"],
                "notmatched": ["ops-patch"],
                "error": [],
                "value": True,
            }

        self.mod._ipa_api.Command.hbactest = top_level_hbactest
        try:
            result = lookup.run(["automation-svc"], variables={})
        finally:
            self.mod._ipa_api.Command.hbactest = original

        rec = result[0]
        self.assertFalse(rec["denied"])
        self.assertIn("ops-deploy", rec["matched"])
        self.assertIn("ops-patch", rec["notmatched"])

    def test_test_access_denied(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "test",
            "targethost": "restricted-host.example.com",
            "service": "sshd",
        }
        lookup = self._make_lookup(options)
        original = self.mod._ipa_api.Command.hbactest

        def denied_hbactest(user, targethost, service, **kwargs):
            return {
                "result": {
                    "matched": [],
                    "notmatched": ["ops-deploy", "allow_all"],
                    "error": [],
                    "value": False,
                }
            }

        self.mod._ipa_api.Command.hbactest = denied_hbactest
        try:
            result = lookup.run(["restricted-svc"], variables={})
        finally:
            self.mod._ipa_api.Command.hbactest = original

        rec = result[0]
        self.assertTrue(rec["denied"])
        self.assertEqual(rec["matched"], [])
        self.assertIn("ops-deploy", rec["notmatched"])

    # ------------------------------------------------------------------
    # test operation — validation errors
    # ------------------------------------------------------------------

    def test_test_missing_targethost_raises(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "test",
            "targethost": None,
            "service": "sshd",
        }
        lookup = self._make_lookup(options)

        with self.assertRaises(Exception):
            lookup.run(["automation-svc"], variables={})

    def test_test_missing_service_raises(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "test",
            "targethost": "app01.example.com",
            "service": None,
        }
        lookup = self._make_lookup(options)

        with self.assertRaises(Exception):
            lookup.run(["automation-svc"], variables={})

    def test_test_missing_user_raises(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "test",
            "targethost": "app01.example.com",
            "service": "sshd",
        }
        lookup = self._make_lookup(options)

        with self.assertRaises(Exception):
            lookup.run([], variables={})

    # ------------------------------------------------------------------
    # error: missing server
    # ------------------------------------------------------------------

    def test_missing_server_raises(self):
        options = {
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "server": None,
        }
        lookup = self._make_lookup(options)

        with self.assertRaises(Exception):
            lookup.run(["any-rule"], variables={})

    # ------------------------------------------------------------------
    # error: unknown operation
    # ------------------------------------------------------------------

    def test_unknown_operation_raises(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "delete",
        }
        lookup = self._make_lookup(options)

        with self.assertRaises(Exception):
            lookup.run(["ops-deploy"], variables={})

    # ------------------------------------------------------------------
    # test operation — NotFound from hbactest
    # ------------------------------------------------------------------

    def test_test_not_found_raises_lookup_error(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "test",
            "targethost": "ghost-host.example.com",
            "service": "sshd",
        }
        lookup = self._make_lookup(options)
        not_found = self.fake_errors.NotFound
        original = self.mod._ipa_api.Command.hbactest

        def not_found_hbactest(user, targethost, service, **kwargs):
            raise not_found("host not found")

        self.mod._ipa_api.Command.hbactest = not_found_hbactest
        try:
            with self.assertRaises(Exception):
                lookup.run(["automation-svc"], variables={})
        finally:
            self.mod._ipa_api.Command.hbactest = original


if __name__ == "__main__":
    unittest.main()
