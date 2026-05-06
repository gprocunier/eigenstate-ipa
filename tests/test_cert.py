import importlib.util
import os
import pathlib
import sys
import tempfile
import textwrap
import types
import unittest

from unittest import mock

from tests.error_helpers import exception_text


def _load_cert_module():
    module_name = "eigenstate_ipa_test_cert"
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "plugins" / "lookup" / "cert.py"
    )

    fake_not_found = type("NotFound", (Exception,), {})
    fake_auth_error = type("AuthorizationError", (Exception,), {})

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
            cert_request=lambda csr, **kwargs: {"result": {}},
            cert_show=lambda serial, **kwargs: {"result": {}},
            cert_find=lambda **kwargs: {"result": []},
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
        return module


# ---------------------------------------------------------------------------
# Sample IPA cert result used across multiple tests
# ---------------------------------------------------------------------------

SAMPLE_IPA_CERT = {
    "certificate": (
        "MIICpDCCAYwCCQDExample1234567890MA0GCSqGSIb3DQEBCwUAMB4xHDAaBgNV"
        "BAMME2V4YW1wbGUuY29tIENBMA0GCSqGSIb3DQEBCwUAMB4xHDAaBgNVBAMM"
    ),
    "subject": "CN=web.example.com,O=EXAMPLE.COM",
    "issuer": "CN=Certificate Authority,O=EXAMPLE.COM",
    "serial_number": 12345,
    "valid_not_before": "2026-04-01 00:00:00",
    "valid_not_after": "2027-04-01 00:00:00",
    "san_dnsname": ["web.example.com", "web"],
    "revoked": False,
    "revocation_reason": None,
}

SAMPLE_CSR = (
    "-----BEGIN CERTIFICATE REQUEST-----\n"
    "MIICvDCCAaQCAQAwdzELMAkGA1UEBhMCVVMxDTALBgNVBAgMBFRlc3QxEDAOBgNV\n"
    "-----END CERTIFICATE REQUEST-----\n"
)


class CertLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_cert_module()

    def _make_lookup(self, options,
                     request_cert=None,
                     retrieve_cert=None,
                     find_certs=None):
        """Build a LookupModule with mocked internals for unit testing."""
        lookup = self.mod.LookupModule()

        defaults = {
            "operation": "request",
            "encoding": "pem",
            "result_format": "value",
            "csr": None,
            "csr_file": None,
            "profile": None,
            "ca": None,
            "add": False,
            "principal": None,
            "subject": None,
            "valid_not_after_from": None,
            "valid_not_after_to": None,
            "revocation_reason": None,
            "exactly": False,
        }

        def set_options(var_options=None, direct=None):
            if var_options:
                options.update(var_options)
            if direct:
                options.update(direct)

        lookup.set_options = set_options
        lookup.get_option = lambda key: options.get(key, defaults.get(key))
        lookup._ensure_ipalib = lambda: None
        lookup._resolve_verify = lambda v: v or "/etc/ipa/ca.crt"
        lookup._connect = lambda *args, **kwargs: None

        if request_cert is not None:
            lookup._request_cert = request_cert
        else:
            lookup._request_cert = (
                lambda principal, csr, profile, ca, add: dict(SAMPLE_IPA_CERT)
            )

        if retrieve_cert is not None:
            lookup._retrieve_cert = retrieve_cert
        else:
            lookup._retrieve_cert = lambda serial: dict(SAMPLE_IPA_CERT)

        if find_certs is not None:
            lookup._find_certs = find_certs
        else:
            lookup._find_certs = lambda *args, **kwargs: [dict(SAMPLE_IPA_CERT)]

        return lookup

    # -----------------------------------------------------------------------
    # Dependency guard
    # -----------------------------------------------------------------------

    def test_ensure_ipalib_raises_when_unavailable(self):
        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod, "HAS_IPALIB", False):
            with self.assertRaises(self.mod.AnsibleLookupError) as ctx:
                lookup._ensure_ipalib()
        message = ctx.exception.args[0] if ctx.exception.args else repr(ctx.exception)
        self.assertIn("python3-ipalib", message)

    def test_ensure_ipalib_passes_when_available(self):
        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod, "HAS_IPALIB", True):
            lookup._ensure_ipalib()  # must not raise

    # -----------------------------------------------------------------------
    # Validation — operation
    # -----------------------------------------------------------------------

    def test_validate_operation_accepts_valid_values(self):
        lookup = self.mod.LookupModule()
        for op in ("request", "retrieve", "find"):
            lookup._validate_operation(op)  # must not raise

    def test_validate_operation_rejects_unknown(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_operation("sign")

    # -----------------------------------------------------------------------
    # Validation — encoding and result_format
    # -----------------------------------------------------------------------

    def test_validate_encoding_accepts_pem_and_base64(self):
        lookup = self.mod.LookupModule()
        lookup._validate_encoding("pem")
        lookup._validate_encoding("base64")

    def test_validate_encoding_rejects_unknown(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_encoding("der")

    def test_validate_result_format_accepts_all_values(self):
        lookup = self.mod.LookupModule()
        for fmt in ("value", "record", "map", "map_record"):
            lookup._validate_result_format(fmt)

    def test_validate_result_format_rejects_unknown(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_result_format("dict")

    # -----------------------------------------------------------------------
    # Validation — request params
    # -----------------------------------------------------------------------

    def test_validate_request_rejects_missing_terms(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_request_params([], SAMPLE_CSR, None)

    def test_validate_request_rejects_csr_and_csr_file_together(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_request_params(
                ["HTTP/web.example.com"], SAMPLE_CSR, "/tmp/web.csr")

    def test_validate_request_rejects_no_csr_source(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_request_params(
                ["HTTP/web.example.com"], None, None)

    def test_validate_request_passes_with_inline_csr(self):
        lookup = self.mod.LookupModule()
        lookup._validate_request_params(
            ["HTTP/web.example.com"], SAMPLE_CSR, None)  # must not raise

    def test_validate_request_passes_with_csr_file(self):
        lookup = self.mod.LookupModule()
        lookup._validate_request_params(
            ["HTTP/web.example.com"], None, "/tmp/web.csr")  # must not raise

    # -----------------------------------------------------------------------
    # Validation — retrieve params
    # -----------------------------------------------------------------------

    def test_validate_retrieve_rejects_missing_terms(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_retrieve_params([])

    def test_validate_retrieve_passes_with_term(self):
        lookup = self.mod.LookupModule()
        lookup._validate_retrieve_params(["12345"])  # must not raise

    # -----------------------------------------------------------------------
    # Validation — find params (date format)
    # -----------------------------------------------------------------------

    def test_validate_find_rejects_invalid_date_format(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_find_params("2026/04/01", None)

    def test_validate_find_rejects_partial_date(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_find_params(None, "April 2026")

    def test_validate_find_passes_with_valid_iso_dates(self):
        lookup = self.mod.LookupModule()
        lookup._validate_find_params(
            "2026-04-01", "2026-05-01")  # must not raise

    def test_validate_find_passes_with_no_dates(self):
        lookup = self.mod.LookupModule()
        lookup._validate_find_params(None, None)  # must not raise

    # -----------------------------------------------------------------------
    # Validation — serial number parsing
    # -----------------------------------------------------------------------

    def test_validate_serial_accepts_integer(self):
        lookup = self.mod.LookupModule()
        self.assertEqual(lookup._validate_serial(12345), 12345)

    def test_validate_serial_accepts_decimal_string(self):
        lookup = self.mod.LookupModule()
        self.assertEqual(lookup._validate_serial("12345"), 12345)

    def test_validate_serial_accepts_hex_string(self):
        lookup = self.mod.LookupModule()
        self.assertEqual(lookup._validate_serial("0x3039"), 12345)

    def test_validate_serial_rejects_non_numeric(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._validate_serial("ABCDE")

    def test_principal_find_filter_maps_host_principal_to_hosts(self):
        lookup = self.mod.LookupModule()
        self.assertEqual(
            lookup._principal_find_filter(
                "host/web.example.com@EXAMPLE.COM"),
            {"host": ["web.example.com"]},
        )

    def test_principal_find_filter_maps_service_principal_to_services(self):
        lookup = self.mod.LookupModule()
        self.assertEqual(
            lookup._principal_find_filter(
                "HTTP/web.example.com@EXAMPLE.COM"),
            {"service": ["HTTP/web.example.com@EXAMPLE.COM"]},
        )

    def test_principal_find_filter_rejects_non_host_non_service(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._principal_find_filter("admin@EXAMPLE.COM")

    # -----------------------------------------------------------------------
    # PEM conversion
    # -----------------------------------------------------------------------

    def test_der_b64_to_pem_wraps_at_64_chars(self):
        lookup = self.mod.LookupModule()
        # 80 chars of base64-safe data
        b64 = "A" * 80
        pem = lookup._der_b64_to_pem(b64)
        self.assertIn("-----BEGIN CERTIFICATE-----", pem)
        self.assertIn("-----END CERTIFICATE-----", pem)
        # Each interior line should be ≤ 64 chars
        lines = pem.strip().splitlines()
        for line in lines[1:-1]:
            self.assertLessEqual(len(line), 64)

    def test_der_b64_to_pem_strips_embedded_whitespace(self):
        lookup = self.mod.LookupModule()
        b64_with_newlines = "AAAA\nBBBB\nCCCC"
        pem = lookup._der_b64_to_pem(b64_with_newlines)
        # Should not have blank lines inside the PEM body
        lines = pem.strip().splitlines()
        body_lines = lines[1:-1]
        self.assertTrue(all(line.strip() for line in body_lines))

    def test_der_b64_to_pem_handles_exact_64_char_input(self):
        lookup = self.mod.LookupModule()
        b64 = "B" * 64
        pem = lookup._der_b64_to_pem(b64)
        lines = pem.strip().splitlines()
        self.assertEqual(lines[1], b64)

    # -----------------------------------------------------------------------
    # _build_record
    # -----------------------------------------------------------------------

    def test_build_record_pem_encoding_adds_headers(self):
        lookup = self.mod.LookupModule()
        record = lookup._build_record(
            "HTTP/web.example.com", SAMPLE_IPA_CERT, "pem")
        self.assertIn("-----BEGIN CERTIFICATE-----", record["value"])
        self.assertEqual(record["encoding"], "pem")

    def test_build_record_base64_encoding_returns_raw_b64(self):
        lookup = self.mod.LookupModule()
        record = lookup._build_record(
            "HTTP/web.example.com", SAMPLE_IPA_CERT, "base64")
        self.assertNotIn("-----BEGIN CERTIFICATE-----", record["value"])
        self.assertEqual(record["encoding"], "base64")

    def test_build_record_metadata_fields_populated(self):
        lookup = self.mod.LookupModule()
        record = lookup._build_record(
            "HTTP/web.example.com", SAMPLE_IPA_CERT, "pem")
        meta = record["metadata"]
        self.assertEqual(meta["serial_number"], 12345)
        self.assertEqual(meta["subject"], "CN=web.example.com,O=EXAMPLE.COM")
        self.assertEqual(meta["san"], ["web.example.com", "web"])
        self.assertFalse(meta["revoked"])

    def test_build_record_san_empty_when_absent(self):
        lookup = self.mod.LookupModule()
        ipa_result = dict(SAMPLE_IPA_CERT)
        del ipa_result["san_dnsname"]
        record = lookup._build_record("HTTP/web.example.com", ipa_result, "pem")
        self.assertEqual(record["metadata"]["san"], [])

    # -----------------------------------------------------------------------
    # Result formatting
    # -----------------------------------------------------------------------

    def test_value_format_returns_bare_cert_string(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "request",
            "csr": SAMPLE_CSR,
            "encoding": "pem",
            "result_format": "value",
        }
        lookup = self._make_lookup(options)
        result = lookup.run(
            ["HTTP/web.example.com@EXAMPLE.COM"], variables={})
        self.assertIsInstance(result, list)
        self.assertIn("-----BEGIN CERTIFICATE-----", result[0])

    def test_record_format_returns_dict_with_metadata(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "request",
            "csr": SAMPLE_CSR,
            "encoding": "pem",
            "result_format": "record",
        }
        lookup = self._make_lookup(options)
        result = lookup.run(
            ["HTTP/web.example.com@EXAMPLE.COM"], variables={})
        self.assertIsInstance(result, list)
        self.assertIn("metadata", result[0])
        self.assertIn("value", result[0])
        self.assertEqual(result[0]["name"], "HTTP/web.example.com@EXAMPLE.COM")

    def test_map_format_returns_dict_keyed_by_principal(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "request",
            "csr": SAMPLE_CSR,
            "encoding": "pem",
            "result_format": "map",
        }
        lookup = self._make_lookup(options)
        result = lookup.run(
            ["HTTP/web.example.com@EXAMPLE.COM"], variables={})
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIn("HTTP/web.example.com@EXAMPLE.COM", result[0])
        self.assertIn(
            "-----BEGIN CERTIFICATE-----",
            result[0]["HTTP/web.example.com@EXAMPLE.COM"])

    def test_map_record_format_returns_dict_of_full_records(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "request",
            "csr": SAMPLE_CSR,
            "encoding": "pem",
            "result_format": "map_record",
        }
        lookup = self._make_lookup(options)
        result = lookup.run(
            ["HTTP/web.example.com@EXAMPLE.COM"], variables={})
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        record = result[0]["HTTP/web.example.com@EXAMPLE.COM"]
        self.assertIn("metadata", record)

    def test_multiple_terms_return_one_result_each(self):
        principals = [
            "HTTP/web.example.com@EXAMPLE.COM",
            "HTTP/api.example.com@EXAMPLE.COM",
        ]
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "request",
            "csr": SAMPLE_CSR,
            "encoding": "pem",
            "result_format": "value",
        }
        lookup = self._make_lookup(options)
        result = lookup.run(principals, variables={})
        self.assertEqual(len(result), 2)

    # -----------------------------------------------------------------------
    # request operation
    # -----------------------------------------------------------------------

    def test_request_passes_principal_to_api(self):
        seen = {}

        def fake_request(principal, csr, profile, ca, add):
            seen["principal"] = principal
            return dict(SAMPLE_IPA_CERT)

        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "request",
            "csr": SAMPLE_CSR,
            "result_format": "value",
        }
        lookup = self._make_lookup(options, request_cert=fake_request)
        lookup.run(["HTTP/web.example.com@EXAMPLE.COM"], variables={})
        self.assertEqual(seen["principal"], "HTTP/web.example.com@EXAMPLE.COM")

    def test_request_passes_profile_when_set(self):
        seen = {}

        def fake_request(principal, csr, profile, ca, add):
            seen["profile"] = profile
            return dict(SAMPLE_IPA_CERT)

        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "request",
            "csr": SAMPLE_CSR,
            "profile": "caIPAserviceCert",
            "result_format": "value",
        }
        lookup = self._make_lookup(options, request_cert=fake_request)
        lookup.run(["HTTP/web.example.com@EXAMPLE.COM"], variables={})
        self.assertEqual(seen["profile"], "caIPAserviceCert")

    def test_request_raises_on_not_found(self):
        def fake_request(principal, csr, profile, ca, add):
            raise self.mod.AnsibleLookupError("Principal not found")

        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "request",
            "csr": SAMPLE_CSR,
            "result_format": "value",
        }
        lookup = self._make_lookup(options, request_cert=fake_request)
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup.run(["HTTP/missing.example.com@EXAMPLE.COM"], variables={})

    def test_request_reads_csr_from_file(self):
        seen = {}

        def fake_request(principal, csr, profile, ca, add):
            seen["csr"] = csr
            return dict(SAMPLE_IPA_CERT)

        with tempfile.NamedTemporaryFile(
                mode='w', suffix='.pem', delete=False) as f:
            f.write(SAMPLE_CSR)
            csr_path = f.name

        try:
            options = {
                "server": "idm-01.example.com",
                "ipaadmin_principal": "admin",
                "ipaadmin_password": "secret",
                "operation": "request",
                "csr_file": csr_path,
                "result_format": "value",
            }
            lookup = self._make_lookup(options, request_cert=fake_request)
            lookup.run(["HTTP/web.example.com@EXAMPLE.COM"], variables={})
            self.assertEqual(seen["csr"], SAMPLE_CSR)
        finally:
            os.unlink(csr_path)

    def test_request_raises_when_csr_file_missing(self):
        lookup = self.mod.LookupModule()
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup._read_csr_file("/nonexistent/path/cert.csr")

    # -----------------------------------------------------------------------
    # retrieve operation
    # -----------------------------------------------------------------------

    def test_retrieve_calls_api_with_integer_serial(self):
        seen = {}

        def fake_retrieve(serial):
            seen["serial"] = serial
            return dict(SAMPLE_IPA_CERT)

        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "retrieve",
            "result_format": "value",
        }
        lookup = self._make_lookup(options, retrieve_cert=fake_retrieve)
        lookup.run(["12345"], variables={})
        self.assertEqual(seen["serial"], 12345)

    def test_retrieve_accepts_hex_serial(self):
        seen = {}

        def fake_retrieve(serial):
            seen["serial"] = serial
            return dict(SAMPLE_IPA_CERT)

        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "retrieve",
            "result_format": "value",
        }
        lookup = self._make_lookup(options, retrieve_cert=fake_retrieve)
        lookup.run(["0x3039"], variables={})
        self.assertEqual(seen["serial"], 12345)

    def test_retrieve_keys_result_by_serial_string(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "retrieve",
            "result_format": "map",
        }
        lookup = self._make_lookup(options)
        result = lookup.run(["12345"], variables={})
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIn("12345", result[0])

    def test_retrieve_rejects_invalid_serial(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "retrieve",
            "result_format": "value",
        }
        lookup = self._make_lookup(options)
        with self.assertRaises(self.mod.AnsibleLookupError):
            lookup.run(["not-a-serial"], variables={})

    # -----------------------------------------------------------------------
    # find operation
    # -----------------------------------------------------------------------

    def test_find_returns_list_for_value_format(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "find",
            "principal": "HTTP/web.example.com@EXAMPLE.COM",
            "result_format": "value",
        }
        lookup = self._make_lookup(options)
        result = lookup.run([], variables={})
        self.assertIsInstance(result, list)
        self.assertIn("-----BEGIN CERTIFICATE-----", result[0])

    def test_find_returns_dict_for_map_format(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "find",
            "principal": "HTTP/web.example.com@EXAMPLE.COM",
            "result_format": "map",
        }
        lookup = self._make_lookup(options)
        result = lookup.run([], variables={})
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)

    def test_find_returns_empty_list_when_no_matches(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "find",
            "subject": "nonexistent.example.com",
            "result_format": "value",
        }
        lookup = self._make_lookup(
            options, find_certs=lambda *a, **kw: [])
        result = lookup.run([], variables={})
        self.assertEqual(result, [])

    def test_find_keys_result_by_serial_number(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "find",
            "principal": "HTTP/web.example.com@EXAMPLE.COM",
            "result_format": "map_record",
        }
        lookup = self._make_lookup(options)
        result = lookup.run([], variables={})
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        # serial_number from SAMPLE_IPA_CERT is 12345
        self.assertIn("12345", result[0])

    def test_find_uses_hosts_filter_for_host_principal(self):
        captured = {}

        def fake_cert_find(**kwargs):
            captured.update(kwargs)
            return {"result": []}

        with mock.patch.object(
            self.mod._ipa_api.Command, "cert_find", side_effect=fake_cert_find
        ):
            lookup = self.mod.LookupModule()
            lookup._find_certs(
                "host/web.example.com@EXAMPLE.COM",
                None, None, None, None, False,
            )

        self.assertEqual(captured["host"], ["web.example.com"])
        self.assertNotIn("service", captured)

    def test_find_uses_services_filter_for_service_principal(self):
        captured = {}

        def fake_cert_find(**kwargs):
            captured.update(kwargs)
            return {"result": []}

        with mock.patch.object(
            self.mod._ipa_api.Command, "cert_find", side_effect=fake_cert_find
        ):
            lookup = self.mod.LookupModule()
            lookup._find_certs(
                "HTTP/web.example.com@EXAMPLE.COM",
                None, None, None, None, False,
            )

        self.assertEqual(
            captured["service"], ["HTTP/web.example.com@EXAMPLE.COM"])
        self.assertNotIn("host", captured)

    def test_find_warns_on_no_filters(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "find",
            "result_format": "value",
        }
        lookup = self._make_lookup(options)
        with mock.patch.object(self.mod.display, "warning") as warning:
            lookup.run([], variables={})
        warning.assert_called()

    def test_find_does_not_warn_when_filter_present(self):
        options = {
            "server": "idm-01.example.com",
            "ipaadmin_principal": "admin",
            "ipaadmin_password": "secret",
            "operation": "find",
            "principal": "HTTP/web.example.com@EXAMPLE.COM",
            "result_format": "value",
        }
        lookup = self._make_lookup(options)
        with mock.patch.object(self.mod.display, "warning") as warning:
            lookup.run([], variables={})
        warning.assert_not_called()

    # -----------------------------------------------------------------------
    # Credential cache lifecycle
    # -----------------------------------------------------------------------

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

    def test_cleanup_ccache_removes_unset_env_when_none_was_set(self):
        lookup = self.mod.LookupModule()
        original = os.environ.pop("KRB5CCNAME", None)
        ccache_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False) as ccache_file:
                ccache_path = ccache_file.name
                lookup._activate_ccache(
                    ccache_path,
                    "FILE:%s" % ccache_path,
                )
                lookup._cleanup_ccache()
                self.assertNotIn("KRB5CCNAME", os.environ)
        finally:
            if original is not None:
                os.environ["KRB5CCNAME"] = original
            if ccache_path and os.path.exists(ccache_path):
                os.unlink(ccache_path)

    def test_cleanup_ccache_disconnects_ipalib_backend_when_managed(self):
        lookup = self.mod.LookupModule()
        disconnect = mock.Mock()
        fake_backend = types.SimpleNamespace(
            isconnected=lambda: True,
            disconnect=disconnect,
        )
        ccache_path = None
        with tempfile.NamedTemporaryFile(delete=False) as ccache_file:
            ccache_path = ccache_file.name
            lookup._activate_ccache(
                ccache_path,
                "FILE:%s" % ccache_path,
            )
            with mock.patch.object(
                self.mod, "_ipa_api",
                types.SimpleNamespace(
                    Backend=types.SimpleNamespace(rpcclient=fake_backend)
                ),
            ), mock.patch.object(self.mod, "HAS_IPALIB", True):
                lookup._cleanup_ccache()
        if ccache_path and os.path.exists(ccache_path):
            os.unlink(ccache_path)
        disconnect.assert_called_once_with()

    # -----------------------------------------------------------------------
    # TLS verification
    # -----------------------------------------------------------------------

    def test_resolve_verify_uses_explicit_path(self):
        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.os.path, "exists", return_value=True):
            result = lookup._resolve_verify("/etc/ipa/custom-ca.crt")
        self.assertEqual(result, "/etc/ipa/custom-ca.crt")

    def test_resolve_verify_falls_back_to_default_ca(self):
        lookup = self.mod.LookupModule()

        def exists_side_effect(path):
            return path == "/etc/ipa/ca.crt"

        with mock.patch.object(
                self.mod.os.path, "exists", side_effect=exists_side_effect):
            result = lookup._resolve_verify(None)
        self.assertEqual(result, "/etc/ipa/ca.crt")

    def test_resolve_verify_requires_explicit_trust_or_opt_out(self):
        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.os.path, "exists", return_value=False):
            with self.assertRaises(self.mod.AnsibleLookupError) as ctx:
                lookup._resolve_verify(None)
        self.assertIn("verify", exception_text(ctx.exception))

    def test_resolve_verify_raises_when_explicit_path_missing(self):
        lookup = self.mod.LookupModule()
        with mock.patch.object(self.mod.os.path, "exists", return_value=False):
            with self.assertRaises(self.mod.AnsibleLookupError):
                lookup._resolve_verify("/nonexistent/ca.crt")

    # -----------------------------------------------------------------------
    # File permission warnings
    # -----------------------------------------------------------------------

    def test_warns_when_sensitive_file_is_group_or_world_readable(self):
        lookup = self.mod.LookupModule()
        with tempfile.NamedTemporaryFile() as secret_file:
            os.chmod(secret_file.name, 0o644)
            with mock.patch.object(self.mod.display, "warning") as warning:
                lookup._warn_if_sensitive_file_permissive(
                    secret_file.name, "csr_file")
        warning.assert_called_once()

    def test_does_not_warn_when_sensitive_file_is_owner_only(self):
        lookup = self.mod.LookupModule()
        with tempfile.NamedTemporaryFile() as secret_file:
            os.chmod(secret_file.name, 0o600)
            with mock.patch.object(self.mod.display, "warning") as warning:
                lookup._warn_if_sensitive_file_permissive(
                    secret_file.name, "kerberos_keytab")
        warning.assert_not_called()


if __name__ == "__main__":
    unittest.main()
