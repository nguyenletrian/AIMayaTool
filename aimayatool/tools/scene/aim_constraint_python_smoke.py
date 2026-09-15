from __future__ import absolute_import
import unittest
from aimayatool.tools.scene.aim_constraint import axis_vector,build_aim_constraint_plan,execute_aim_constraint_plan

class AimConstraintSmokeTest(unittest.TestCase):
    def test_plan_and_injected_execution(self):
        self.assertEqual(axis_vector("-z"),(0.0,0.0,-1.0))
        plan=build_aim_constraint_plan({"child":"head","parent":"target","reference":"up","constraintContent":"Constraints_GRP","maintain":False,"mainAxis":"-z","secondAxis":"y"})
        op=plan[0]; self.assertEqual(op["offset_name"],"head_AimGrp"); self.assertEqual(op["aim_vector"],(0.0,0.0,-1.0)); self.assertEqual(op["up_vector"],(0.0,1.0,0.0)); self.assertFalse(op["maintain_offset"])
        class FakeCmds(object):
            def __init__(self): self.calls=[]
            def objExists(self,node): return node in ("head","target","up","Constraints_GRP")
            def aimConstraint(self,parent,offset,**kwargs): self.calls.append(("aim",parent,offset,kwargs)); return ["aimConstraint1"]
            def parent(self,node,parent): self.calls.append(("parent",node,parent)); return [node]
        fake=FakeCmds(); offsets=[]
        def create_offset(child,name): offsets.append((child,name)); return name,child
        result=execute_aim_constraint_plan(plan,cmds_module=fake,create_offset_fn=create_offset)
        self.assertEqual(offsets,[("head","head_AimGrp")]); self.assertEqual(result[0]["constraint"],"aimConstraint1"); self.assertIn(("parent","aimConstraint1","Constraints_GRP"),fake.calls)
        kwargs=fake.calls[0][3]; self.assertEqual(kwargs["worldUpType"],"object"); self.assertEqual(kwargs["worldUpObject"],"up"); self.assertFalse(kwargs["mo"])
        print("SCENE_AIM_CONSTRAINT_PYTHON_SMOKE_OK")
    def test_invalid_axis(self):
        with self.assertRaises(ValueError): axis_vector("bad")

if __name__=="__main__": unittest.main()
