from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import transforms


class FakeCmds(object):
    def __init__(self):
        self.nodes={"|root","|root|a","|root|a|b"}; self.parents={"|root|a":"|root","|root|a|b":"|root|a"}; self.calls=[]
    def objExists(self,node): return node in self.nodes
    def ls(self,node,long=False): return [node]
    def listRelatives(self,node,**kwargs):
        if kwargs.get("allDescendents"): return ["|root|a|b","|root|a"]
        if kwargs.get("parent"):
            p=self.parents.get(node); return [p] if p else []
        return []
    def select(self,**kwargs): self.calls.append(("select",kwargs))
    def createNode(self,node_type,name=None): self.calls.append(("createNode",node_type,name)); self.nodes.add(name); return name
    def matchTransform(self,target,source,**kwargs): self.calls.append(("matchTransform",target,source,kwargs))
    def parent(self,child,parent,absolute=False): self.calls.append(("parent",child,parent,absolute)); return [child]


class SetupTransformHierarchyTests(unittest.TestCase):
    def test_missing_root_rejected(self):
        with mock.patch.object(transforms,"_cmds",return_value=FakeCmds()):
            with self.assertRaises(ValueError): transforms.create_joint_hierarchy_from_transforms("missing")

    def test_preserves_hierarchy_and_input_order(self):
        fake=FakeCmds()
        with mock.patch.object(transforms,"_cmds",return_value=fake): result=transforms.create_joint_hierarchy_from_transforms("|root",name_prefix="rig_")
        self.assertEqual(("|root","|root|a","|root|a|b"),result["sources"])
        self.assertEqual(("rig_root_JNT","rig_a_JNT","rig_b_JNT"),result["joints"])
        self.assertIn(("parent","rig_a_JNT","rig_root_JNT",True),fake.calls)
        self.assertIn(("parent","rig_b_JNT","rig_a_JNT",True),fake.calls)

    def test_matches_each_source_transform(self):
        fake=FakeCmds()
        with mock.patch.object(transforms,"_cmds",return_value=fake): transforms.create_joint_hierarchy_from_transforms("|root")
        matched=[c for c in fake.calls if c[0]=="matchTransform"]
        self.assertEqual(3,len(matched)); self.assertEqual("|root",matched[0][2]); self.assertEqual("|root|a|b",matched[2][2])


if __name__ == "__main__": unittest.main()
