from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import transforms


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"src", "dst", "bad", "|src", "|src|mid", "|src|mid|end", "|dst", "|dst|mid", "|dst|mid|end", "|bad", "|bad|mid"}
        self.children = {
            "|src": ["|src|mid|end", "|src|mid"],
            "|dst": ["|dst|mid|end", "|dst|mid"],
            "|bad": ["|bad|mid"],
        }
        self.match_calls = []
        self.xform_sets = []

    def objExists(self, node): return node in self.nodes
    def ls(self, node, long=False): return ["|" + node if long and not node.startswith("|") else node]
    def listRelatives(self, node, allDescendents=False, fullPath=False, type=None): return list(self.children.get(node, []))
    def matchTransform(self, target, source, **kwargs): self.match_calls.append((target, source, kwargs))
    def xform(self, node, query=False, worldSpace=False, matrix=None, **kwargs):
        if query and matrix is True:
            base = {"|src": 1, "|src|mid": 2, "|src|mid|end": 3}.get(node, 0)
            return [float(base + i) for i in range(16)]
        self.xform_sets.append((node, tuple(matrix), worldSpace))


class SetupMatchHierarchyTests(unittest.TestCase):
    def test_full_trs_uses_world_matrices_in_dag_order(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            result = transforms.match_transform_hierarchy("src", ["dst"])
        self.assertEqual(("|src", "|src|mid", "|src|mid|end"), result["source_nodes"])
        self.assertEqual(3, len(fake.xform_sets))
        self.assertEqual(("|dst|mid", tuple(float(2 + i) for i in range(16)), True), fake.xform_sets[1])
        self.assertEqual([], fake.match_calls)

    def test_partial_channels_use_match_transform(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            transforms.match_transform_hierarchy("src", ["dst"], translate=True, rotate=True, scale=False)
        self.assertEqual(3, len(fake.match_calls))
        self.assertEqual(("|dst|mid", "|src|mid", {"position": True, "rotation": True, "scale": False}), fake.match_calls[1])

    def test_rejects_mismatched_hierarchy_size(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            with self.assertRaises(ValueError): transforms.match_transform_hierarchy("src", ["bad"])

    def test_requires_destination_and_enabled_channel(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            with self.assertRaises(ValueError): transforms.match_transform_hierarchy("src", [])
            with self.assertRaises(ValueError): transforms.match_transform_hierarchy("src", ["dst"], False, False, False)


if __name__ == "__main__": unittest.main()
