import importlib.util
import pathlib
import sys
import types
import unittest

from unittest import mock


def _load_principal_module():
    module_name = "eigenstate_ipa_test_principal"
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "plugins" / "lookup" / "principal.py"
    )

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
            )
        ),
        Command=types.SimpleNamespace(
            service_show=lambda principal, **kwargs: {
                "result": {
                    "krbprincipalname": [principal + "@EXAMPLE.COM"],
                    "has_keytab": True,
                }
            },
            host_show=lambda fqdn, **kwargs: {
                "result": {
                    "fqdn": [fqdn],
                    "krbprincipalname": ["host/" + fqdn + "@EXAMPLE.COM"],
                    "has_keytab": False,
                }
            },
            user_show=lambda uid, **kwargs: {
                "result": {
                    "uid": [uid],
                    "krbprincipalname": [uid + "@EXAMPLE.COM"],
                    "has_keytab": True,
                    "nsaccountlock": False,
                    "krblastsuccessfulauth": None,
                }
            },
            service_find=lambda criteria, **kwargs: {
                "result": [
                    {
                        "krbprincipalname": ["HTTP/web01.example.com@EXAMPLE.COM"],
                        "has_keytab": True,
                    },
                    {
                        "krbprincipalname": ["ldap/ldap01.example.com@EXAMPLE.COM"],
                        "has_keytab": False,
                    },
                ],
                "count": 2,
            },
            host_find=lambda criteria, **kwargs: {
                "result": [
                    {
                        "fqdn": ["node01.example.com"],
                        "krbprincipalname": ["host/node01.example.com@EXAMPLE.COM"],
                        "has_keytab": True,
                    },
                ],
                "count": 1,
            },
            user_find=lambda criteria, **kwargs: {
                "result": [
                    {
                        "uid": ["alice"],
                        "krbprincipalname": ["alice@EXAMPLE.COM"],
                        "has_keytab": False,
                        "nsaccountlock": False,
                        "krblastsuccessfulauth": None,
                    },
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
        spec = importlib.util.spec_from_file_location(
            module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module, fake_errors


class PrincipalLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod, cls.fake_errors = _load_principal_module()

    def _make_lookup(self, options, show_principal=None):
        lookup = self.mod.LookupModule()
        defaults = {
            "operation": "show",
            "principal_type": "auto",
            "result_format": "record",
            "ipaadmin_principal": "admin",
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
        if show_principal is not None:
            lookup._show_principal = show_principal
        return lookup

    # ------------------------------------------------------------------
    # show — service principal
    # ------------------------------------------------------------------

    def test_service_principal_exists_with_keytab(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)

        result = lookup.run(["HTTP/web01.example.com"], variables={})

        self.assertEqual(len(result), 1)
        rec = result[0]
        self.assertEqual(rec["name"], "HTTP/web01.example.com")
        self.assertEqual(rec["type"], "service")
        self.assertTrue(rec["exists"])
        self.assertTrue(rec["has_keytab"])
        self.assertIsNone(rec["disabled"])
        self.assertIsNone(rec["last_auth"])

    def test_service_principal_not_found_returns_exists_false(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)
        not_found = self.fake_errors.NotFound

        def raising_service_show(principal, **kwargs):
            raise not_found("not found")

        lookup._show_principal = lambda name, pt: (
            self.mod.LookupModule._show_principal(lookup, name, pt)
        )

        # Patch the module-level ipalib Command for this test
        original_service_show = self.mod._ipa_api.Command.service_show
        self.mod._ipa_api.Command.service_show = raising_service_show
        try:
            result = lookup.run(["HTTP/missing.example.com"], variables={})
        finally:
            self.mod._ipa_api.Command.service_show = original_service_show

        self.assertEqual(len(result), 1)
        rec = result[0]
        self.assertFalse(rec["exists"])
        self.assertFalse(rec["has_keytab"])
        self.assertEqual(rec["type"], "service")

    # ------------------------------------------------------------------
    # show — host principal
    # ------------------------------------------------------------------

    def test_host_principal_exists_no_keytab(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)

        result = lookup.run(["host/node01.example.com"], variables={})

        rec = result[0]
        self.assertEqual(rec["type"], "host")
        self.assertTrue(rec["exists"])
        self.assertFalse(rec["has_keytab"])
        self.assertIn("host/node01.example.com", rec["canonical"])

    def test_host_principal_bare_fqdn_with_override(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "principal_type": "host",
        }
        lookup = self._make_lookup(options)

        result = lookup.run(["node01.example.com"], variables={})

        rec = result[0]
        self.assertEqual(rec["type"], "host")
        self.assertTrue(rec["exists"])

    # ------------------------------------------------------------------
    # show — user principal
    # ------------------------------------------------------------------

    def test_user_principal_exists_with_keytab(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)

        result = lookup.run(["admin"], variables={})

        rec = result[0]
        self.assertEqual(rec["type"], "user")
        self.assertTrue(rec["exists"])
        self.assertTrue(rec["has_keytab"])
        self.assertFalse(rec["disabled"])
        self.assertIsNone(rec["last_auth"])

    def test_user_principal_disabled_state(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)

        original_user_show = self.mod._ipa_api.Command.user_show

        def locked_user_show(uid, **kwargs):
            return {
                "result": {
                    "uid": [uid],
                    "krbprincipalname": [uid + "@EXAMPLE.COM"],
                    "has_keytab": True,
                    "nsaccountlock": True,
                    "krblastsuccessfulauth": None,
                }
            }

        self.mod._ipa_api.Command.user_show = locked_user_show
        try:
            result = lookup.run(["locked-user"], variables={})
        finally:
            self.mod._ipa_api.Command.user_show = original_user_show

        rec = result[0]
        self.assertTrue(rec["disabled"])

    def test_user_principal_last_auth_populated(self):
        import datetime
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)

        ts = datetime.datetime(2026, 1, 15, 14, 23, 0)
        original_user_show = self.mod._ipa_api.Command.user_show

        def ts_user_show(uid, **kwargs):
            return {
                "result": {
                    "uid": [uid],
                    "krbprincipalname": [uid + "@EXAMPLE.COM"],
                    "has_keytab": True,
                    "nsaccountlock": False,
                    "krblastsuccessfulauth": ts,
                }
            }

        self.mod._ipa_api.Command.user_show = ts_user_show
        try:
            result = lookup.run(["admin"], variables={})
        finally:
            self.mod._ipa_api.Command.user_show = original_user_show

        rec = result[0]
        self.assertEqual(rec["last_auth"], ts.isoformat())

    def test_user_principal_not_found_returns_exists_false(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)
        not_found = self.fake_errors.NotFound

        original_user_show = self.mod._ipa_api.Command.user_show
        self.mod._ipa_api.Command.user_show = (
            lambda uid, **kwargs: (_ for _ in ()).throw(not_found("gone"))
        )
        try:
            result = lookup.run(["no-such-user"], variables={})
        finally:
            self.mod._ipa_api.Command.user_show = original_user_show

        rec = result[0]
        self.assertFalse(rec["exists"])
        self.assertEqual(rec["type"], "user")

    # ------------------------------------------------------------------
    # show — multiple terms
    # ------------------------------------------------------------------

    def test_multiple_terms_return_one_record_each(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        records = [
            {"name": "HTTP/web01.example.com", "type": "service",
             "exists": True, "has_keytab": True,
             "canonical": "HTTP/web01.example.com@EXAMPLE.COM",
             "disabled": None, "last_auth": None},
            {"name": "admin", "type": "user",
             "exists": True, "has_keytab": True,
             "canonical": "admin@EXAMPLE.COM",
             "disabled": False, "last_auth": None},
        ]
        call_count = [0]

        def fake_show(name, pt):
            rec = records[call_count[0]]
            call_count[0] += 1
            return rec

        lookup = self._make_lookup(options, show_principal=fake_show)

        result = lookup.run(
            ["HTTP/web01.example.com", "admin"], variables={})

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["type"], "service")
        self.assertEqual(result[1]["type"], "user")

    # ------------------------------------------------------------------
    # result_format — map_record
    # ------------------------------------------------------------------

    def test_map_record_format_keyed_by_name(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "result_format": "map_record",
        }
        lookup = self._make_lookup(options)

        result = lookup.run(["HTTP/web01.example.com"], variables={})

        self.assertIsInstance(result, dict)
        self.assertIn("HTTP/web01.example.com", result)
        self.assertTrue(result["HTTP/web01.example.com"]["exists"])

    # ------------------------------------------------------------------
    # find operation
    # ------------------------------------------------------------------

    def test_find_service_returns_list_of_records(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "find",
            "principal_type": "service",
        }
        lookup = self._make_lookup(options)

        result = lookup.run([], variables={})

        self.assertEqual(len(result), 2)
        for rec in result:
            self.assertEqual(rec["type"], "service")
            self.assertTrue(rec["exists"])

    def test_find_host_returns_list_of_records(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "find",
            "principal_type": "host",
        }
        lookup = self._make_lookup(options)

        result = lookup.run([], variables={})

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "host")
        self.assertIn("node01.example.com", result[0]["canonical"])

    def test_find_user_returns_list_of_records(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "find",
            "principal_type": "user",
        }
        lookup = self._make_lookup(options)

        result = lookup.run([], variables={})

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "user")

    def test_find_with_auto_type_raises_error(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "find",
            "principal_type": "auto",
        }
        lookup = self._make_lookup(options)

        with self.assertRaises(Exception) as ctx:
            lookup.run([], variables={})

        self.assertIn("explicit principal_type", str(ctx.exception))

    # ------------------------------------------------------------------
    # validation errors
    # ------------------------------------------------------------------

    def test_show_with_no_terms_raises_error(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)

        with self.assertRaises(Exception) as ctx:
            lookup.run([], variables={})

        self.assertIn("_terms", str(ctx.exception))

    def test_unknown_operation_raises_error(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "delete",
        }
        lookup = self._make_lookup(options)

        with self.assertRaises(Exception) as ctx:
            lookup.run(["admin"], variables={})

        self.assertIn("delete", str(ctx.exception))

    def test_missing_server_raises_error(self):
        options = {
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "server": None,
        }
        lookup = self._make_lookup(options)

        with self.assertRaises(Exception) as ctx:
            lookup.run(["admin"], variables={})

        self.assertIn("server", str(ctx.exception))

    def test_authorization_error_raises_lookup_error(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)
        auth_error = self.fake_errors.AuthorizationError

        original_service_show = self.mod._ipa_api.Command.service_show
        self.mod._ipa_api.Command.service_show = (
            lambda principal, **kwargs: (_ for _ in ()).throw(
                auth_error("denied"))
        )
        try:
            with self.assertRaises(Exception) as ctx:
                lookup.run(["HTTP/web01.example.com"], variables={})
        finally:
            self.mod._ipa_api.Command.service_show = original_service_show

        self.assertIn("Not authorized", str(ctx.exception))

    # ------------------------------------------------------------------
    # principal type detection
    # ------------------------------------------------------------------

    def test_detect_service_principal(self):
        lookup = self.mod.LookupModule()
        ptype, arg = lookup._detect_principal_type("HTTP/web01.example.com")
        self.assertEqual(ptype, "service")
        self.assertEqual(arg, "HTTP/web01.example.com")

    def test_detect_service_principal_with_realm(self):
        lookup = self.mod.LookupModule()
        ptype, arg = lookup._detect_principal_type(
            "HTTP/web01.example.com@EXAMPLE.COM")
        self.assertEqual(ptype, "service")
        self.assertEqual(arg, "HTTP/web01.example.com")

    def test_detect_host_principal(self):
        lookup = self.mod.LookupModule()
        ptype, arg = lookup._detect_principal_type("host/node01.example.com")
        self.assertEqual(ptype, "host")
        self.assertEqual(arg, "node01.example.com")

    def test_detect_host_principal_with_realm(self):
        lookup = self.mod.LookupModule()
        ptype, arg = lookup._detect_principal_type(
            "host/node01.example.com@EXAMPLE.COM")
        self.assertEqual(ptype, "host")
        self.assertEqual(arg, "node01.example.com")

    def test_detect_user_principal(self):
        lookup = self.mod.LookupModule()
        ptype, arg = lookup._detect_principal_type("admin")
        self.assertEqual(ptype, "user")
        self.assertEqual(arg, "admin")

    def test_detect_user_principal_with_realm(self):
        lookup = self.mod.LookupModule()
        ptype, arg = lookup._detect_principal_type("admin@EXAMPLE.COM")
        self.assertEqual(ptype, "user")
        self.assertEqual(arg, "admin")


if __name__ == "__main__":
    unittest.main()
