from __future__ import absolute_import


def _cmds():
    import maya.cmds as cmds
    return cmds


def _require_node(cmds, node, label):
    if not node or not cmds.objExists(node):
        raise ValueError("{0} does not exist: {1}".format(label, node))


def _long_name(cmds, node):
    matches = cmds.ls(node, long=True) or []
    if not matches:
        raise ValueError("Node does not exist: {0}".format(node))
    return matches[0]


def _short_name(node):
    return node.rsplit("|", 1)[-1]


def _intermediate_joint_names(source_chain, name_prefix=None):
    internal = list(source_chain[1:-1])
    if name_prefix:
        return ["{0}{1}".format(name_prefix, index + 1) for index in range(len(internal))]
    return ["{0}_copy".format(_short_name(node)) for node in internal]


def world_matrix(node):
    """Return a node world matrix as an immutable tuple."""
    cmds = _cmds()
    _require_node(cmds, node, "Node")
    return tuple(cmds.xform(node, query=True, worldSpace=True, matrix=True))


def match_world_transform(target, source, translate=True, rotate=True, scale=False):
    """Match explicit world transform channels from source onto target."""
    cmds = _cmds()
    _require_node(cmds, target, "Target")
    _require_node(cmds, source, "Source")
    if not any((translate, rotate, scale)):
        raise ValueError("At least one transform channel must be enabled.")
    cmds.matchTransform(target, source, position=bool(translate), rotation=bool(rotate), scale=bool(scale))
    return target


def hierarchy_between(parent, child, node_type=None):
    """Return the inclusive DAG chain from parent to child, validating ancestry."""
    cmds = _cmds()
    _require_node(cmds, parent, "Parent")
    _require_node(cmds, child, "Child")
    parent = _long_name(cmds, parent)
    child = _long_name(cmds, child)
    if parent == child:
        return [parent]
    chain = [child]
    current = child
    while current != parent:
        parents = cmds.listRelatives(current, parent=True, fullPath=True) or []
        if not parents:
            raise ValueError("{0} is not a descendant of {1}".format(child, parent))
        current = parents[0]
        if node_type and cmds.nodeType(current) != node_type:
            raise ValueError("Hierarchy node has unexpected type: {0}".format(current))
        chain.append(current)
    chain.reverse()
    if node_type and any(cmds.nodeType(node) != node_type for node in chain):
        raise ValueError("Hierarchy contains nodes outside required type: {0}".format(node_type))
    return chain


def match_joint_chain(source_begin, source_end, destination_begin, destination_end, name_prefix=None):
    """Rebuild destination intermediate joints to match a source joint chain."""
    cmds = _cmds()
    source_chain = hierarchy_between(source_begin, source_end, node_type="joint")
    destination_chain = hierarchy_between(destination_begin, destination_end, node_type="joint")
    destination_begin = destination_chain[0]
    destination_end = destination_chain[-1]
    match_world_transform(destination_begin, source_chain[0], translate=True, rotate=False, scale=False)
    match_world_transform(destination_end, source_chain[-1], translate=True, rotate=False, scale=False)
    if len(destination_chain) > 2:
        destination_end = cmds.parent(destination_end, destination_begin, absolute=True)[0]
        cmds.delete(destination_chain[1])
        destination_begin = _long_name(cmds, destination_begin)
        destination_end = _long_name(cmds, destination_end)
    mappings = [(destination_begin, source_chain[0])]
    parent_joint = destination_begin
    names = _intermediate_joint_names(source_chain, name_prefix=name_prefix)
    for source_joint, joint_name in zip(source_chain[1:-1], names):
        joint = cmds.createNode("joint", name=joint_name)
        cmds.matchTransform(joint, source_joint, position=True, rotation=False, scale=False)
        cmds.matchTransform(joint, destination_begin, position=False, rotation=True, scale=False)
        joint = cmds.parent(joint, parent_joint, absolute=True)[0]
        parent_joint = _long_name(cmds, joint)
        mappings.append((parent_joint, source_joint))
    if source_chain[1:-1]:
        destination_end = cmds.parent(destination_end, parent_joint, absolute=True)[0]
    destination_end = _long_name(cmds, destination_end)
    match_world_transform(destination_end, source_chain[-1], translate=True, rotate=False, scale=False)
    mappings.append((destination_end, source_chain[-1]))
    return tuple(mappings)


