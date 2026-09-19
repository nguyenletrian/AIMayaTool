import unittest
from aimayatool.tools.scene.control_shape_snapshot import normalize_curve_shape_snapshot,build_curve_shape_restore_plan
class Tests(unittest.TestCase):
 def data(self): return {"RigA":{"overrideEnabled":1,"overrideRGBColors":0,"overrideColor":17,"curveData":{"RigAShape":{"pointData":{"controlPoints[1]":[1,0,0],"controlPoints[0]":[0,0,0]}}}}}
 def test_normalize(self):
  x=normalize_curve_shape_snapshot(self.data()); self.assertEqual(list(x["controls"]),["RigA"]); self.assertEqual(len(x["controls"]["RigA"]["shapes"]["RigAShape"]["points"]),2)
 def test_update_same_count(self):
  p=build_curve_shape_restore_plan(self.data(),{"RigA":{"RigAShape":2}}); self.assertEqual(p["shapes"][0]["action"],"update")
 def test_rebuild_missing_or_count_changed(self):
  self.assertEqual(build_curve_shape_restore_plan(self.data(),{})["shapes"][0]["action"],"rebuild")
 def test_invalid(self):
  with self.assertRaises(TypeError): normalize_curve_shape_snapshot([])
if __name__=="__main__": unittest.main()
