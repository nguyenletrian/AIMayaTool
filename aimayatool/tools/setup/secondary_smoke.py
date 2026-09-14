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
