from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import constraints


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"driver", "driverB", "driven", "up", "container"}
        self.calls = []
    def objExists(self, node): return node in self.nodes
    def parentConstraint(self, *args, **kwargs): self.calls.append(("parent", args, kwargs)); return ["parentConstraint1"]
    def orientConstraint(self, *args, **kwargs): self.calls.append(("orient", args, kwargs)); return ["orientConstraint1"]
    def aimConstraint(self, *args, **kwargs): self.calls.append(("aim", args, kwargs)); return ["aimConstraint1"]
    def setAttr(self, *args, **kwargs): self.calls.append(("setAttr", args, kwargs))
    def parent(self, *args, **kwargs): self.calls.append(("parentNode", args, kwargs)); return list(args)


class SetupConstraintTests(unittest.TestCase):
    def test_axis_vector_signed_axes(self):
        self.assertEqual((1, 0, 0), constraints.axis_vector("x"))
        self.assertEqual((0, 0, -1), constraints.axis_vector("-Z"))
        with self.assertRaises(ValueError): constraints.axis_vector("q")

    def test_parent_constraint_passes_multiple_drivers(self):
        fake = FakeCmds()
        with mock.patch.object(constraints, "_cmds", return_value=fake):
            result = constraints.create_parent_constraint(["driver", "driverB"], "driven", maintain_offset=False)
        self.assertEqual("parentConstraint1", result["constraint"])
        self.assertEqual(("driver", "driverB", "driven"), fake.calls[0][1])
        self.assertEqual(False, fake.calls[0][2]["mo"])

    def test_orient_constraint_explicit_flags(self):
        fake = FakeCmds()
        with mock.patch.object(constraints, "_cmds", return_value=fake):
            result = constraints.create_orient_constraint("driver", "driven", maintain_offset=True, use_offset_group=False)
        self.assertEqual("driven", result["target"])
        self.assertEqual(("driver", "driven"), fake.calls[0][1])
        self.assertEqual(True, fake.calls[0][2]["mo"])

    def test_aim_constraint_uses_axis_and_object_up(self):
        fake = FakeCmds()
        with mock.patch.object(constraints, "_cmds", return_value=fake):
            constraints.create_aim_constraint("driver", "driven", "up", aim_axis="-x", up_axis="z", use_offset_group=False)
        kwargs = fake.calls[0][2]
        self.assertEqual((-1, 0, 0), kwargs["aimVector"])
        self.assertEqual((0, 0, 1), kwargs["upVector"])
        self.assertEqual("object", kwargs["worldUpType"])
        self.assertEqual("up", kwargs["worldUpObject"])


if __name__ == "__main__": unittest.main()
