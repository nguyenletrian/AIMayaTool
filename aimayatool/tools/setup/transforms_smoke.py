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


def run_setup_offset_group_smoke():
    transforms = _transforms(); cmds.file(new=True, force=True)
    parent = cmds.createNode("transform", name="offsetParent")
    ctrl = cmds.createNode("transform", name="offsetCtrl", parent=parent)
    cmds.xform(parent, worldSpace=True, translation=(3, 4, 5), rotation=(10, 20, 30))
    cmds.xform(ctrl, worldSpace=True, translation=(8, 2, -1), rotation=(25, -15, 40))
    before_t = cmds.xform(ctrl, query=True, worldSpace=True, translation=True); before_r = cmds.xform(ctrl, query=True, worldSpace=True, rotation=True)
    inserted = transforms.insert_offset_group(ctrl)
    group = inserted["group"]; ctrl_after = inserted["node"]
    if (cmds.listRelatives(group, parent=True, fullPath=False) or []) != [parent]: raise RuntimeError("Offset group parent mismatch.")
    if (cmds.listRelatives(ctrl_after, parent=True, fullPath=False) or []) != [group.rsplit("|", 1)[-1]]: raise RuntimeError("Offset child parent mismatch.")
    after_t = cmds.xform(ctrl_after, query=True, worldSpace=True, translation=True); after_r = cmds.xform(ctrl_after, query=True, worldSpace=True, rotation=True)
    if max(abs(before_t[i] - after_t[i]) for i in range(3)) > 1e-4 or max(abs(before_r[i] - after_r[i]) for i in range(3)) > 1e-3: raise RuntimeError("Offset insertion changed world pose.")
    removed = transforms.remove_offset_group(group); restored = removed["children"][0]
    if (cmds.listRelatives(restored, parent=True, fullPath=False) or []) != [parent]: raise RuntimeError("Offset restore parent mismatch.")
    final_t = cmds.xform(restored, query=True, worldSpace=True, translation=True); final_r = cmds.xform(restored, query=True, worldSpace=True, rotation=True)
    if max(abs(before_t[i] - final_t[i]) for i in range(3)) > 1e-4 or max(abs(before_r[i] - final_r[i]) for i in range(3)) > 1e-3: raise RuntimeError("Offset removal changed world pose.")
    if cmds.objExists(group): raise RuntimeError("Offset group still exists after removal.")
    return "SETUP_OFFSET_GROUP_SMOKE_OK:1"


def run_setup_transform_snapshot_smoke():
    transforms = _transforms(); cmds.file(new=True, force=True)
    src_a = cmds.createNode("transform", name="snapshotSrcA"); src_b = cmds.createNode("transform", name="snapshotSrcB")
    dst_a = cmds.createNode("transform", name="snapshotDstA"); dst_b = cmds.createNode("transform", name="snapshotDstB")
    cmds.xform(src_a, worldSpace=True, translation=(1, 2, 3), rotation=(10, 20, 30)); cmds.xform(src_b, worldSpace=True, translation=(-4, 5, 6), rotation=(0, 45, 0))
    snapshot = transforms.capture_transform_snapshot([src_a, src_b]); transforms.apply_transform_snapshot([dst_a, dst_b], snapshot)
    for source, target in ((src_a, dst_a), (src_b, dst_b)):
        source_t = cmds.xform(source, query=True, worldSpace=True, translation=True); target_t = cmds.xform(target, query=True, worldSpace=True, translation=True)
        source_r = cmds.xform(source, query=True, worldSpace=True, rotation=True); target_r = cmds.xform(target, query=True, worldSpace=True, rotation=True)
        if max(abs(source_t[i] - target_t[i]) for i in range(3)) > 1e-4: raise RuntimeError("Snapshot translation mismatch: {0}".format(target))
        if max(abs(source_r[i] - target_r[i]) for i in range(3)) > 1e-3: raise RuntimeError("Snapshot rotation mismatch: {0}".format(target))
    return "SETUP_TRANSFORM_SNAPSHOT_SMOKE_OK:2"


def run_setup_match_hierarchy_smoke():
    transforms = _transforms(); cmds.file(new=True, force=True)
    src_root = cmds.createNode("transform", name="matchSrcRoot"); src_mid = cmds.createNode("transform", name="matchSrcMid", parent=src_root); src_end = cmds.createNode("transform", name="matchSrcEnd", parent=src_mid)
    dst_root = cmds.createNode("transform", name="matchDstRoot"); dst_mid = cmds.createNode("transform", name="matchDstMid", parent=dst_root); dst_end = cmds.createNode("transform", name="matchDstEnd", parent=dst_mid)
    cmds.xform(src_root, worldSpace=True, translation=(2, 3, 4), rotation=(10, 20, 30), scale=(1.2, 1.1, 0.9)); cmds.xform(src_mid, translation=(3, 1, -2), rotation=(5, 15, 25), scale=(1.0, 1.3, 1.0)); cmds.xform(src_end, translation=(4, -1, 2), rotation=(0, 35, 10), scale=(0.8, 1.0, 1.2))
    transforms.match_transform_hierarchy(src_root, [dst_root])
    src_nodes = [src_root, src_mid, src_end]; dst_nodes = [dst_root, dst_mid, dst_end]
    for source, target in zip(src_nodes, dst_nodes):
        source_m = cmds.xform(source, query=True, worldSpace=True, matrix=True); target_m = cmds.xform(target, query=True, worldSpace=True, matrix=True)
        if max(abs(source_m[i] - target_m[i]) for i in range(16)) > 1e-4: raise RuntimeError("Hierarchy world matrix mismatch: {0}".format(target))
    return "SETUP_MATCH_HIERARCHY_SMOKE_OK:3"
