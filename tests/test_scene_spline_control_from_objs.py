import unittest
from aimayatool.tools.scene.spline_control_from_objs import normalize_spline_control_from_objs
class Tests(unittest.TestCase):
 def test_normalize(self):
  p=normalize_spline_control_from_objs({"parent":"rig","parentGlobal":"world","curve":"c","joints":"a_SplineJnt\nb_SplineJnt\nc_SplineJnt","numberCtrls":"2"})
  self.assertEqual(p["controls"],["a","b","c"]); self.assertEqual(p["parameters"],[0.0,1.0/3.0,2.0/3.0,1.0]); self.assertEqual(p["globalGroup"],"a_SplineControls_GlobalGrp")
 def test_defaults(self):
  p=normalize_spline_control_from_objs({"parent":"rig","parentGlobal":"world","curve":"c","joints":["a_SplineJnt","b_SplineJnt"]}); self.assertEqual(p["numberCtrls"],1)
 def test_invalid(self):
  for v in ({},{"parent":"r","parentGlobal":"w","curve":"c","joints":["a"]},{"parent":"r","parentGlobal":"w","curve":"c","joints":["a","b"],"numberCtrls":-1}):
   with self.assertRaises((ValueError,TypeError)): normalize_spline_control_from_objs(v)
if __name__=="__main__": unittest.main()
