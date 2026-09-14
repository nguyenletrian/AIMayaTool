from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import transforms


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"a", "b"}; self.identity_calls = []; self.set_calls = []
    def objExists(self, node): return node in self.nodes
    def makeIdentity(self, node, **kwargs): self.identity_calls.append((node, kwargs))
    def setAttr(self, plug, value): self.set_calls.append((plug, value))


class SetupFreezeResetTests(unittest.TestCase):
    def test_freeze_transforms_uses_explicit_flags(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            self.assertEqual(("a", "b"), transforms.freeze_transforms(["a", "b"], translate=False, rotate=False, scale=True))
        self.assertEqual(("a", {"apply": True, "t": False, "r": False, "s": True, "n": 0}), fake.identity_calls[0])

    def test_reset_transforms_resets_enabled_channels(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            transforms.reset_transforms(["a"], translate=True, rotate=True, scale=True)
        self.assertIn(("a.translateX", 0), fake.set_calls)
        self.assertIn(("a.rotateZ", 0), fake.set_calls)
        self.assertIn(("a.scaleY", 1), fake.set_calls)
        self.assertEqual(9, len(fake.set_calls))

    def test_requires_nodes_and_enabled_channel(self):
        fake = FakeCmds()
        with mock.patch.object(transforms, "_cmds", return_value=fake):
            with self.assertRaises(ValueError): transforms.freeze_transforms([])
            with self.assertRaises(ValueError): transforms.reset_transforms(["a"], False, False, False)


if __name__ == "__main__": unittest.main()
