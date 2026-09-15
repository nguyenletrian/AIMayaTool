from __future__ import absolute_import
import unittest
from aimayatool.tools.setup.mesh_sampling import sample_mesh_at_frame

class MeshSamplingSmokeTest(unittest.TestCase):
    def test_sampling_contract(self):
        class FakeCmds(object):
            def __init__(self): self.calls=[]
            def objExists(self,node): return node in ("meshAnim","sculpt.outMesh","shot")
            def duplicate(self,node,**kwargs): self.calls.append(("duplicate",node,kwargs)); return ["shot"]
            def delete(self,node,**kwargs): self.calls.append(("delete",node,kwargs))
            def listRelatives(self,node,**kwargs): return ["|shot|shotShape"]
            def connectAttr(self,src,dst,force): self.calls.append(("connect",src,dst,force))
            def currentTime(self,frame,edit): self.calls.append(("time",frame,edit))
            def disconnectAttr(self,src,dst): self.calls.append(("disconnect",src,dst))
        fake=FakeCmds(); result=sample_mesh_at_frame("meshAnim","sculpt.outMesh",5,"shot",cmds_module=fake)
        self.assertEqual(result,"shot"); self.assertIn(("connect","sculpt.outMesh","|shot|shotShape.inMesh",True),fake.calls); self.assertIn(("time",5,True),fake.calls); self.assertIn(("disconnect","sculpt.outMesh","|shot|shotShape.inMesh"),fake.calls)
        print("SETUP_MESH_SAMPLING_PYTHON_SMOKE_OK")
    def test_cleanup_on_failure(self):
        class Broken(object):
            def __init__(self): self.deleted=[]
            def objExists(self,node): return node in ("meshAnim","sculpt.outMesh","shot")
            def duplicate(self,*args,**kwargs): return ["shot"]
            def delete(self,node,**kwargs): self.deleted.append(node)
            def listRelatives(self,*args,**kwargs): return []
        fake=Broken()
        with self.assertRaises(ValueError): sample_mesh_at_frame("meshAnim","sculpt.outMesh",5,"shot",cmds_module=fake)
        self.assertIn("shot",fake.deleted)

if __name__=="__main__": unittest.main()
