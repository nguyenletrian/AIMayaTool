from __future__ import absolute_import

import unittest
from unittest import mock
from aimayatool.tools.setup import secondary

class FakeCmds(object):
    def __init__(self):
        self.nodes = {"driver", "end", "start", "orientRef", "obj1", "obj2", "dst1", "dst2", "constraints", "ref1", "ref2", "ref3", "curve", "curveShape"}; self.calls = []; self.constraint_index = 0
    def objExists(self, name): return name in self.nodes
    def nodeType(self, node): return "nurbsCurve" if node == "curveShape" else "transform"
    def listRelatives(self, node, **kwargs):
        if kwargs.get("shapes") and node == "curve": return ["curveShape"]
        return []
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
    def setAttr(self, plug, *values, **kwargs): self.calls.append(("setAttr", plug, values, kwargs))
    def getAttr(self, plug):
        if plug.endswith("_Nearest_01.parameter"): return 0.25
        if plug.endswith("_Nearest_02.parameter"): return 0.75
        raise KeyError(plug)
    def delete(self, node): self.calls.append(("delete", node))
    def setDrivenKeyframe(self, plug, currentDriver=None): self.calls.append(("setDrivenKeyframe", plug, currentDriver))
    def parent(self, child, parent): self.calls.append(("parent", child, parent)); return [child]
    def xform(self, node, **kwargs):
        self.calls.append(("xform", node, kwargs))
        return {"ref1":[0,0,0],"ref2":[5,1,0],"ref3":[10,0,0],"obj1":[1,2,3],"obj2":[4,5,6],"start":[0,0,0],"end":[9,3,0]}[node]
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
        self.assertEqual(("pc1","pc2"),result["constraints"]); self.assertTrue(any(call[0]=="setAttr" and call[1]=="driver.fold" and call[2][0]==2 for call in fake.calls))
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
    def test_object_on_curve_requires_objects(self):
        with mock.patch.object(secondary,"_cmds",return_value=FakeCmds()):
            with self.assertRaises(ValueError): secondary.attach_objects_to_curve("curve",[])
    def test_object_on_curve_captures_parameters_and_parent_space(self):
        fake=FakeCmds()
        with mock.patch.object(secondary,"_cmds",return_value=fake): result=secondary.attach_objects_to_curve("curve",["obj1","obj2"],name_prefix="follow")
        self.assertEqual((0.25,0.75),result["parameters"])
        self.assertEqual(("follow_Point_01","follow_Point_02"),result["point_nodes"])
        self.assertIn(("connectAttr","curveShape.worldSpace[0]","follow_Point_01.inputCurve",True),fake.calls)
        self.assertIn(("connectAttr","obj1.parentInverseMatrix[0]","follow_Localize_01.inMatrix",True),fake.calls)
        self.assertIn(("connectAttr","follow_Localize_01.output","obj1.translate",True),fake.calls)
    def test_joints_between_rejects_zero_count(self):
        with mock.patch.object(secondary,"_cmds",return_value=FakeCmds()):
            with self.assertRaises(ValueError): secondary.create_joints_between("start","end",0)
    def test_joints_between_creates_even_interior_chain(self):
        fake=FakeCmds()
        with mock.patch.object(secondary,"_cmds",return_value=fake): result=secondary.create_joints_between("start","end",2,name_prefix="mid")
        self.assertEqual(("mid_BetweenJnt_01","mid_BetweenJnt_02"),result["joints"])
        joint_calls=[call for call in fake.calls if call[0]=="joint" and "position" in call[1]]
        self.assertEqual([3.0,1.0,0.0],joint_calls[0][1]["position"]); self.assertEqual([6.0,2.0,0.0],joint_calls[1][1]["position"])
        self.assertIn(("parent","mid_BetweenJnt_02","mid_BetweenJnt_01"),fake.calls)

if __name__ == "__main__": unittest.main()
