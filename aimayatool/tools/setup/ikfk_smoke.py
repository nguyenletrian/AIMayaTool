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


def run_setup_rp_ik_smoke():
    ikfk = _ikfk()
    cmds.file(new=True, force=True)
    j1 = cmds.joint(name="rpIK_j1", position=(0, 0, 0))
    j2 = cmds.joint(name="rpIK_j2", position=(5, 2, 0))
    j3 = cmds.joint(name="rpIK_j3", position=(10, 0, 0))
    cmds.select(clear=True)
    ik_ctrl = cmds.createNode("transform", name="rpIK_ctrl")
    pole_ctrl = cmds.createNode("transform", name="rpIK_pole")
    cmds.xform(ik_ctrl, worldSpace=True, translation=(10, 0, 0))
    cmds.xform(pole_ctrl, worldSpace=True, translation=(5, 6, 0))
    result = ikfk.create_rp_ik([j1, j2, j3], ik_ctrl, pole_ctrl, handle_name="rpIK_handle", maintain_offset=False)
    for node in (result["handle"], result["pole_constraint"], result["orient_constraint"]):
        if not node or not cmds.objExists(node):
            raise RuntimeError("RP IK node missing: {0}".format(node))
    parent = cmds.listRelatives(result["handle"], parent=True, fullPath=False) or []
    if parent != [ik_ctrl]:
        raise RuntimeError("IK handle was not parented under IK control: {0}".format(parent))
    cmds.xform(ik_ctrl, worldSpace=True, translation=(8, 4, 0))
    cmds.dgdirty(allPlugs=True)
    end_pos = cmds.xform(j3, query=True, worldSpace=True, translation=True)
    if abs(end_pos[0] - 8.0) > 1e-3 or abs(end_pos[1] - 4.0) > 1e-3:
        raise RuntimeError("RP IK end-joint did not follow IK control: {0}".format(end_pos))
    return "SETUP_RP_IK_SMOKE_OK:1"


def run_setup_ikfk_switch_smoke():
    ikfk = _ikfk()
    cmds.file(new=True, force=True)
    settings = cmds.createNode("transform", name="switchSettings")
    cmds.addAttr(settings, longName="ikfk", attributeType="double", minValue=0, maxValue=1, defaultValue=0, keyable=True)
    fk_ctrl = cmds.createNode("transform", name="switchFKCtrl")
    fk_offset = cmds.createNode("transform", name="switchFKOffset")
    ik_offset = cmds.createNode("transform", name="switchIKOffset")
    pole_offset = cmds.createNode("transform", name="switchPoleOffset")
    result = ikfk.wire_ikfk_switch(settings + ".ikfk", [fk_offset], [ik_offset, pole_offset], proxy_nodes=[fk_ctrl], proxy_attr_name="SwitchIKFK")
    if not cmds.objExists(result["reverse"]) or not cmds.objExists(fk_ctrl + ".SwitchIKFK"):
        raise RuntimeError("IK/FK switch wiring nodes or proxy attribute were not created.")
    cmds.setAttr(settings + ".ikfk", 0)
    cmds.dgdirty(allPlugs=True)
    if cmds.getAttr(fk_offset + ".visibility") < 0.5 or cmds.getAttr(ik_offset + ".visibility") > 0.5:
        raise RuntimeError("FK visibility state mismatch at switch=0.")
    cmds.setAttr(fk_ctrl + ".SwitchIKFK", 1)
    cmds.dgdirty(allPlugs=True)
    if abs(cmds.getAttr(settings + ".ikfk") - 1.0) > 1e-5:
        raise RuntimeError("Proxy switch attribute did not drive source switch.")
    if cmds.getAttr(fk_offset + ".visibility") > 0.5 or cmds.getAttr(ik_offset + ".visibility") < 0.5 or cmds.getAttr(pole_offset + ".visibility") < 0.5:
        raise RuntimeError("IK visibility state mismatch at switch=1.")
    return "SETUP_IKFK_SWITCH_SMOKE_OK:2"
