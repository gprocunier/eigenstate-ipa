import base64
import importlib.util
import pathlib
import sys
import tempfile
import types
import unittest

from unittest import mock

from tests.test_vault_write import _fake_ipalib, _load_ipa_client


COLLECTION_ROOT = pathlib.Path(__file__).resolve().parents[1]
FAKE_KEYTAB = b"\x05\x02managed-keytab"


def _load_module():
    _fake_ipalib_mod, _fake_errors, _fake_api, sys_patches = _fake_ipalib()
    ipa_client_mod = _load_ipa_client(sys_patches)

    collection_pkg = types.ModuleType(
        "ansible_collections.eigenstate.ipa.plugins.module_utils.ipa_client")
    collection_pkg.IPAClient = ipa_client_mod.IPAClient
    collection_pkg.IPAClientError = ipa_client_mod.IPAClientError

    patches = dict(sys_patches)
    patches.update({
        "ansible_collections": types.ModuleType("ansible_collections"),
        "ansible_collections.eigenstate": types.ModuleType(
            "ansible_collections.eigenstate"),
        "ansible_collections.eigenstate.ipa": types.ModuleType(
            "ansible_collections.eigenstate.ipa"),
        "ansible_collections.eigenstate.ipa.plugins": types.ModuleType(
            "ansible_collections.eigenstate.ipa.plugins"),
        "ansible_collections.eigenstate.ipa.plugins.module_utils": types.ModuleType(
            "ansible_collections.eigenstate.ipa.plugins.module_utils"),
        "ansible_collections.eigenstate.ipa.plugins.module_utils.ipa_client": (
            collection_pkg),
    })

    path = COLLECTION_ROOT / "plugins" / "modules" / "keytab_manage.py"
    with mock.patch.dict(sys.modules, patches, clear=False):
        spec = importlib.util.spec_from_file_location(
            "eigenstate_ipa_test_keytab_manage", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
    return mod


def _params(**overrides):
    defaults = dict(
        principal="HTTP/app.example.com@EXAMPLE.COM",
        state="retrieved",
        confirm_rotation=False,
        server="idm-01.example.com",
        ipaadmin_principal="admin",
        ipaadmin_password="secret",
        kerberos_keytab=None,
        verify=None,
        enctypes=[],
        destination=None,
        mode="0600",
        owner=None,
        group=None,
        return_content=False,
    )
    defaults.update(overrides)
    return defaults


def _module_mock(params, check_mode=False):
    module = mock.MagicMock()
    module.params = params
    module.check_mode = check_mode
    module.warn = mock.MagicMock()
    captured = {}

    def exit_json(**kwargs):
        captured.update(kwargs)
        raise SystemExit(0)

    def fail_json(**kwargs):
        captured.update(kwargs)
        raise SystemExit(1)

    module.exit_json.side_effect = exit_json
    module.fail_json.side_effect = fail_json
    module._captured = captured
    return module


class KeytabManageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def _run(self, params, check_mode=False):
        module = _module_mock(params, check_mode=check_mode)
        client = mock.MagicMock()
        client.resolve_verify.return_value = "/etc/ipa/ca.crt"

        with mock.patch.object(self.mod, "AnsibleModule", return_value=module), \
                mock.patch.object(self.mod, "IPAClient", return_value=client), \
                mock.patch.object(self.mod, "_ensure_ipa_getkeytab"), \
                mock.patch.object(self.mod, "_retrieve_keytab",
                                  return_value=FAKE_KEYTAB):
            try:
                self.mod.run_module()
            except SystemExit:
                pass
        return module._captured

    def test_rotated_requires_confirmation(self):
        result = self._run(_params(state="rotated"))
        self.assertIn("confirm_rotation=true", result.get("msg", ""))

    def test_does_not_return_content_by_default(self):
        result = self._run(_params())
        self.assertNotIn("content", result)
        self.assertEqual(result["rotation_performed"], False)

    def test_return_content_is_explicit(self):
        result = self._run(_params(return_content=True))
        self.assertEqual(
            result["content"],
            base64.b64encode(FAKE_KEYTAB).decode("ascii"))
        self.assertEqual(result["encoding"], "base64")

    def test_check_mode_rotation_does_not_perform_rotation(self):
        result = self._run(
            _params(state="rotated", confirm_rotation=True),
            check_mode=True)
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["rotation_performed"], False)
        self.assertNotIn("content", result)

    def test_writes_destination(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dest = pathlib.Path(tmpdir) / "service.keytab"
            result = self._run(_params(destination=str(dest)))
            self.assertEqual(result["changed"], True)
            self.assertEqual(dest.read_bytes(), FAKE_KEYTAB)


if __name__ == "__main__":
    unittest.main()
