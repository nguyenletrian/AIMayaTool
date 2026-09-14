from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import spline_controls


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"curve1", "curveShape1"}
        self.calls = []
        self.poc_index = 0
        self.joint_index = 0
        self.constraint_index = 0
    def objExists(self, name): return name in self.nodes
    def listRelatives(self, node, **kwargs):
        self.calls.append(("listRelatives", node, kwargs))
        return ["curveShape1"] if node == "curve1" else []
    def arclen(self, curve): self.calls.append(("arclen", curve)); return 20.0
    def createNode(self, node_type, name=None):
        self.calls.append(("createNode", node_type, name))
        self.nodes.add(name)
        return name
    def connectAttr(self, src, dst, force=False): self.calls.append(("connectAttr", src, dst, force))
    def setAttr(self, plug, value): self.calls.append(("setAttr", plug, value))
    def getAttr(self, plug):
        self.calls.append(("getAttr", plug))
        if plug.endswith("_01.position"): return [(0.0, 0.0, 0.0)]
        if plug.endswith("_02.position"): return [(5.0, 1.0, 0.0)]
        return [(10.0, 0.0, 0.0)]
    def delete(self, node): self.calls.append(("delete", node)); self.nodes.discard(node)
    def select(self, **kwargs): self.calls.append(("select", kwargs))
    def joint(self, **kwargs):
        name = kwargs["name"]
        self.nodes.add(name)
        self.calls.append(("joint", kwargs))
        return name
    def skinCluster(self, *args, **kwargs):
        self.calls.append(("skinCluster", args, kwargs))
        self.nodes.add(kwargs["name"])
        return [kwargs["name"]]
    def curve(self, **kwargs):
        self.calls.append(("curve", kwargs))
        self.nodes.add(kwargs["name"])
        return kwargs["name"]
    def scale(self, *args): self.calls.append(("scale", args))
    def makeIdentity(self, node, **kwargs): self.calls.append(("makeIdentity", node, kwargs))
    def group(self, child, name=None):
        self.calls.append(("group", child, name))
        self.nodes.add(name)
        return name
    def xform(self, node, **kwargs): self.calls.append(("xform", node, kwargs))
    def parentConstraint(self, source, target, **kwargs):
        self.constraint_index += 1
        name = "pc{0}".format(self.constraint_index)
        self.calls.append(("parentConstraint", source, target, kwargs, name))
        return [name]


class SetupSplineControlsTests(unittest.TestCase):
    def test_requires_valid_curve_and_two_controls(self):
        fake = FakeCmds()
        with mock.patch.object(spline_controls, "_cmds", return_value=fake):
            with self.assertRaises(ValueError): spline_controls.create_spline_curve_controls("missing", 3)
            with self.assertRaises(ValueError): spline_controls.create_spline_curve_controls("curve1", 1)

    def test_builds_sampled_joints_skin_and_animator_controls(self):
        fake = FakeCmds()
        with mock.patch.object(spline_controls, "_cmds", return_value=fake):
            result = spline_controls.create_spline_curve_controls("curve1", 3, name_prefix="tail")
        self.assertEqual(("tail_SplineCtrlJnt_01", "tail_SplineCtrlJnt_02", "tail_SplineCtrlJnt_03"), result["control_joints"])
        self.assertEqual(("tail_SplineCtrl_01", "tail_SplineCtrl_02", "tail_SplineCtrl_03"), result["controls"])
        self.assertEqual("tail_SplineSkin", result["skin_cluster"])
        self.assertAlmostEqual(0.6, result["control_size"])
        connects = [call for call in fake.calls if call[0] == "connectAttr"]
        self.assertIn(("connectAttr", "curveShape1.worldSpace[0]", "tail_SplinePOC_01.inputCurve", True), connects)
        self.assertIn(("skinCluster", ("tail_SplineCtrlJnt_01", "tail_SplineCtrlJnt_02", "tail_SplineCtrlJnt_03", "curve1"), {"toSelectedBones": True, "maximumInfluences": 2, "name": "tail_SplineSkin"}), fake.calls)
        self.assertIn(("xform", "tail_SplineCtrl_02_Zero", {"worldSpace": True, "translation": (5.0, 1.0, 0.0)}), fake.calls)
        self.assertIn(("parentConstraint", "tail_SplineCtrl_03", "tail_SplineCtrlJnt_03", {"maintainOffset": False}, "pc3"), fake.calls)


if __name__ == "__main__": unittest.main()
