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

    def objExists(self, node): return node in self.nodes
    def ls(self, node, long=False): return ["|" + node if long and not node.startswith("|") else node]
    def listRelatives(self, node, allDescendents=False, fullPath=False, type=None): return list(self.children.get(node, []))
    def matchTransform(self, target, source, **kwargs): self.match_calls.append((target, source, kwargs))


class SetupMatchHierarchyTests(unittest.TestCase):
    def test_matches_equal_hierarchies_in_dag_order(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            result = transforms.match_transform_hierarchy("src", ["dst"])
        self.assertEqual(("|src", "|src|mid", "|src|mid|end"), result["source_nodes"])
        self.assertEqual(3, len(fake.match_calls))
        self.assertEqual(("|dst|mid", "|src|mid", {"position": True, "rotation": True, "scale": True}), fake.match_calls[1])

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
