from __future__ import absolute_import
import importlib
import maya.cmds as cmds
from . import transforms as transforms_module


def _transforms(): return importlib.reload(transforms_module)


def run_setup_joint_creation_smoke():
    transforms = _transforms(); cmds.file(new=True, force=True)
    a = cmds.createNode("transform", name="jointRefA"); b = cmds.createNode("transform", name="jointRefB")
    cmds.xform(a, worldSpace=True, translation=(1, 2, 3), rotation=(10, 20, 30)); cmds.xform(b, worldSpace=True, translation=(-4, 5, 6), rotation=(0, 45, 0))
    joints = transforms.create_joints_at_references([a, b])
    if joints != ("jointRefA_JNT", "jointRefB_JNT"): raise RuntimeError("Joint creation naming/order mismatch.")
    for ref, joint in zip((a, b), joints):
        if cmds.listRelatives(joint, parent=True): raise RuntimeError("Created joint unexpectedly parented: {0}".format(joint))
        ref_t = cmds.xform(ref, query=True, worldSpace=True, translation=True); joint_t = cmds.xform(joint, query=True, worldSpace=True, translation=True)
        ref_r = cmds.xform(ref, query=True, worldSpace=True, rotation=True); joint_r = cmds.xform(joint, query=True, worldSpace=True, rotation=True)
        if max(abs(ref_t[i] - joint_t[i]) for i in range(3)) > 1e-4: raise RuntimeError("Joint translation mismatch: {0}".format(joint))
        if max(abs(ref_r[i] - joint_r[i]) for i in range(3)) > 1e-3: raise RuntimeError("Joint rotation mismatch: {0}".format(joint))
    return "SETUP_JOINT_CREATION_SMOKE_OK:2"


def run_setup_transform_hierarchy_smoke():
    transforms = _transforms(); cmds.file(new=True, force=True)
    root = cmds.createNode("transform", name="rigRoot")
    mid = cmds.createNode("transform", name="rigMid", parent=root)
    end = cmds.createNode("transform", name="rigEnd", parent=mid)
    cmds.xform(root, worldSpace=True, translation=(1, 2, 3), rotation=(10, 20, 30))
    cmds.xform(mid, worldSpace=True, translation=(4, 6, 8), rotation=(15, 25, 35))
    cmds.xform(end, worldSpace=True, translation=(9, 7, 5), rotation=(5, 45, 10))
    result = transforms.create_joint_hierarchy_from_transforms(root, name_prefix="copy_")
    joints = result["joints"]
    if joints != ("copy_rigRoot_JNT", "copy_rigMid_JNT", "copy_rigEnd_JNT"): raise RuntimeError("Hierarchy joint naming/order mismatch: {0}".format(joints))
    if (cmds.listRelatives(joints[1], parent=True, fullPath=False) or []) != [joints[0]]: raise RuntimeError("Mid joint parent mismatch.")
    if (cmds.listRelatives(joints[2], parent=True, fullPath=False) or []) != [joints[1]]: raise RuntimeError("End joint parent mismatch.")
    for source, joint in zip((root, mid, end), joints):
        source_t = cmds.xform(source, query=True, worldSpace=True, translation=True); joint_t = cmds.xform(joint, query=True, worldSpace=True, translation=True)
        source_r = cmds.xform(source, query=True, worldSpace=True, rotation=True); joint_r = cmds.xform(joint, query=True, worldSpace=True, rotation=True)
        if max(abs(source_t[i] - joint_t[i]) for i in range(3)) > 1e-4: raise RuntimeError("Hierarchy joint translation mismatch: {0}".format(joint))
        if max(abs(source_r[i] - joint_r[i]) for i in range(3)) > 1e-3: raise RuntimeError("Hierarchy joint rotation mismatch: {0}".format(joint))
    return "SETUP_TRANSFORM_HIERARCHY_SMOKE_OK:3"
