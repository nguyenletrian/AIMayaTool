from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _om():
    import maya.api.OpenMaya as om
    return om


def _require_node(cmds, node, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def _require_attr(cmds, plug, label):
    if not plug or "." not in plug or not cmds.objExists(plug):
        raise ValueError("{0} does not exist: {1}".format(label, plug))


def _require_unique(nodes, label):
    seen = set()
    duplicates = []
    for node in nodes:
        if node in seen and node not in duplicates:
            duplicates.append(node)
        seen.add(node)
    if duplicates:
        raise ValueError("{0} contains duplicate nodes: {1}".format(label, ", ".join(duplicates)))


def _require_disjoint(named_groups):
    owners = {}
    overlaps = []
    for label, nodes in named_groups:
        for node in nodes:
            previous = owners.get(node)
            if previous is not None and previous != label:
                overlaps.append("{0} ({1}/{2})".format(node, previous, label))
            else:
                owners[node] = label
    if overlaps:
        raise ValueError("IK/FK role groups must be disjoint: {0}".format(", ".join(overlaps)))


def create_ikfk_blend(bind_joints, fk_joints, ik_joints, switch_attr, reverse_name=None):
    cmds = _cmds()
    bind_joints = list(bind_joints or [])
    fk_joints = list(fk_joints or [])
    ik_joints = list(ik_joints or [])
    if not bind_joints or len(bind_joints) != len(fk_joints) or len(bind_joints) != len(ik_joints):
        raise ValueError("Bind, FK and IK chains must be non-empty and equal length.")
    _require_unique(bind_joints, "Bind chain")
    _require_unique(fk_joints, "FK chain")
    _require_unique(ik_joints, "IK chain")
    _require_disjoint((("bind", bind_joints), ("fk", fk_joints), ("ik", ik_joints)))
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
    cmds = _cmds()
    ik_joints = list(ik_joints or [])
    if len(ik_joints) < 2:
        raise ValueError("RP IK requires at least two joints.")
    _require_unique(ik_joints, "RP IK chain")
    if ik_control == pole_control:
        raise ValueError("IK control and pole control must be different nodes.")
    if ik_control in ik_joints or pole_control in ik_joints:
        raise ValueError("IK and pole controls must be disjoint from the IK joint chain.")
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
    return {"handle": handle, "effector": effector, "pole_constraint": pole_constraint, "orient_constraint": orient_constraint, "ik_joints": tuple(ik_joints)}


def wire_ikfk_switch(switch_attr, fk_nodes, ik_nodes, proxy_nodes=None, reverse_node=None, proxy_attr_name=None):
    cmds = _cmds()
    fk_nodes = list(fk_nodes or [])
    ik_nodes = list(ik_nodes or [])
    proxy_nodes = list(proxy_nodes or [])
    if not fk_nodes or not ik_nodes:
        raise ValueError("At least one FK node and one IK node are required.")
    _require_unique(fk_nodes, "FK visibility nodes")
    _require_unique(ik_nodes, "IK visibility nodes")
    _require_unique(proxy_nodes, "Proxy controls")
    _require_disjoint((("fk", fk_nodes), ("ik", ik_nodes)))
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


def capture_ikfk_snap_offsets(sources, targets):
    cmds = _cmds()
    om = _om()
    sources = list(sources or [])
    targets = list(targets or [])
    if not sources or len(sources) != len(targets):
        raise ValueError("Snap sources and targets must be non-empty and equal length.")
    _require_unique(sources, "Snap sources")
    _require_unique(targets, "Snap targets")
    offsets = []
    for source, target in zip(sources, targets):
        if source == target:
            raise ValueError("Snap source and target must be different nodes: {0}".format(source))
        _require_node(cmds, source, "Snap source")
        _require_node(cmds, target, "Snap target")
        source_mtx = om.MMatrix(cmds.getAttr(source + ".worldMatrix[0]"))
        target_mtx = om.MMatrix(cmds.getAttr(target + ".worldMatrix[0]"))
        offsets.append(tuple(source_mtx * target_mtx.inverse()))
    return tuple(offsets)


def snap_ikfk(sources, targets, switch_attr, switch_value, offsets=None, key=False, key_attrs=None):
    cmds = _cmds()
    om = _om()
    sources = list(sources or [])
    targets = list(targets or [])
    if not sources or len(sources) != len(targets):
        raise ValueError("Snap sources and targets must be non-empty and equal length.")
    _require_unique(sources, "Snap sources")
    _require_unique(targets, "Snap targets")
    _require_attr(cmds, switch_attr, "IK/FK switch attribute")
    for source, target in zip(sources, targets):
        if source == target:
            raise ValueError("Snap source and target must be different nodes: {0}".format(source))
        _require_node(cmds, source, "Snap source")
        _require_node(cmds, target, "Snap target")
    if offsets is not None and len(offsets) != len(sources):
        raise ValueError("Snap offsets must match source/target count.")
    matrices = []
    for index, target in enumerate(targets):
        target_mtx = om.MMatrix(cmds.getAttr(target + ".worldMatrix[0]"))
        offset_mtx = om.MMatrix() if offsets is None else om.MMatrix(offsets[index])
        matrices.append(offset_mtx * target_mtx)
    cmds.setAttr(switch_attr, switch_value)
    if key:
        cmds.setKeyframe(switch_attr)
    attrs = tuple(key_attrs or ("tx", "ty", "tz", "rx", "ry", "rz"))
    for source, matrix in zip(sources, matrices):
        cmds.xform(source, worldSpace=True, matrix=list(matrix))
        if key:
            cmds.setKeyframe(source, attribute=list(attrs))
    return {"switch_attr": switch_attr, "switch_value": switch_value, "sources": tuple(sources), "targets": tuple(targets), "matrices": tuple(tuple(matrix) for matrix in matrices)}
