import importlib.util
import os
import pathlib
import sys
import tempfile
import types
import unittest

from unittest import mock


def _load_otp_module():
    module_name = "eigenstate_ipa_test_otp"
    module_path = pathlib.Path(__file__).resolve().parents[1] / "plugins" / "lookup" / "otp.py"

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
            otptoken_add=lambda **kwargs: {
                "result": {
                    "ipatokenuniqueid": ["tok-default-id"],
                    "ipatokentype": ["totp"],
                    "ipatokenotpalgorithm": ["sha1"],
                    "ipatokenotpdigits": [6],
                    "ipatokentotptimestep": [30],
                    "uri": ["otpauth://totp/default?secret=ABC"],
                    "ipatokenowner": ["testuser"],
                    "ipatokendisabled": [False],
                    "description": [],
                }
            },
            otptoken_find=lambda *args, **kwargs: {"result": []},
            otptoken_show=lambda token_id, **kwargs: {
                "result": {
                    "ipatokenuniqueid": [token_id],
                    "ipatokentype": ["totp"],
                    "ipatokenotpalgorithm": ["sha1"],
                    "ipatokenotpdigits": [6],
                    "ipatokentotptimestep": [30],
                    "ipatokenowner": ["someuser"],
                    "ipatokendisabled": [False],
                    "description": [],
                }
            },
            otptoken_del=lambda token_id: {"result": None},
            host_mod=lambda fqdn, **kwargs: {
                "result": {
                    "randompassword": ["EnrollP@ss1"],
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
    fake_install_kinit.kinit_password = lambda principal, password, ccache_path: None

    fake_ipalib_kinit = types.ModuleType("ipalib.kinit")
    fake_ipalib_kinit.kinit_password = lambda principal, password, ccache_path: None

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
        return module


class OtpLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_otp_module()

    def _make_lookup(self, options=None, add_user_token=None,
                     add_host_enroll=None, find_tokens=None,
                     show_token=None, revoke_token=None):
        lookup = self.mod.LookupModule()
        defaults = {
            "operation": "add",
            "token_type": "totp",
            "algorithm": "sha1",
            "digits": 6,
            "interval": 30,
            "owner": None,
            "description": None,
            "result_format": None,
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "kerberos_keytab": None,
            "verify": None,
        }
        merged = {**defaults, **(options or {})}

        def set_options(var_options=None, direct=None):
            if var_options:
                merged.update(var_options)
            if direct:
                merged.update(direct)

        lookup.set_options = set_options
        lookup.get_option = lambda key: merged.get(key)
        lookup._ensure_ipalib = lambda: None
        lookup._resolve_verify = lambda verify: verify or "/etc/ipa/ca.crt"
        lookup._connect = lambda *args, **kwargs: None
        lookup._cleanup_ccache = lambda: None

        if add_user_token is not None:
            lookup._add_user_token = add_user_token
        if add_host_enroll is not None:
            lookup._add_host_enroll = add_host_enroll
        if find_tokens is not None:
            lookup._find_tokens = find_tokens
        if show_token is not None:
            lookup._show_token = show_token
        if revoke_token is not None:
            lookup._revoke_token = revoke_token

        return lookup

    # ------------------------------------------------------------------
    # add totp
    # ------------------------------------------------------------------

    def test_add_totp_defaults_returns_uri_list(self):
        lookup = self._make_lookup(
            add_user_token=lambda owner, token_type, algorithm, digits,
            interval, description: {
                "owner": owner, "token_id": "tok-001", "type": "totp",
                "uri": "otpauth://totp/user1?secret=XYZ",
                "algorithm": "sha1", "digits": 6, "interval": 30,
                "disabled": False, "description": None, "exists": True,
            }
        )
        result = lookup.run(["user1"], variables={})
        self.assertEqual(result, ["otpauth://totp/user1?secret=XYZ"])

    def test_add_totp_custom_algorithm_passed_through(self):
        seen = {}

        def fake_add(owner, token_type, algorithm, digits, interval, description):
            seen["algorithm"] = algorithm
            return {"owner": owner, "token_id": "tok-002", "type": "totp",
                    "uri": "otpauth://totp/user2?secret=ABC",
                    "algorithm": algorithm, "digits": digits, "interval": interval,
                    "disabled": False, "description": None, "exists": True}

        lookup = self._make_lookup(
            options={"algorithm": "sha256"},
            add_user_token=fake_add,
        )
        lookup.run(["user2"], variables={})
        self.assertEqual(seen["algorithm"], "sha256")

    def test_add_user_token_uses_otptoken_add_type_option(self):
        lookup = self.mod.LookupModule()
        with mock.patch.object(
            self.mod._ipa_api.Command,
            "otptoken_add",
            return_value={
                "result": {
                    "ipatokenuniqueid": ["tok-type-001"],
                    "ipatokentype": ["totp"],
                    "ipatokenotpalgorithm": ["sha1"],
                    "ipatokenotpdigits": [6],
                    "ipatokentotptimestep": [30],
                    "uri": ["otpauth://totp/check?secret=ABC"],
                    "ipatokenowner": ["typeuser"],
                    "ipatokendisabled": [False],
                    "description": [],
                }
            },
        ) as otptoken_add:
            lookup._add_user_token("typeuser", "totp", "sha1", 6, 30, None)
        self.assertEqual(otptoken_add.call_args.kwargs["type"], "totp")

    def test_build_token_record_prefers_live_uri_field(self):
        lookup = self.mod.LookupModule()
        record = lookup._build_token_record(
            "alice",
            {
                "ipatokenuniqueid": ["tok-live-uri"],
                "ipatokentype": ["totp"],
                "ipatokenotpalgorithm": ["sha1"],
                "ipatokenotpdigits": [6],
                "ipatokentotptimestep": [30],
                "uri": ["otpauth://totp/alice?secret=LIVE"],
                "ipatokenowner": ["alice"],
                "ipatokendisabled": [False],
                "description": [],
            },
            include_uri=True,
        )
        self.assertEqual(record["uri"], "otpauth://totp/alice?secret=LIVE")

    def test_build_token_record_uses_live_type_field(self):
        lookup = self.mod.LookupModule()
        record = lookup._build_token_record(
            "alice",
            {
                "ipatokenuniqueid": ["tok-live-hotp"],
                "type": ["HOTP"],
                "ipatokenotpalgorithm": ["sha256"],
                "ipatokenotpdigits": [8],
                "uri": ["otpauth://hotp/alice?secret=LIVE"],
                "ipatokenowner": ["alice"],
                "ipatokendisabled": [False],
                "description": [],
            },
            include_uri=True,
        )
        self.assertEqual(record["type"], "hotp")

    def test_add_totp_custom_digits_8(self):
        seen = {}

        def fake_add(owner, token_type, algorithm, digits, interval, description):
            seen["digits"] = digits
            return {"owner": owner, "token_id": "tok-003", "type": "totp",
                    "uri": "otpauth://totp/user3?secret=DEF",
                    "algorithm": "sha1", "digits": digits, "interval": 30,
                    "disabled": False, "description": None, "exists": True}

        lookup = self._make_lookup(
            options={"digits": 8},
            add_user_token=fake_add,
        )
        lookup.run(["user3"], variables={})
        self.assertEqual(seen["digits"], 8)

    def test_add_totp_with_description_passed_through(self):
        seen = {}

        def fake_add(owner, token_type, algorithm, digits, interval, description):
            seen["description"] = description
            return {"owner": owner, "token_id": "tok-004", "type": "totp",
                    "uri": "otpauth://totp/user4?secret=GHI",
                    "algorithm": "sha1", "digits": 6, "interval": 30,
                    "disabled": False, "description": description, "exists": True}

        lookup = self._make_lookup(
            options={"description": "Main 2FA token"},
            add_user_token=fake_add,
        )
        lookup.run(["user4"], variables={})
        self.assertEqual(seen["description"], "Main 2FA token")

    def test_add_totp_value_format_returns_bare_uri(self):
        lookup = self._make_lookup(
            options={"result_format": "value"},
            add_user_token=lambda owner, token_type, algorithm, digits,
            interval, description: {
                "owner": owner, "token_id": "tok-005", "type": "totp",
                "uri": "otpauth://totp/user5?secret=JKL",
                "algorithm": "sha1", "digits": 6, "interval": 30,
                "disabled": False, "description": None, "exists": True,
            }
        )
        result = lookup.run(["user5"], variables={})
        self.assertIsInstance(result, list)
        self.assertEqual(result[0], "otpauth://totp/user5?secret=JKL")

    # ------------------------------------------------------------------
    # add hotp
    # ------------------------------------------------------------------

    def test_add_hotp_defaults_returns_uri(self):
        lookup = self._make_lookup(
            options={"token_type": "hotp"},
            add_user_token=lambda owner, token_type, algorithm, digits,
            interval, description: {
                "owner": owner, "token_id": "tok-hotp-001", "type": "hotp",
                "uri": "otpauth://hotp/user6?secret=MNO",
                "algorithm": "sha1", "digits": 6, "interval": None,
                "disabled": False, "description": None, "exists": True,
            }
        )
        result = lookup.run(["user6"], variables={})
        self.assertEqual(result, ["otpauth://hotp/user6?secret=MNO"])

    def test_add_hotp_with_interval_warns_and_ignores(self):
        lookup = self._make_lookup(
            options={"token_type": "hotp", "interval": 60},
            add_user_token=lambda owner, token_type, algorithm, digits,
            interval, description: {
                "owner": owner, "token_id": "tok-hotp-002", "type": "hotp",
                "uri": "otpauth://hotp/user7?secret=PQR",
                "algorithm": "sha1", "digits": 6, "interval": None,
                "disabled": False, "description": None, "exists": True,
            }
        )
        with mock.patch.object(self.mod.display, "warning") as warning:
            lookup.run(["user7"], variables={})
        warning.assert_called_once()
        self.assertIn("interval", warning.call_args[0][0])

    # ------------------------------------------------------------------
    # add host
    # ------------------------------------------------------------------

    def test_add_host_returns_password_field(self):
        lookup = self._make_lookup(
            options={"token_type": "host"},
            add_host_enroll=lambda fqdn: {
                "fqdn": fqdn, "type": "host",
                "password": "EnrollP@ss1", "exists": True,
            }
        )
        result = lookup.run(["web-01.example.com"], variables={})
        self.assertEqual(result, ["EnrollP@ss1"])

    def test_add_host_record_format_includes_fqdn(self):
        lookup = self._make_lookup(
            options={"token_type": "host", "result_format": "record"},
            add_host_enroll=lambda fqdn: {
                "fqdn": fqdn, "type": "host",
                "password": "EnrollP@ss2", "exists": True,
            }
        )
        result = lookup.run(["db-01.example.com"], variables={})
        self.assertEqual(result[0]["fqdn"], "db-01.example.com")
        self.assertEqual(result[0]["password"], "EnrollP@ss2")
        self.assertEqual(result[0]["type"], "host")

    # ------------------------------------------------------------------
    # find
    # ------------------------------------------------------------------

    def test_find_no_owner_returns_all_records(self):
        tokens = [
            {"token_id": "tok-a", "owner": "alice", "type": "totp",
             "algorithm": "sha1", "digits": 6, "interval": 30,
             "disabled": False, "description": None, "exists": True},
            {"token_id": "tok-b", "owner": "bob", "type": "hotp",
             "algorithm": "sha1", "digits": 6, "interval": None,
             "disabled": False, "description": None, "exists": True},
        ]
        lookup = self._make_lookup(
            options={"operation": "find"},
            find_tokens=lambda criteria, owner: tokens,
        )
        result = lookup.run([], variables={})
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["owner"], "alice")

    def test_find_with_owner_filter_passes_owner(self):
        seen = {}

        def fake_find(criteria, owner):
            seen["owner"] = owner
            return []

        lookup = self._make_lookup(
            options={"operation": "find", "owner": "alice"},
            find_tokens=fake_find,
        )
        lookup.run([], variables={})
        self.assertEqual(seen["owner"], "alice")

    def test_find_empty_result_returns_empty_list(self):
        lookup = self._make_lookup(
            options={"operation": "find"},
            find_tokens=lambda criteria, owner: [],
        )
        result = lookup.run([], variables={})
        self.assertEqual(result, [])

    # ------------------------------------------------------------------
    # show
    # ------------------------------------------------------------------

    def test_show_existing_token_returns_exists_true(self):
        lookup = self._make_lookup(
            options={"operation": "show"},
            show_token=lambda token_id: {
                "token_id": token_id, "owner": "carol", "type": "totp",
                "algorithm": "sha1", "digits": 6, "interval": 30,
                "disabled": False, "description": None, "exists": True,
            }
        )
        result = lookup.run(["tok-123"], variables={})
        self.assertTrue(result[0]["exists"])
        self.assertEqual(result[0]["owner"], "carol")

    def test_show_missing_token_returns_exists_false_without_error(self):
        lookup = self._make_lookup(
            options={"operation": "show"},
            show_token=lambda token_id: None,
        )
        result = lookup.run(["tok-missing"], variables={})
        self.assertFalse(result[0]["exists"])
        self.assertEqual(result[0]["token_id"], "tok-missing")

    def test_show_multiple_ids_returns_all_records(self):
        responses = {
            "tok-aaa": {"token_id": "tok-aaa", "owner": "alice", "type": "totp",
                        "algorithm": "sha1", "digits": 6, "interval": 30,
                        "disabled": False, "description": None, "exists": True},
            "tok-bbb": None,
        }
        lookup = self._make_lookup(
            options={"operation": "show"},
            show_token=lambda token_id: responses.get(token_id),
        )
        result = lookup.run(["tok-aaa", "tok-bbb"], variables={})
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0]["exists"])
        self.assertFalse(result[1]["exists"])

    # ------------------------------------------------------------------
    # revoke
    # ------------------------------------------------------------------

    def test_revoke_success_returns_token_ids(self):
        lookup = self._make_lookup(
            options={"operation": "revoke"},
            revoke_token=lambda token_id: token_id,
        )
        result = lookup.run(["tok-del-1", "tok-del-2"], variables={})
        self.assertEqual(result, ["tok-del-1", "tok-del-2"])

    def test_revoke_not_found_raises_error(self):
        def fake_revoke(token_id):
            raise self.mod.AnsibleLookupError("Token '%s' not found" % token_id)

        lookup = self._make_lookup(
            options={"operation": "revoke"},
            revoke_token=fake_revoke,
        )
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup.run(["tok-ghost"], variables={})

    # ------------------------------------------------------------------
    # result_format
    # ------------------------------------------------------------------

    def test_add_map_format_keys_by_owner(self):
        lookup = self._make_lookup(
            options={"result_format": "map"},
            add_user_token=lambda owner, token_type, algorithm, digits,
            interval, description: {
                "owner": owner, "token_id": "tok-map-1", "type": "totp",
                "uri": "otpauth://totp/%s?secret=ZZZ" % owner,
                "algorithm": "sha1", "digits": 6, "interval": 30,
                "disabled": False, "description": None, "exists": True,
            }
        )
        result = lookup.run(["mapuser"], variables={})
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIn("mapuser", result[0])
        self.assertEqual(result[0]["mapuser"], "otpauth://totp/mapuser?secret=ZZZ")

    def test_add_map_record_format_keys_by_owner_with_full_record(self):
        lookup = self._make_lookup(
            options={"result_format": "map_record"},
            add_user_token=lambda owner, token_type, algorithm, digits,
            interval, description: {
                "owner": owner, "token_id": "tok-mr-1", "type": "totp",
                "uri": "otpauth://totp/%s?secret=YYY" % owner,
                "algorithm": "sha1", "digits": 6, "interval": 30,
                "disabled": False, "description": None, "exists": True,
            }
        )
        result = lookup.run(["mruser"], variables={})
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIn("mruser", result[0])
        self.assertEqual(result[0]["mruser"]["token_id"], "tok-mr-1")
        self.assertEqual(result[0]["mruser"]["uri"], "otpauth://totp/mruser?secret=YYY")

    def test_find_map_record_format_keys_by_token_id(self):
        tokens = [
            {"token_id": "tok-find-1", "owner": "diana", "type": "totp",
             "algorithm": "sha1", "digits": 6, "interval": 30,
             "disabled": False, "description": None, "exists": True},
        ]
        lookup = self._make_lookup(
            options={"operation": "find", "result_format": "map_record"},
            find_tokens=lambda criteria, owner: tokens,
        )
        result = lookup.run([], variables={})
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIn("tok-find-1", result[0])
        self.assertEqual(result[0]["tok-find-1"]["owner"], "diana")

    def test_show_map_record_format_keys_by_token_id(self):
        lookup = self._make_lookup(
            options={"operation": "show", "result_format": "map_record"},
            show_token=lambda token_id: {
                "token_id": token_id, "owner": "eve", "type": "totp",
                "algorithm": "sha1", "digits": 6, "interval": 30,
                "disabled": False, "description": None, "exists": True,
            }
        )
        result = lookup.run(["tok-show-1"], variables={})
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIn("tok-show-1", result[0])
        self.assertEqual(result[0]["tok-show-1"]["owner"], "eve")

    # ------------------------------------------------------------------
    # validation
    # ------------------------------------------------------------------

    def test_invalid_digits_raises_error(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_options(
                "add", "totp", "sha1", 7, 30, None, "record")

    def test_type_host_with_find_raises_error(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_options(
                "find", "host", "sha1", 6, 30, None, "record")

    def test_empty_terms_for_add_raises_error(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_terms("add", [])

    def test_missing_terms_for_revoke_raises_error(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_terms("revoke", [])

    # ------------------------------------------------------------------
    # ccache + environment helpers
    # ------------------------------------------------------------------

    def test_activate_and_cleanup_ccache_restores_environment(self):
        lookup = self.mod.LookupModule()
        with tempfile.NamedTemporaryFile() as ccache_file:
            original = os.environ.get("KRB5CCNAME")
            os.environ["KRB5CCNAME"] = "FILE:/tmp/original-cache"
            try:
                lookup._activate_ccache(
                    ccache_file.name,
                    "FILE:%s" % ccache_file.name,
                )
                self.assertEqual(
                    os.environ.get("KRB5CCNAME"),
                    "FILE:%s" % ccache_file.name,
                )
                lookup._cleanup_ccache()
                self.assertEqual(
                    os.environ.get("KRB5CCNAME"),
                    "FILE:/tmp/original-cache",
                )
                self.assertFalse(os.path.exists(ccache_file.name))
            finally:
                if original is None:
                    os.environ.pop("KRB5CCNAME", None)
                else:
                    os.environ["KRB5CCNAME"] = original

    def test_cleanup_ccache_disconnects_connected_backend(self):
        lookup = self.mod.LookupModule()
        backend = types.SimpleNamespace(
            isconnected=lambda: True,
            disconnect=mock.Mock(),
        )
        with mock.patch.object(self.mod._ipa_api.Backend, "rpcclient", backend):
            lookup._cleanup_ccache()
        backend.disconnect.assert_called_once_with()

    def test_warns_when_sensitive_file_is_world_readable(self):
        lookup = self.mod.LookupModule()
        with tempfile.NamedTemporaryFile() as secret_file:
            os.chmod(secret_file.name, 0o644)
            with mock.patch.object(self.mod.display, "warning") as warning:
                lookup._warn_if_sensitive_file_permissive(
                    secret_file.name,
                    "kerberos_keytab",
                )
        warning.assert_called_once()

    def test_resolve_verify_warns_when_no_local_ca_is_available(self):
        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.os.path, "exists", return_value=False):
            with mock.patch.object(self.mod.display, "warning") as warning:
                self.assertFalse(lookup._resolve_verify(None))
        warning.assert_called_once()

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


if __name__ == "__main__":
    unittest.main()
