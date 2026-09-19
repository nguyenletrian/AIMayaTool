from __future__ import absolute_import
import os
import tempfile
import unittest
from aimayatool.tools.scene import script_hooks

class ScriptHooksTests(unittest.TestCase):
    def test_descriptors(self):
        self.assertEqual(script_hooks.get_hook("current_after")["phase"], "after")
        self.assertEqual(script_hooks.get_hook("current_post")["phase"], "post")
        self.assertEqual(script_hooks.get_hook("up_after")["scope"], "up")
        self.assertRaises(KeyError, script_hooks.get_hook, "missing")

    def test_current_and_up_paths(self):
        scene = os.path.join("root", "shot", "work", "scene.ma")
        current = script_hooks.scene_data_path(scene, "current_after")
        up = script_hooks.scene_data_path(scene, "up_post")
        self.assertTrue(current.endswith(os.path.join("work", "SceneData", "Scene_Pattern_CurrentAfterScript.py")))
        self.assertTrue(up.endswith(os.path.join("shot", "SceneData", "Scene_Pattern_UpPostScript.py")))

    def test_run_hook_delegates_execution(self):
        fd, path = tempfile.mkstemp(suffix=".py")
        os.close(fd)
        try:
            with open(path, "w") as stream:
                stream.write("RESULT = VALUE + 1\n")
            ns = script_hooks.run_hook(path, {"VALUE": 4})
            self.assertEqual(ns["RESULT"], 5)
        finally:
            os.remove(path)

if __name__ == "__main__":
    unittest.main()
