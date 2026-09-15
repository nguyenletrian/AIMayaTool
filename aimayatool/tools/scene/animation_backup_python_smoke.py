from __future__ import absolute_import
import unittest
from aimayatool.tools.scene.animation_backup import build_animation_apply_plan,collect_animation_data,apply_animation_data

class AnimationBackupSmokeTest(unittest.TestCase):
    def test_capture_plan_apply(self):
        class FakeCmds(object):
            def __init__(self): self.calls=[]
            def objExists(self,node): return node in ("ctrl","|rig|ctrl","ctrl.tx","ctrl.ty")
            def ls(self,obj,long): return ["|rig|ctrl"]
            def listAttr(self,obj,keyable): return ["tx","ty"]
            def listConnections(self,plug,source,destination,type): return ["anim_tx"] if plug.endswith(".tx") else []
            def keyframe(self,curve,query,timeChange=False,valueChange=False): return [1,5] if timeChange else [2,8]
            def cutKey(self,plug,clear): self.calls.append(("cut",plug))
            def setKeyframe(self,plug,time,value): self.calls.append(("key",plug,time,value))
        fake=FakeCmds(); data=collect_animation_data(("ctrl",),cmds_module=fake)
        self.assertEqual(data["ctrl"]["tx"]["times"],(1.0,5.0)); self.assertNotIn("ty",data["ctrl"])
        plan=build_animation_apply_plan({"ctrl":{"tx":{"times":[1,5],"values":[2,8]}}}); self.assertEqual(plan[0]["keys"],((1.0,2.0),(5.0,8.0)))
        result=apply_animation_data({"ctrl":{"tx":{"times":[1,5],"values":[2,8]}}},cmds_module=fake)
        self.assertEqual(result[0]["key_count"],2); self.assertIn(("cut","ctrl.tx"),fake.calls); self.assertIn(("key","ctrl.tx",5.0,8.0),fake.calls)
        print("SCENE_ANIMATION_BACKUP_PYTHON_SMOKE_OK")
    def test_mismatch(self):
        with self.assertRaises(ValueError): build_animation_apply_plan({"ctrl":{"tx":{"times":[1],"values":[]}}})

if __name__=="__main__": unittest.main()
