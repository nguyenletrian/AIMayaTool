from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import spline_composition


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"group", "local", "global", "orientCtrl", "visCtrl", "visible", "follow", "proxy"}
        self.attrs = set()
        self.calls = []
        self.constraints = 0
    def objExists(self, name): return name in self.nodes
    def attributeQuery(self, attr, node=None, exists=False): return node + "." + attr in self.attrs
    def addAttr(self, node, **kwargs):
        self.calls.append(("addAttr", node, kwargs)); self.attrs.add(node + "." + kwargs["longName"])
    def parentConstraint(self, *args, **kwargs):
        if kwargs.get("query") and kwargs.get("weightAliasList"):
            return ["targetW0"]
        self.constraints += 1
        name = "pc{0}".format(self.constraints)
        self.calls.append(("parentConstraint", args, kwargs, name)); self.nodes.add(name); return [name]
    def orientConstraint(self, *args, **kwargs):
        self.constraints += 1
        name = "oc{0}".format(self.constraints)
        self.calls.append(("orientConstraint", args, kwargs, name)); self.nodes.add(name); return [name]
    def setAttr(self, plug, value): self.calls.append(("setAttr", plug, value))
    def listConnections(self, plug, **kwargs): return ["old." + plug.rsplit(".", 1)[-1]]
    def disconnectAttr(self, src, dst): self.calls.append(("disconnectAttr", src, dst))
    def shadingNode(self, node_type, **kwargs):
        name = kwargs["name"]; self.nodes.add(name); self.calls.append(("shadingNode", node_type, kwargs)); return name
    def connectAttr(self, src, dst, force=False): self.calls.append(("connectAttr", src, dst, force))


class SetupSplineCompositionTests(unittest.TestCase):
    def test_composition_builds_orientation_and_visibility_network(self):
        fake = FakeCmds()
        with mock.patch.object(spline_composition, "_cmds", return_value=fake):
            result = spline_composition.compose_spline_global("group", "local", "global", "orientCtrl", visibility_group="visible", visibility_control="visCtrl", driven_constraints=["follow"], proxy_controls=["proxy"])
        self.assertEqual("pc1", result["parent_constraint"])
        self.assertEqual("oc2", result["orient_constraint"])
        self.assertEqual("group_GlobalOrientBlend", result["blend_node"])
        self.assertIn(("connectAttr", "pc1.constraintRotate", "group_GlobalOrientBlend.color1", True), fake.calls)
        self.assertIn(("connectAttr", "oc2.constraintRotate", "group_GlobalOrientBlend.color2", True), fake.calls)
        self.assertIn(("connectAttr", "orientCtrl.Global", "group_GlobalOrientBlend.blender", True), fake.calls)
        self.assertIn(("connectAttr", "visCtrl.SplineControls", "visible.visibility", True), fake.calls)
        self.assertIn(("connectAttr", "visCtrl.SplineControls", "follow.targetW0", True), fake.calls)
        self.assertIn(("addAttr", "proxy", {"longName": "SplineControls", "proxy": "visCtrl.SplineControls"}), fake.calls)

    def test_follow_constraint_requires_one_target(self):
        fake = FakeCmds()
        def query(*args, **kwargs):
            if kwargs.get("query") and kwargs.get("weightAliasList"): return ["a", "b"]
            return FakeCmds.parentConstraint(fake, *args, **kwargs)
        fake.parentConstraint = query
        with mock.patch.object(spline_composition, "_cmds", return_value=fake):
            with self.assertRaises(ValueError):
                spline_composition.compose_spline_global("group", "local", "global", "orientCtrl", visibility_control="visCtrl", driven_constraints=["follow"])


if __name__ == "__main__": unittest.main()