def create_joint_at_reference(reference, name=None, match_rotation=True):
    """Create one joint at an explicit transform reference without selection dependency."""
    cmds = _cmds(); _require_node(cmds, reference, "Joint reference")
    joint_name = name or (_short_name(reference) + "_JNT")
    cmds.select(clear=True)
    joint = cmds.createNode("joint", name=joint_name)
    cmds.matchTransform(joint, reference, position=True, rotation=bool(match_rotation), scale=False)
    return joint


def create_joints_at_references(references, suffix="_JNT", match_rotation=True):
    """Create one unparented joint per explicit reference and return them in input order."""
    cmds = _cmds(); references = list(references or [])
    if not references: raise ValueError("At least one joint reference is required.")
    for reference in references: _require_node(cmds, reference, "Joint reference")
    result = []
    for reference in references:
        result.append(create_joint_at_reference(reference, name=_short_name(reference) + suffix, match_rotation=match_rotation))
    return tuple(result)


def create_joint_hierarchy_from_transforms(root, suffix="_JNT", name_prefix=None, match_rotation=True):
    """Create a joint hierarchy matching an explicit transform DAG hierarchy."""
    cmds = _cmds(); _require_node(cmds, root, "Hierarchy root")
    root = _long_name(cmds, root)
    descendants = cmds.listRelatives(root, allDescendents=True, fullPath=True, type="transform") or []
    sources = [root] + list(reversed(descendants))
    source_set = set(sources); mapping = {}; created = []
    for source in sources:
        base = _short_name(source); joint_name = "{0}{1}{2}".format(name_prefix or "", base, suffix)
        joint = create_joint_at_reference(source, name=joint_name, match_rotation=match_rotation)
        parents = cmds.listRelatives(source, parent=True, fullPath=True) or []
        parent_source = parents[0] if parents and parents[0] in source_set else None
        if parent_source:
            joint = cmds.parent(joint, mapping[parent_source], absolute=True)[0]
        mapping[source] = joint; created.append(joint)
    return {"root": root, "sources": tuple(sources), "joints": tuple(created), "mapping": mapping}


def insert_offset_group(node, name=None, suffix="_fixOffset"):
    """Insert a matched transform group directly above a node while preserving world pose."""
    cmds = _cmds(); _require_node(cmds, node, "Offset node")
    node = _long_name(cmds, node)
    parents = cmds.listRelatives(node, parent=True, fullPath=True) or []
    parent = parents[0] if parents else None
    group_name = name or (_short_name(node) + suffix)
    group = cmds.createNode("transform", name=group_name)
    cmds.matchTransform(group, node, position=True, rotation=True, scale=True)
    if parent:
        group = cmds.parent(group, parent, absolute=True)[0]
    node = cmds.parent(node, group, absolute=True)[0]
    return {"node": node, "group": group, "parent": parent}


def remove_offset_group(group):
    """Remove an explicit offset group and reparent its children while preserving world pose."""
    cmds = _cmds(); _require_node(cmds, group, "Offset group")
    group = _long_name(cmds, group)
    parents = cmds.listRelatives(group, parent=True, fullPath=True) or []
    parent = parents[0] if parents else None
    children = cmds.listRelatives(group, children=True, fullPath=True, type="transform") or []
    restored = []
    for child in children:
        if parent:
            child = cmds.parent(child, parent, absolute=True)[0]
        else:
            child = cmds.parent(child, world=True, absolute=True)[0]
        restored.append(child)
    cmds.delete(group)
    return {"group": group, "parent": parent, "children": tuple(restored)}
