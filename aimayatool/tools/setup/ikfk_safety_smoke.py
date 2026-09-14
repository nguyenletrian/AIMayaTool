from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import ikfk as ikfk_module


def _ikfk():
    return importlib.reload(ikfk_module)


def _expect_value_error(fn, label):
    try:
        fn()
    except ValueError:
        return
    raise RuntimeError("Expected ValueError: {0}".format(label))


def run_setup_ikfk_safety_smoke():
    ikfk = _ikfk()
    cmds.file(new=True, force=True)
    settings = cmds.createNode("transform", name="ikfkSafetySettings")
    cmds.addAttr(settings, longName="ikfk", attributeType="double", minValue=0, maxValue=1, defaultValue=0, keyable=True)
    bind1 = cmds.createNode("joint", name="safeBind1")
    bind2 = cmds.createNode("joint", name="safeBind2")
    fk1 = cmds.createNode("joint", name="safeFk1")
    fk2 = cmds.createNode("joint", name="safeFk2")
    ik1 = cmds.createNode("joint", name="safeIk1")
    ik2 = cmds.createNode("joint", name="safeIk2")
    ik_ctrl = cmds.createNode("transform", name="safeIkCtrl")
    pole_ctrl = cmds.createNode("transform", name="safePoleCtrl")
    before_reverse = set(cmds.ls(type="reverse") or [])
    before_constraints = set(cmds.ls(type="parentConstraint") or [])
    _expect_value_error(lambda: ikfk.create_ikfk_blend([bind1, bind1], [fk1, fk2], [ik1, ik2], settings + ".ikfk"), "duplicate bind chain")
    if set(cmds.ls(type="reverse") or []) != before_reverse or set(cmds.ls(type="parentConstraint") or []) != before_constraints:
        raise RuntimeError("Duplicate blend preflight created partial nodes.")
    _expect_value_error(lambda: ikfk.create_ikfk_blend([bind1, bind2], [bind1, fk2], [ik1, ik2], settings + ".ikfk"), "overlapping bind/FK roles")
    if set(cmds.ls(type="reverse") or []) != before_reverse:
        raise RuntimeError("Role-overlap blend preflight created a reverse node.")
    before_handles = set(cmds.ls(type="ikHandle") or [])
    _expect_value_error(lambda: ikfk.create_rp_ik([ik1, ik2], ik_ctrl, ik_ctrl), "shared IK/pole control")
    if set(cmds.ls(type="ikHandle") or []) != before_handles:
        raise RuntimeError("RP IK preflight created a partial IK handle.")
    fk_vis = cmds.createNode("transform", name="safeFkVis")
    ik_vis = cmds.createNode("transform", name="safeIkVis")
    _expect_value_error(lambda: ikfk.wire_ikfk_switch(settings + ".ikfk", [fk_vis], [fk_vis]), "overlapping visibility roles")
    if set(cmds.ls(type="reverse") or []) != before_reverse:
        raise RuntimeError("Visibility preflight created a reverse node.")
    snap_a = cmds.createNode("transform", name="safeSnapA")
    snap_b = cmds.createNode("transform", name="safeSnapB")
    _expect_value_error(lambda: ikfk.capture_ikfk_snap_offsets([snap_a, snap_a], [snap_b, snap_a]), "duplicate snap sources")
    cmds.setAttr(settings + ".ikfk", 0)
    _expect_value_error(lambda: ikfk.snap_ikfk([snap_a], [snap_a], settings + ".ikfk", 1), "self snap")
    if abs(cmds.getAttr(settings + ".ikfk")) > 1e-6:
        raise RuntimeError("Snap preflight mutated switch state.")
    result = ikfk.create_ikfk_blend([bind1, bind2], [fk1, fk2], [ik1, ik2], settings + ".ikfk", reverse_name="safeBlendReverse")
    if len(result["constraints"]) != 2 or not cmds.objExists(result["reverse"]):
        raise RuntimeError("Valid IK/FK blend no longer composes correctly.")
    return "SETUP_IKFK_SAFETY_OK:7"
