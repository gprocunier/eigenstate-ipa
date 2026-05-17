import importlib.util
import pathlib
import sys
import unittest


def _load_normalization_module():
    module_name = "eigenstate_ipa_test_attribute_normalization"
    module_path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "plugins"
        / "module_utils"
        / "attribute_normalization.py"
    )
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AttributeNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_normalization_module()

    def test_missing_list_becomes_empty_with_type_metadata(self):
        result = self.mod.normalize_attribute(
            None, attribute="idm_userclass", expected="list", missing=True)
        self.assertEqual(result["value"], [])
        self.assertIsNone(result["raw"])
        self.assertEqual(result["type"], "missing")
        self.assertEqual(result["warnings"], [])

    def test_none_list_becomes_empty_with_none_type(self):
        result = self.mod.normalize_attribute(
            None, attribute="idm_userclass", expected="list")
        self.assertEqual(result["value"], [])
        self.assertEqual(result["type"], "none")

    def test_string_list_becomes_single_item_with_warning(self):
        result = self.mod.normalize_attribute(
            "blue", attribute="idm_userclass", expected="list")
        self.assertEqual(result["value"], ["blue"])
        self.assertEqual(result["raw"], "blue")
        self.assertEqual(result["type"], "string")
        self.assertEqual(result["warnings"][0]["action"], "normalized")

    def test_empty_string_list_becomes_empty_with_warning(self):
        result = self.mod.normalize_attribute(
            "", attribute="idm_userclass", expected="list")
        self.assertEqual(result["value"], [])
        self.assertEqual(result["warnings"][0]["action"], "empty")

    def test_list_of_strings_is_preserved(self):
        result = self.mod.normalize_attribute(
            ["db", "web"], attribute="idm_userclass", expected="list")
        self.assertEqual(result["value"], ["db", "web"])
        self.assertEqual(result["raw"], ["db", "web"])
        self.assertEqual(result["type"], "list")
        self.assertEqual(result["warnings"], [])

    def test_list_of_non_strings_converts_scalars_and_rejects_nested(self):
        result = self.mod.normalize_attribute(
            ["db", 42, {"bad": "shape"}, ["nested"]],
            attribute="idm_userclass",
            expected="list",
        )
        self.assertEqual(result["value"], ["db", "42"])
        self.assertEqual(
            [warning["action"] for warning in result["warnings"]],
            ["rejected", "normalized"],
        )

    def test_dict_list_is_rejected_not_stringified(self):
        result = self.mod.normalize_attribute(
            {"class": "db"}, attribute="idm_userclass", expected="list")
        self.assertEqual(result["value"], [])
        self.assertEqual(result["raw"], {"class": "db"})
        self.assertEqual(result["type"], "dict")
        self.assertEqual(result["warnings"][0]["action"], "rejected")

    def test_nested_dict_list_is_rejected_not_stringified(self):
        result = self.mod.normalize_attribute(
            {"outer": {"inner": "value"}},
            attribute="idm_userclass",
            expected="list",
        )
        self.assertEqual(result["value"], [])
        self.assertEqual(result["warnings"][0]["actual"], "dict")

    def test_unicode_values_are_preserved(self):
        result = self.mod.normalize_attribute(
            ["cafe", "naive", "東京"],
            attribute="idm_userclass",
            expected="list",
        )
        self.assertEqual(result["value"], ["cafe", "naive", "東京"])

    def test_ensure_list_returns_normalized_value_only(self):
        self.assertEqual(self.mod.ensure_list("ops"), ["ops"])

    def test_attribute_type_labels(self):
        self.assertEqual(self.mod.attribute_type([], missing=False), "list")
        self.assertEqual(self.mod.attribute_type({}, missing=False), "dict")
        self.assertEqual(self.mod.attribute_type(None, missing=False), "none")
        self.assertEqual(self.mod.attribute_type(None, missing=True), "missing")


if __name__ == "__main__":
    unittest.main()
