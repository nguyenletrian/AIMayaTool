import unittest

from aimayatool import preflight


class PreflightGuidanceTests(unittest.TestCase):
    def test_ok_result_has_stable_shape(self):
        result = preflight.preflight_ok("selection", "Selection is ready.")
        self.assertEqual(result, {"valid": True, "severity": "info", "category": "selection", "message": "Selection is ready."})

    def test_issue_is_actionable_and_nonmutating(self):
        source = ["meshA"]
        before = list(source)
        result = preflight.preflight_issue("selection", "Select at least two transforms.", severity="warning")
        self.assertEqual(source, before)
        self.assertFalse(result["valid"])
        self.assertEqual(result["severity"], "warning")
        self.assertEqual(result["category"], "selection")
        self.assertTrue(result["message"])

    def test_invalid_contract_values_are_rejected(self):
        with self.assertRaises(ValueError):
            preflight.preflight_result("", "Message")
        with self.assertRaises(ValueError):
            preflight.preflight_result("selection", "")
        with self.assertRaises(ValueError):
            preflight.preflight_result("selection", "Message", severity="fatal")


if __name__ == "__main__":
    unittest.main()
