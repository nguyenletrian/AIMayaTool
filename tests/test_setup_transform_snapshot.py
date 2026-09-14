from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import transforms


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"srcA", "srcB", "dstA", "dstB"}
        self.values = {
            "srcA": {"translation": (1, 2, 3), "rotation": (10, 20, 30)},
            "srcB": {"translation": (-4, 5, 6), "rotation": (0, 45, 0)},
            "dstA": {"translation": (0, 0, 0), "rotation": (0, 0, 0)},
            "dstB": {"translation": (0, 0, 0), "rotation": (0, 0, 0)},
        }

    def objExists(self, node):
        return node in self.nodes

    def xform(self, node, query=False, worldSpace=False, translation=None, rotation=None):
        if query:
            if translation is True: return self.values[node]["translation"]
            if rotation is True: return self.values[node]["rotation"]
        if translation is not None: self.values[node]["translation"] = tuple(translation)
        if rotation is not None: self.values[node]["rotation"] = tuple(rotation)


class SetupTransformSnapshotTests(unittest.TestCase):
    def test_capture_preserves_input_order_and_world_values(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            snapshot = transforms.capture_transform_snapshot(["srcA", "srcB"])
        self.assertEqual((1, 2, 3), snapshot[0]["translation"])
        self.assertEqual((0, 45, 0), snapshot[1]["rotation"])

    def test_apply_uses_positional_order(self):
        fake = FakeCmds()
        snapshot = ({"translation": (1, 2, 3), "rotation": (10, 20, 30)}, {"translation": (-4, 5, 6), "rotation": (0, 45, 0)})
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            result = transforms.apply_transform_snapshot(["dstA", "dstB"], snapshot)
        self.assertEqual(("dstA", "dstB"), result)
        self.assertEqual((1, 2, 3), fake.values["dstA"]["translation"])
        self.assertEqual((0, 45, 0), fake.values["dstB"]["rotation"])

    def test_apply_rejects_count_mismatch(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            with self.assertRaises(ValueError):
                transforms.apply_transform_snapshot(["dstA"], [{"translation": (0, 0, 0), "rotation": (0, 0, 0)}, {"translation": (1, 1, 1), "rotation": (1, 1, 1)}])


if __name__ == "__main__":
    unittest.main()
