import unittest

from aimayatool.tools.scene.default_value import _coerce_default_value


class DefaultValueTests(unittest.TestCase):
    def test_numeric_coercion(self):
        self.assertEqual(_coerce_default_value("double", "12.5"), 12.5)
        self.assertEqual(_coerce_default_value("long", "12"), 12)

    def test_string_and_passthrough(self):
        self.assertEqual(_coerce_default_value("string", 42), "42")
        marker = object()
        self.assertIs(_coerce_default_value("matrix", marker), marker)

    def test_invalid_numeric_raises_before_host_mutation(self):
        with self.assertRaises(ValueError):
            _coerce_default_value("double", "not-a-number")
        with self.assertRaises(ValueError):
            _coerce_default_value("long", "12.5")


if __name__ == "__main__":
    unittest.main()
