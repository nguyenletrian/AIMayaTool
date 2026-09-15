from __future__ import absolute_import
import unittest
from aimayatool.tools.scene.bs_sequence_from_obj_keys import build_bs_sequence_plan,execute_bs_sequence


class FakeCmds(object):
    def __init__(self):
        self.nodes=set(("mesh","anim","source.out","main","proxy","joint","parent")); self.attrs={}; self.time=17.0; self.connections=set()
    def objExists(self,value): return value in self.nodes or value in self.attrs or value.endswith(".visibility") and value.rsplit(".",1)[0] in self.nodes or value.startswith("mesh_smile_BS.w[")
    def currentTime(self,value=None,query=False,edit=False):
        if query: return self.time
        self.time=float(value); return self.time
    def group(self,children,name): self.nodes.add(name); return name
    def parent(self,node,parent): return [node]
    def getAttr(self,plug): return self.attrs.get(plug,0.0)
    def setAttr(self,plug,value=None,**kwargs):
        if value is not None: self.attrs[plug]=value
    def connectAttr(self,source,target,force=False): self.connections.add((source,target))
    def isConnected(self,source,target): return (source,target) in self.connections
    def disconnectAttr(self,source,target): self.connections.discard((source,target))
    def deleteAttr(self,plug): self.attrs.pop(plug,None)
    def delete(self,node): self.nodes.discard(node)


def helpers(cmds,fail_schedule=False):
    def sample(mesh_animation,source_output,frame,name,cmds_module=None): cmds.nodes.add(name); return name
    def blend(targets,destination,name,cmds_module=None): cmds.nodes.add(name); return name
    def attr(node,name,attr_type="float",default=None,minimum=None,maximum=None,cmds_module=None,**kwargs):
        plug=node+"."+name; cmds.attrs[plug]=default if default is not None else 0.0; return plug
    def proxy(source,node,attribute=None,cmds_module=None):
        plug=node+"."+(attribute or source.rsplit(".",1)[-1]); cmds.attrs[plug]=0.0; return plug
    def visibility(source,node,cmds_module=None): target=node+".visibility"; cmds.connections.add((source,target)); return target
    def schedule(driver,driven,schedule,cmds_module=None):
        cmds.attrs[driver]=6.0
        if fail_schedule: raise RuntimeError("schedule failed")
        cmds.attrs[driver]=0.0; return True
    return sample,blend,attr,proxy,visibility,schedule


class BSSequenceTransactionSmokeTest(unittest.TestCase):
    def run_transaction(self,cmds,fail=False):
        sample,blend,attr,proxy,visibility,schedule=helpers(cmds,fail)
        plan=build_bs_sequence_plan("mesh","smile",(2,4))
        return execute_bs_sequence(plan,"anim","source.out",("main","proxy"),"joint","parent",cmds,sample,blend,attr,proxy,visibility,schedule)

    def test_composes_and_restores_time(self):
        cmds=FakeCmds(); result=self.run_transaction(cmds)
        self.assertEqual(result["generated_meshes"],("mesh_Shoot_2","mesh_Shoot_4")); self.assertEqual(cmds.time,17.0)
        self.assertIn(("main.smile","joint.smile"),cmds.connections); self.assertIn(("main.smileShowBS","mesh_BSs.visibility"),cmds.connections)
        self.assertEqual(cmds.attrs["main.smile"],0.0)

    def test_failure_rolls_back_created_scene_state_and_restores_time(self):
        cmds=FakeCmds()
        with self.assertRaises(RuntimeError): self.run_transaction(cmds,True)
        self.assertEqual(cmds.time,17.0); self.assertNotIn("mesh_BSs",cmds.nodes); self.assertNotIn("mesh_smile_BS",cmds.nodes)
        self.assertNotIn("main.smile",cmds.attrs); self.assertNotIn("joint.smile",cmds.attrs); self.assertFalse(cmds.connections)


if __name__=="__main__":
    unittest.main()
    print("SCENE_BS_SEQUENCE_TRANSACTION_PYTHON_SMOKE_OK")
