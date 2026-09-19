import unittest
from aimayatool.tools.scene.spline_curve_from_objs import normalize_spline_curve_from_objs

class SplineCurveFromObjsTests(unittest.TestCase):
    def test_normalize(self):
        p=normalize_spline_curve_from_objs({"parent":"rig","controls":"a\nb\nc","rebuild":"24"})
        self.assertEqual(p["controls"],["a","b","c"]); self.assertEqual(p["rebuild"],24)
        self.assertEqual(p["joints"],["a_SplineJnt","b_SplineJnt","c_SplineJnt"])
        self.assertEqual(p["curve"],"a_SplineJnt_SplineCurve")
        self.assertEqual(p["hiddenGroup"],"a_SplineRigHidden")
    def test_defaults(self):
        p=normalize_spline_curve_from_objs({"parent":"rig","controls":["a","b"]})
        self.assertEqual(p["rebuild"],100)
    def test_invalid(self):
        for value in ({},{"parent":"rig","controls":["a"]},{"parent":"rig","controls":["a","b"],"rebuild":0}):
            with self.assertRaises((ValueError,TypeError)): normalize_spline_curve_from_objs(value)

if __name__=="__main__": unittest.main()
