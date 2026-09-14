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


def create_rp_ik(ik_joints, ik_control, pole_control, handle_name=None, orient_end=True, maintain_offset=True):
    """Create a reusable rotate-plane IK setup for an explicit joint chain.

    The IK handle is parented under ``ik_control`` and constrained by
    ``pole_control``. When ``orient_end`` is True the IK control also drives the
    end-joint orientation. This intentionally excludes control creation, shape
    choice and character naming so callers can compose those separately.
    """
    cmds = _cmds()
    ik_joints = list(ik_joints or [])
    if len(ik_joints) < 2:
        raise ValueError("RP IK requires at least two joints.")
    for node in ik_joints: _require_node(cmds, node, "IK joint")
    _require_node(cmds, ik_control, "IK control")
    _require_node(cmds, pole_control, "Pole control")

    handle_name = handle_name or ik_joints[0] + "_IKHandle"
    handle, effector = cmds.ikHandle(sj=ik_joints[0], ee=ik_joints[-1], sol="ikRPsolver", n=handle_name)
    cmds.parent(handle, ik_control)
    pole_constraint = cmds.poleVectorConstraint(pole_control, handle)[0]
    orient_constraint = None
    if orient_end:
        orient_constraint = cmds.orientConstraint(ik_control, ik_joints[-1], mo=bool(maintain_offset))[0]
    return {
        "handle": handle,
        "effector": effector,
        "pole_constraint": pole_constraint,
        "orient_constraint": orient_constraint,
        "ik_joints": tuple(ik_joints),
    }


def wire_ikfk_switch(switch_attr, fk_nodes, ik_nodes, proxy_nodes=None, reverse_node=None, proxy_attr_name=None):
    """Wire IK/FK visibility and optional proxy switch attributes.

    ``switch_attr`` value 0 shows FK nodes and hides IK nodes; value 1 does the
    opposite. Existing proxy attributes are left untouched so this helper can be
    safely composed with controls that already expose the switch.
    """
    cmds = _cmds()
    fk_nodes = list(fk_nodes or [])
    ik_nodes = list(ik_nodes or [])
    proxy_nodes = list(proxy_nodes or [])
    if not fk_nodes or not ik_nodes:
        raise ValueError("At least one FK node and one IK node are required.")
    _require_attr(cmds, switch_attr, "IK/FK switch attribute")
    for node in fk_nodes: _require_node(cmds, node, "FK visibility node")
    for node in ik_nodes: _require_node(cmds, node, "IK visibility node")
    for node in proxy_nodes: _require_node(cmds, node, "Proxy control")

    reverse = reverse_node
    if reverse:
        _require_node(cmds, reverse, "IK/FK reverse node")
    else:
        reverse = cmds.createNode("reverse", name=switch_attr.replace(".", "_") + "_VisibilityReverse")
        cmds.connectAttr(switch_attr, reverse + ".inputX", force=True)
    for node in fk_nodes:
        cmds.connectAttr(reverse + ".outputX", node + ".visibility", force=True)
    for node in ik_nodes:
        cmds.connectAttr(switch_attr, node + ".visibility", force=True)

    attr_name = proxy_attr_name or switch_attr.rsplit(".", 1)[1]
    proxies = []
    for node in proxy_nodes:
        proxy_plug = node + "." + attr_name
        if not cmds.objExists(proxy_plug):
            cmds.addAttr(node, longName=attr_name, proxy=switch_attr)
        proxies.append(proxy_plug)
    return {"switch_attr": switch_attr, "reverse": reverse, "fk_nodes": tuple(fk_nodes), "ik_nodes": tuple(ik_nodes), "proxy_attrs": tuple(proxies)}
