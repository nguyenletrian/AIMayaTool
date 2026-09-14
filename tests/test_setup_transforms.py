from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import transforms


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"src", "dst", "|root", "|root|mid", "|root|mid|end"}
        self.parents = {"|root|mid": "|root", "|root|mid|end": "|root|mid"}
        self.match_calls = []

    def objExists(self, node):
        return node in self.nodes

    def xform(self, node, query=False, worldSpace=False, matrix=False):
        return list(range(16))

    def matchTransform(self, target, source, **kwargs):
        self.match_calls.append((target, source, kwargs))

    def listRelatives(self, node, parent=False, fullPath=False):
        value = self.parents.get(node)
        return [value] if value else []

    def nodeType(self, node):
        return "joint"


class SetupTransformsTests(unittest.TestCase):
    def test_world_matrix_is_tuple(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            self.assertEqual(tuple(range(16)), transforms.world_matrix("src"))

    def test_match_world_transform_passes_explicit_flags(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            self.assertEqual("dst", transforms.match_world_transform("dst", "src", translate=True, rotate=False, scale=True))
        self.assertEqual(("dst", "src", {"position": True, "rotation": False, "scale": True}), fake.match_calls[0])

    def test_match_requires_enabled_channel(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            with self.assertRaises(ValueError):
                transforms.match_world_transform("dst", "src", False, False, False)

    def test_hierarchy_between_returns_inclusive_chain(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            result = transforms.hierarchy_between("|root", "|root|mid|end", node_type="joint")
        self.assertEqual(["|root", "|root|mid", "|root|mid|end"], result)


if __name__ == "__main__":
    unittest.main()
