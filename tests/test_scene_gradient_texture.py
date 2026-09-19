import unittest

from aimayatool.tools.scene.gradient_texture import normalize_gradient_texture


class GradientTextureTests(unittest.TestCase):
    def test_normalize(self):
        plan = normalize_gradient_texture({"object": "body", "type": 1, "interpolation": 2, "whiteBegin": .2, "blackBegin": .8, "runColor": "white", "minValue": -1, "maxValue": 2, "objConnect": "ctrl", "attrConnect": "fade"})
        self.assertEqual(plan["driverAttr"], "ctrl.fade")
        self.assertEqual(plan["runIndex"], 0)
        self.assertEqual((plan["inputMin"], plan["inputMax"]), (0.0, 10.0))

    def test_reverse_black(self):
        plan = normalize_gradient_texture({"object": "body", "runColor": "black", "objConnect": "ctrl", "attrConnect": "fade", "reverse": True})
        self.assertEqual(plan["runIndex"], 1)
        self.assertEqual((plan["inputMin"], plan["inputMax"]), (10.0, 0.0))

    def test_invalid(self):
        for value in ({}, {"object": "body", "objConnect": "ctrl", "attrConnect": ""}, {"object": "body", "objConnect": "ctrl", "attrConnect": "fade", "runColor": "blue"}):
            with self.assertRaises(ValueError):
                normalize_gradient_texture(value)


if __name__ == "__main__":
    unittest.main()
