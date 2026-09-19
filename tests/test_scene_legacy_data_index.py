import unittest
from aimayatool.tools.scene.pattern_descriptor import normalize_legacy_scene_data_index,build_legacy_scene_data_index_plan
class Tests(unittest.TestCase):
 def test_path_string_and_list(self):
  data=[{"id":"2","moduleName":"B","order":2,"path":["D:\\Work\\b.json"]},{"id":"1","moduleName":"A","order":1,"path":"D:\\Work\\a.json"}]
  out=normalize_legacy_scene_data_index(data); self.assertEqual([x["id"] for x in out],["1","2"]); self.assertEqual(out[1]["path"],"D:/Work/b.json")
 def test_plan_by_id(self):
  p=build_legacy_scene_data_index_plan([{"id":"7","moduleName":"Scene_Pattern_Global","path":"x.json"}]); self.assertEqual(p["by_id"]["7"]["module_name"],"Scene_Pattern_Global")
 def test_invalid(self):
  with self.assertRaises(TypeError): normalize_legacy_scene_data_index({})
if __name__=="__main__": unittest.main()
