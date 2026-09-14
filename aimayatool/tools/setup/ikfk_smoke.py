from __future__ import absolute_import

import importlib
import maya.cmds as cmds

from . import ikfk as ikfk_module


def _ikfk():
    return importlib.reload(ikfk_module)


def _joint(name, x):
    joint = cmds.createNode("joint", name=name)
    cmds.setAttr(joint + ".translateX", float(x))
    return joint


def run_setup_ikfk_blend_smoke():
    ikfk = _ikfk()
    cmds.file(new=True, force=True)
    settings = cmds.createNode("transform", name="ikfkSettings")
    cmds.addAttr(settings, longName="ikfk", attributeType="double", minValue=0, maxValue=1, defaultValue=0, keyable=True)
    bind = [_joint("bind1", 0), _joint("bind2", 0)]
    fk = [_joint("fk1", 1), _joint("fk2", 2)]
    ik = [_joint("ik1", 5), _joint("ik2", 6)]
    result = ikfk.create_ikfk_blend(bind, fk, ik, settings + ".ikfk", reverse_name="ikfkBlendReverse")
    if len(result["constraints"]) != 2 or not cmds.objExists(result["reverse"]):
        raise RuntimeError("IK/FK blend nodes were not created as expected.")
    cmds.setAttr(settings + ".ikfk", 0)
    cmds.dgdirty(allPlugs=True)
    if abs(cmds.getAttr(bind[0] + ".translateX") - 1.0) > 1e-5:
        raise RuntimeError("FK blend evaluation mismatch.")
    cmds.setAttr(settings + ".ikfk", 1)
    cmds.dgdirty(allPlugs=True)
    if abs(cmds.getAttr(bind[0] + ".translateX") - 5.0) > 1e-5:
        raise RuntimeError("IK blend evaluation mismatch.")
    return "SETUP_IKFK_BLEND_SMOKE_OK:2"
