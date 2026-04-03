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


class InventoryPluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_inventory_module()

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
        with tempfile.NamedTemporaryFile() as ccache_file:
            original = os.environ.get("KRB5CCNAME")
            os.environ["KRB5CCNAME"] = "FILE:/tmp/original-inventory-cache"
            try:
                inventory._activate_ccache(
                    ccache_file.name,
                    "FILE:%s" % ccache_file.name,
                )
                self.assertEqual(
                    os.environ.get("KRB5CCNAME"),
                    "FILE:%s" % ccache_file.name,
                )
                inventory._cleanup_ccache()
                self.assertEqual(
                    os.environ.get("KRB5CCNAME"),
                    "FILE:/tmp/original-inventory-cache",
                )
                self.assertFalse(os.path.exists(ccache_file.name))
            finally:
                if original is None:
                    os.environ.pop("KRB5CCNAME", None)
                else:
                    os.environ["KRB5CCNAME"] = original

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


if __name__ == "__main__":
    unittest.main()
