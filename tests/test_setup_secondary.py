from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import secondary


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"driver", "end", "start", "orientRef", "obj1", "obj2", "dst1", "dst2", "constraints"}
        self.calls = []
        self.constraint_index = 0
    def objExists(self, name): return name in self.nodes
    def addAttr(self, node, **kwargs):
        self.calls.append(("addAttr", node, kwargs))
        self.nodes.add(node + "." + kwargs["longName"])
    def createNode(self, node_type, name=None):
        self.calls.append(("createNode", node_type, name))
        self.nodes.add(name)
        return name
    def connectAttr(self, src, dst, force=False): self.calls.append(("connectAttr", src, dst, force))
    def parentConstraint(self, *args, **kwargs):
        if kwargs.get("query") and kwargs.get("weightAliasList"):
            return ["endW0", "dst1W1", "dst2W2"]
        self.constraint_index += 1
        name = "pc{0}".format(self.constraint_index)
        self.calls.append(("parentConstraint", args, kwargs, name))
        return [name]
    def pointConstraint(self, *args, **kwargs):
        if kwargs.get("query") and kwargs.get("weightAliasList"):
            return ["startW0", "endW1", "destW2"]
        self.constraint_index += 1
        name = "pt{0}".format(self.constraint_index)
        self.calls.append(("pointConstraint", args, kwargs, name))
        return [name]
    def orientConstraint(self, *args, **kwargs):
        if kwargs.get("query") and kwargs.get("weightAliasList"):
            return ["orientRefW0", "destW1"]
        self.constraint_index += 1
        name = "oc{0}".format(self.constraint_index)
        self.calls.append(("orientConstraint", args, kwargs, name))
        return [name]
    def setAttr(self, plug, value): self.calls.append(("setAttr", plug, value))
    def setDrivenKeyframe(self, plug, currentDriver=None): self.calls.append(("setDrivenKeyframe", plug, currentDriver))
    def parent(self, child, parent): self.calls.append(("parent", child, parent)); return [child]


class SetupSecondaryTests(unittest.TestCase):
    def test_fold_requires_equal_non_empty_lists(self):
        fake = FakeCmds()
        with mock.patch.object(secondary, "_cmds", return_value=fake):
            with self.assertRaises(ValueError):
                secondary.create_fold_rig(["obj1"], "end", ["dst1", "dst2"], "driver.fold")

    def test_fold_creates_driver_constraints_and_expected_key_states(self):
        fake = FakeCmds()
        with mock.patch.object(secondary, "_cmds", return_value=fake):
            result = secondary.create_fold_rig(["obj1", "obj2"], "end", ["dst1", "dst2"], "driver.fold", constraint_parent="constraints")
        self.assertEqual(("pc1", "pc2"), result["constraints"])
        self.assertIn(("addAttr", "driver", {"longName": "fold", "attributeType": "long", "minValue": 0, "maxValue": 2, "defaultValue": 2, "keyable": True}), fake.calls)
        self.assertIn(("parentConstraint", ("end", "dst1", "dst2", "obj1"), {"maintainOffset": False}, "pc1"), fake.calls)
        self.assertIn(("parent", "pc1", "constraints"), fake.calls)
        self.assertIn(("setAttr", "pc1.dst1W1", 1), fake.calls)
        self.assertIn(("setAttr", "pc2.dst2W2", 1), fake.calls)
        self.assertGreaterEqual(fake.calls.count(("setAttr", "pc1.endW0", 1)), 1)
        self.assertGreaterEqual(fake.calls.count(("setAttr", "pc2.endW0", 1)), 1)
        self.assertEqual(("setAttr", "driver.fold", 2), fake.calls[-1])

    def test_rope_straight_requires_equal_non_empty_lists(self):
        fake = FakeCmds()
        with mock.patch.object(secondary, "_cmds", return_value=fake):
            with self.assertRaises(ValueError):
                secondary.create_rope_straight(["obj1"], "start", "end", ["dst1", "dst2"], "orientRef", "driver.rope")

    def test_rope_straight_builds_progressive_constraint_network(self):
        fake = FakeCmds()
        with mock.patch.object(secondary, "_cmds", return_value=fake):
            result = secondary.create_rope_straight(["obj1", "obj2"], "start", "end", ["dst1", "dst2"], "orientRef", "driver.rope", constraint_parent="constraints")
        self.assertEqual(2, len(result["point_constraints"]))
        self.assertEqual(2, len(result["orient_constraints"]))
        self.assertIn(("addAttr", "driver", {"longName": "rope", "attributeType": "long", "minValue": 0, "maxValue": 2, "defaultValue": 0, "keyable": True}), fake.calls)
        self.assertIn(("pointConstraint", ("start", "end", "dst1", "obj1"), {"maintainOffset": False}, "pt1"), fake.calls)
        self.assertIn(("orientConstraint", ("orientRef", "dst1", "obj1"), {"maintainOffset": False}, "oc2"), fake.calls)
        connects = [call for call in fake.calls if call[0] == "connectAttr"]
        self.assertIn(("connectAttr", "driver.rope", "driver_rope_Offset.input1D[0]", True), connects)
        self.assertIn(("connectAttr", "obj1_RopeDestinationReverse.outputX", "pt1.destW2", True), connects)
        self.assertIn(("connectAttr", "obj1_RopeCondition.outColorR", "oc2.orientRefW0", True), connects)


if __name__ == "__main__": unittest.main()
