from __future__ import absolute_import

import unittest
from unittest import mock

from aimayatool.tools.setup import ikfk


class FakeMatrix(object):
    def __init__(self, values=None):
        self.values = tuple(values or (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
    def __mul__(self, other): return FakeMatrix(tuple(a + b for a, b in zip(self.values, other.values)))
    def inverse(self): return FakeMatrix(tuple(-x for x in self.values))
    def __iter__(self): return iter(self.values)


class FakeOM(object):
    MMatrix = FakeMatrix


class FakeCmds(object):
    def __init__(self):
        self.nodes = {"settings.ikfk", "bind1", "bind2", "fk1", "fk2", "ik1", "ik2", "ik3", "ikCtrl", "poleCtrl", "fkCtrl", "fkOffset", "ikOffset", "poleOffset", "source1", "target1"}
        self.calls = []
        self.attrs = {"source1.worldMatrix[0]": tuple(range(16)), "target1.worldMatrix[0]": tuple(range(16, 32))}
    def objExists(self, name): return name in self.nodes
    def createNode(self, node_type, name=None): self.calls.append(("createNode", node_type, name)); self.nodes.add(name or "reverse1"); return name or "reverse1"
    def connectAttr(self, src, dst, force=False): self.calls.append(("connectAttr", src, dst, force))
    def addAttr(self, node, **kwargs): self.calls.append(("addAttr", node, kwargs)); self.nodes.add(node + "." + kwargs["longName"])
    def getAttr(self, plug): return self.attrs[plug]
    def setAttr(self, plug, value): self.calls.append(("setAttr", plug, value))
    def xform(self, node, **kwargs): self.calls.append(("xform", node, kwargs))
    def setKeyframe(self, node, **kwargs): self.calls.append(("setKeyframe", node, kwargs))
    def parentConstraint(self, *args, **kwargs):
        if kwargs.get("query") and kwargs.get("weightAliasList"):
            return ["fkW0", "ikW1"]
        name = "pc{0}".format(1 + len([x for x in self.calls if x[0] == "parentConstraint"]))
        self.calls.append(("parentConstraint", args, kwargs, name))
        return [name]
    def ikHandle(self, **kwargs): self.calls.append(("ikHandle", kwargs)); return [kwargs.get("n", "ikHandle1"), "effector1"]
    def parent(self, child, parent): self.calls.append(("parent", child, parent)); return [child]
    def poleVectorConstraint(self, pole, handle): self.calls.append(("poleVectorConstraint", pole, handle)); return ["poleConstraint1"]
    def orientConstraint(self, control, joint, mo=False): self.calls.append(("orientConstraint", control, joint, mo)); return ["orientConstraint1"]


class SetupIKFKTests(unittest.TestCase):
    def test_requires_equal_non_empty_chains(self):
        fake = FakeCmds()
        with mock.patch.object(ikfk, "_cmds", return_value=fake):
            with self.assertRaises(ValueError): ikfk.create_ikfk_blend(["bind1"], ["fk1", "fk2"], ["ik1"], "settings.ikfk")

    def test_creates_reverse_and_two_weight_connections_per_joint(self):
        fake = FakeCmds()
        with mock.patch.object(ikfk, "_cmds", return_value=fake):
            result = ikfk.create_ikfk_blend(["bind1", "bind2"], ["fk1", "fk2"], ["ik1", "ik2"], "settings.ikfk", reverse_name="ikfkReverse")
        self.assertEqual("ikfkReverse", result["reverse"])
        self.assertEqual(("pc1", "pc2"), result["constraints"])
        connects = [x for x in fake.calls if x[0] == "connectAttr"]
        self.assertIn(("connectAttr", "settings.ikfk", "ikfkReverse.inputX", True), connects)
        self.assertIn(("connectAttr", "ikfkReverse.outputX", "pc1.fkW0", True), connects)
        self.assertIn(("connectAttr", "settings.ikfk", "pc1.ikW1", True), connects)

    def test_create_rp_ik_wires_handle_pole_and_end_orient(self):
        fake = FakeCmds()
        with mock.patch.object(ikfk, "_cmds", return_value=fake):
            result = ikfk.create_rp_ik(["ik1", "ik2", "ik3"], "ikCtrl", "poleCtrl", handle_name="armIKHandle")
        self.assertEqual("armIKHandle", result["handle"])
        self.assertEqual("effector1", result["effector"])
        self.assertEqual("poleConstraint1", result["pole_constraint"])
        self.assertEqual("orientConstraint1", result["orient_constraint"])
        self.assertIn(("ikHandle", {"sj": "ik1", "ee": "ik3", "sol": "ikRPsolver", "n": "armIKHandle"}), fake.calls)
        self.assertIn(("parent", "armIKHandle", "ikCtrl"), fake.calls)
        self.assertIn(("poleVectorConstraint", "poleCtrl", "armIKHandle"), fake.calls)
        self.assertIn(("orientConstraint", "ikCtrl", "ik3", True), fake.calls)

    def test_create_rp_ik_requires_two_joints(self):
        fake = FakeCmds()
        with mock.patch.object(ikfk, "_cmds", return_value=fake):
            with self.assertRaises(ValueError): ikfk.create_rp_ik(["ik1"], "ikCtrl", "poleCtrl")

    def test_wire_ikfk_switch_connects_visibility_and_adds_proxy(self):
        fake = FakeCmds()
        with mock.patch.object(ikfk, "_cmds", return_value=fake):
            result = ikfk.wire_ikfk_switch("settings.ikfk", ["fkOffset"], ["ikOffset", "poleOffset"], proxy_nodes=["fkCtrl"], reverse_node="fk1", proxy_attr_name="SwitchIKFK")
        self.assertEqual("fk1", result["reverse"])
        self.assertEqual(("fkCtrl.SwitchIKFK",), result["proxy_attrs"])
        self.assertIn(("connectAttr", "fk1.outputX", "fkOffset.visibility", True), fake.calls)
        self.assertIn(("connectAttr", "settings.ikfk", "ikOffset.visibility", True), fake.calls)
        self.assertIn(("connectAttr", "settings.ikfk", "poleOffset.visibility", True), fake.calls)
        self.assertIn(("addAttr", "fkCtrl", {"longName": "SwitchIKFK", "proxy": "settings.ikfk"}), fake.calls)

    def test_wire_ikfk_switch_requires_both_visibility_sets(self):
        fake = FakeCmds()
        with mock.patch.object(ikfk, "_cmds", return_value=fake):
            with self.assertRaises(ValueError): ikfk.wire_ikfk_switch("settings.ikfk", [], ["ikOffset"])

    def test_capture_snap_offsets_uses_source_times_target_inverse(self):
        fake = FakeCmds()
        with mock.patch.object(ikfk, "_cmds", return_value=fake), mock.patch.object(ikfk, "_om", return_value=FakeOM()):
            offsets = ikfk.capture_ikfk_snap_offsets(["source1"], ["target1"])
        self.assertEqual(tuple(a - b for a, b in zip(range(16), range(16, 32))), offsets[0])

    def test_snap_ikfk_sets_switch_matches_matrix_and_keys_explicitly(self):
        fake = FakeCmds()
        offset = tuple([1] * 16)
        with mock.patch.object(ikfk, "_cmds", return_value=fake), mock.patch.object(ikfk, "_om", return_value=FakeOM()):
            result = ikfk.snap_ikfk(["source1"], ["target1"], "settings.ikfk", 1, offsets=[offset], key=True)
        expected = list(tuple(a + 1 for a in range(16, 32)))
        self.assertEqual(1, result["switch_value"])
        self.assertIn(("setAttr", "settings.ikfk", 1), fake.calls)
        self.assertIn(("xform", "source1", {"worldSpace": True, "matrix": expected}), fake.calls)
        self.assertIn(("setKeyframe", "settings.ikfk", {}), fake.calls)
        self.assertIn(("setKeyframe", "source1", {"attribute": ["tx", "ty", "tz", "rx", "ry", "rz"]}), fake.calls)


if __name__ == "__main__": unittest.main()
