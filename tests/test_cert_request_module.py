import importlib.util
import pathlib
import sys
import tempfile
import types
import unittest

from unittest import mock

from tests.test_vault_write import _fake_ipalib, _load_ipa_client


COLLECTION_ROOT = pathlib.Path(__file__).resolve().parents[1]
SAMPLE_CERT = {
    "certificate": "MIIBexamplecertificatebytes",
    "subject": "CN=app.example.com,O=EXAMPLE.COM",
    "issuer": "CN=Certificate Authority,O=EXAMPLE.COM",
    "serial_number": 42,
    "valid_not_before": "2026-05-05 00:00:00",
    "valid_not_after": "2027-05-05 00:00:00",
    "san_dnsname": ["app.example.com"],
}
SAMPLE_CSR = (
    "-----BEGIN CERTIFICATE REQUEST-----\n"
    "MIIBexamplecsr\n"
    "-----END CERTIFICATE REQUEST-----\n"
)


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

    path = COLLECTION_ROOT / "plugins" / "modules" / "cert_request.py"
    with mock.patch.dict(sys.modules, patches, clear=False):
        spec = importlib.util.spec_from_file_location(
            "eigenstate_ipa_test_cert_request", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
    return mod


def _params(**overrides):
    defaults = dict(
        principal="HTTP/app.example.com@EXAMPLE.COM",
        csr=SAMPLE_CSR,
        csr_file=None,
        destination=None,
        mode="0644",
        owner=None,
        group=None,
        return_content=False,
        encoding="pem",
        profile=None,
        ca=None,
        add=False,
        server="idm-01.example.com",
        ipaadmin_principal="admin",
        ipaadmin_password="secret",
        kerberos_keytab=None,
        verify="/etc/ipa/ca.crt",
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


class CertRequestModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()
        cls.mod.HAS_IPALIB = True

    def _run(self, params, check_mode=False):
        module = _module_mock(params, check_mode=check_mode)
        client = mock.MagicMock()
        client.api = mock.MagicMock()

        with mock.patch.object(self.mod, "AnsibleModule", return_value=module), \
                mock.patch.object(self.mod, "IPAClient", return_value=client), \
                mock.patch.object(self.mod, "_request_cert",
                                  return_value=dict(SAMPLE_CERT)):
            try:
                self.mod.run_module()
            except SystemExit:
                pass
        return module._captured

    def test_returns_metadata_without_content_by_default(self):
        result = self._run(_params())
        self.assertEqual(result["changed"], True)
        self.assertNotIn("content", result)
        self.assertEqual(result["metadata"]["serial_number"], 42)
        self.assertEqual(result["metadata"]["san"], ["app.example.com"])

    def test_return_content_is_explicit(self):
        result = self._run(_params(return_content=True))
        self.assertIn("content", result)
        self.assertTrue(result["content"].startswith("-----BEGIN CERTIFICATE-----"))
        self.assertEqual(result["encoding"], "pem")

    def test_writes_destination(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dest = pathlib.Path(tmpdir) / "app.pem"
            result = self._run(_params(destination=str(dest)))
            self.assertEqual(result["changed"], True)
            self.assertTrue(dest.read_text().startswith("-----BEGIN CERTIFICATE-----"))

    def test_reads_csr_file(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as fh:
            fh.write(SAMPLE_CSR)
            csr_path = fh.name
        try:
            result = self._run(_params(csr=None, csr_file=csr_path))
            self.assertEqual(result["changed"], True)
        finally:
            pathlib.Path(csr_path).unlink(missing_ok=True)

    def test_check_mode_is_metadata_only(self):
        result = self._run(_params(return_content=True), check_mode=True)
        self.assertEqual(result["changed"], True)
        self.assertEqual(result["metadata"], {})
        self.assertNotIn("content", result)


if __name__ == "__main__":
    unittest.main()
