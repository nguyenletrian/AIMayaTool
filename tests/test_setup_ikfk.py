from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import ikfk


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"settings.ikfk", "bind1", "bind2", "fk1", "fk2", "ik1", "ik2"}
        self.calls = []
    def objExists(self, name): return name in self.nodes
    def createNode(self, node_type, name=None): self.calls.append(("createNode", node_type, name)); return name or "reverse1"
    def connectAttr(self, src, dst, force=False): self.calls.append(("connectAttr", src, dst, force))
    def parentConstraint(self, *args, **kwargs):
        if kwargs.get("query") and kwargs.get("weightAliasList"):
            return ["fkW0", "ikW1"]
        name = "pc{0}".format(1 + len([x for x in self.calls if x[0] == "parentConstraint"]))
        self.calls.append(("parentConstraint", args, kwargs, name))
        return [name]


class SetupIKFKTests(unittest.TestCase):
    def test_requires_equal_non_empty_chains(self):
        fake = FakeCmds()
        with mock.patch.object(ikfk, "_cmds", return_value=fake):
            with self.assertRaises(ValueError): ikfk.create_ikfk_blend(["bind1"], ["fk1", "fk2"], ["ik1"], "settings.ikfk")

    def test_creates_reverse_and_two_weight_connections_per_joint(self):
        fake = FakeCmds()
        with mock.patch.object(ikfk, "_cmds", return_value=fake):
            result = ikfk.create_ikfk_blend(["bind1", "bind2"], ["fk1", "fk2"], ["ik1", "ik2"], "settings.ikfk", reverse_name="ikfkReverse")
        self.assertEqual("ikfkReverse", result["reverse"])
        self.assertEqual(("pc1", "pc2"), result["constraints"])
        connects = [x for x in fake.calls if x[0] == "connectAttr"]
        self.assertIn(("connectAttr", "settings.ikfk", "ikfkReverse.inputX", True), connects)
        self.assertIn(("connectAttr", "ikfkReverse.outputX", "pc1.fkW0", True), connects)
        self.assertIn(("connectAttr", "settings.ikfk", "pc1.ikW1", True), connects)


if __name__ == "__main__": unittest.main()
