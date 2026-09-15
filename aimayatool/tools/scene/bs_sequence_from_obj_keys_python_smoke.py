from __future__ import absolute_import
import unittest
from aimayatool.tools.scene.bs_sequence_from_obj_keys import normalize_keyframes,build_bs_sequence_plan

class BSSequenceSmokeTest(unittest.TestCase):
    def test_plan_and_weight_schedule(self):
        frames=normalize_keyframes({"tx":[0,5,10],"ry":[5,15],"custom":[99]})
        self.assertEqual(frames,(5.0,10.0,15.0))
        plan=build_bs_sequence_plan("face","Smile",frames)
        self.assertEqual(plan["generated_meshes"],("face_Shoot_5","face_Shoot_10","face_Shoot_15")); self.assertEqual(plan["group_name"],"face_BSs"); self.assertEqual(plan["blendshape_name"],"face_Smile_BS")
        schedule=plan["weight_schedule"]; self.assertAlmostEqual(schedule["segment"],10.0/3.0); rows=schedule["rows"]
        self.assertEqual(rows[0]["weights"],(0.0,0.0,0.0)); self.assertEqual(rows[1]["weights"],(1.0,0.5,0.0)); self.assertEqual(rows[2]["weights"],(0.5,1.0,0.5)); self.assertEqual(rows[3]["weights"],(0.0,0.5,1.0)); self.assertAlmostEqual(rows[3]["driver"],10.0-(10.0/3.0)*0.5); self.assertEqual(rows[-1],{"driver":10.0,"weights":(0.0,0.0,0.0)})
        print("SCENE_BS_SEQUENCE_PYTHON_SMOKE_OK")
    def test_empty(self):
        with self.assertRaises(ValueError): build_bs_sequence_plan("face","Smile",())

if __name__=="__main__": unittest.main()
