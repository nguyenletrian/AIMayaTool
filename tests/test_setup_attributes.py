from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import attributes


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"src", "dstA", "dstB", "src.tx", "dstA.tx", "dstB.tx"}
        self.values = {"src.tx": 7.5, "dstA.tx": 0.0, "dstB.tx": 1.0}

    def objExists(self, node): return node in self.nodes
    def getAttr(self, plug): return self.values[plug]
    def setAttr(self, plug, value): self.values[plug] = value


class SetupAttributesTests(unittest.TestCase):
    def test_copies_value_to_targets(self):
        fake = FakeCmds()
        with mock.patch.object(attributes, "_cmds", return_value=fake):
            result = attributes.copy_attribute_value("src", ["dstA", "dstB"], "tx")
        self.assertEqual(7.5, fake.values["dstA.tx"])
        self.assertEqual(7.5, fake.values["dstB.tx"])
        self.assertEqual(("dstA", "dstB"), result["targets"])

    def test_requires_targets(self):
        fake = FakeCmds()
        with mock.patch.object(attributes, "_cmds", return_value=fake):
            with self.assertRaises(ValueError): attributes.copy_attribute_value("src", [], "tx")

    def test_rejects_missing_attribute(self):
        fake = FakeCmds()
        with mock.patch.object(attributes, "_cmds", return_value=fake):
            with self.assertRaises(ValueError): attributes.copy_attribute_value("src", ["dstA"], "ry")


if __name__ == "__main__": unittest.main()
