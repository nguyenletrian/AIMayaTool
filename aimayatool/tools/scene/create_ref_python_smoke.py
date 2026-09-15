from __future__ import absolute_import

import unittest
from aimayatool.tools.scene.create_ref import build_create_ref_plan, execute_create_ref_plan


class CreateRefSmokeTest(unittest.TestCase):
    def test_plan_and_injected_execution(self):
        plan=build_create_ref_plan([{"objects":"arm_L\narm_R","parent":"Rig_GRP"}])
        self.assertEqual(plan,({"object":"arm_L","reference_name":"arm_L_Ref","parent":"Rig_GRP"},{"object":"arm_R","reference_name":"arm_R_Ref","parent":"Rig_GRP"}))
        class FakeCmds(object):
            def __init__(self): self.existing={"arm_L","arm_R","Rig_GRP"}; self.calls=[]
            def objExists(self,node): return node in self.existing
            def group(self,empty,name): self.calls.append(("group",name)); self.existing.add(name); return name
            def matchTransform(self,ref,obj): self.calls.append(("matchTransform",ref,obj))
            def parent(self,ref,parent): self.calls.append(("parent",ref,parent)); return [ref]
        fake=FakeCmds(); result=execute_create_ref_plan(plan,cmds_module=fake)
        self.assertEqual(tuple(x["reference"] for x in result),("arm_L_Ref","arm_R_Ref")); self.assertEqual(result[0]["status"],"created")
        self.assertIn(("matchTransform","arm_L_Ref","arm_L"),fake.calls); self.assertIn(("parent","arm_R_Ref","Rig_GRP"),fake.calls)
        print("SCENE_CREATE_REF_PYTHON_SMOKE_OK")


if __name__ == "__main__": unittest.main()
