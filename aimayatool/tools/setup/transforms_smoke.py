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
