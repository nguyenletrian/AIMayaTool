import unittest
from aimayatool.tools.scene.ikfk_switch import normalize_ikfk_snap_item,expand_ikfk_snap_items,build_ikfk_snap_plan
class Tests(unittest.TestCase):
 def data(self):
  return {"controlParent":"Main","switchControl":"FKIKArm_R","switchAttr":"FKIKBlend","valueActive":"10","refObjects":"FKShoulder_R\nFKElbow_R","sources":"PoleArm_R\nIKArm_R","targets":"Elbow_R\nWrist_R","mirror":True}
 def test_normalize(self):
  x=normalize_ikfk_snap_item(self.data()); self.assertEqual(x["valueActive"],10); self.assertEqual(x["sources"],["PoleArm_R","IKArm_R"])
 def test_mirror_expand(self):
  xs=expand_ikfk_snap_items([self.data()],lambda n:n.replace("_R","_L")); self.assertEqual(len(xs),2); self.assertEqual(xs[1]["switchControl"],"FKIKArm_L"); self.assertFalse(xs[1]["mirror"])
 def test_add_keys_variant(self):
  p=build_ikfk_snap_plan([dict(self.data(),mirror=False)],add_keys=True); self.assertEqual(p["keyAttributes"],["tx","ty","tz","rx","ry","rz"]); self.assertEqual(len(p["matrixAttributes"]),2)
 def test_invalid_pair(self):
  with self.assertRaises(ValueError): normalize_ikfk_snap_item({"switchControl":"a","switchAttr":"b","sources":"x","targets":"y\nz"})
if __name__=="__main__": unittest.main()
