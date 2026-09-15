from __future__ import absolute_import
import unittest
from aimayatool.tools.setup.proxy_attributes import create_proxy_attribute,connect_visibility

class ProxyAttributesSmokeTest(unittest.TestCase):
    def test_proxy_and_visibility(self):
        class FakeCmds(object):
            def __init__(self): self.exists={"main.bs","main.showBS","holder","grp.visibility"}; self.calls=[]
            def objExists(self,node): return node in self.exists
            def addAttr(self,node,**kwargs): self.calls.append(("add",node,kwargs)); self.exists.add(node+"."+kwargs["longName"])
            def listConnections(self,*args,**kwargs): return []
            def connectAttr(self,src,dst,force=False): self.calls.append(("connect",src,dst,force))
        fake=FakeCmds(); self.assertEqual(create_proxy_attribute("main.bs","holder",cmds_module=fake),"holder.bs"); self.assertEqual(connect_visibility("main.showBS","grp",cmds_module=fake),"grp.visibility")
        self.assertIn(("add","holder",{"longName":"bs","proxy":"main.bs"}),fake.calls); self.assertIn(("connect","main.showBS","grp.visibility",False),fake.calls)
        print("SETUP_PROXY_VISIBILITY_PYTHON_SMOKE_OK")
    def test_collision(self):
        class FakeCmds(object):
            def objExists(self,node): return node in ("main.bs","holder","holder.bs")
        with self.assertRaises(ValueError): create_proxy_attribute("main.bs","holder",cmds_module=FakeCmds())

if __name__=="__main__": unittest.main()
