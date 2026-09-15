from __future__ import absolute_import

import unittest
from aimayatool.tools.scene.create_offset import build_create_offset_plan, create_offsets


class CreateOffsetSmokeTest(unittest.TestCase):
    def test_legacy_names_and_injected_execution(self):
        plan=build_create_offset_plan([{"objects":"arm_L\narm_R", "extraName":"_Offset"},{"objects":"root", "extraName":""}])
        self.assertEqual(plan,({"object":"arm_L","group_name":"arm_L_Offset"},{"object":"arm_R","group_name":"arm_R_Offset"},{"object":"root","group_name":"rootExtraName"}))
        calls=[]
        def create(node,name): calls.append((node,name)); return name,node
        result=create_offsets([{"objects":"arm_L\nmissing", "extraName":"_Offset"}],create_offset_group_fn=create,exists_fn=lambda node: node!="missing")
        self.assertEqual(result[0]["group"],"arm_L_Offset"); self.assertEqual(result[1]["status"],"skipped_missing"); self.assertEqual(calls,[("arm_L","arm_L_Offset")])
        print("SCENE_CREATE_OFFSET_PYTHON_SMOKE_OK")


if __name__ == "__main__": unittest.main()
