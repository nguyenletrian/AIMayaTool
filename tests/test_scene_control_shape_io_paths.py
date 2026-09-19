import os,tempfile,unittest
from aimayatool.tools.scene.control_shape_io import resolve_scene_data_path
class Tests(unittest.TestCase):
 def test_local(self):
  p=resolve_scene_data_path(os.path.join("work","char","rig.ma"),"local"); self.assertTrue(p.endswith(os.path.join("char","SceneData","dataCurveShape.json")))
 def test_parent(self):
  p=resolve_scene_data_path(os.path.join("work","char","rig.ma"),"parent"); self.assertTrue(p.endswith(os.path.join("work","SceneData","dataCurveShape.json")))
 def test_missing(self):
  with self.assertRaises(ValueError): resolve_scene_data_path("")
 def test_layout(self):
  with self.assertRaises(ValueError): resolve_scene_data_path("rig.ma","other")
if __name__=="__main__": unittest.main()
