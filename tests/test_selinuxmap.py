import importlib.util
import pathlib
import sys
import types
import unittest

from unittest import mock


def _load_selinuxmap_module():
    module_name = "eigenstate_ipa_test_selinuxmap"
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "plugins" / "lookup" / "selinuxmap.py"
    )

    # Pre-import ansible so mock.patch.dict preserves it across the context
    # manager exit (rather than removing it, which breaks re-import on Py 3.14).
    import ansible.errors  # noqa: F401
    import ansible.plugins.lookup  # noqa: F401
    import ansible.utils.display  # noqa: F401
    import ansible.module_utils.common.text.converters  # noqa: F401

    fake_not_found = type("NotFound", (Exception,), {})
    fake_auth_error = type("AuthorizationError", (Exception,), {})

    def _default_map_result(name):
        return {
            "result": {
                "cn": [name],
                "ipaselinuxuser": ["staff_u:s0-s0:c0.c1023"],
                "ipaenabledflag": ["TRUE"],
                "usercategory": None,
                "hostcategory": None,
                "seealso": None,
                "memberuser_user": ["alice", "bob"],
                "memberuser_group": ["ops-deploy"],
                "memberhost_host": ["app01.example.com"],
                "memberhost_hostgroup": ["app-servers"],
                "description": ["Ops deploy confinement map"],
            }
        }

    fake_api = types.SimpleNamespace(
        isdone=lambda _state: True,
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
            selinuxusermap_show=lambda name, **kwargs: _default_map_result(name),
            selinuxusermap_find=lambda criteria, **kwargs: {
                "result": [
                    {
                        "cn": ["ops-deploy-map"],
                        "ipaselinuxuser": ["staff_u:s0-s0:c0.c1023"],
                        "ipaenabledflag": ["TRUE"],
                        "usercategory": None,
                        "hostcategory": None,
                        "seealso": None,
                        "memberuser_user": ["alice"],
                        "memberuser_group": [],
                        "memberhost_host": [],
                        "memberhost_hostgroup": ["app-servers"],
                        "description": None,
                    },
                    {
                        "cn": ["ops-patch-map"],
                        "ipaselinuxuser": ["unconfined_u:s0-s0:c0.c1023"],
                        "ipaenabledflag": ["FALSE"],
                        "usercategory": None,
                        "hostcategory": None,
                        "seealso": [
                            "cn=allow-patch,cn=hbac,dc=example,dc=com"
                        ],
                        "memberuser_user": [],
                        "memberuser_group": [],
                        "memberhost_host": [],
                        "memberhost_hostgroup": [],
                        "description": ["Patch window map"],
                    },
                ],
                "count": 2,
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


class SelinuxmapLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod, cls.fake_errors = _load_selinuxmap_module()

    def _make_lookup(self, options):
        lookup = self.mod.LookupModule()
        defaults = {
            "operation": "show",
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

        result = lookup.run(["ops-deploy-map"], variables={})

        self.assertEqual(len(result), 1)
        rec = result[0]
        self.assertEqual(rec["name"], "ops-deploy-map")
        self.assertTrue(rec["exists"])
        self.assertEqual(rec["selinuxuser"], "staff_u:s0-s0:c0.c1023")
        self.assertTrue(rec["enabled"])
        self.assertIsNone(rec["usercategory"])
        self.assertIsNone(rec["hostcategory"])
        self.assertIsNone(rec["hbacrule"])
        self.assertIn("alice", rec["users"])
        self.assertIn("bob", rec["users"])
        self.assertIn("ops-deploy", rec["groups"])
        self.assertIn("app01.example.com", rec["hosts"])
        self.assertIn("app-servers", rec["hostgroups"])
        self.assertEqual(rec["description"], "Ops deploy confinement map")

    def test_show_not_found_returns_exists_false(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)
        not_found = self.fake_errors.NotFound

        original = self.mod._ipa_api.Command.selinuxusermap_show

        def raising_show(name, **kwargs):
            raise not_found("not found")

        self.mod._ipa_api.Command.selinuxusermap_show = raising_show
        try:
            result = lookup.run(["missing-map"], variables={})
        finally:
            self.mod._ipa_api.Command.selinuxusermap_show = original

        rec = result[0]
        self.assertFalse(rec["exists"])
        self.assertEqual(rec["name"], "missing-map")
        self.assertIsNone(rec["selinuxuser"])
        self.assertIsNone(rec["enabled"])
        self.assertEqual(rec["users"], [])
        self.assertEqual(rec["groups"], [])
        self.assertEqual(rec["hosts"], [])
        self.assertEqual(rec["hostgroups"], [])

    # ------------------------------------------------------------------
    # show — disabled map
    # ------------------------------------------------------------------

    def test_show_disabled_map_enabled_is_false(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)
        original = self.mod._ipa_api.Command.selinuxusermap_show

        def disabled_show(name, **kwargs):
            return {
                "result": {
                    "cn": [name],
                    "ipaselinuxuser": ["staff_u:s0-s0:c0.c1023"],
                    "ipaenabledflag": ["FALSE"],
                    "usercategory": None,
                    "hostcategory": None,
                    "seealso": None,
                    "memberuser_user": [],
                    "memberuser_group": [],
                    "memberhost_host": [],
                    "memberhost_hostgroup": [],
                    "description": None,
                }
            }

        self.mod._ipa_api.Command.selinuxusermap_show = disabled_show
        try:
            result = lookup.run(["ops-disabled-map"], variables={})
        finally:
            self.mod._ipa_api.Command.selinuxusermap_show = original

        rec = result[0]
        self.assertFalse(rec["enabled"])

    # ------------------------------------------------------------------
    # show — HBAC-linked scope
    # ------------------------------------------------------------------

    def test_show_hbac_linked_scope_extracts_cn(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)
        original = self.mod._ipa_api.Command.selinuxusermap_show

        def hbac_linked_show(name, **kwargs):
            return {
                "result": {
                    "cn": [name],
                    "ipaselinuxuser": ["staff_u:s0-s0:c0.c1023"],
                    "ipaenabledflag": ["TRUE"],
                    "usercategory": None,
                    "hostcategory": None,
                    "seealso": [
                        "cn=allow_all,cn=hbac,dc=example,dc=com"
                    ],
                    "memberuser_user": [],
                    "memberuser_group": [],
                    "memberhost_host": [],
                    "memberhost_hostgroup": [],
                    "description": None,
                }
            }

        self.mod._ipa_api.Command.selinuxusermap_show = hbac_linked_show
        try:
            result = lookup.run(["ops-hbac-map"], variables={})
        finally:
            self.mod._ipa_api.Command.selinuxusermap_show = original

        rec = result[0]
        self.assertEqual(rec["hbacrule"], "allow_all")
        self.assertEqual(rec["users"], [])

    # ------------------------------------------------------------------
    # show — usercategory=all
    # ------------------------------------------------------------------

    def test_show_usercategory_all(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)
        original = self.mod._ipa_api.Command.selinuxusermap_show

        def all_users_show(name, **kwargs):
            return {
                "result": {
                    "cn": [name],
                    "ipaselinuxuser": ["unconfined_u:s0-s0:c0.c1023"],
                    "ipaenabledflag": ["TRUE"],
                    "usercategory": ["all"],
                    "hostcategory": None,
                    "seealso": None,
                    "memberuser_user": [],
                    "memberuser_group": [],
                    "memberhost_host": [],
                    "memberhost_hostgroup": [],
                    "description": None,
                }
            }

        self.mod._ipa_api.Command.selinuxusermap_show = all_users_show
        try:
            result = lookup.run(["unconfined-map"], variables={})
        finally:
            self.mod._ipa_api.Command.selinuxusermap_show = original

        rec = result[0]
        self.assertEqual(rec["usercategory"], "all")

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

        result = lookup.run(
            ["ops-deploy-map", "ops-patch-map"], variables={})

        self.assertEqual(len(result), 2)
        names = [r["name"] for r in result]
        self.assertIn("ops-deploy-map", names)
        self.assertIn("ops-patch-map", names)

    # ------------------------------------------------------------------
    # find operation
    # ------------------------------------------------------------------

    def test_find_returns_all_maps(self):
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
        self.assertIn("ops-deploy-map", names)
        self.assertIn("ops-patch-map", names)

    def test_find_maps_hbac_linkage_extracted(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "operation": "find",
        }
        lookup = self._make_lookup(options)

        result = lookup.run([], variables={})

        # ops-patch-map has seealso set in the fake find response
        patch_map = next(r for r in result if r["name"] == "ops-patch-map")
        self.assertEqual(patch_map["hbacrule"], "allow-patch")
        self.assertFalse(patch_map["enabled"])
        self.assertEqual(patch_map["description"], "Patch window map")

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
        self.assertIn("ops-deploy-map", keyed)
        self.assertIn("ops-patch-map", keyed)
        self.assertEqual(keyed["ops-deploy-map"]["selinuxuser"],
                         "staff_u:s0-s0:c0.c1023")

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
            lookup.run(["any-map"], variables={})

    # ------------------------------------------------------------------
    # error: show with no terms
    # ------------------------------------------------------------------

    def test_show_no_terms_raises(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
        }
        lookup = self._make_lookup(options)

        with self.assertRaises(Exception):
            lookup.run([], variables={})

    # ------------------------------------------------------------------
    # helpers: _extract_cn_from_dn
    # ------------------------------------------------------------------

    def test_extract_cn_from_dn_standard(self):
        lookup = self.mod.LookupModule()
        dn = "cn=allow_all,cn=hbac,dc=example,dc=com"
        self.assertEqual(lookup._extract_cn_from_dn(dn), "allow_all")

    def test_extract_cn_from_dn_none(self):
        lookup = self.mod.LookupModule()
        self.assertIsNone(lookup._extract_cn_from_dn(None))

    def test_extract_cn_from_dn_bare_string(self):
        lookup = self.mod.LookupModule()
        self.assertEqual(lookup._extract_cn_from_dn("no-equals"), "no-equals")

    # ------------------------------------------------------------------
    # helpers: _unwrap_list
    # ------------------------------------------------------------------

    def test_unwrap_list_none_returns_empty(self):
        lookup = self.mod.LookupModule()
        self.assertEqual(lookup._unwrap_list(None), [])

    def test_unwrap_list_scalar_wraps(self):
        lookup = self.mod.LookupModule()
        self.assertEqual(lookup._unwrap_list("alice"), ["alice"])

    def test_unwrap_list_list_passthrough(self):
        lookup = self.mod.LookupModule()
        self.assertEqual(lookup._unwrap_list(["alice", "bob"]),
                         ["alice", "bob"])


if __name__ == "__main__":
    unittest.main()
