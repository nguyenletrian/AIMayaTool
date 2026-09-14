from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_node(cmds, node, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def _require_attr(cmds, plug, label):
    if not plug or "." not in plug or not cmds.objExists(plug):
        raise ValueError("{0} does not exist: {1}".format(label, plug))


def create_ikfk_blend(bind_joints, fk_joints, ik_joints, switch_attr, reverse_name=None):
    """Blend FK and IK joint chains onto a bind chain using one 0..1 switch.

    switch_attr value 0 selects FK and value 1 selects IK. The function is
    naming-agnostic and only requires three equal-length node sequences.
    """
    cmds = _cmds()
    bind_joints = list(bind_joints or [])
    fk_joints = list(fk_joints or [])
    ik_joints = list(ik_joints or [])
    if not bind_joints or len(bind_joints) != len(fk_joints) or len(bind_joints) != len(ik_joints):
        raise ValueError("Bind, FK and IK chains must be non-empty and equal length.")
    _require_attr(cmds, switch_attr, "IK/FK switch attribute")
    for node in bind_joints: _require_node(cmds, node, "Bind joint")
    for node in fk_joints: _require_node(cmds, node, "FK joint")
    for node in ik_joints: _require_node(cmds, node, "IK joint")

    reverse_name = reverse_name or switch_attr.replace(".", "_") + "_Reverse"
    reverse = cmds.createNode("reverse", name=reverse_name)
    cmds.connectAttr(switch_attr, reverse + ".inputX", force=True)
    constraints = []
    for bind, fk, ik in zip(bind_joints, fk_joints, ik_joints):
        constraint = cmds.parentConstraint(fk, ik, bind, maintainOffset=False)[0]
        aliases = cmds.parentConstraint(constraint, query=True, weightAliasList=True) or []
        if len(aliases) < 2:
            raise RuntimeError("IK/FK parentConstraint did not expose two weights: {0}".format(constraint))
        cmds.connectAttr(reverse + ".outputX", constraint + "." + aliases[0], force=True)
        cmds.connectAttr(switch_attr, constraint + "." + aliases[1], force=True)
        constraints.append(constraint)
    return {"switch_attr": switch_attr, "reverse": reverse, "constraints": tuple(constraints)}
