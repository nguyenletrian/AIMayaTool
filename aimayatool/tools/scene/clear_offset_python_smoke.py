from __future__ import absolute_import

import unittest
from aimayatool.tools.scene.clear_offset import build_clear_offset_plan, execute_clear_offset_plan


class FakeCmds(object):
    def __init__(self,existing=(),parents=None): self.existing=set(existing); self.parents=dict(parents or {}); self.calls=[]
    def objExists(self,node): return node in self.existing
    def listRelatives(self,node,parent,fullPath): return list(self.parents.get(node,()))
    def group(self,empty,name): self.calls.append(("group",name)); self.existing.add(name); return name
    def parentConstraint(self,obj,group,maintainOffset): self.calls.append(("parentConstraint",obj,group,maintainOffset)); return ["tmpConstraint"]
    def delete(self,node): self.calls.append(("delete",node))
    def parent(self,node,parent): self.calls.append(("parent",node,parent)); return [node]


class ClearOffsetSmokeTest(unittest.TestCase):
    def test_parented_object_applies(self):
        plan=build_clear_offset_plan([{"objects":"arm_L"}])
        fake=FakeCmds(existing=("arm_L",),parents={"arm_L":("|Rig_GRP",)})
        result=execute_clear_offset_plan(plan,cmds_module=fake)
        self.assertEqual(result[0]["status"],"applied")
        self.assertEqual(result[0]["original_parent"],"|Rig_GRP")
        self.assertIn(("parent","arm_L_ClearOffsetGrp","|Rig_GRP"),fake.calls)
        self.assertIn(("parent","arm_L","arm_L_ClearOffsetGrp"),fake.calls)

    def test_missing_object_skips_without_mutation(self):
        fake=FakeCmds()
        result=execute_clear_offset_plan(({"object":"missing","group_name":"missing_ClearOffsetGrp"},),cmds_module=fake)
        self.assertEqual(result,({"object":"missing","status":"skipped_missing_object"},))
        self.assertEqual(fake.calls,[])

    def test_root_object_skips_without_mutation(self):
        fake=FakeCmds(existing=("root",),parents={"root":()})
        result=execute_clear_offset_plan(({"object":"root","group_name":"root_ClearOffsetGrp"},),cmds_module=fake)
        self.assertEqual(result,({"object":"root","status":"skipped_root_object"},))
        self.assertEqual(fake.calls,[])

    def test_name_collision_skips_without_mutation(self):
        fake=FakeCmds(existing=("arm_L","arm_L_ClearOffsetGrp"),parents={"arm_L":("|Rig_GRP",)})
        result=execute_clear_offset_plan(({"object":"arm_L","group_name":"arm_L_ClearOffsetGrp"},),cmds_module=fake)
        self.assertEqual(result,({"object":"arm_L","status":"skipped_name_collision","group_name":"arm_L_ClearOffsetGrp"},))
        self.assertEqual(fake.calls,[])


if __name__ == "__main__":
    print("SCENE_CLEAR_OFFSET_PYTHON_SMOKE_OK")
    unittest.main()
