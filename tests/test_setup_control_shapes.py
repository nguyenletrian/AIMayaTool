import unittest

from aimayatool.tools.setup import controls


class SetupControlShapeTests(unittest.TestCase):
    def test_legacy_catalog_core_shapes_available(self):
        shapes = set(controls.available_shapes())
        for name in ("circle", "box", "cube", "sphere", "diamond", "locator", "eye"):
            self.assertIn(name, shapes)

    def test_cube_alias_matches_box_points(self):
        self.assertEqual(controls._scaled_points("cube", 1.0), controls._scaled_points("box", 1.0))

    def test_scaling_is_deterministic(self):
        base = controls._scaled_points("diamond", 1.0)
        doubled = controls._scaled_points("diamond", 2.0)
        self.assertEqual(doubled, [(x * 2.0, y * 2.0, z * 2.0) for x, y, z in base])

    def test_invalid_shape_and_size_raise(self):
        with self.assertRaises(ValueError):
            controls._scaled_points("missing", 1.0)
        with self.assertRaises(ValueError):
            controls._scaled_points("circle", 0.0)

    def test_shape_plug_remap_only_changes_target_shape_prefix(self):
        self.assertEqual("|ctrl|newShape.visibility", controls._remap_shape_plug("|ctrl|oldShape.visibility", "|ctrl|oldShape", "|ctrl|newShape"))
        self.assertEqual("driver.output", controls._remap_shape_plug("driver.output", "|ctrl|oldShape", "|ctrl|newShape"))


if __name__ == "__main__":
    unittest.main()
