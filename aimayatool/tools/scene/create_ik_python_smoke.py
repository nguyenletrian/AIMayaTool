from __future__ import absolute_import

import unittest
from aimayatool.tools.scene.create_ik import build_create_ik_plan, build_three_point_frame


class CreateIKSmokeTest(unittest.TestCase):
    def test_plan_and_math(self):
        plan=build_create_ik_plan(("upper","lower","end"),"rig","world",((0,0,0),(1,1,0),(2,0,0)))
        self.assertEqual(plan["system"],"upper_IKFKSystem"); self.assertEqual(plan["joints"],("upper_Jnt","lower_Jnt","end_Jnt"))
        self.assertEqual(plan["fk_joints"],("upper_Jnt_FK","lower_Jnt_FK","end_Jnt_FK")); self.assertEqual(plan["ik_joints"],("upper_Jnt_IK","lower_Jnt_IK","end_Jnt_IK"))
        self.assertEqual(plan["pole_control"],"lower_PoleVector"); self.assertEqual(plan["ik_control"],"end_IK"); self.assertTrue(plan["use_space_switch"])
        self.assertEqual(plan["frame"]["pole_position"],(1.0,2.0,0.0)); self.assertEqual(len(plan["frame"]["frames"]),3)
        print("SCENE_CREATE_IK_PYTHON_SMOKE_OK")
    def test_validation(self):
        with self.assertRaises(ValueError): build_create_ik_plan(("a","b"),"rig")
        with self.assertRaises(ValueError): build_create_ik_plan(("a","a","c"),"rig")
        with self.assertRaises(ValueError): build_create_ik_plan(("a","","c"),"rig")
        with self.assertRaises(ValueError): build_three_point_frame(((0,0,0),(1,0,0),(2,0,0)))


if __name__ == "__main__": unittest.main()
