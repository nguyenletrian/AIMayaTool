import unittest
from aimayatool.tools.scene.spline_rig import normalize_spline_rig

class SplineRigTests(unittest.TestCase):
    def test_normalize(self):
        plan = normalize_spline_rig({"parent":"rig","parentGlobal":"world","controls":"a\nb\nc","numberCtrls":"2","rebuild":"24"})
        self.assertEqual(plan["controls"], ["a","b","c"])
        self.assertEqual(plan["totalControlJoints"], 4)
        self.assertEqual(plan["parameters"], [0.0, 1.0/3.0, 2.0/3.0, 1.0])
        self.assertEqual(plan["splineJoints"], ["a_SplineJnt","b_SplineJnt","c_SplineJnt"])
        self.assertEqual(plan["rigGroup"], "a_SplineRig")
        self.assertEqual(plan["rebuild"], 24)

    def test_defaults(self):
        plan = normalize_spline_rig({"parent":"rig","parentGlobal":"world","controls":["a","b"]})
        self.assertEqual(plan["numberCtrls"], 1)
        self.assertEqual(plan["rebuild"], 100)
        self.assertEqual(plan["parameters"], [0.0, 0.5, 1.0])

    def test_invalid(self):
        values = [
            {}, {"parent":"rig","parentGlobal":"world","controls":["a"]},
            {"parent":"rig","parentGlobal":"","controls":["a","b"]},
            {"parent":"rig","parentGlobal":"world","controls":["a","b"],"numberCtrls":-1},
            {"parent":"rig","parentGlobal":"world","controls":["a","b"],"rebuild":0},
        ]
        for value in values:
            with self.assertRaises((ValueError, TypeError)):
                normalize_spline_rig(value)

if __name__ == "__main__":
    unittest.main()
