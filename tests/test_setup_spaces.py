from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import spaces


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"child", "parentA", "parentB", "root"}
        self.calls = []
        self.attrs = set()
    def objExists(self, node): return node in self.nodes
    def listRelatives(self, *args, **kwargs): return ["root"]
    def attributeQuery(self, name, node=None, exists=False): return (node, name) in self.attrs
    def addAttr(self, node, **kwargs): self.attrs.add((node, kwargs["longName"])); self.calls.append(("addAttr", node, kwargs))
    def setAttr(self, *args, **kwargs): self.calls.append(("setAttr", args, kwargs))
    def createNode(self, *args, **kwargs): self.calls.append(("createNode", args, kwargs)); return kwargs.get("name", "defaultSpace")
    def matchTransform(self, *args, **kwargs): self.calls.append(("match", args, kwargs))
    def parentConstraint(self, *args, **kwargs):
        if kwargs.get("q") and kwargs.get("targetList"):
            return ["parentA", "parentB"] if args[0] == "parentConstraint1" else ["root"]
        if kwargs.get("q") and kwargs.get("weightAliasList"):
            return ["parentAW0", "parentBW1"] if args[0] == "parentConstraint1" else ["rootW0"]
        self.calls.append(("parentConstraint", args, kwargs)); return ["parentConstraint1"]
    def shadingNode(self, node_type, **kwargs): self.calls.append(("shadingNode", node_type, kwargs)); return kwargs.get("name", node_type + "1")
    def connectAttr(self, *args, **kwargs): self.calls.append(("connectAttr", args, kwargs))


class SetupSpaceTests(unittest.TestCase):
    def test_requires_parent(self):
        fake = FakeCmds()
        with mock.patch.object(spaces, "_cmds", return_value=fake):
            with self.assertRaises(ValueError): spaces.create_space_switch("child", [])

    def test_label_count_must_match(self):
        fake = FakeCmds()
        with mock.patch.object(spaces, "_cmds", return_value=fake):
            with self.assertRaises(ValueError): spaces.create_space_switch("child", ["parentA", "parentB"], labels=["A"])

    def test_enum_labels_and_parent_constraint(self):
        fake = FakeCmds()
        with mock.patch.object(spaces, "_cmds", return_value=fake), mock.patch.object(spaces.controls, "create_zero_group", return_value=("offset", "child")):
            result = spaces.create_space_switch("child", ["parentA", "parentB"], labels=["World", "Chest"], maintain_offset=True)
        self.assertEqual(("World", "Chest"), result["enum_labels"])
        parent_call = next(call for call in fake.calls if call[0] == "parentConstraint")
        self.assertEqual(("parentA", "parentB", "offset"), parent_call[1])
        self.assertTrue(parent_call[2]["mo"])


if __name__ == "__main__": unittest.main()
