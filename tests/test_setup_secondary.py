from __future__ import absolute_import

import unittest
from unittest import mock
from aimayatool.tools.setup import secondary

class FakeCmds(object):
    def __init__(self):
        self.nodes = {"driver", "end", "start", "orientRef", "obj1", "obj2", "dst1", "dst2", "constraints", "ref1", "ref2", "ref3"}; self.calls = []; self.constraint_index = 0
    def objExists(self, name): return name in self.nodes
    def addAttr(self, node, **kwargs): self.calls.append(("addAttr", node, kwargs)); self.nodes.add(node + "." + kwargs["longName"])
    def createNode(self, node_type, name=None): self.calls.append(("createNode", node_type, name)); self.nodes.add(name); return name
    def connectAttr(self, src, dst, force=False): self.calls.append(("connectAttr", src, dst, force))
    def parentConstraint(self, *args, **kwargs):
        if kwargs.get("query") and kwargs.get("weightAliasList"): return ["endW0", "dst1W1", "dst2W2"]
        self.constraint_index += 1; name = "pc{0}".format(self.constraint_index); self.calls.append(("parentConstraint", args, kwargs, name)); return [name]
    def pointConstraint(self, *args, **kwargs):
        if kwargs.get("query") and kwargs.get("weightAliasList"): return ["startW0", "endW1", "destW2"]
        self.constraint_index += 1; name = "pt{0}".format(self.constraint_index); self.calls.append(("pointConstraint", args, kwargs, name)); return [name]
    def orientConstraint(self, *args, **kwargs):
        if kwargs.get("query") and kwargs.get("weightAliasList"): return ["orientRefW0", "destW1"]
        self.constraint_index += 1; name = "oc{0}".format(self.constraint_index); self.calls.append(("orientConstraint", args, kwargs, name)); return [name]
    def setAttr(self, plug, value): self.calls.append(("setAttr", plug, value))
    def setDrivenKeyframe(self, plug, currentDriver=None): self.calls.append(("setDrivenKeyframe", plug, currentDriver))
    def parent(self, child, parent): self.calls.append(("parent", child, parent)); return [child]
    def xform(self, node, **kwargs): self.calls.append(("xform", node, kwargs)); return {"ref1":[0,0,0],"ref2":[5,1,0],"ref3":[10,0,0]}[node]
    def select(self, **kwargs): self.calls.append(("select", kwargs))
    def joint(self, *args, **kwargs):
        if kwargs.get("edit"): self.calls.append(("joint_edit", args, kwargs)); return args[0] if args else None
        name=kwargs["name"]; self.nodes.add(name); self.calls.append(("joint", kwargs)); return name
    def curve(self, **kwargs): self.nodes.add(kwargs["name"]); self.calls.append(("curve", kwargs)); return kwargs["name"]
    def ikHandle(self, **kwargs): self.nodes.add(kwargs["name"]); self.calls.append(("ikHandle", kwargs)); return [kwargs["name"], kwargs["name"]+"Effector"]

class SetupSecondaryTests(unittest.TestCase):
    def test_fold_requires_equal_non_empty_lists(self):
        with mock.patch.object(secondary,"_cmds",return_value=FakeCmds()):
            with self.assertRaises(ValueError): secondary.create_fold_rig(["obj1"],"end",["dst1","dst2"],"driver.fold")
    def test_fold_creates_driver_constraints_and_expected_key_states(self):
        fake=FakeCmds()
        with mock.patch.object(secondary,"_cmds",return_value=fake): result=secondary.create_fold_rig(["obj1","obj2"],"end",["dst1","dst2"],"driver.fold",constraint_parent="constraints")
        self.assertEqual(("pc1","pc2"),result["constraints"]); self.assertIn(("setAttr","driver.fold",2),fake.calls)
    def test_rope_straight_requires_equal_non_empty_lists(self):
        with mock.patch.object(secondary,"_cmds",return_value=FakeCmds()):
            with self.assertRaises(ValueError): secondary.create_rope_straight(["obj1"],"start","end",["dst1","dst2"],"orientRef","driver.rope")
    def test_rope_straight_builds_progressive_constraint_network(self):
        fake=FakeCmds()
        with mock.patch.object(secondary,"_cmds",return_value=fake): result=secondary.create_rope_straight(["obj1","obj2"],"start","end",["dst1","dst2"],"orientRef","driver.rope",constraint_parent="constraints")
        self.assertEqual(2,len(result["point_constraints"])); self.assertIn(("connectAttr","driver.rope","driver_rope_Offset.input1D[0]",True),fake.calls); self.assertIn(("connectAttr","obj1_RopeDestinationReverse.outputX","pt1.destW2",True),fake.calls)
    def test_rope_roll_requires_equal_non_empty_lists(self):
        with mock.patch.object(secondary,"_cmds",return_value=FakeCmds()):
            with self.assertRaises(ValueError): secondary.create_rope_roll(["obj1"],"start","end",["dst1","dst2"],"orientRef","driver.roll")
    def test_rope_roll_builds_inverse_progressive_network(self):
        fake=FakeCmds()
        with mock.patch.object(secondary,"_cmds",return_value=fake): result=secondary.create_rope_roll(["obj1","obj2"],"start","end",["dst1","dst2"],"orientRef","driver.roll",constraint_parent="constraints")
        self.assertEqual(2,len(result["point_constraints"])); self.assertIn(("createNode","plusMinusAverage","driver_roll_ActiveCount"),fake.calls); self.assertIn(("connectAttr","driver_roll_Offset.output1D","driver_roll_ActiveCount.input1D[1]",True),fake.calls); self.assertIn(("connectAttr","obj1_RopeRollDestinationReverse.outputX","pt1.destW2",True),fake.calls)
    def test_spline_ik_requires_two_references(self):
        with mock.patch.object(secondary,"_cmds",return_value=FakeCmds()):
            with self.assertRaises(ValueError): secondary.create_spline_ik_chain(["ref1"])
    def test_spline_ik_builds_joint_curve_and_handle(self):
        fake=FakeCmds()
        with mock.patch.object(secondary,"_cmds",return_value=fake): result=secondary.create_spline_ik_chain(["ref1","ref2","ref3"],name_prefix="tail")
        self.assertEqual(("tail_SplineJnt_01","tail_SplineJnt_02","tail_SplineJnt_03"),result["joints"]); self.assertEqual("tail_SplineCurve",result["curve"]); self.assertEqual("tail_SplineIKHandle",result["handle"])

if __name__ == "__main__": unittest.main()
