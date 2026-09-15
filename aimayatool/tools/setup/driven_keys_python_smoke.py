from __future__ import absolute_import
import unittest
from aimayatool.tools.setup.driven_keys import apply_driven_weight_schedule

class DrivenKeysSmokeTest(unittest.TestCase):
    def test_apply_and_restore(self):
        class FakeCmds(object):
            def __init__(self): self.values={"ctrl.bs":3.0,"bs.w[0]":0.0,"bs.w[1]":0.0}; self.keys=[]
            def objExists(self,plug): return plug in self.values
            def getAttr(self,plug): return self.values[plug]
            def setAttr(self,plug,value): self.values[plug]=value
            def setDrivenKeyframe(self,plug,currentDriver): self.keys.append((plug,currentDriver,self.values[currentDriver],self.values[plug]))
        fake=FakeCmds(); schedule={"rows":({"driver":0,"weights":(0,0)},{"driver":5,"weights":(1,.5)},{"driver":10,"weights":(0,0)})}
        self.assertTrue(apply_driven_weight_schedule("ctrl.bs",("bs.w[0]","bs.w[1]"),schedule,cmds_module=fake)); self.assertEqual(fake.values["ctrl.bs"],3.0); self.assertEqual(len(fake.keys),6); self.assertIn(("bs.w[0]","ctrl.bs",5.0,1.0),fake.keys)
        print("SETUP_DRIVEN_KEYS_PYTHON_SMOKE_OK")
    def test_restore_on_failure(self):
        class Broken(object):
            def __init__(self): self.values={"ctrl.bs":2.0,"bs.w":0.0}
            def objExists(self,plug): return plug in self.values
            def getAttr(self,plug): return self.values[plug]
            def setAttr(self,plug,value): self.values[plug]=value
            def setDrivenKeyframe(self,*args,**kwargs): raise RuntimeError("boom")
        fake=Broken()
        with self.assertRaises(RuntimeError): apply_driven_weight_schedule("ctrl.bs",("bs.w",),{"rows":({"driver":5,"weights":(1,)},)},cmds_module=fake)
        self.assertEqual(fake.values["ctrl.bs"],2.0)

if __name__=="__main__": unittest.main()
