import importlib.util
import os
import pathlib
import sys
import tempfile
import types
import unittest

from unittest import mock

from tests.error_helpers import exception_text


def _load_vault_module():
    module_name = "eigenstate_ipa_test_vault"
    module_path = pathlib.Path(__file__).resolve().parents[1] / "plugins" / "lookup" / "vault.py"

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
            vault_retrieve=lambda name, **kwargs: {"result": {"data": "secret"}}
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
    fake_install_kinit.kinit_password = lambda principal, password, ccache_path: None

    fake_ipalib_install_kinit = types.ModuleType("ipalib.kinit")
    fake_ipalib_install_kinit.kinit_password = lambda principal, password, ccache_path: None

    with mock.patch.dict(
        sys.modules,
        {
            "ipalib": fake_ipalib,
            "ipalib.errors": fake_errors,
            "ipalib.install": fake_install,
            "ipalib.install.kinit": fake_install_kinit,
            "ipalib.kinit": fake_ipalib_install_kinit,
        },
        clear=False,
    ):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module


class VaultLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_vault_module()

    def _make_lookup(self, options, retrieve=None):
        lookup = self.mod.LookupModule()
        defaults = {
            "operation": "retrieve",
            "encoding": "utf-8",
            "result_format": "value",
            "include_metadata": False,
            "decode_json": False,
            "strip_trailing_newline": False,
            "shared": False,
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
        lookup._retrieve_vault = retrieve or (
            lambda name, scope_label, **kwargs: "%s-secret" % name
        )
        return lookup

    def test_lookup_prefers_usr_bin_kinit(self):
        lookup = self.mod.LookupModule()
        client_globals = lookup._ipa_client._resolve_kinit_command.__globals__
        with mock.patch.object(client_globals['os'].path, 'exists', side_effect=lambda path: path == '/usr/bin/kinit'):
            with mock.patch.object(client_globals['shutil'], 'which', return_value='/custom/bin/kinit'):
                self.assertEqual(lookup._resolve_kinit_command(), '/usr/bin/kinit')

    def test_lookup_falls_back_to_path_kinit(self):
        lookup = self.mod.LookupModule()
        client_globals = lookup._ipa_client._resolve_kinit_command.__globals__
        with mock.patch.object(client_globals['os'].path, 'exists', return_value=False):
            with mock.patch.object(client_globals['shutil'], 'which', return_value='/custom/bin/kinit'):
                self.assertEqual(lookup._resolve_kinit_command(), '/custom/bin/kinit')

    def test_lookup_formats_subprocess_stderr(self):
        lookup = self.mod.LookupModule()
        rendered = lookup._format_subprocess_stderr(('line one is quite long ' * 5) + '\nline two', limit=30)
        self.assertTrue(rendered.startswith('line one is quite long'))
        self.assertTrue(rendered.endswith('...'))

    def test_value_format_returns_secret_values(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "username": "appuser",
            "encoding": "utf-8",
            "result_format": "value",
        }
        lookup = self._make_lookup(options)

        result = lookup.run(["db-pass", "api-key"], variables={})

        self.assertEqual(result, ["db-pass-secret", "api-key-secret"])

    def test_record_format_includes_scope_and_encoding(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "shared": True,
            "encoding": "base64",
            "result_format": "record",
        }
        lookup = self._make_lookup(options, retrieve=lambda name, scope_label, **kwargs: b"binary-data")

        result = lookup.run(["service-keytab"], variables={})

        self.assertEqual(
            result,
            [
                {
                    "name": "service-keytab",
                    "scope": "shared",
                    "encoding": "base64",
                    "value": "YmluYXJ5LWRhdGE=",
                }
            ],
        )

    def test_map_format_returns_named_values(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "shared": True,
            "encoding": "utf-8",
            "result_format": "map",
        }
        lookup = self._make_lookup(options)

        result = lookup.run(["db-pass", "api-key"], variables={})

        self.assertEqual(
            result,
            {
                "db-pass": "db-pass-secret",
                "api-key": "api-key-secret",
            },
        )

    def test_record_format_can_include_metadata(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "shared": True,
            "encoding": "base64",
            "result_format": "record",
            "include_metadata": True,
        }
        lookup = self._make_lookup(
            options,
            retrieve=lambda name, scope_label, **kwargs: b"sealed-bundle",
        )
        lookup._get_vault_metadata = mock.Mock(
            return_value={
                "name": "payments-bootstrap-bundle",
                "scope": "shared",
                "type": "standard",
                "description": "sealed bootstrap payload",
                "vault_id": "vault-42",
            }
        )

        result = lookup.run(["payments-bootstrap-bundle"], variables={})

        self.assertEqual(result[0]["value"], "c2VhbGVkLWJ1bmRsZQ==")
        self.assertEqual(result[0]["description"], "sealed bootstrap payload")
        self.assertEqual(result[0]["vault_id"], "vault-42")

    def test_run_normalizes_term_to_text_before_retrieval(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "shared": True,
            "encoding": "utf-8",
            "result_format": "value",
        }
        seen = {}

        def retrieve(name, scope_label, **kwargs):
            seen["name"] = name
            return "secret"

        lookup = self._make_lookup(options, retrieve=retrieve)

        result = lookup.run([b"db-pass"], variables={})

        self.assertEqual(result, ["secret"])
        self.assertEqual(seen["name"], "db-pass")
        self.assertIsInstance(seen["name"], str)
        self.assertEqual(type(seen["name"]), str)

    def test_retrieve_vault_normalizes_name_to_text(self):
        lookup = self.mod.LookupModule()
        seen = {}

        def fake_retrieve(name, **kwargs):
            seen["name"] = name
            return {"result": {"data": "secret"}}

        self.mod._ipa_api.Command = types.SimpleNamespace(
            vault_retrieve=fake_retrieve
        )

        result = lookup._retrieve_vault(
            b"db-pass",
            "shared",
            shared=True,
        )

        self.assertEqual(result, "secret")
        self.assertEqual(seen["name"], "db-pass")
        self.assertIsInstance(seen["name"], str)
        self.assertEqual(type(seen["name"]), str)

    def test_show_vault_normalizes_name_to_text(self):
        lookup = self.mod.LookupModule()
        seen = {}

        def fake_show(name, **kwargs):
            seen["name"] = name
            return {"result": {"cn": ["db-pass"], "ipavaulttype": ["standard"]}}

        self.mod._ipa_api.Command = types.SimpleNamespace(
            vault_show=fake_show
        )

        result = lookup._show_vault(
            b"db-pass",
            "shared",
            shared=True,
        )

        self.assertEqual(result["name"], "db-pass")
        self.assertEqual(seen["name"], "db-pass")
        self.assertIsInstance(seen["name"], str)
        self.assertEqual(type(seen["name"]), str)

    def test_show_vault_omits_unsupported_no_members_option(self):
        lookup = self.mod.LookupModule()
        seen = {}

        def fake_show(name, **kwargs):
            seen["kwargs"] = kwargs
            return {"result": {"cn": ["db-pass"], "ipavaulttype": ["standard"]}}

        self.mod._ipa_api.Command = types.SimpleNamespace(
            vault_show=fake_show
        )

        lookup._show_vault("db-pass", "shared", shared=True)

        self.assertNotIn("no_members", seen["kwargs"])
        self.assertEqual(seen["kwargs"]["all"], True)
        self.assertEqual(seen["kwargs"]["raw"], False)
        self.assertEqual(seen["kwargs"]["shared"], True)

    def test_find_vaults_omits_unsupported_no_members_option(self):
        lookup = self.mod.LookupModule()
        seen = {}

        def fake_find(*args, **kwargs):
            seen["args"] = args
            seen["kwargs"] = kwargs
            return {
                "result": [
                    {"cn": ["db-pass"], "ipavaulttype": ["standard"]},
                ]
            }

        self.mod._ipa_api.Command = types.SimpleNamespace(
            vault_find=fake_find
        )

        result = lookup._find_vaults("db", "shared", shared=True)

        self.assertEqual(result[0]["name"], "db-pass")
        self.assertEqual(seen["args"], ("db",))
        self.assertNotIn("no_members", seen["kwargs"])
        self.assertEqual(seen["kwargs"]["all"], True)
        self.assertEqual(seen["kwargs"]["raw"], False)
        self.assertEqual(seen["kwargs"]["sizelimit"], 0)
        self.assertEqual(seen["kwargs"]["shared"], True)

    def test_run_collapses_string_subclasses_before_retrieval(self):
        class UnsafeText(str):
            pass

        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "shared": True,
            "encoding": "utf-8",
            "result_format": "value",
        }
        seen = {}

        def retrieve(name, scope_label, **kwargs):
            seen["name"] = name
            return "secret"

        lookup = self._make_lookup(options, retrieve=retrieve)
        result = lookup.run([UnsafeText("db-pass")], variables={})

        self.assertEqual(result, ["secret"])
        self.assertEqual(seen["name"], "db-pass")
        self.assertEqual(type(seen["name"]), str)

    def test_run_collapses_option_string_subclasses_before_find(self):
        class UnsafeText(str):
            pass

        options = {
            "operation": "find",
            "server": UnsafeText("idm-01.example.com"),
            "ipaadmin_principal": UnsafeText("admin"),
            "ipaadmin_password": UnsafeText("secret"),
            "verify": UnsafeText("/etc/ipa/ca.crt"),
            "criteria": UnsafeText("db"),
            "username": UnsafeText("appuser"),
            "result_format": "record",
        }
        seen = {}

        lookup = self._make_lookup(options)

        def connect(server, principal, password, keytab, verify):
            seen["connect"] = {
                "server": server,
                "principal": principal,
                "password": password,
                "keytab": keytab,
                "verify": verify,
            }

        def find(criteria, scope_label, **kwargs):
            seen["criteria"] = criteria
            seen["scope_label"] = scope_label
            seen["scope_username"] = kwargs["username"]
            return []

        lookup._connect = connect
        lookup._find_vaults = find

        result = lookup.run([], variables={})

        self.assertEqual(result, [])
        self.assertEqual(seen["criteria"], "db")
        self.assertEqual(type(seen["criteria"]), str)
        self.assertEqual(seen["scope_username"], "appuser")
        self.assertEqual(type(seen["scope_username"]), str)
        self.assertEqual(seen["scope_label"], "username=appuser")
        self.assertEqual(seen["connect"]["server"], "idm-01.example.com")
        self.assertEqual(type(seen["connect"]["server"]), str)
        self.assertEqual(seen["connect"]["principal"], "admin")
        self.assertEqual(type(seen["connect"]["principal"]), str)
        self.assertEqual(seen["connect"]["password"], "secret")
        self.assertEqual(type(seen["connect"]["password"]), str)
        self.assertEqual(seen["connect"]["keytab"], None)
        self.assertEqual(seen["connect"]["verify"], "/etc/ipa/ca.crt")
        self.assertEqual(type(seen["connect"]["verify"]), str)

    def test_password_fallback_normalizes_stdin_newline(self):
        lookup = self.mod.LookupModule()
        client_globals = lookup._ipa_client._kinit_password.__globals__
        with mock.patch.dict(client_globals, {'HAS_KINIT_PASSWORD': False}),                 mock.patch.object(client_globals['subprocess'], 'run') as run_mock,                 mock.patch.object(client_globals['tempfile'], 'mkstemp', return_value=(12, '/tmp/ccache-vault')),                 mock.patch.object(client_globals['os'], 'close'),                 mock.patch.object(client_globals['os'], 'remove'),                 mock.patch.object(lookup._ipa_client, '_activate_ccache') as activate_mock:
            run_mock.return_value = types.SimpleNamespace(returncode=0, stderr='')
            lookup._ipa_client._kinit_password('admin', 'secret')
        self.assertEqual(run_mock.call_args.kwargs['input'], 'secret\n')
        activate_mock.assert_called_once_with('/tmp/ccache-vault', 'FILE:/tmp/ccache-vault')


    def test_show_operation_returns_metadata(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "shared": True,
            "operation": "show",
            "result_format": "record",
        }
        lookup = self._make_lookup(options)
        lookup._show_vault = lambda name, scope_label, **kwargs: {
            "name": name,
            "scope": scope_label,
            "type": "standard",
            "description": "shared db password",
            "vault_id": None,
        }

        result = lookup.run(["database-password"], variables={})

        self.assertEqual(result[0]["type"], "standard")
        self.assertEqual(result[0]["scope"], "shared")

    def test_find_operation_returns_named_metadata_map(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "verify": "/etc/ipa/ca.crt",
            "shared": True,
            "operation": "find",
            "criteria": "db",
            "result_format": "map_record",
        }
        lookup = self._make_lookup(options)
        lookup._find_vaults = lambda criteria, scope_label, **kwargs: [
            {
                "name": "database-password",
                "scope": scope_label,
                "type": "standard",
                "description": "db secret",
                "vault_id": None,
            }
        ]

        result = lookup.run([], variables={})

        self.assertIn("database-password", result)
        self.assertEqual(result["database-password"]["type"], "standard")

    def test_scope_validation_rejects_conflicts(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_scope("user", "svc", True)

    def test_scope_args_normalize_text_values(self):
        lookup = self.mod.LookupModule()
        self.assertEqual(
            lookup._scope_args(b"appuser", None, False),
            {"username": "appuser"},
        )
        self.assertEqual(
            lookup._scope_args(None, b"HTTP/app.example.com", False),
            {"service": "HTTP/app.example.com"},
        )

    def test_decryption_validation_rejects_conflicts(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_decryption_inputs("pw", "/tmp/pw", None)

    def test_retrieve_requires_terms(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_terms_for_operation("retrieve", [])

    def test_standard_vault_rejects_decryption_inputs(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_vault_type_inputs(
                "db-pass", "standard", "pw", None, None
            )

    def test_symmetric_vault_requires_password_input(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_vault_type_inputs(
                "api-key", "symmetric", None, None, None
            )

    def test_asymmetric_vault_requires_private_key(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_vault_type_inputs(
                "tls-key", "asymmetric", None, None, None
            )

    def test_preflight_falls_back_when_metadata_unavailable(self):
        lookup = self.mod.LookupModule()
        lookup._get_vault_metadata = mock.Mock(
            side_effect=self.mod.AnsibleLookupError("metadata unavailable")
        )

        lookup._preflight_retrieve(
            "db-pass",
            "shared",
            shared=True,
            vault_password=None,
            vault_password_file=None,
            private_key_file=None,
        )

        lookup._get_vault_metadata.assert_called_once()

    def test_decode_json_returns_structured_value(self):
        lookup = self.mod.LookupModule()
        result = lookup._format_vault_result(
            "app-config",
            '{"enabled": true, "replicas": 2}',
            "utf-8",
            "record",
            "shared",
            decode_json=True,
        )
        self.assertEqual(result["value"]["enabled"], True)
        self.assertEqual(result["value"]["replicas"], 2)

    def test_strip_trailing_newline_normalizes_text(self):
        lookup = self.mod.LookupModule()
        result = lookup._format_vault_result(
            "db-pass",
            "secret\n",
            "utf-8",
            "value",
            "shared",
            strip_trailing_newline=True,
        )
        self.assertEqual(result, "secret")

    def test_decode_json_requires_utf8(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_output_options(
                "retrieve", "base64", "value", False, True, False
            )

    def test_decode_json_rejected_for_metadata_operations(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_output_options(
                "show", "utf-8", "record", False, True, False
            )

    def test_strip_trailing_newline_rejected_for_metadata_operations(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_output_options(
                "find", "utf-8", "record", False, False, True
            )

    def test_include_metadata_requires_retrieve(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_output_options(
                "show", "utf-8", "record", True, False, False
            )

    def test_include_metadata_requires_structured_retrieve_result(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_output_options(
                "retrieve", "utf-8", "value", True, False, False
            )

    def test_decode_json_reports_invalid_payload(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._format_vault_result(
                "app-config",
                "not-json",
                "utf-8",
                "value",
                "shared",
                decode_json=True,
            )

    def test_decode_vault_value_handles_bytes(self):
        lookup = self.mod.LookupModule()
        result = lookup._format_vault_result(
            "tls-key",
            b"abc",
            "base64",
            "record",
            "shared",
        )
        self.assertEqual(result["value"], "YWJj")

    def test_resolve_verify_uses_explicit_path(self):
        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.os.path, "exists", return_value=True):
            self.assertEqual(
                lookup._resolve_verify("/etc/ipa/custom-ca.crt"),
                "/etc/ipa/custom-ca.crt",
            )

    def test_resolve_verify_false_disables_tls_explicitly(self):
        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.display, "warning") as warning:
            self.assertFalse(lookup._resolve_verify(False))
        warning.assert_called_once()

    def test_resolve_verify_string_false_disables_tls_explicitly(self):
        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.display, "warning") as warning:
            self.assertFalse(lookup._resolve_verify("false"))
        warning.assert_called_once()

    def test_resolve_verify_requires_explicit_trust_or_opt_out(self):
        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.os.path, "exists", return_value=False):
            with self.assertRaises(self.mod.AnsibleLookupError) as ctx:
                lookup._resolve_verify(None)
        self.assertIn("verify", exception_text(ctx.exception))

    def test_activate_and_cleanup_ccache_restores_environment(self):
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

    def test_warns_when_sensitive_file_is_group_or_world_readable(self):
        lookup = self.mod.LookupModule()
        with tempfile.NamedTemporaryFile() as secret_file:
            os.chmod(secret_file.name, 0o644)
            with mock.patch.object(self.mod.display, "warning") as warning:
                lookup._warn_if_sensitive_file_permissive(
                    secret_file.name,
                    "vault_password_file",
                )
        warning.assert_called_once()

    def test_does_not_warn_when_sensitive_file_is_owner_only(self):
        lookup = self.mod.LookupModule()
        with tempfile.NamedTemporaryFile() as secret_file:
            os.chmod(secret_file.name, 0o600)
            with mock.patch.object(self.mod.display, "warning") as warning:
                lookup._warn_if_sensitive_file_permissive(
                    secret_file.name,
                    "private_key_file",
                )
        warning.assert_not_called()


if __name__ == "__main__":
    unittest.main()
