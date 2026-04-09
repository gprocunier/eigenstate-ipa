import base64
import importlib.util
import os
import pathlib
import subprocess
import sys
import tempfile
import types
import unittest

from unittest import mock


def _load_keytab_module():
    module_name = "eigenstate_ipa_test_keytab"
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "plugins" / "lookup" / "keytab.py"
    )

    # keytab.py does not call ipalib.api at all, but it imports
    # ipalib.install.kinit / ipalib.kinit (optional).  Provide stubs so
    # the module loads on a system without python3-ipaclient.
    fake_kinit_password = lambda principal, password, ccache_path: None

    fake_install = types.ModuleType("ipalib.install")
    fake_install_kinit = types.ModuleType("ipalib.install.kinit")
    fake_install_kinit.kinit_password = fake_kinit_password

    fake_ipalib = types.ModuleType("ipalib")
    fake_ipalib_kinit = types.ModuleType("ipalib.kinit")
    fake_ipalib_kinit.kinit_password = fake_kinit_password

    with mock.patch.dict(
        sys.modules,
        {
            "ipalib": fake_ipalib,
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
        return module


# ---------------------------------------------------------------------------
# Shared binary keytab fixture
# ---------------------------------------------------------------------------
_FAKE_KEYTAB = b"\x05\x02\x00\x00\x00\x2a" + b"\xde\xad\xbe\xef" * 10
_FAKE_B64 = base64.b64encode(_FAKE_KEYTAB).decode("ascii")


class KeytabLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_keytab_module()

    def _make_lookup(self, options, retrieve=None):
        """Build a LookupModule with infrastructure mocked out."""
        lookup = self.mod.LookupModule()

        defaults = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": None,
            "kerberos_keytab": None,
            "verify": None,
            "retrieve_mode": "retrieve",
            "enctypes": [],
            "result_format": "value",
        }

        def set_options(var_options=None, direct=None):
            if var_options:
                options.update(var_options)
            if direct:
                options.update(direct)

        lookup.set_options = set_options
        lookup.get_option = lambda key: options.get(key, defaults.get(key))
        lookup._ensure_ipa_getkeytab_available = lambda: None
        lookup._resolve_verify = (
            lambda verify: "/etc/ipa/ca.crt" if verify is None else verify
        )

        # Default retrieve stub returns _FAKE_KEYTAB
        if retrieve is not None:
            lookup._retrieve_keytab = retrieve
        else:
            lookup._retrieve_keytab = (
                lambda principal, server, enctypes, retrieve_mode, verify:
                _FAKE_KEYTAB
            )

        # Skip kinit
        lookup._kinit_keytab = lambda keytab, principal: None
        lookup._kinit_password = lambda principal, password: None

        return lookup

    # -----------------------------------------------------------------------
    # retrieve_mode flag tests
    # -----------------------------------------------------------------------

    def test_retrieve_mode_adds_r_flag(self):
        """retrieve_mode='retrieve' must pass -r to ipa-getkeytab."""
        seen_cmd = {}

        def fake_run(cmd, **kwargs):
            seen_cmd["cmd"] = cmd
            # Write a non-empty tempfile so the method succeeds
            with open(cmd[cmd.index("-k") + 1], "wb") as fh:
                fh.write(_FAKE_KEYTAB)
            return mock.Mock(returncode=0, stderr="")

        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.subprocess, "run", fake_run):
            lookup._retrieve_keytab(
                "HTTP/host.example.com",
                "idm-01.example.com",
                [],
                "retrieve",
                "/etc/ipa/ca.crt",
            )

        self.assertIn("-r", seen_cmd["cmd"])

    def test_generate_mode_omits_r_flag(self):
        """retrieve_mode='generate' must NOT pass -r to ipa-getkeytab."""
        seen_cmd = {}

        def fake_run(cmd, **kwargs):
            seen_cmd["cmd"] = cmd
            with open(cmd[cmd.index("-k") + 1], "wb") as fh:
                fh.write(_FAKE_KEYTAB)
            return mock.Mock(returncode=0, stderr="")

        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.subprocess, "run", fake_run):
            lookup._retrieve_keytab(
                "HTTP/host.example.com",
                "idm-01.example.com",
                [],
                "generate",
                "/etc/ipa/ca.crt",
            )

        self.assertNotIn("-r", seen_cmd["cmd"])

    # -----------------------------------------------------------------------
    # Encryption type tests
    # -----------------------------------------------------------------------

    def test_enctypes_added_to_command(self):
        """-e flags appear for every requested enctype."""
        seen_cmd = {}

        def fake_run(cmd, **kwargs):
            seen_cmd["cmd"] = cmd
            with open(cmd[cmd.index("-k") + 1], "wb") as fh:
                fh.write(_FAKE_KEYTAB)
            return mock.Mock(returncode=0, stderr="")

        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.subprocess, "run", fake_run):
            lookup._retrieve_keytab(
                "HTTP/host.example.com",
                "idm-01.example.com",
                ["aes256-cts", "aes128-cts"],
                "retrieve",
                "/etc/ipa/ca.crt",
            )

        cmd = seen_cmd["cmd"]
        e_values = [cmd[i + 1] for i, v in enumerate(cmd) if v == "-e"]
        self.assertIn("aes256-cts", e_values)
        self.assertIn("aes128-cts", e_values)

    def test_empty_enctypes_no_e_flags(self):
        """No -e flags when enctypes is empty."""
        seen_cmd = {}

        def fake_run(cmd, **kwargs):
            seen_cmd["cmd"] = cmd
            with open(cmd[cmd.index("-k") + 1], "wb") as fh:
                fh.write(_FAKE_KEYTAB)
            return mock.Mock(returncode=0, stderr="")

        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.subprocess, "run", fake_run):
            lookup._retrieve_keytab(
                "HTTP/host.example.com",
                "idm-01.example.com",
                [],
                "retrieve",
                False,
            )

        self.assertNotIn("-e", seen_cmd["cmd"])

    def test_verify_path_adds_cacert_flag(self):
        """verify path must be passed via --cacert."""
        seen_cmd = {}

        def fake_run(cmd, **kwargs):
            seen_cmd["cmd"] = cmd
            with open(cmd[cmd.index("-k") + 1], "wb") as fh:
                fh.write(_FAKE_KEYTAB)
            return mock.Mock(returncode=0, stderr="")

        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.subprocess, "run", fake_run):
            lookup._retrieve_keytab(
                "HTTP/host.example.com",
                "idm-01.example.com",
                [],
                "retrieve",
                "/etc/ipa/ca.crt",
            )

        cmd = seen_cmd["cmd"]
        self.assertIn("--cacert", cmd)
        self.assertEqual(cmd[cmd.index("--cacert") + 1], "/etc/ipa/ca.crt")

    def test_verify_false_omits_cacert_flag(self):
        """verify=false should rely on system trust and omit --cacert."""
        seen_cmd = {}

        def fake_run(cmd, **kwargs):
            seen_cmd["cmd"] = cmd
            with open(cmd[cmd.index("-k") + 1], "wb") as fh:
                fh.write(_FAKE_KEYTAB)
            return mock.Mock(returncode=0, stderr="")

        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.subprocess, "run", fake_run):
            lookup._retrieve_keytab(
                "HTTP/host.example.com",
                "idm-01.example.com",
                [],
                "retrieve",
                False,
            )

        self.assertNotIn("--cacert", seen_cmd["cmd"])

    def test_keytab_output_path_is_not_precreated(self):
        """ipa-getkeytab must receive a path that does not already exist."""
        seen = {}

        def fake_run(cmd, **kwargs):
            keytab_path = cmd[cmd.index("-k") + 1]
            seen["exists_before"] = os.path.exists(keytab_path)
            with open(keytab_path, "wb") as fh:
                fh.write(_FAKE_KEYTAB)
            return mock.Mock(returncode=0, stderr="")

        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.subprocess, "run", fake_run):
            lookup._retrieve_keytab(
                "HTTP/host.example.com",
                "idm-01.example.com",
                [],
                "retrieve",
                "/etc/ipa/ca.crt",
            )

        self.assertFalse(seen["exists_before"])

    # -----------------------------------------------------------------------
    # Result format tests
    # -----------------------------------------------------------------------

    def test_value_format_returns_base64(self):
        options = {"result_format": "value"}
        lookup = self._make_lookup(options)

        result = lookup.run(["HTTP/host.example.com"], variables={})

        self.assertEqual(result, [_FAKE_B64])

    def test_record_format_includes_principal(self):
        options = {"result_format": "record"}
        lookup = self._make_lookup(options)

        result = lookup.run(["HTTP/host.example.com"], variables={})

        self.assertEqual(len(result), 1)
        record = result[0]
        self.assertEqual(record["principal"], "HTTP/host.example.com")
        self.assertEqual(record["value"], _FAKE_B64)
        self.assertEqual(record["encoding"], "base64")

    def test_map_format_keyed_by_principal(self):
        options = {"result_format": "map"}
        lookup = self._make_lookup(options)

        result = lookup.run(["HTTP/host.example.com"], variables={})

        # map returns a one-element list containing a dict
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        mapping = result[0]
        self.assertIn("HTTP/host.example.com", mapping)
        self.assertEqual(mapping["HTTP/host.example.com"], _FAKE_B64)

    def test_multiple_principals(self):
        """Two principals produce two results in order."""
        keytab_a = b"\x05\x02" + b"\xaa" * 8
        keytab_b = b"\x05\x02" + b"\xbb" * 8
        payloads = iter([keytab_a, keytab_b])

        def retrieve(principal, server, enctypes, retrieve_mode, verify):
            return next(payloads)

        options = {"result_format": "value"}
        lookup = self._make_lookup(options, retrieve=retrieve)

        result = lookup.run(
            ["HTTP/web-01.example.com", "HTTP/web-02.example.com"],
            variables={},
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(
            result[0], base64.b64encode(keytab_a).decode("ascii")
        )
        self.assertEqual(
            result[1], base64.b64encode(keytab_b).decode("ascii")
        )

    # -----------------------------------------------------------------------
    # Error condition tests
    # -----------------------------------------------------------------------

    def test_ipa_getkeytab_not_found(self):
        """Missing ipa-getkeytab binary raises an actionable install hint."""
        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.shutil, "which", return_value=None):
            with mock.patch.object(lookup, "_rhel_major_version", return_value=10):
                with self.assertRaises(self.mod.AnsibleLookupError) as ctx:
                    lookup._ensure_ipa_getkeytab_available()
        self.assertIn("dnf install ipa-client", str(ctx.exception))

    def test_resolve_verify_false_returns_false(self):
        """Boolean false should disable the explicit --cacert override."""
        lookup = self.mod.LookupModule()
        self.assertIs(lookup._resolve_verify(False), False)

    def test_resolve_verify_missing_path_raises(self):
        """A missing CA path should raise an AnsibleLookupError."""
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._resolve_verify('/tmp/definitely-missing-ca.crt')


    def test_resolve_verify_without_default_ca_falls_back_to_system_trust(self):
        """Missing local IPA CA should still use the system trust store."""
        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.os.path, 'exists', return_value=False):
            self.assertIs(lookup._resolve_verify(None), False)

    def test_nonzero_exit_raises_error(self):
        """Non-zero ipa-getkeytab exit raises AnsibleLookupError with stderr."""
        def fake_run(cmd, **kwargs):
            return mock.Mock(returncode=1, stderr="Principal not found")

        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.subprocess, "run", fake_run):
            with self.assertRaises(self.mod.AnsibleLookupError) as ctx:
                lookup._retrieve_keytab(
                    "HTTP/missing.example.com",
                    "idm-01.example.com",
                    [],
                    "retrieve",
                    "/etc/ipa/ca.crt",
                )
        self.assertIn("Principal not found", str(ctx.exception))

    def test_empty_keytab_raises_error(self):
        """Empty keytab output raises AnsibleLookupError."""
        def fake_run(cmd, **kwargs):
            # Write nothing to the temp file — leave it empty
            return mock.Mock(returncode=0, stderr="")

        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.subprocess, "run", fake_run):
            with self.assertRaises(self.mod.AnsibleLookupError) as ctx:
                lookup._retrieve_keytab(
                    "HTTP/host.example.com",
                    "idm-01.example.com",
                    [],
                    "retrieve",
                    "/etc/ipa/ca.crt",
                )
        self.assertIn("empty keytab", str(ctx.exception))

    def test_timeout_raises_error(self):
        """subprocess.TimeoutExpired is wrapped into AnsibleLookupError."""
        def fake_run(cmd, **kwargs):
            raise subprocess.TimeoutExpired(cmd, 30)

        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.subprocess, "run", fake_run):
            with self.assertRaises(self.mod.AnsibleLookupError) as ctx:
                lookup._retrieve_keytab(
                    "HTTP/slow.example.com",
                    "idm-01.example.com",
                    [],
                    "retrieve",
                    "/etc/ipa/ca.crt",
                )
        self.assertIn("timed out", str(ctx.exception))

    def test_server_required(self):
        """Missing server raises AnsibleLookupError."""
        options = {"server": None}
        lookup = self._make_lookup(options)
        with self.assertRaises(self.mod.AnsibleLookupError) as ctx:
            lookup.run(["HTTP/host.example.com"], variables={})
        self.assertIn("server", str(ctx.exception))

    def test_terms_required(self):
        """Empty terms list raises AnsibleLookupError."""
        options = {}
        lookup = self._make_lookup(options)
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup.run([], variables={})

    def test_invalid_retrieve_mode(self):
        """Unknown retrieve_mode raises AnsibleLookupError."""
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_retrieve_mode("overwrite")

    def test_invalid_result_format(self):
        """Unknown result_format raises AnsibleLookupError."""
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_result_format("yaml")

    # -----------------------------------------------------------------------
    # ccache lifecycle
    # -----------------------------------------------------------------------

    def test_ccache_activate_and_cleanup_restores_environment(self):
        lookup = self.mod.LookupModule()
        ccache_path = None
        with tempfile.NamedTemporaryFile(delete=False) as ccache_file:
            ccache_path = ccache_file.name
            original = os.environ.get("KRB5CCNAME")
            os.environ["KRB5CCNAME"] = "FILE:/tmp/original-cache"
            try:
                lookup._activate_ccache(
                    ccache_path,
                    "FILE:%s" % ccache_path,
                )
                self.assertEqual(
                    os.environ.get("KRB5CCNAME"),
                    "FILE:%s" % ccache_path,
                )
                lookup._cleanup_ccache()
                self.assertEqual(
                    os.environ.get("KRB5CCNAME"),
                    "FILE:/tmp/original-cache",
                )
                self.assertFalse(os.path.exists(ccache_path))
            finally:
                if original is None:
                    os.environ.pop("KRB5CCNAME", None)
                else:
                    os.environ["KRB5CCNAME"] = original
                if ccache_path and os.path.exists(ccache_path):
                    os.unlink(ccache_path)

    # -----------------------------------------------------------------------
    # File permission warning
    # -----------------------------------------------------------------------

    def test_auth_keytab_permission_warning(self):
        """Group/world readable keytab triggers display.warning."""
        lookup = self.mod.LookupModule()
        with tempfile.NamedTemporaryFile() as keytab_file:
            os.chmod(keytab_file.name, 0o644)
            with mock.patch.object(self.mod.display, "warning") as warning:
                lookup._warn_if_sensitive_file_permissive(
                    keytab_file.name, "kerberos_keytab"
                )
        warning.assert_called_once()

    def test_owner_only_keytab_no_warning(self):
        """0600 keytab does not trigger a warning."""
        lookup = self.mod.LookupModule()
        with tempfile.NamedTemporaryFile() as keytab_file:
            os.chmod(keytab_file.name, 0o600)
            with mock.patch.object(self.mod.display, "warning") as warning:
                lookup._warn_if_sensitive_file_permissive(
                    keytab_file.name, "kerberos_keytab"
                )
        warning.assert_not_called()

    # -----------------------------------------------------------------------
    # format_keytab_result unit tests
    # -----------------------------------------------------------------------

    def test_format_keytab_result_encodes_bytes(self):
        lookup = self.mod.LookupModule()
        record = lookup._format_keytab_result(
            "HTTP/host.example.com", _FAKE_KEYTAB
        )
        self.assertEqual(record["principal"], "HTTP/host.example.com")
        self.assertEqual(record["value"], _FAKE_B64)
        self.assertEqual(record["encoding"], "base64")

    def test_finalize_results_value_extracts_values(self):
        lookup = self.mod.LookupModule()
        records = [
            {"principal": "HTTP/a.example.com", "value": "aaa=", "encoding": "base64"},
            {"principal": "HTTP/b.example.com", "value": "bbb=", "encoding": "base64"},
        ]
        result = lookup._finalize_results(records, "value")
        self.assertEqual(result, ["aaa=", "bbb="])

    def test_finalize_results_map_keys_by_principal(self):
        lookup = self.mod.LookupModule()
        records = [
            {"principal": "HTTP/a.example.com", "value": "aaa=", "encoding": "base64"},
            {"principal": "HTTP/b.example.com", "value": "bbb=", "encoding": "base64"},
        ]
        result = lookup._finalize_results(records, "map")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        mapping = result[0]
        self.assertEqual(mapping["HTTP/a.example.com"], "aaa=")
        self.assertEqual(mapping["HTTP/b.example.com"], "bbb=")


if __name__ == "__main__":
    unittest.main()
