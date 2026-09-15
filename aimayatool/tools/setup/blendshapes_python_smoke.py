from __future__ import absolute_import
import unittest
from aimayatool.tools.setup.blendshapes import create_blendshape

class BlendShapeSmokeTest(unittest.TestCase):
    def test_create_contract(self):
        class FakeCmds(object):
            def __init__(self): self.calls=[]
            def objExists(self,node): return node in ("shootA","shootB","face")
            def blendShape(self,*args,**kwargs): self.calls.append((args,kwargs)); return [kwargs["name"]]
        fake=FakeCmds(); node=create_blendshape(("shootA","shootB"),"face","face_Smile_BS",cmds_module=fake)
        self.assertEqual(node,"face_Smile_BS"); self.assertEqual(fake.calls[0][0],("shootA","shootB","face")); self.assertEqual(fake.calls[0][1]["name"],"face_Smile_BS")
        print("SETUP_BLENDSHAPE_PYTHON_SMOKE_OK")
    def test_preconditions(self):
        class FakeCmds(object):
            def objExists(self,node): return node=="face"
        fake=FakeCmds()
        with self.assertRaises(ValueError): create_blendshape((),"face","face_BS",cmds_module=fake)
        with self.assertRaises(ValueError): create_blendshape(("missing",),"face","face_BS",cmds_module=fake)

if __name__=="__main__": unittest.main()
