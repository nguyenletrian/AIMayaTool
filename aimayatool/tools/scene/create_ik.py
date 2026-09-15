from __future__ import absolute_import

from aimayatool.tools.setup.controls import create_control, create_zero_group
from aimayatool.tools.setup.ikfk import create_ikfk_blend, create_rp_ik, wire_ikfk_switch


def _cmds():
    import maya.cmds as cmds
    return cmds


def _om():
    import maya.api.OpenMaya as om
    return om


def _require(cmds, node, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def _duplicate_chain(cmds, joints, suffix):
    duplicates = []
    parent = None
    for joint in joints:
        dup = cmds.createNode("joint", name=joint + suffix)
        cmds.xform(dup, worldSpace=True, matrix=cmds.xform(joint, query=True, worldSpace=True, matrix=True))
        if parent:
            cmds.parent(dup, parent)
        duplicates.append(dup)
        parent = dup
    return duplicates


def build_create_ik(objects, parent, world_parent=None):
    """Build the useful three-object legacy ScenePattern IK/FK system from AIMayaTool setup primitives."""
    cmds = _cmds()
    om = _om()
    objects = tuple(objects or ())
    if len(objects) != 3:
        return {"status": "skipped_invalid_count", "objects": objects}
    missing = tuple(node for node in objects if not node or not cmds.objExists(node))
    if missing:
        return {"status": "skipped_missing", "objects": objects, "missing": missing}
    _require(cmds, parent, "Parent")
    if world_parent:
        _require(cmds, world_parent, "World parent")

    pts = [om.MVector(cmds.xform(node, query=True, worldSpace=True, translation=True)) for node in objects]
    a, b, c = pts
    normal = (b - a) ^ (c - b)
    if normal.length() < 0.0001:
        return {"status": "skipped_collinear", "objects": objects}
    normal.normalize()

    origin_offsets = [create_zero_group(node, suffix="_IKFKExtraOffset")[0] for node in objects]
    system = cmds.createNode("transform", name=objects[0] + "_IKFKSystem")
    cmds.xform(system, worldSpace=True, matrix=cmds.xform(parent, query=True, worldSpace=True, matrix=True))
    system = cmds.parent(system, parent)[0]

    joints = []
    connect_groups = []
    forwards = [(b - a).normal(), (c - b).normal(), (c - b).normal()]
    for node, pos, forward in zip(objects, pts, forwards):
        z_axis = (forward ^ normal).normal()
        y_axis = (z_axis ^ forward).normal()
        matrix = [forward.x, forward.y, forward.z, 0, y_axis.x, y_axis.y, y_axis.z, 0, z_axis.x, z_axis.y, z_axis.z, 0, pos.x, pos.y, pos.z, 1]
        joint = cmds.createNode("joint", name=node + "_Jnt")
        cmds.xform(joint, worldSpace=True, matrix=matrix)
        joints.append(joint)
        group = cmds.createNode("transform", name=node + "_ConnectGroup")
        cmds.xform(group, worldSpace=True, matrix=cmds.xform(node, query=True, worldSpace=True, matrix=True))
        connect_groups.append(group)
    cmds.parent(joints[2], joints[1]); cmds.parent(joints[1], joints[0]); cmds.parent(joints[0], system)
    cmds.makeIdentity(joints[0], apply=True, rotate=True)
    fk_joints = _duplicate_chain(cmds, joints, "_FK")
    ik_joints = _duplicate_chain(cmds, joints, "_IK")
    for group, joint in zip(connect_groups, joints): cmds.parent(group, joint)

    pole = create_control(objects[1] + "_PoleVector", shape="diamond", size=2.0)
    pole_offset = create_zero_group(pole, suffix="_GrpOffset")[0]
    mid = (a + c) * 0.5; pole_pos = b + (b - mid)
    cmds.xform(pole_offset, worldSpace=True, translation=(pole_pos.x, pole_pos.y, pole_pos.z)); cmds.parent(pole_offset, system)
    ik_ctrl = create_control(objects[2] + "_IK", shape="box", size=2.0, match=joints[-1])
    ik_offset = create_zero_group(ik_ctrl, suffix="_GrpOffset")[0]; cmds.parent(ik_offset, system)

    fk_ctrls = []; fk_offsets = []
    for node, joint in zip(objects, joints):
        ctrl = create_control(node + "_FK", shape="circle", size=2.0, match=joint)
        offset = create_zero_group(ctrl, suffix="Offset")[0]
        fk_ctrls.append(ctrl); fk_offsets.append(offset)
    for index in range(len(fk_ctrls) - 1): cmds.parent(fk_offsets[index + 1], fk_ctrls[index])
    cmds.parent(fk_offsets[0], system)
    for ctrl, joint in zip(fk_ctrls, fk_joints): cmds.parentConstraint(ctrl, joint)

    rp = create_rp_ik(ik_joints, ik_ctrl, pole, handle_name=ik_joints[0] + "_IKHandle", orient_end=True, maintain_offset=True)
    switch_attr = ik_ctrl + ".SwitchIKFK"
    cmds.addAttr(ik_ctrl, longName="SwitchIKFK", attributeType="double", min=0, max=1, defaultValue=1, keyable=True)
    blend = create_ikfk_blend(joints, fk_joints, ik_joints, switch_attr, reverse_name=ik_ctrl + "_IKFK_Reverse")
    visibility = wire_ikfk_switch(switch_attr, fk_offsets, [ik_offset, pole_offset], proxy_nodes=fk_ctrls + [pole], reverse_node=blend["reverse"])

    space_constraints = []
    if world_parent:
        for ctrl, offset in ((ik_ctrl, ik_offset), (pole, pole_offset)):
            space = create_zero_group(offset, suffix=ctrl + "_IKFKSpaceSwitch")[0]
            constraint = cmds.parentConstraint(parent, world_parent, space, maintainOffset=True)[0]
            cmds.addAttr(ctrl, longName="Space", attributeType="enum", enumName="Local:World", keyable=True)
            reverse = cmds.createNode("reverse", name=ctrl + "_SpaceReverse")
            cmds.connectAttr(ctrl + ".Space", reverse + ".inputX", force=True)
            weights = cmds.parentConstraint(constraint, query=True, weightAliasList=True) or []
            cmds.connectAttr(reverse + ".outputX", constraint + "." + weights[0], force=True)
            cmds.connectAttr(ctrl + ".Space", constraint + "." + weights[1], force=True)
            space_constraints.append(constraint)

    origin_constraints = [cmds.parentConstraint(group, offset, maintainOffset=True)[0] for group, offset in zip(connect_groups, origin_offsets)]
    for node in joints + fk_joints + ik_joints + [rp["handle"]]: cmds.setAttr(node + ".visibility", 0)
    for node in objects:
        for shape in cmds.listRelatives(node, shapes=True, noIntermediate=True, fullPath=True) or []: cmds.setAttr(shape + ".visibility", 0)
    return {"status": "applied", "system": system, "joints": tuple(joints), "fk_joints": tuple(fk_joints), "ik_joints": tuple(ik_joints), "fk_controls": tuple(fk_ctrls), "ik_control": ik_ctrl, "pole_control": pole, "ik_handle": rp["handle"], "switch_attr": switch_attr, "origin_offsets": tuple(origin_offsets), "origin_constraints": tuple(origin_constraints), "space_constraints": tuple(space_constraints), "visibility": visibility}
