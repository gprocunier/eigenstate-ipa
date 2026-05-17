import importlib.util
import pathlib
import sys
import types
import unittest

from datetime import datetime, timezone


def _load_vault_health_module():
    module_name = "eigenstate_ipa_test_vault_health"
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "plugins"
        / "modules"
        / "vault_health.py"
    )
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class VaultHealthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_vault_health_module()

    def _params(self, **overrides):
        params = {
            "server": "idm-01.example.com",
            "username": None,
            "service": None,
            "shared": True,
            "canary_vault": "health-canary",
            "canary_max_age_seconds": 3600,
            "require_direct_kra": False,
        }
        params.update(overrides)
        return params

    def test_healthy_kra_with_canary(self):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%SZ")
        api = types.SimpleNamespace(Command=types.SimpleNamespace(
            kra_is_enabled=lambda: {"result": True},
            vault_show=lambda name, **kwargs: {
                "result": {"cn": [name], "modifytimestamp": [timestamp]},
            },
        ))

        result = self.mod.run_health(api, self._params())

        self.assertTrue(result["idm_reachable"])
        self.assertTrue(result["vault_reachable"])
        self.assertTrue(result["kra_available"])
        self.assertTrue(result["canary_present"])
        self.assertFalse(result["canary_stale"])
        self.assertEqual(result["failure_class"], "none")

    def test_kra_unavailable_is_not_generic_ldap_failure(self):
        def kra_is_enabled():
            raise Exception("KRA is not enabled on this server")

        api = types.SimpleNamespace(Command=types.SimpleNamespace(
            kra_is_enabled=kra_is_enabled,
            vault_find=lambda *args, **kwargs: {"result": []},
        ))

        result = self.mod.run_health(
            api,
            self._params(
                canary_vault=None,
                require_direct_kra=True,
            ),
        )

        self.assertFalse(result["kra_available"])
        self.assertEqual(result["failure_class"], "kra_unavailable")

    def test_canary_missing_keeps_vault_reachable(self):
        NotFound = type("NotFound", (Exception,), {})

        def vault_show(name, **kwargs):
            raise NotFound("not found")

        api = types.SimpleNamespace(Command=types.SimpleNamespace(
            kra_is_enabled=lambda: {"result": True},
            vault_show=vault_show,
        ))

        result = self.mod.run_health(api, self._params())

        self.assertTrue(result["vault_reachable"])
        self.assertFalse(result["canary_present"])
        self.assertEqual(result["failure_class"], "vault_not_found")

    def test_canary_stale_is_structured(self):
        api = types.SimpleNamespace(Command=types.SimpleNamespace(
            kra_is_enabled=lambda: {"result": True},
            vault_show=lambda name, **kwargs: {
                "result": {
                    "cn": [name],
                    "modifytimestamp": ["20000101000000Z"],
                },
            },
        ))

        result = self.mod.run_health(
            api,
            self._params(canary_max_age_seconds=1),
        )

        self.assertTrue(result["canary_stale"])
        self.assertEqual(result["failure_class"], "unknown")
        self.assertIn("stale", result["message"])

    def test_vault_find_without_canary_sets_reachable(self):
        api = types.SimpleNamespace(Command=types.SimpleNamespace(
            vaultconfig_show=lambda: {"result": {"kra_server_server": ["idm-01"]}},
            vault_find=lambda *args, **kwargs: {"result": []},
        ))

        result = self.mod.run_health(
            api,
            self._params(canary_vault=None),
        )

        self.assertTrue(result["kra_available"])
        self.assertTrue(result["vault_reachable"])
        self.assertEqual(result["canary_present"], "unknown")
        self.assertEqual(result["failure_class"], "none")

    def test_ca_failure_classification(self):
        self.assertEqual(
            self.mod._classify_exception(
                Exception("certificate verify failed: unknown CA")),
            "ca",
        )

    def test_auth_failure_classification(self):
        self.assertEqual(
            self.mod._classify_exception(
                Exception("Kerberos credential error")),
            "auth",
        )

    def test_timeout_failure_classification(self):
        self.assertEqual(
            self.mod._classify_exception(Exception("request timed out")),
            "timeout",
        )


if __name__ == "__main__":
    unittest.main()
