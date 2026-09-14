from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import secondary as secondary_module


def _secondary():
    return importlib.reload(secondary_module)


def _transform(name, x):
    node = cmds.createNode("transform", name=name)
    cmds.setAttr(node + ".translateX", float(x))
    return node


def run_setup_fold_rig_smoke():
    secondary = _secondary()
    cmds.file(new=True, force=True)
    driver = cmds.createNode("transform", name="foldSettings")
    end = _transform("foldEnd", 0)
    dst1 = _transform("foldDst1", 10)
    dst2 = _transform("foldDst2", 20)
    obj1 = _transform("foldObj1", -5)
    obj2 = _transform("foldObj2", -10)
    result = secondary.create_fold_rig([obj1, obj2], end, [dst1, dst2], driver + ".fold")
    if len(result["constraints"]) != 2 or not cmds.objExists(driver + ".fold"):
        raise RuntimeError("Fold rig nodes were not created as expected.")

    cmds.setAttr(driver + ".fold", 0)
    cmds.dgdirty(allPlugs=True)
    if abs(cmds.getAttr(obj1 + ".translateX")) > 1e-4 or abs(cmds.getAttr(obj2 + ".translateX")) > 1e-4:
        raise RuntimeError("Fold state mismatch at driver=0.")

    cmds.setAttr(driver + ".fold", 1)
    cmds.dgdirty(allPlugs=True)
    if abs(cmds.getAttr(obj1 + ".translateX")) > 1e-4 or abs(cmds.getAttr(obj2 + ".translateX") - 10.0) > 1e-4:
        raise RuntimeError("Fold state mismatch at driver=1.")

    cmds.setAttr(driver + ".fold", 2)
    cmds.dgdirty(allPlugs=True)
    if abs(cmds.getAttr(obj1 + ".translateX") - 10.0) > 1e-4 or abs(cmds.getAttr(obj2 + ".translateX") - 20.0) > 1e-4:
        raise RuntimeError("Fold state mismatch at driver=2.")
    return "SETUP_FOLD_RIG_SMOKE_OK:3"


def run_setup_rope_straight_smoke():
    secondary = _secondary()
    cmds.file(new=True, force=True)
    driver = cmds.createNode("transform", name="ropeSettings")
    start = _transform("ropeStart", 0)
    end = _transform("ropeEnd", 12)
    orient_ref = cmds.createNode("transform", name="ropeOrientRef")
    dst1 = _transform("ropeDst1", 2)
    dst2 = _transform("ropeDst2", 9)
    obj1 = _transform("ropeObj1", -5)
    obj2 = _transform("ropeObj2", -10)
    result = secondary.create_rope_straight([obj1, obj2], start, end, [dst1, dst2], orient_ref, driver + ".rope")
    if len(result["point_constraints"]) != 2 or len(result["orient_constraints"]) != 2 or not cmds.objExists(driver + ".rope"):
        raise RuntimeError("RopeStraight nodes were not created as expected.")

    cmds.setAttr(driver + ".rope", 0)
    cmds.dgdirty(allPlugs=True)
    if abs(cmds.getAttr(obj1 + ".translateX") - 2.0) > 1e-4 or abs(cmds.getAttr(obj2 + ".translateX") - 9.0) > 1e-4:
        raise RuntimeError("RopeStraight destination-follow state mismatch at driver=0.")

    cmds.setAttr(driver + ".rope", 1)
    cmds.dgdirty(allPlugs=True)
    if abs(cmds.getAttr(obj1 + ".translateX") - 6.0) > 1e-4 or abs(cmds.getAttr(obj2 + ".translateX") - 9.0) > 1e-4:
        raise RuntimeError("RopeStraight progressive state mismatch at driver=1.")

    cmds.setAttr(driver + ".rope", 2)
    cmds.dgdirty(allPlugs=True)
    if abs(cmds.getAttr(obj1 + ".translateX") - 4.0) > 1e-4 or abs(cmds.getAttr(obj2 + ".translateX") - 8.0) > 1e-4:
        raise RuntimeError("RopeStraight straightened state mismatch at driver=2.")
    return "SETUP_ROPE_STRAIGHT_SMOKE_OK:3"


def run_setup_spline_ik_chain_smoke():
    secondary = _secondary()
    cmds.file(new=True, force=True)
    refs = []
    for name, pos in (("splineRef1", (0, 0, 0)), ("splineRef2", (4, 2, 0)), ("splineRef3", (8, 0, 0))):
        node = cmds.createNode("transform", name=name)
        cmds.xform(node, worldSpace=True, translation=pos)
        refs.append(node)
    result = secondary.create_spline_ik_chain(refs, name_prefix="splineTest")
    for node in list(result["joints"]) + [result["curve"], result["handle"], result["effector"]]:
        if not node or not cmds.objExists(node):
            raise RuntimeError("Spline IK node missing: {0}".format(node))
    if cmds.nodeType(result["handle"]) != "ikHandle":
        raise RuntimeError("Spline IK handle type mismatch.")
    curve_shapes = cmds.listRelatives(result["curve"], shapes=True, fullPath=False) or []
    if not curve_shapes or cmds.nodeType(curve_shapes[0]) != "nurbsCurve":
        raise RuntimeError("Spline curve was not created correctly.")
    return "SETUP_SPLINE_IK_CHAIN_SMOKE_OK:3"
