from __future__ import absolute_import

import unittest
from aimayatool.tools.scene.clear_offset import build_clear_offset_plan, execute_clear_offset_plan


class ClearOffsetSmokeTest(unittest.TestCase):
    def test_plan_and_parent_preserving_execution(self):
        plan=build_clear_offset_plan([{"objects":"arm_L\narm_R"}])
        self.assertEqual(plan,({"object":"arm_L","group_name":"arm_L_ClearOffsetGrp"},{"object":"arm_R","group_name":"arm_R_ClearOffsetGrp"}))
        class FakeCmds(object):
            def __init__(self): self.calls=[]
            def objExists(self,node): return node in ("arm_L","arm_R")
            def listRelatives(self,node,parent,fullPath): return ["|Rig_GRP"]
            def group(self,empty,name): self.calls.append(("group",name)); return name
            def parentConstraint(self,obj,group,maintainOffset): self.calls.append(("parentConstraint",obj,group,maintainOffset)); return ["tmpConstraint"]
            def delete(self,node): self.calls.append(("delete",node))
            def parent(self,node,parent): self.calls.append(("parent",node,parent)); return [node]
        fake=FakeCmds(); result=execute_clear_offset_plan(plan,cmds_module=fake)
        self.assertEqual(result[0]["original_parent"],"|Rig_GRP"); self.assertEqual(result[0]["group"],"arm_L_ClearOffsetGrp")
        self.assertIn(("parent","arm_L_ClearOffsetGrp","|Rig_GRP"),fake.calls); self.assertIn(("parent","arm_L","arm_L_ClearOffsetGrp"),fake.calls)
        print("SCENE_CLEAR_OFFSET_PYTHON_SMOKE_OK")


if __name__ == "__main__": unittest.main()
