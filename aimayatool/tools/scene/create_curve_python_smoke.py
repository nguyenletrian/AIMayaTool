from __future__ import absolute_import

import unittest
from aimayatool.tools.scene.create_curve import build_create_curve_plan, execute_create_curve_plan


class CreateCurveSmokeTest(unittest.TestCase):
    def test_plan_and_injected_execution(self):
        plan = build_create_curve_plan({"points":"0 0 0\n1 0 0\n2 1 0\n3 1 0", "curveName":"Path_CTRL", "parent":"Rig_GRP", "rebuild":"5"})
        self.assertEqual(plan["points"], ((0.0,0.0,0.0),(1.0,0.0,0.0),(2.0,1.0,0.0),(3.0,1.0,0.0)))
        self.assertEqual(plan["degree"], 3); self.assertEqual(plan["rebuild_spans"], 5); self.assertTrue(plan["hidden"])
        class FakeCmds(object):
            def __init__(self): self.calls=[]
            def objExists(self, value): return value == "Rig_GRP"
            def curve(self, **kwargs): self.calls.append(("curve",kwargs)); return "Path_CTRL"
            def setAttr(self, *args): self.calls.append(("setAttr",args))
            def parent(self, node, parent): self.calls.append(("parent",node,parent)); return [node]
            def rebuildCurve(self, *args, **kwargs): self.calls.append(("rebuildCurve",args,kwargs)); return ["rebuildResult"]
            def rename(self, node, name): self.calls.append(("rename",node,name)); return name
        fake=FakeCmds(); result=execute_create_curve_plan(plan, cmds_module=fake)
        self.assertEqual(result["curve"], "Path_CTRL"); self.assertEqual(result["rebuilt_curve"], "Path_CTRL_Rebuild")
        self.assertEqual(result["degree"], 3); self.assertEqual(result["point_count"], 4); self.assertEqual(result["rebuild_spans"], 5)
        self.assertEqual(fake.calls[0][0], "curve"); self.assertTrue(any(call[0] == "rebuildCurve" for call in fake.calls))
        print("SCENE_CREATE_CURVE_PYTHON_SMOKE_OK")

    def test_validation_and_degree(self):
        self.assertEqual(build_create_curve_plan({"points":"0 0 0\n1 0 0", "curveName":"line"})["degree"], 1)
        with self.assertRaises(ValueError): build_create_curve_plan({"points":"0 0 0", "curveName":"bad"})
        with self.assertRaises(ValueError): build_create_curve_plan({"points":"0 0\n1 0 0", "curveName":"bad"})


if __name__ == "__main__": unittest.main()
