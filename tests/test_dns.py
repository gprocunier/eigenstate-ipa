import importlib.util
import importlib.abc
import pathlib
import sys
import types
import unittest

from unittest import mock


def _load_dns_module():
    module_name = "eigenstate_ipa_test_dns"
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "plugins" / "lookup" / "dns.py"
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
            dnsrecord_show=lambda zone, name, **kwargs: {
                "result": {
                    "idnsname": [name],
                    "arecord": ["172.16.0.10"],
                    "sshfprecord": ["1 1 DEADBEEF"],
                    "dnsttl": [1200],
                    "objectclass": ["top", "idnsrecord"],
                }
            },
            dnszone_show=lambda zone, **kwargs: {
                "result": {
                    "idnsname": ["workshop.lan."],
                    "objectclass": ["top", "idnsrecord", "idnszone"],
                }
            },
            dnsrecord_find=lambda zone, criteria, **kwargs: {
                "result": [
                    {
                        "idnsname": ["@"],
                        "nsrecord": ["idm-01.workshop.lan."],
                        "idnszoneactive": ["TRUE"],
                        "idnsallowdynupdate": ["TRUE"],
                        "idnssoamname": ["idm-01.workshop.lan."],
                        "idnssoarname": ["hostmaster.workshop.lan."],
                        "idnssoaserial": [1775586710],
                        "idnsupdatepolicy": ["grant WORKSHOP.LAN krb5-self * A;"],
                        "objectclass": ["top", "idnsrecord", "idnszone"],
                    },
                    {
                        "idnsname": ["idm-01"],
                        "arecord": ["172.16.0.10"],
                        "sshfprecord": ["1 1 DEADBEEF"],
                        "dnsttl": [1200],
                        "objectclass": ["top", "idnsrecord"],
                    },
                    {
                        "idnsname": ["30"],
                        "ptrrecord": ["bastion-01.workshop.lan."],
                        "objectclass": ["top", "idnsrecord"],
                    },
                ],
                "count": 3,
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


class DnsLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod, cls.fake_errors = _load_dns_module()

    def _make_lookup(self, options):
        lookup = self.mod.LookupModule()
        defaults = {
            "operation": "show",
            "result_format": "record",
            "ipaadmin_principal": "admin",
            "criteria": None,
            "record_type": None,
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

    def test_show_record_returns_expected_fields(self):
        lookup = self._make_lookup({
            "server": "idm-01.example.com",
            "zone": "workshop.lan",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        })

        result = lookup.run(["idm-01"], variables={})

        self.assertEqual(len(result), 1)
        rec = result[0]
        self.assertEqual(rec["name"], "idm-01")
        self.assertEqual(rec["zone"], "workshop.lan")
        self.assertEqual(rec["fqdn"], "idm-01.workshop.lan")
        self.assertTrue(rec["exists"])
        self.assertEqual(rec["ttl"], 1200)
        self.assertEqual(rec["records"]["arecord"], ["172.16.0.10"])
        self.assertEqual(rec["record_types"], ["arecord", "sshfprecord"])

    def test_show_missing_record_returns_exists_false(self):
        lookup = self._make_lookup({
            "server": "idm-01.example.com",
            "zone": "workshop.lan",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        })
        not_found = self.fake_errors.NotFound
        original = self.mod._ipa_api.Command.dnsrecord_show

        def raising_show(zone, name, **kwargs):
            raise not_found("not found")

        self.mod._ipa_api.Command.dnsrecord_show = raising_show
        try:
            result = lookup.run(["missing-host"], variables={})
        finally:
            self.mod._ipa_api.Command.dnsrecord_show = original

        self.assertEqual(result[0]["name"], "missing-host")
        self.assertFalse(result[0]["exists"])
        self.assertEqual(result[0]["records"], {})
        self.assertEqual(result[0]["template_records"], {})

    def test_show_zone_apex_returns_zone_marker(self):
        lookup = self._make_lookup({
            "server": "idm-01.example.com",
            "zone": "workshop.lan",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        })

        result = lookup.run(["@"], variables={})

        self.assertTrue(result[0]["exists"])
        self.assertTrue(result[0]["is_zone_apex"])
        self.assertIn("idnszone", result[0]["object_classes"])

    def test_find_with_record_type_filter_returns_only_matching_records(self):
        lookup = self._make_lookup({
            "server": "idm-01.example.com",
            "zone": "workshop.lan",
            "operation": "find",
            "record_type": "arecord",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        })

        result = lookup.run([], variables={})

        self.assertEqual(len(result), 1)
        rec = result[0]
        self.assertEqual(rec["name"], "idm-01")
        self.assertEqual(rec["records"]["arecord"], ["172.16.0.10"])

    def test_find_map_record_keys_by_name(self):
        lookup = self._make_lookup({
            "server": "idm-01.example.com",
            "zone": "workshop.lan",
            "operation": "find",
            "result_format": "map_record",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        })

        result = lookup.run([], variables={})

        self.assertIn("@", result[0])
        self.assertIn("idm-01", result[0])
        self.assertTrue(result[0]["@"]["is_zone_apex"])
        self.assertIn("idnszone", result[0]["@"]["object_classes"])

    def test_unknown_operation_raises(self):
        lookup = self._make_lookup({
            "server": "idm-01.example.com",
            "zone": "workshop.lan",
            "operation": "explode",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        })

        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup.run(["idm-01"], variables={})

    def test_missing_ipalib_reports_requirement_without_cleanup_nameerror(self):
        class BlockIpalib(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if fullname == "ipalib" or fullname.startswith("ipalib."):
                    raise ImportError("blocked ipalib for test")
                return None

        module_name = "eigenstate_ipa_test_dns_no_ipalib"
        module_path = (
            pathlib.Path(__file__).resolve().parents[1]
            / "plugins" / "lookup" / "dns.py"
        )
        saved_ipalib = {
            name: module
            for name, module in list(sys.modules.items())
            if name == "ipalib" or name.startswith("ipalib.")
        }
        for name in saved_ipalib:
            sys.modules.pop(name, None)

        blocker = BlockIpalib()
        sys.meta_path.insert(0, blocker)
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            assert spec.loader is not None
            spec.loader.exec_module(module)

            lookup = module.LookupModule()
            options = {
                "server": "idm-01.example.com",
                "zone": "workshop.lan",
                "ipaadmin_password": "secret",
                "verify": "/etc/ipa/ca.crt",
            }
            defaults = {
                "operation": "show",
                "result_format": "record",
                "ipaadmin_principal": "admin",
                "criteria": None,
                "record_type": None,
            }

            def set_options(var_options=None, direct=None):
                if var_options:
                    options.update(var_options)
                if direct:
                    options.update(direct)

            lookup.set_options = set_options
            lookup.get_option = lambda key: options.get(key, defaults.get(key))

            with self.assertRaises(module.AnsibleLookupError) as ctx:
                lookup.run(["idm-01"], variables={})

            self.assertIn("ipalib", str(ctx.exception))
            self.assertNotIn("_ipa_api", str(ctx.exception))
        finally:
            if blocker in sys.meta_path:
                sys.meta_path.remove(blocker)
            sys.modules.pop(module_name, None)
            for name in list(sys.modules):
                if name == "ipalib" or name.startswith("ipalib."):
                    sys.modules.pop(name, None)
            sys.modules.update(saved_ipalib)


if __name__ == "__main__":
    unittest.main()
