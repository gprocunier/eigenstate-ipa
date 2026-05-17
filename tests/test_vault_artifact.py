import base64
import hashlib
import importlib.util
import pathlib
import sys
import types
import unittest


def _load_vault_artifact_module():
    module_name = "eigenstate_ipa_test_vault_artifact"
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "plugins"
        / "modules"
        / "vault_artifact.py"
    )
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class NotFound(Exception):
    pass


class FakeVaultCommands:
    def __init__(self):
        self.vaults = {}

    def vault_show(self, name, **kwargs):
        if name not in self.vaults:
            raise NotFound("not found")
        return {"result": dict(self.vaults[name]["entry"])}

    def vault_add(self, name, **kwargs):
        self.vaults[name] = {
            "entry": {
                "cn": [name],
                "ipavaulttype": [kwargs.get("ipavaulttype", "standard")],
                "description": [kwargs.get("description", "")],
                "ipavaultid": ["vault-%s" % name],
            },
            "data": b"",
        }
        return {"result": dict(self.vaults[name]["entry"])}

    def vault_archive(self, name, **kwargs):
        if name not in self.vaults:
            raise NotFound("not found")
        self.vaults[name]["data"] = kwargs["data"]
        return {"result": {}}

    def vault_retrieve(self, name, **kwargs):
        if name not in self.vaults:
            raise NotFound("not found")
        return {"result": {"data": self.vaults[name]["data"]}}

    def vault_del(self, name, **kwargs):
        if name not in self.vaults:
            raise NotFound("not found")
        del self.vaults[name]
        return {"result": {}}


class VaultArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_vault_artifact_module()

    def _api(self):
        commands = FakeVaultCommands()
        return types.SimpleNamespace(Command=commands), commands

    def _params(self, **overrides):
        params = {
            "name": "bundle",
            "state": "present",
            "server": "idm-01.example.com",
            "username": None,
            "service": None,
            "shared": True,
            "vault_type": "standard",
            "description": "bootstrap bundle",
            "payload": "artifact data",
            "payload_file": None,
            "expected_sha256": None,
            "read_back": True,
            "include_metadata": True,
            "include_payload": False,
            "payload_encoding": "base64",
            "vault_password": None,
            "vault_password_file": None,
            "private_key_file": None,
        }
        params.update(overrides)
        return params

    def test_write_artifact_returns_digest_and_verified_readback(self):
        api, commands = self._api()
        params = self._params()

        result = self.mod.run_artifact(api, params)

        expected_digest = hashlib.sha256(b"artifact data").hexdigest()
        self.assertTrue(result["changed"])
        self.assertEqual(result["artifact_ref"], "shared/bundle")
        self.assertEqual(result["artifact_sha256"], expected_digest)
        self.assertTrue(result["read_back_verified"])
        self.assertEqual(result["vault_type"], "standard")
        self.assertEqual(result["vault_id"], "vault-bundle")
        self.assertNotIn("artifact_payload", result)
        self.assertEqual(commands.vaults["bundle"]["data"], b"artifact data")

    def test_expected_digest_mismatch_fails_before_archive(self):
        api, commands = self._api()
        params = self._params(expected_sha256="0" * 64)

        with self.assertRaises(self.mod.VaultArtifactError) as ctx:
            self.mod.run_artifact(api, params)

        self.assertEqual(ctx.exception.failure_class, "digest_mismatch")
        self.assertEqual(commands.vaults, {})

    def test_read_artifact_verifies_digest_without_payload_by_default(self):
        api, commands = self._api()
        commands.vault_add("bundle", ipavaulttype="standard")
        commands.vault_archive("bundle", data=b"read me")
        digest = hashlib.sha256(b"read me").hexdigest()

        result = self.mod.run_artifact(
            api,
            self._params(
                state="read",
                payload=None,
                expected_sha256=digest,
            ),
        )

        self.assertFalse(result["changed"])
        self.assertEqual(result["artifact_sha256"], digest)
        self.assertTrue(result["read_back_verified"])
        self.assertNotIn("artifact_payload", result)

    def test_read_artifact_can_return_base64_payload_when_requested(self):
        api, commands = self._api()
        commands.vault_add("bundle", ipavaulttype="standard")
        commands.vault_archive("bundle", data=b"read me")

        result = self.mod.run_artifact(
            api,
            self._params(
                state="read",
                payload=None,
                include_payload=True,
            ),
        )

        self.assertEqual(
            result["artifact_payload"],
            base64.b64encode(b"read me").decode("ascii"),
        )

    def test_read_missing_artifact_is_structured_error(self):
        api, _commands = self._api()

        with self.assertRaises(self.mod.VaultArtifactError) as ctx:
            self.mod.run_artifact(
                api,
                self._params(state="read", payload=None),
            )

        self.assertEqual(ctx.exception.failure_class, "vault_not_found")

    def test_readback_mismatch_fails(self):
        api, commands = self._api()
        original_retrieve = commands.vault_retrieve

        def mismatch_once(name, **kwargs):
            return {"result": {"data": b"different"}}

        commands.vault_retrieve = mismatch_once

        with self.assertRaises(self.mod.VaultArtifactError) as ctx:
            self.mod.run_artifact(api, self._params())

        commands.vault_retrieve = original_retrieve
        self.assertEqual(ctx.exception.failure_class, "digest_mismatch")

    def test_absent_deletes_existing_artifact(self):
        api, commands = self._api()
        commands.vault_add("bundle", ipavaulttype="standard")

        result = self.mod.run_artifact(
            api,
            self._params(state="absent", payload=None),
        )

        self.assertTrue(result["changed"])
        self.assertNotIn("bundle", commands.vaults)

    def test_sha256_helper(self):
        self.assertEqual(
            self.mod._sha256(b"abc"),
            hashlib.sha256(b"abc").hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
