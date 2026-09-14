from __future__ import absolute_import

import unittest
from unittest import mock
from aimayatool.tools.setup import transforms


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"refA", "refB"}; self.calls = []
    def objExists(self, node): return node in self.nodes
    def select(self, **kwargs): self.calls.append(("select", kwargs))
    def createNode(self, node_type, name=None): self.nodes.add(name); self.calls.append(("createNode", node_type, name)); return name
    def matchTransform(self, target, source, **kwargs): self.calls.append(("matchTransform", target, source, kwargs))


class SetupJointCreationTests(unittest.TestCase):
    def test_requires_reference(self):
        with mock.patch.object(transforms, "_cmds", return_value=FakeCmds()):
            with self.assertRaises(ValueError): transforms.create_joint_at_reference("missing")
    def test_single_joint_matches_explicit_reference(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake): result = transforms.create_joint_at_reference("refA", name="bindA", match_rotation=False)
        self.assertEqual("bindA", result)
        self.assertIn(("matchTransform", "bindA", "refA", {"position": True, "rotation": False, "scale": False}), fake.calls)
    def test_batch_preserves_order_and_naming(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake): result = transforms.create_joints_at_references(["refA", "refB"])
        self.assertEqual(("refA_JNT", "refB_JNT"), result)
        self.assertEqual([("createNode", "joint", "refA_JNT"), ("createNode", "joint", "refB_JNT")], [c for c in fake.calls if c[0] == "createNode"])


if __name__ == "__main__": unittest.main()
