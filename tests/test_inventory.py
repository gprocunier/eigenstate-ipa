import importlib.util
import os
import pathlib
import sys
import tempfile
import types
import unittest

from unittest import mock


def _load_inventory_module():
    module_name = "eigenstate_ipa_test_inventory"
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "plugins"
        / "inventory"
        / "idm.py"
    )

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeInventory:
    def __init__(self):
        self.hosts = {}

    def add_host(self, name, group=None):
        self.hosts.setdefault(name, {"groups": set(), "vars": {}})
        if group is not None:
            self.hosts[name]["groups"].add(group)

    def set_variable(self, name, key, value):
        self.hosts.setdefault(name, {"groups": set(), "vars": {}})
        self.hosts[name]["vars"][key] = value


class InventoryPluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_inventory_module()

    def _inventory_with_options(self, **options):
        inventory = self.mod.InventoryModule()
        inventory.inventory = FakeInventory()
        defaults = {
            "hostvars_enabled": True,
            "hostvars_include": [],
        }
        defaults.update(options)
        inventory.get_option = lambda name: defaults[name]
        return inventory

    def test_inventory_prefers_usr_bin_kinit(self):
        inventory = self.mod.InventoryModule()
        with mock.patch.object(self.mod.os.path, 'exists', side_effect=lambda path: path == '/usr/bin/kinit'):
            with mock.patch.object(self.mod.shutil, 'which', return_value='/custom/bin/kinit'):
                self.assertEqual(inventory._resolve_kinit_command(), '/usr/bin/kinit')

    def test_inventory_falls_back_to_path_kinit(self):
        inventory = self.mod.InventoryModule()
        with mock.patch.object(self.mod.os.path, 'exists', return_value=False):
            with mock.patch.object(self.mod.shutil, 'which', return_value='/custom/bin/kinit'):
                self.assertEqual(inventory._resolve_kinit_command(), '/custom/bin/kinit')

    def test_inventory_formats_subprocess_stderr(self):
        inventory = self.mod.InventoryModule()
        rendered = inventory._format_subprocess_stderr(('line one is quite long ' * 5) + '\nline two', limit=40)
        self.assertTrue(rendered.startswith('line one is quite long'))
        self.assertTrue(rendered.endswith('...'))
        self.assertLessEqual(len(rendered), 40)

    def test_resolve_verify_uses_explicit_path(self):
        inventory = self.mod.InventoryModule()
        with mock.patch.object(self.mod.os.path, "exists", return_value=True):
            self.assertEqual(
                inventory._resolve_verify("/etc/ipa/custom-ca.crt"),
                "/etc/ipa/custom-ca.crt",
            )

    def test_resolve_verify_rejects_missing_explicit_path(self):
        inventory = self.mod.InventoryModule()
        with mock.patch.object(self.mod.os.path, "exists", return_value=False):
            with self.assertRaises(self.mod.AnsibleParserError):
                inventory._resolve_verify("/etc/ipa/missing-ca.crt")

    def test_resolve_verify_auto_detects_default_ca(self):
        inventory = self.mod.InventoryModule()
        with mock.patch.object(
            self.mod.os.path,
            "exists",
            side_effect=lambda path: path == "/etc/ipa/ca.crt",
        ):
            with mock.patch.object(self.mod.display, "warning") as warning:
                self.assertEqual(
                    inventory._resolve_verify(None),
                    "/etc/ipa/ca.crt",
                )
        warning.assert_not_called()

    def test_resolve_verify_warns_before_disabling_tls(self):
        inventory = self.mod.InventoryModule()
        fake_urllib3 = types.SimpleNamespace(
            disable_warnings=mock.Mock(),
            exceptions=types.SimpleNamespace(InsecureRequestWarning=object),
        )
        with mock.patch.object(self.mod.os.path, "exists", return_value=False):
            with mock.patch.object(self.mod.display, "warning") as warning:
                with mock.patch.object(self.mod, "urllib3", fake_urllib3):
                    self.assertFalse(inventory._resolve_verify(None))
        warning.assert_called_once()
        fake_urllib3.disable_warnings.assert_called_once()

    def test_activate_and_cleanup_ccache_restores_environment(self):
        inventory = self.mod.InventoryModule()
        ccache_path = None
        with tempfile.NamedTemporaryFile(delete=False) as ccache_file:
            ccache_path = ccache_file.name
            original = os.environ.get("KRB5CCNAME")
            os.environ["KRB5CCNAME"] = "FILE:/tmp/original-inventory-cache"
            try:
                inventory._activate_ccache(
                    ccache_path,
                    "FILE:%s" % ccache_path,
                )
                self.assertEqual(
                    os.environ.get("KRB5CCNAME"),
                    "FILE:%s" % ccache_path,
                )
                inventory._cleanup_ccache()
                self.assertEqual(
                    os.environ.get("KRB5CCNAME"),
                    "FILE:/tmp/original-inventory-cache",
                )
                self.assertFalse(os.path.exists(ccache_path))
            finally:
                if original is None:
                    os.environ.pop("KRB5CCNAME", None)
                else:
                    os.environ["KRB5CCNAME"] = original
                if ccache_path and os.path.exists(ccache_path):
                    os.unlink(ccache_path)

    def test_warns_when_keytab_permissions_are_too_permissive(self):
        inventory = self.mod.InventoryModule()
        with tempfile.NamedTemporaryFile() as keytab_file:
            os.chmod(keytab_file.name, 0o640)
            with mock.patch.object(self.mod.display, "warning") as warning:
                inventory._warn_if_sensitive_file_permissive(
                    keytab_file.name,
                    "kerberos_keytab",
                )
        warning.assert_called_once()

    def test_does_not_warn_when_keytab_permissions_are_owner_only(self):
        inventory = self.mod.InventoryModule()
        with tempfile.NamedTemporaryFile() as keytab_file:
            os.chmod(keytab_file.name, 0o600)
            with mock.patch.object(self.mod.display, "warning") as warning:
                inventory._warn_if_sensitive_file_permissive(
                    keytab_file.name,
                    "kerberos_keytab",
                )
        warning.assert_not_called()

    def test_selected_host_attrs_returns_default_curated_set(self):
        inventory = self._inventory_with_options()
        self.assertEqual(inventory._selected_host_attrs(), self.mod._IPA_HOST_ATTRS)

    def test_selected_host_attrs_can_be_disabled(self):
        inventory = self._inventory_with_options(hostvars_enabled=False)
        self.assertEqual(inventory._selected_host_attrs(), {})

    def test_selected_host_attrs_filters_to_allowlist(self):
        inventory = self._inventory_with_options(
            hostvars_include=["idm_location", "idm_hostgroups"],
        )
        self.assertEqual(
            inventory._selected_host_attrs(),
            {
                "nshostlocation": ("idm_location", False),
                "memberof_hostgroup": ("idm_hostgroups", True),
            },
        )

    def test_selected_host_attrs_rejects_unknown_allowlist_values(self):
        inventory = self._inventory_with_options(
            hostvars_include=["idm_location", "idm_not_real"],
        )
        with self.assertRaises(self.mod.AnsibleParserError) as ctx:
            inventory._selected_host_attrs()
        self.assertIn("idm_not_real", str(ctx.exception))

    def test_add_host_exports_curated_hostvars(self):
        inventory = self._inventory_with_options()
        inventory._add_host(
            "web-01.corp.example.com",
            {
                "fqdn": ["web-01.corp.example.com"],
                "nshostlocation": ["DC East"],
                "memberof_hostgroup": ["webservers", "prod"],
                "ipasshpubkey": ["ssh-ed25519 AAAA..."],
            },
        )
        host = inventory.inventory.hosts["web-01.corp.example.com"]
        self.assertEqual(host["vars"]["idm_fqdn"], "web-01.corp.example.com")
        self.assertEqual(host["vars"]["idm_location"], "DC East")
        self.assertEqual(host["vars"]["idm_hostgroups"], ["webservers", "prod"])
        self.assertEqual(host["vars"]["idm_ssh_public_keys"], ["ssh-ed25519 AAAA..."])

    def test_add_host_respects_hostvars_include(self):
        inventory = self._inventory_with_options(
            hostvars_include=["idm_location", "idm_hostgroups"],
        )
        inventory._add_host(
            "web-01.corp.example.com",
            {
                "fqdn": ["web-01.corp.example.com"],
                "nshostlocation": ["DC East"],
                "memberof_hostgroup": ["webservers", "prod"],
            },
        )
        hostvars = inventory.inventory.hosts["web-01.corp.example.com"]["vars"]
        self.assertEqual(
            hostvars,
            {
                "idm_location": "DC East",
                "idm_hostgroups": ["webservers", "prod"],
            },
        )

    def test_add_host_skips_hostvars_when_disabled(self):
        inventory = self._inventory_with_options(hostvars_enabled=False)
        inventory._add_host(
            "web-01.corp.example.com",
            {
                "fqdn": ["web-01.corp.example.com"],
                "nshostlocation": ["DC East"],
            },
        )
        host = inventory.inventory.hosts["web-01.corp.example.com"]
        self.assertEqual(host["vars"], {})


if __name__ == "__main__":
    unittest.main()
