from __future__ import absolute_import

import unittest
from unittest import mock
from aimayatool.tools.setup import plane_projection


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"refA", "refB", "refC", "control", "projected"}; self.calls = []
    def objExists(self, name): return name in self.nodes
    def createNode(self, node_type, name=None): self.calls.append(("createNode", node_type, name)); self.nodes.add(name); return name
    def connectAttr(self, src, dst, force=False): self.calls.append(("connectAttr", src, dst, force))
    def setAttr(self, plug, *values, **kwargs): self.calls.append(("setAttr", plug, values, kwargs))


class SetupPlaneProjectionTests(unittest.TestCase):
    def test_requires_exactly_three_references(self):
        with mock.patch.object(plane_projection, "_cmds", return_value=FakeCmds()):
            with self.assertRaises(ValueError): plane_projection.create_plane_projection(["refA", "refB"], "control")

    def test_builds_world_plane_projection_and_localizes_output(self):
        fake = FakeCmds()
        with mock.patch.object(plane_projection, "_cmds", return_value=fake):
            result = plane_projection.create_plane_projection(["refA", "refB", "refC"], "control", projected="projected", name_prefix="plane")
        self.assertEqual("projected", result["projected"])
        self.assertIn(("connectAttr", "refA.worldMatrix[0]", "plane_Ref01World.inputMatrix", True), fake.calls)
        self.assertIn(("connectAttr", "plane_PlaneVectorA.output3D", "plane_PlaneNormal.input1", True), fake.calls)
        self.assertIn(("connectAttr", "plane_PlaneVectorB.output3D", "plane_PlaneNormal.input2", True), fake.calls)
        self.assertIn(("connectAttr", "projected.parentInverseMatrix[0]", "plane_ProjectedLocal.inMatrix", True), fake.calls)
        self.assertIn(("connectAttr", "plane_ProjectedLocal.output", "projected.translate", True), fake.calls)

    def test_can_create_projected_transform(self):
        fake = FakeCmds()
        with mock.patch.object(plane_projection, "_cmds", return_value=fake):
            result = plane_projection.create_plane_projection(["refA", "refB", "refC"], "control", name_prefix="auto")
        self.assertEqual("auto_Projected", result["projected"])
        self.assertIn(("createNode", "transform", "auto_Projected"), fake.calls)


if __name__ == "__main__": unittest.main()
